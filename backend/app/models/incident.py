"""Incident / case management models.

Incidents aggregate related alerts into a single triage → investigate →
escalate → resolve → close workflow owned by SOC analysts.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.base import Base, BigIntPK, IdMixin, TimestampMixin


class Incident(Base, IdMixin, TimestampMixin):
    __tablename__ = "incidents"

    incident_id = Column(String(40), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, default="medium", index=True)
    status = Column(String(20), nullable=False, default="triaging", index=True)
    category = Column(String(60), nullable=True)
    source = Column(String(60), nullable=True)

    unit_id = Column(String(32), ForeignKey("units.id"), nullable=True, index=True)
    hostname = Column(String(120), nullable=True)
    source_ip = Column(String(45), nullable=True)
    username = Column(String(120), nullable=True)

    mitre_technique = Column(String(20), nullable=True)
    mitre_name = Column(String(200), nullable=True)
    risk_score = Column(Integer, nullable=False, default=0)

    alert_count = Column(Integer, nullable=False, default=0)
    event_count = Column(Integer, nullable=False, default=0)

    assigned_to = Column(String(32), ForeignKey("users.id"), nullable=True)
    created_by = Column(String(32), ForeignKey("users.id"), nullable=True)

    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)


class IncidentAlert(Base, TimestampMixin):
    __tablename__ = "incident_alerts"

    id = Column(BigIntPK, primary_key=True, autoincrement=True)
    incident_id = Column(String(32), ForeignKey("incidents.id"), nullable=False, index=True)
    alert_id = Column(String(32), ForeignKey("alerts.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)


class IncidentNote(Base, TimestampMixin):
    __tablename__ = "incident_notes"

    id = Column(BigIntPK, primary_key=True, autoincrement=True)
    incident_id = Column(String(32), ForeignKey("incidents.id"), nullable=False, index=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=True)
    username = Column(String(120), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
