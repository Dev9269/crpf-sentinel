from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text

from app.database.base import Base, IdMixin, TimestampMixin


class DetectionRule(Base, IdMixin, TimestampMixin):
    __tablename__ = "detection_rules"

    rule_id = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(60), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    event_id = Column(JSON, nullable=False, default=list)
    conditions = Column(JSON, nullable=False, default=dict)
    correlation_type = Column(String(20), nullable=False, default="none")
    threshold = Column(Integer, nullable=False, default=1)
    time_window_seconds = Column(Integer, nullable=False, default=300)
    correlation_key = Column(String(60), nullable=True)
    mitre_technique = Column(String(20), nullable=True)
    mitre_name = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, default="enabled", index=True)
    created_by = Column(String(32), ForeignKey("users.id"), nullable=True)
    times_matched = Column(Integer, nullable=False, default=0)
    last_matched_at = Column(DateTime(timezone=True), nullable=True)
