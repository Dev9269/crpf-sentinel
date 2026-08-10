"""Audit log and notification endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.database.session import get_db
from app.models.audit import AuditLog, Notification
from app.models.user import User

router = APIRouter(tags=["audit"])


@router.get("/audit-logs")
def list_audit_logs(
    action: str | None = Query(None),
    category: str | None = Query(None),
    q: str | None = Query(None, max_length=120),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    _=Depends(require_permission("audit.view")),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if category:
        query = query.filter(AuditLog.category == category)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                AuditLog.username.ilike(like),
                AuditLog.action.ilike(like),
                AuditLog.category.ilike(like),
            )
        )
    total = query.count()
    rows = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        {
            "id": a.id,
            "user_id": a.user_id,
            "username": a.username,
            "action": a.action,
            "category": a.category,
            "details": a.details,
            "ip_address": a.ip_address,
            "created_at": a.created_at,
        }
        for a in rows
    ]
    return {
        "items": items,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.get("/notifications")
def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    _=Depends(get_current_user),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "type": n.type,
            "severity": n.severity,
            "title": n.title,
            "message": n.message,
            "alert_id": n.alert_id,
            "is_read": n.is_read,
            "created_at": n.created_at,
        }
        for n in rows
    ]


@router.get("/notifications/unread-count")
def unread_count(_=Depends(get_current_user), user=Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).count()
    return {"count": count}


@router.post("/notifications/{notification_id}/read", status_code=204)
def mark_read(notification_id: str, _=Depends(get_current_user), user=Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if notification:
        notification.is_read = True
        db.add(notification)
        db.commit()
    return None


@router.post("/notifications/read-all", status_code=204)
def mark_all_read(_=Depends(get_current_user), user=Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id).update({"is_read": True})
    db.commit()
    return None
