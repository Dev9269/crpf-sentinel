"""Asset inventory aggregated from agents and observed event/alert activity."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission, scope_unit_ids
from app.database.session import get_db
from app.models.agent import Agent
from app.models.alert import Alert
from app.models.event import NormalizedEvent
from app.models.unit import Unit

router = APIRouter(tags=["assets"])

_SEV_RANK = case(
    (Alert.severity == "critical", 4),
    (Alert.severity == "high", 3),
    (Alert.severity == "medium", 2),
    (Alert.severity == "low", 1),
    else_=0,
)
_RANK_SEV = {4: "critical", 3: "high", 2: "medium", 1: "low"}


@router.get("/assets")
def list_assets(
    unit_id: str | None = Query(None),
    status: str | None = Query(None),
    _=Depends(require_permission("logs.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Host-level inventory: one row per monitored asset (agent)."""
    unit_scope = scope_unit_ids(user)
    query = db.query(Agent)
    if unit_scope:
        query = query.filter(Agent.unit_id.in_(unit_scope))
    if unit_id:
        query = query.filter(Agent.unit_id == unit_id)
    if status:
        query = query.filter(Agent.status == status)
    agents = query.order_by(Agent.hostname.asc()).all()

    units = {u.id: u for u in db.query(Unit).all()}

    event_rows = (
        db.query(NormalizedEvent.agent_id, func.count(NormalizedEvent.id))
        .group_by(NormalizedEvent.agent_id)
        .all()
    )
    event_counts = {row[0]: row[1] for row in event_rows}

    alert_rows = (
        db.query(Alert.agent_id, func.count(Alert.id), func.max(_SEV_RANK))
        .group_by(Alert.agent_id)
        .all()
    )
    alert_stats = {
        row[0]: {"count": row[1], "max_severity": _RANK_SEV.get(row[2])} for row in alert_rows
    }

    open_rows = (
        db.query(Alert.agent_id, func.count(Alert.id))
        .filter(Alert.status.in_(["open", "investigating"]))
        .group_by(Alert.agent_id)
        .all()
    )
    open_counts = {row[0]: row[1] for row in open_rows}

    items = []
    for agent in agents:
        astat = alert_stats.get(agent.id, {"count": 0, "max_severity": None})
        items.append(
            {
                "hostname": agent.hostname,
                "unit_id": agent.unit_id,
                "unit_name": units[agent.unit_id].unit_code if agent.unit_id in units else None,
                "unit": units[agent.unit_id].name if agent.unit_id in units else None,
                "ip_address": agent.ip_address,
                "os_version": agent.os_version,
                "status": agent.status,
                "last_seen_at": agent.last_seen_at,
                "events_per_sec": agent.events_per_sec,
                "total_events": event_counts.get(agent.id, 0),
                "open_alerts": open_counts.get(agent.id, 0),
                "total_alerts": astat["count"],
                "max_alert_severity": astat["max_severity"],
                "risk_score": _risk(astat["count"], open_counts.get(agent.id, 0), astat["max_severity"]),
            }
        )

    return {"items": items, "total": len(items)}


def _risk(total_alerts: int, open_alerts: int, max_severity: str | None) -> int:
    score = min(open_alerts, 10) * 5
    if max_severity == "critical":
        score += 30
    elif max_severity == "high":
        score += 20
    elif max_severity == "medium":
        score += 10
    return min(100, score)
