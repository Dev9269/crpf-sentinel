"""Detection rule builder + management endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.deps import client_ip, get_current_user, require_permission
from app.core.exceptions import ConflictError, NotFoundError
from app.database.session import get_db
from app.detection.matcher import event_matches
from app.models.alert import Alert
from app.models.rule import DetectionRule
from app.models.user import User
from app.schemas.rule import RuleCreate, RuleOut, RuleTestRequest, RuleTestResult, RuleUpdate
from app.services.audit import record_audit

router = APIRouter(tags=["rules"])


def _to_out(r: DetectionRule) -> RuleOut:
    return RuleOut(
        id=r.id,
        rule_id=r.rule_id,
        name=r.name,
        description=r.description,
        category=r.category,
        severity=r.severity,
        event_id=r.event_id or [],
        conditions=r.conditions or {},
        correlation_type=r.correlation_type,
        threshold=r.threshold,
        time_window_seconds=r.time_window_seconds,
        correlation_key=r.correlation_key,
        mitre_technique=r.mitre_technique,
        mitre_name=r.mitre_name,
        status=r.status,
        times_matched=r.times_matched,
        last_matched_at=r.last_matched_at,
        created_by=r.created_by,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.get("/rules")
def list_rules(
    category: str | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    q: str | None = Query(None, max_length=120),
    _=Depends(require_permission("rules.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(DetectionRule)
    if category:
        query = query.filter(DetectionRule.category == category)
    if severity:
        query = query.filter(DetectionRule.severity == severity)
    if status:
        query = query.filter(DetectionRule.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            func.lower(DetectionRule.name).like(like)
            | func.lower(DetectionRule.rule_id).like(like)
        )
    rows = query.order_by(DetectionRule.created_at.asc()).all()
    return [_to_out(r).model_dump() for r in rows]


@router.post("/rules", response_model=RuleOut, status_code=201)
def create_rule(
    body: RuleCreate,
    request: Request,
    _=Depends(require_permission("rules.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = db.query(DetectionRule).filter(DetectionRule.rule_id == body.rule_id).first()
    if exists:
        raise ConflictError("RULE_EXISTS", f"Rule id {body.rule_id} already exists")
    rule = DetectionRule(
        id=uuid.uuid4().hex[:16],
        created_by=user.id,
        **body.model_dump(),
    )
    db.add(rule)
    record_audit(
        db, "rule_created", "rules", username=user.username, user_id=user.id,
        ip_address=client_ip(request), details={"rule_id": body.rule_id, "name": body.name},
    )
    db.commit()
    return _to_out(rule)


@router.put("/rules/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: str,
    body: RuleUpdate,
    request: Request,
    _=Depends(require_permission("rules.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = db.query(DetectionRule).filter(or_(DetectionRule.id == rule_id, DetectionRule.rule_id == rule_id)).first()
    if rule is None:
        raise NotFoundError("RULE_NOT_FOUND", "Rule not found")
    changes = {}
    for field, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(rule, field, value)
            changes[field] = value
    db.add(rule)
    record_audit(
        db, "rule_updated", "rules", username=user.username, user_id=user.id,
        ip_address=client_ip(request), details={"rule_id": rule.rule_id, "changes": changes},
    )
    db.commit()
    return _to_out(rule)


@router.delete("/rules/{rule_id}", status_code=204)
def delete_rule(
    rule_id: str,
    request: Request,
    _=Depends(require_permission("rules.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = db.query(DetectionRule).filter(or_(DetectionRule.id == rule_id, DetectionRule.rule_id == rule_id)).first()
    if rule is None:
        raise NotFoundError("RULE_NOT_FOUND", "Rule not found")
    db.delete(rule)
    record_audit(
        db, "rule_deleted", "rules", username=user.username, user_id=user.id,
        ip_address=client_ip(request), details={"rule_id": rule.rule_id},
    )
    db.commit()
    return None


@router.get("/rules/{rule_id}", response_model=RuleOut)
def get_rule(rule_id: str, _=Depends(require_permission("rules.view")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(DetectionRule).filter(or_(DetectionRule.id == rule_id, DetectionRule.rule_id == rule_id)).first()
    if rule is None:
        raise NotFoundError("RULE_NOT_FOUND", "Rule not found")
    return _to_out(rule)


@router.post("/rules/{rule_id}/test", response_model=RuleTestResult)
def test_rule(
    rule_id: str,
    body: RuleTestRequest,
    _=Depends(require_permission("rules.manage")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = db.query(DetectionRule).filter(or_(DetectionRule.id == rule_id, DetectionRule.rule_id == rule_id)).first()
    if rule is None:
        raise NotFoundError("RULE_NOT_FOUND", "Rule not found")

    event = {
        "event_id": body.event_id or (rule.event_id[0] if rule.event_id else None),
        "hostname": body.hostname,
        "username": body.username,
        "source_ip": body.source_ip,
        "process_name": body.process_name,
        "command_line": body.command_line,
        "severity": "medium",
        **(body.data or {}),
    }
    matched, reason = event_matches(event, rule)
    details: dict = {"reason": reason or "no match", "correlation_type": rule.correlation_type}

    will_alert = False
    if not matched:
        explanation = "Static conditions did not match"
    elif rule.correlation_type == "count":
        if rule.correlation_key:
            key_value = event.get(rule.correlation_key)
            will_alert = body.count >= rule.threshold and bool(key_value)
            explanation = (
                f"{body.count} occurrences {'meet' if will_alert else 'do not meet'} threshold {rule.threshold} "
                f"in {rule.time_window_seconds}s window"
            )
        else:
            will_alert = True
            explanation = "Static match (no correlation key)"
    elif rule.correlation_type == "sequence":
        will_alert = body.count >= rule.threshold
        explanation = f"{body.count} failures in window followed by success -> {'ALERT' if will_alert else 'below threshold'}"
    else:
        will_alert = True
        explanation = "Static signature match"

    if will_alert:
        details["predicted_alert"] = {
            "title": rule.name,
            "severity": rule.severity,
            "mitre_technique": rule.mitre_technique,
        }
    return RuleTestResult(
        matched=matched,
        reason=explanation,
        will_create_alert=will_alert,
        details=details,
    )


@router.get("/rules/{rule_id}/stats")
def rule_stats(rule_id: str, _=Depends(require_permission("rules.view")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(DetectionRule).filter(or_(DetectionRule.id == rule_id, DetectionRule.rule_id == rule_id)).first()
    if rule is None:
        raise NotFoundError("RULE_NOT_FOUND", "Rule not found")
    total = db.query(func.count(Alert.id)).filter(Alert.rule_id == rule.id).scalar() or 0
    open_count = (
        db.query(func.count(Alert.id))
        .filter(Alert.rule_id == rule.id, Alert.status.in_(["open", "investigating"]))
        .scalar() or 0
    )
    resolved = total - open_count
    return {
        "rule_id": rule.rule_id,
        "total_alerts": total,
        "open_alerts": open_count,
        "resolved_alerts": resolved,
        "times_matched": rule.times_matched,
    }


@router.get("/rules/{rule_id}/matches")
def rule_matches(rule_id: str, limit: int = Query(50, ge=1, le=200), _=Depends(require_permission("rules.view")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(DetectionRule).filter(or_(DetectionRule.id == rule_id, DetectionRule.rule_id == rule_id)).first()
    if rule is None:
        raise NotFoundError("RULE_NOT_FOUND", "Rule not found")
    rows = (
        db.query(Alert)
        .filter(Alert.rule_id == rule.id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "alert_id": a.alert_id,
            "title": a.title,
            "severity": a.severity,
            "status": a.status,
            "hostname": a.hostname,
            "source_ip": a.source_ip,
            "risk_score": a.risk_score,
            "created_at": a.created_at.isoformat(),
        }
        for a in rows
    ]


@router.get("/signatures")
def signatures(_=Depends(require_permission("rules.view")), user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Signature library grouped by MITRE technique."""
    rows = db.query(DetectionRule).filter(DetectionRule.status == "enabled").all()
    grouped: dict[str, list] = {}
    for r in rows:
        key = r.mitre_technique or "Unmapped"
        grouped.setdefault(key, []).append(
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "severity": r.severity,
                "event_id": r.event_id,
                "mitre_name": r.mitre_name,
                "times_matched": r.times_matched,
            }
        )
    return grouped
