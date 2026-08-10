from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RuleBase(BaseModel):
    rule_id: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=3, max_length=200)
    description: str | None = None
    category: str = Field(min_length=2, max_length=60)
    severity: str = Field(pattern=r"^(critical|high|medium|low|informational)$")
    event_id: list[int] = Field(default_factory=list)
    conditions: dict[str, Any] = Field(default_factory=dict)
    correlation_type: str = Field(default="none", pattern=r"^(none|count|sequence)$")
    threshold: int = Field(default=1, ge=1, le=100000)
    time_window_seconds: int = Field(default=300, ge=1, le=86400)
    correlation_key: str | None = None
    mitre_technique: str | None = None
    mitre_name: str | None = None
    status: str = Field(default="enabled", pattern=r"^(enabled|disabled)$")


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    severity: str | None = None
    event_id: list[int] | None = None
    conditions: dict[str, Any] | None = None
    correlation_type: str | None = None
    threshold: int | None = None
    time_window_seconds: int | None = None
    correlation_key: str | None = None
    mitre_technique: str | None = None
    mitre_name: str | None = None
    status: str | None = None


class RuleOut(RuleBase):
    id: str
    times_matched: int
    last_matched_at: datetime | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class RuleTestRequest(BaseModel):
    event_id: int | None = None
    hostname: str | None = None
    username: str | None = None
    source_ip: str | None = None
    process_name: str | None = None
    command_line: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    count: int = Field(default=1, ge=1, le=1000)


class RuleTestResult(BaseModel):
    matched: bool
    reason: str
    will_create_alert: bool
    details: dict[str, Any] | None = None
