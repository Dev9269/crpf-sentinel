"""Unit management and unit overview endpoints."""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import client_ip, get_current_user, require_permission
from app.core.exceptions import ConflictError, NotFoundError
from app.database.session import get_db
from app.models.agent import Agent
from app.models.alert import Alert
from app.models.event import NormalizedEvent
from app.models.unit import Unit
from app.models.user import User
from app.schemas.unit import UnitCreate, UnitOut, UnitStats, UnitUpdate
from app.services.audit import record_audit

router = APIRouter(tags=["units"])


@router.get("/units")
def list_units(_=Depends(require_permission("units.view")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Unit).order_by(Unit.name)
    if user.role.name == "unit_admin" and user.unit_id:
        query = query.filter(Unit.id == user.unit_id)
    rows = query.all()
    return [UnitOut.model_validate(u).model_dump() for u in rows]


@router.get("/units/{unit_id}", response_model=UnitStats)
def unit_detail(unit_id: str, _=Depends(require_permission("units.view")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if unit is None:
        raise NotFoundError("UNIT_NOT_FOUND", "Unit not found")
    if user.role.name == "unit_admin" and unit.id != user.unit_id:
        raise NotFoundError("UNIT_NOT_FOUND", "Unit not found")
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    agents = db.query(func.count(Agent.id)).filter(Agent.unit_id == unit.id).scalar() or 0
    online = db.query(func.count(Agent.id)).filter(Agent.unit_id == unit.id, Agent.status == "online").scalar() or 0
    events = db.query(func.count(NormalizedEvent.id)).filter(NormalizedEvent.unit_id == unit.id, NormalizedEvent.timestamp >= since).scalar() or 0
    alerts = db.query(func.count(Alert.id)).filter(Alert.unit_id == unit.id, Alert.created_at >= since).scalar() or 0
    open_alerts = db.query(func.count(Alert.id)).filter(Alert.unit_id == unit.id, Alert.status.in_(["open", "investigating"])).scalar() or 0

    risk = 0
    counts = dict(
        db.query(Alert.severity, func.count(Alert.id))
        .filter(Alert.unit_id == unit.id, Alert.status.in_(["open", "investigating"]))
        .group_by(Alert.severity)
        .all()
    )
    risk += counts.get("critical", 0) * 30 + counts.get("high", 0) * 15 + counts.get("medium", 0) * 8

    return UnitStats(
        unit=UnitOut.model_validate(unit),
        agent_count=agents,
        agents_online=online,
        event_count_24h=events,
        alert_count_24h=alerts,
        open_alert_count=open_alerts,
        risk_score=min(100, risk),
    )


@router.post("/units", response_model=UnitOut, status_code=201)
def create_unit(
    body: UnitCreate,
    request: Request,
    _=Depends(require_permission("units.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = db.query(Unit).filter(Unit.unit_code == body.unit_code).first()
    if exists:
        raise ConflictError("UNIT_EXISTS", f"Unit {body.unit_code} already exists")
    unit = Unit(id=uuid.uuid4().hex[:16], **body.model_dump())
    db.add(unit)
    record_audit(
        db, "unit_created", "units", username=user.username, user_id=user.id,
        ip_address=client_ip(request), details={"unit_code": body.unit_code},
    )
    db.commit()
    return UnitOut.model_validate(unit)


@router.patch("/units/{unit_id}", response_model=UnitOut)
def update_unit(
    unit_id: str,
    body: UnitUpdate,
    request: Request,
    _=Depends(require_permission("units.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if unit is None:
        raise NotFoundError("UNIT_NOT_FOUND", "Unit not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(unit, field, value)
    db.add(unit)
    db.commit()
    return UnitOut.model_validate(unit)
