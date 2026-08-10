from app.database.base import BigIntPK
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text

from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigIntPK, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=True)
    username = Column(String(64), nullable=True)
    action = Column(String(80), nullable=False, index=True)
    category = Column(String(40), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False, default="alert")
    severity = Column(String(20), nullable=False, default="info")
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    alert_id = Column(String(32), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
