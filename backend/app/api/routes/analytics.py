"""Threat analytics: top indicators, hosts, rules and technique breakdowns."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission, scope_unit_ids
from app.database.session import get_db
from app.models.alert import Alert
from app.models.event import NormalizedEvent
from app.models.rule import DetectionRule

router = APIRouter(tags=["analytics"])


def _base_scoped(query, unit_col, user):
    unit_scope = scope_unit_ids(user)
    if unit_scope:
        return query.filter(unit_col.in_(unit_scope))
    return query


@router.get("/analytics/top")
def analytics_top(
    limit: int = Query(10, ge=1, le=50),
    _=Depends(require_permission("dashboard.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Top source IPs, usernames, hosts and alert rules."""

    def top_events(column):
        query = db.query(column, func.count(NormalizedEvent.id))
        query = _base_scoped(query, NormalizedEvent.unit_id, user)
        query = query.filter(column.isnot(None)).group_by(column)
        return query.order_by(func.count(NormalizedEvent.id).desc()).limit(limit).all()

    def top_alerts(column):
        query = db.query(column, func.count(Alert.id))
        query = _base_scoped(query, Alert.unit_id, user)
        query = query.filter(column.isnot(None)).group_by(column)
        return query.order_by(func.count(Alert.id).desc()).limit(limit).all()

    return {
        "top_source_ips": [
            {"value": row[0], "count": row[1]} for row in top_events(NormalizedEvent.source_ip)
        ],
        "top_usernames": [
            {"value": row[0], "count": row[1]} for row in top_events(NormalizedEvent.username)
        ],
        "top_hosts": [
            {"value": row[0], "count": row[1]} for row in top_events(NormalizedEvent.hostname)
        ],
        "top_alert_rules": [
            {"value": row[0], "count": row[1]} for row in top_alerts(Alert.rule_id)
        ],
    }


@router.get("/analytics/threat-activity")
def analytics_threat_activity(
    _=Depends(require_permission("dashboard.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Alert volumes by rule and by MITRE technique."""
    rule_query = _base_scoped(
        db.query(Alert.rule_id, func.count(Alert.id)),
        Alert.unit_id,
        user,
    )
    rule_rows = (
        rule_query.group_by(Alert.rule_id)
        .order_by(func.count(Alert.id).desc())
        .limit(20)
        .all()
    )
    rules_by_id = {r.id: r for r in db.query(DetectionRule).all()}

    tech_query = _base_scoped(
        db.query(Alert.mitre_technique, func.count(Alert.id)),
        Alert.unit_id,
        user,
    )
    tech_rows = (
        tech_query.filter(Alert.mitre_technique.isnot(None))
        .group_by(Alert.mitre_technique)
        .order_by(func.count(Alert.id).desc())
        .all()
    )

    from app.detection.mitre import MITRE_MAP

    return {
        "alerts_by_rule": [
            {
                "rule_id": row[0],
                "rule_name": rules_by_id.get(row[0]).name if rules_by_id.get(row[0]) else "IOC Match",
                "severity": rules_by_id.get(row[0]).severity if rules_by_id.get(row[0]) else "medium",
                "count": row[1],
            }
            for row in rule_rows
        ],
        "alerts_by_technique": [
            {
                "technique": row[0],
                "name": MITRE_MAP.get(row[0], {}).get("name"),
                "count": row[1],
            }
            for row in tech_rows
        ],
    }
