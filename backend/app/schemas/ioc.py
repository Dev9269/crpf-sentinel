from datetime import datetime

from pydantic import BaseModel, Field


class IocBase(BaseModel):
    ioc_type: str = Field(pattern=r"^(ip|domain|hash|url|command)$")
    value: str = Field(min_length=1, max_length=512)
    description: str | None = None
    source: str = Field(default="manual", max_length=60)
    severity: str = Field(default="medium", pattern=r"^(critical|high|medium|low|informational)$")
    threat_type: str | None = None
    reference_url: str | None = None
    status: str = Field(default="enabled", pattern=r"^(enabled|disabled)$")


class IocCreate(IocBase):
    pass


class IocUpdate(BaseModel):
    description: str | None = None
    source: str | None = None
    severity: str | None = None
    threat_type: str | None = None
    reference_url: str | None = None
    status: str | None = Field(default=None, pattern=r"^(enabled|disabled)$")


class IocOut(IocBase):
    id: str
    ioc_id: str
    times_matched: int
    last_matched_at: datetime | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
