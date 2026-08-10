from app.database.base import BigIntPK
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String, Text

from app.database.base import Base, IdMixin, TimestampMixin


class Alert(Base, IdMixin, TimestampMixin):
    __tablename__ = "alerts"

    alert_id = Column(String(40), unique=True, nullable=False, index=True)
    rule_id = Column(String(32), ForeignKey("detection_rules.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, index=True)
    unit_id = Column(String(32), ForeignKey("units.id"), nullable=True, index=True)
    agent_id = Column(String(32), ForeignKey("agents.id"), nullable=True)
    hostname = Column(String(120), nullable=True)
    source_ip = Column(String(45), nullable=True)
    username = Column(String(120), nullable=True)
    event_count = Column(Integer, nullable=False, default=1)
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default="open", index=True)
    risk_score = Column(Integer, nullable=False, default=0)
    risk_factors = Column(JSON, nullable=True)
    mitre_technique = Column(String(20), nullable=True)
    mitre_name = Column(String(200), nullable=True)
    detection_explanation = Column(Text, nullable=True)
    recommended_steps = Column(JSON, nullable=True)
    assigned_to = Column(String(32), ForeignKey("users.id"), nullable=True)
    correlation_key = Column(String(255), nullable=True, index=True)


class AlertEvent(Base, TimestampMixin):
    __tablename__ = "alert_events"

    id = Column(BigIntPK, primary_key=True, autoincrement=True)
    alert_id = Column(String(32), ForeignKey("alerts.id"), nullable=False, index=True)
    normalized_event_id = Column(BigIntPK, ForeignKey("normalized_events.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
