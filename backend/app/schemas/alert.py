from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.log import EventOut


class AlertOut(BaseModel):
    id: str
    alert_id: str
    rule_id: str | None = None
    rule_name: str | None = None
    title: str
    description: str | None = None
    severity: str
    unit_id: str | None = None
    unit_name: str | None = None
    agent_id: str | None = None
    hostname: str | None = None
    source_ip: str | None = None
    username: str | None = None
    event_count: int
    first_seen: datetime
    last_seen: datetime
    status: str
    risk_score: int
    risk_factors: list[dict[str, Any]] | None = None
    mitre_technique: str | None = None
    mitre_name: str | None = None
    detection_explanation: str | None = None
    recommended_steps: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    status: str | None = Field(default=None, pattern=r"^(open|investigating|resolved|false_positive)$")
    assigned_to: str | None = None


class AlertDetail(AlertOut):
    events: list[EventOut] = Field(default_factory=list)


class AlertEventOut(BaseModel):
    id: int
    alert_id: str
    normalized_event_id: int
    timestamp: datetime
    event: EventOut | None = None
