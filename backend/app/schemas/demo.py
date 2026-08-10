from pydantic import BaseModel, Field


class ScenarioOut(BaseModel):
    scenario: str
    name: str
    events_ingested: int
    alerts_triggered: int
    alert_ids: list[str]
    explanation: str


class SeedResult(BaseModel):
    units: int
    agents: int
    events: int
    rules: int
    users: int
    alerts: int
    demo_notice: str
