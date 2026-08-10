"""Audit logging for administrative and security-relevant actions."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def record_audit(
    db: Session,
    action: str,
    category: str,
    username: str | None = None,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        category=category,
        details=details or {},
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    return entry
