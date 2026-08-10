from app.database.base import BigIntPK
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text

from app.database.base import Base, TimestampMixin


class Log(Base, TimestampMixin):
    """Raw ingested log payload (before normalization)."""

    __tablename__ = "logs"

    id = Column(BigIntPK, primary_key=True, autoincrement=True)
    unit_id = Column(String(32), ForeignKey("units.id"), nullable=True, index=True)
    agent_id = Column(String(32), ForeignKey("agents.id"), nullable=True, index=True)
    source = Column(String(30), nullable=False, default="windows")
    format = Column(String(20), nullable=False, default="json")
    raw_log = Column(Text, nullable=False)
    parsed = Column(Boolean, nullable=False, default=False)
    received_at = Column(DateTime(timezone=True), nullable=False, index=True)
    normalized_event_id = Column(BigIntPK, ForeignKey("normalized_events.id"), nullable=True)
