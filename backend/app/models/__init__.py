"""Model registry — import every model so metadata is complete."""

from app.database.base import Base
from app.models.agent import Agent
from app.models.alert import Alert, AlertEvent
from app.models.audit import AuditLog, Notification
from app.models.event import NormalizedEvent
from app.models.incident import Incident, IncidentAlert, IncidentNote
from app.models.ioc import IocEntry
from app.models.log import Log
from app.models.rule import DetectionRule
from app.models.unit import Unit
from app.models.user import Role, User

__all__ = [
    "Base",
    "Role",
    "User",
    "Unit",
    "Agent",
    "Log",
    "NormalizedEvent",
    "DetectionRule",
    "Alert",
    "AlertEvent",
    "AuditLog",
    "Notification",
    "Incident",
    "IncidentAlert",
    "IncidentNote",
    "IocEntry",
]
