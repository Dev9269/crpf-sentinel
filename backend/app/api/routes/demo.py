"""Demo mode endpoints: seed data + safe synthetic attack scenarios.

All data is synthetic. Nothing here executes attacks — it only generates
fictional log records that flow through the real detection pipeline.
"""

from fastapi import APIRouter, Depends, Request

from app.core.deps import client_ip, get_current_user, require_permission
from app.core.exceptions import NotFoundError
from app.database.session import get_db
from app.models.alert import Alert
from app.schemas.demo import ScenarioOut, SeedResult
from app.seed.demo_data import DEMO_NOTICE, seed_agents, seed_demo_users, seed_units
from app.seed.demo_rules import seed_rules
from app.simulation.scenarios import SCENARIOS, run_scenario
from app.database.init_db import seed_roles

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", response_model=SeedResult)
def seed_demo(
    request: Request,
    _=Depends(require_permission("demo.run")),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    roles = seed_roles(db)
    units = seed_units(db)
    agents = seed_agents(db, units)
    seed_demo_users(db, units, roles)
    rules_seeded = seed_rules(db, created_by=user)
    from app.seed.demo_data import seed_demo_data

    demo = seed_demo_data(db, units, agents)
    alert_count = db.query(Alert).count()
    return SeedResult(
        units=len(units),
        agents=len(agents),
        events=demo.get("events_created", 0),
        rules=rules_seeded,
        users=3,
        alerts=alert_count,
        demo_notice=DEMO_NOTICE,
    )


@router.get("/scenarios")
def list_scenarios(_=Depends(get_current_user)):
    return [
        {"id": sid, "name": meta["name"], "explanation": meta["explanation"]}
        for sid, meta in SCENARIOS.items()
    ]


@router.post("/scenarios/{scenario}", response_model=ScenarioOut)
def trigger_scenario(
    scenario: str,
    request: Request,
    _=Depends(require_permission("demo.run")),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    if scenario not in SCENARIOS:
        raise NotFoundError("UNKNOWN_SCENARIO", f"Unknown scenario: {scenario}")
    result = run_scenario(db, scenario)
    from app.services.audit import record_audit

    record_audit(
        db, "demo_scenario_triggered", "demo", username=user.username, user_id=user.id,
        ip_address=client_ip(request), details={"scenario": scenario},
    )
    db.commit()
    return ScenarioOut(**result)


@router.get("/status")
def demo_status(_=Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import func

    from app.models.agent import Agent
    from app.models.alert import Alert
    from app.models.event import NormalizedEvent
    from app.models.unit import Unit

    return {
        "active": True,
        "notice": DEMO_NOTICE,
        "units": db.query(func.count(Unit.id)).scalar(),
        "agents": db.query(func.count(Agent.id)).scalar(),
        "events": db.query(func.count(NormalizedEvent.id)).scalar(),
        "alerts": db.query(func.count(Alert.id)).scalar(),
    }
