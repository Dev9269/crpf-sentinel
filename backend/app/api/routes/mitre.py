"""MITRE ATT&CK coverage and alert heatmap endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.database.session import get_db
from app.models.alert import Alert
from app.models.rule import DetectionRule

router = APIRouter(tags=["mitre"])

_SEV_RANK = case(
    (Alert.severity == "critical", 4),
    (Alert.severity == "high", 3),
    (Alert.severity == "medium", 2),
    (Alert.severity == "low", 1),
    else_=0,
)
_RANK_SEV = {4: "critical", 3: "high", 2: "medium", 1: "low"}


@router.get("/mitre/techniques")
def mitre_techniques(
    _=Depends(require_permission("threat_intel.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Per-technique coverage: enabled rules, total and open alerts, max severity."""
    rules = (
        db.query(DetectionRule)
        .filter(DetectionRule.mitre_technique.isnot(None))
        .all()
    )

    alert_rows = (
        db.query(Alert.mitre_technique, func.count(Alert.id), func.max(_SEV_RANK))
        .filter(Alert.mitre_technique.isnot(None))
        .group_by(Alert.mitre_technique)
        .all()
    )
    alert_stats = {
        row[0]: {"count": row[1], "max_severity": _RANK_SEV.get(row[2])} for row in alert_rows
    }

    open_rows = (
        db.query(Alert.mitre_technique, func.count(Alert.id))
        .filter(Alert.mitre_technique.isnot(None), Alert.status.in_(["open", "investigating"]))
        .group_by(Alert.mitre_technique)
        .all()
    )
    open_counts = {row[0]: row[1] for row in open_rows}

    from app.detection.mitre import MITRE_MAP

    covered: dict[str, dict] = {}
    for rule in rules:
        tech = rule.mitre_technique
        entry = covered.setdefault(
            tech,
            {
                "technique": tech,
                "name": MITRE_MAP.get(tech, {}).get("name"),
                "sub": MITRE_MAP.get(tech, {}).get("sub"),
                "rules": 0,
                "alerts": 0,
                "open_alerts": 0,
                "max_severity": None,
            },
        )
        entry["rules"] += 1
        entry["alerts"] += alert_stats.get(tech, {}).get("count", 0)
        entry["open_alerts"] += open_counts.get(tech, 0)
        sev = alert_stats.get(tech, {}).get("max_severity")
        if sev and (entry["max_severity"] is None or _sev_rank(sev) > _sev_rank(entry["max_severity"])):
            entry["max_severity"] = sev

    items = sorted(covered.values(), key=lambda x: (-x["alerts"], x["technique"]))
    return {"items": items, "total_techniques": len(items)}


def _sev_rank(severity: str) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(severity, 0)
