from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.alert import AlertOut


class IncidentBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    severity: str = Field(default="medium", pattern=r"^(critical|high|medium|low|informational)$")
    category: str | None = None
    source: str | None = None
    unit_id: str | None = None
    hostname: str | None = None
    source_ip: str | None = None
    username: str | None = None
    mitre_technique: str | None = None
    mitre_name: str | None = None
    assigned_to: str | None = None


class IncidentCreate(IncidentBase):
    alert_ids: list[str] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = Field(
        default=None,
        pattern=r"^(triaging|investigating|escalated|resolved|closed)$",
    )
    category: str | None = None
    source: str | None = None
    hostname: str | None = None
    source_ip: str | None = None
    username: str | None = None
    mitre_technique: str | None = None
    mitre_name: str | None = None
    assigned_to: str | None = None


class IncidentOut(IncidentBase):
    id: str
    incident_id: str
    unit_name: str | None = None
    alert_count: int
    event_count: int
    risk_score: int
    status: str
    created_by: str | None = None
    first_seen: datetime
    last_seen: datetime
    resolved_at: datetime | None = None
    closed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class IncidentNoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class IncidentNoteOut(BaseModel):
    id: int
    incident_id: str
    user_id: str | None = None
    username: str
    content: str
    timestamp: datetime
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class IncidentDetail(IncidentOut):
    alerts: list[AlertOut] = Field(default_factory=list)
    notes: list[IncidentNoteOut] = Field(default_factory=list)
