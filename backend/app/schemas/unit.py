from pydantic import BaseModel, Field


class UnitOut(BaseModel):
    id: str
    unit_code: str
    name: str
    region: str | None = None
    city: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str

    model_config = {"from_attributes": True}


class UnitCreate(BaseModel):
    unit_code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=2, max_length=120)
    region: str | None = None
    city: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str = "operational"


class UnitUpdate(BaseModel):
    name: str | None = None
    region: str | None = None
    city: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str | None = None


class UnitStats(BaseModel):
    unit: UnitOut
    agent_count: int
    agents_online: int
    event_count_24h: int
    alert_count_24h: int
    open_alert_count: int
    risk_score: int
