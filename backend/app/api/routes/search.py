"""Global search across logs, alerts, incidents, rules, IOCs, agents and units."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission, scope_unit_ids
from app.database.session import get_db
from app.models.agent import Agent
from app.models.alert import Alert
from app.models.event import NormalizedEvent
from app.models.incident import Incident
from app.models.ioc import IocEntry
from app.models.rule import DetectionRule
from app.models.unit import Unit

router = APIRouter(tags=["search"])


@router.get("/search")
def global_search(
    q: str = Query(..., min_length=1, max_length=120),
    limit: int = Query(10, ge=1, le=50),
    _=Depends(require_permission("logs.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    needle = f"%{q.strip()}%"
    unit_scope = scope_unit_ids(user)
    # Rules and IOCs are platform-global configuration; unit admins are not
    # granted rules.view / threat_intel.view, so keep them out of search too.
    can_see_global = unit_scope is None

    def scoped(query, unit_col):
        if unit_scope:
            return query.filter(unit_col.in_(unit_scope))
        return query

    # Events
    event_query = scoped(
        db.query(NormalizedEvent).filter(
            or_(
                NormalizedEvent.hostname.ilike(needle),
                NormalizedEvent.username.ilike(needle),
                NormalizedEvent.source_ip.ilike(needle),
                NormalizedEvent.destination_ip.ilike(needle),
                NormalizedEvent.command_line.ilike(needle),
                NormalizedEvent.process_name.ilike(needle),
            )
        ),
        NormalizedEvent.unit_id,
    )
    events = event_query.order_by(NormalizedEvent.timestamp.desc()).limit(limit).all()

    # Alerts
    alert_query = scoped(
        db.query(Alert).filter(
            or_(
                Alert.alert_id.ilike(needle),
                Alert.title.ilike(needle),
                Alert.hostname.ilike(needle),
                Alert.source_ip.ilike(needle),
                Alert.username.ilike(needle),
            )
        ),
        Alert.unit_id,
    )
    alerts = alert_query.order_by(Alert.created_at.desc()).limit(limit).all()

    # Incidents
    inc_query = scoped(
        db.query(Incident).filter(
            or_(
                Incident.incident_id.ilike(needle),
                Incident.title.ilike(needle),
                Incident.hostname.ilike(needle),
                Incident.source_ip.ilike(needle),
                Incident.username.ilike(needle),
            )
        ),
        Incident.unit_id,
    )
    incidents = inc_query.order_by(Incident.created_at.desc()).limit(limit).all()

    rules = (
        db.query(DetectionRule)
        .filter(
            or_(
                DetectionRule.rule_id.ilike(needle),
                DetectionRule.name.ilike(needle),
            )
        )
        .order_by(DetectionRule.times_matched.desc())
        .limit(limit)
        .all()
        if can_see_global
        else []
    )

    iocs = (
        db.query(IocEntry)
        .filter(IocEntry.value.ilike(needle))
        .order_by(IocEntry.times_matched.desc())
        .limit(limit)
        .all()
        if can_see_global
        else []
    )

    agents = scoped(
        db.query(Agent)
        .filter(
            or_(
                Agent.agent_id.ilike(needle),
                Agent.hostname.ilike(needle),
                Agent.ip_address.ilike(needle),
            )
        ),
        Agent.unit_id,
    )
    agents = agents.limit(limit).all()

    units = scoped(
        db.query(Unit)
        .filter(
            or_(
                Unit.unit_code.ilike(needle),
                Unit.name.ilike(needle),
                Unit.city.ilike(needle),
            )
        ),
        Unit.id,
    )
    units = units.limit(limit).all()

    return {
        "q": q,
        "events": [
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "hostname": e.hostname,
                "event_id": e.event_id,
                "category": e.category,
                "severity": e.severity,
                "username": e.username,
                "source_ip": e.source_ip,
            }
            for e in events
        ],
        "alerts": [
            {
                "id": a.id,
                "alert_id": a.alert_id,
                "title": a.title,
                "severity": a.severity,
                "status": a.status,
                "hostname": a.hostname,
                "source_ip": a.source_ip,
                "created_at": a.created_at,
            }
            for a in alerts
        ],
        "incidents": [
            {
                "id": i.id,
                "incident_id": i.incident_id,
                "title": i.title,
                "severity": i.severity,
                "status": i.status,
                "hostname": i.hostname,
                "created_at": i.created_at,
            }
            for i in incidents
        ],
        "rules": [
            {"id": r.id, "rule_id": r.rule_id, "name": r.name, "severity": r.severity, "times_matched": r.times_matched}
            for r in rules
        ],
        "iocs": [
            {"id": i.id, "ioc_id": i.ioc_id, "ioc_type": i.ioc_type, "value": i.value, "severity": i.severity}
            for i in iocs
        ],
        "agents": [
            {"id": a.id, "agent_id": a.agent_id, "hostname": a.hostname, "ip_address": a.ip_address, "status": a.status}
            for a in agents
        ],
        "units": [
            {"id": u.id, "unit_code": u.unit_code, "name": u.name, "status": u.status}
            for u in units
        ],
    }
