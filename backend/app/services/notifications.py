"""In-app notification creation for alerts and system events."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit import Notification


def notify_user(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    severity: str = "info",
    type_: str = "alert",
    alert_id: str | None = None,
) -> Notification:
    notification = Notification(
        id=uuid.uuid4().hex[:16],
        user_id=user_id,
        title=title,
        message=message,
        severity=severity,
        type=type_,
        alert_id=alert_id,
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(notification)
    return notification
