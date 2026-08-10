"""Demo attack scenarios.

These generate SYNTHETIC logs only — nothing on disk is modified and no
real system is attacked. Events are pushed through the standard ingestion
pipeline (parse → normalize → detect → alert).
"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.unit import Unit
from app.services.ingest import ingest_payload

SCENARIOS = {
    "brute_force": {
        "name": "Brute Force (4625 x10 → 4624)",
        "explanation": "10 failed logons from a single source followed by a successful logon.",
    },
    "audit_clear": {
        "name": "Security Audit Log Cleared (1102)",
        "explanation": "Security event log cleared on a monitored host.",
    },
    "new_service": {
        "name": "New Service Installed (7045)",
        "explanation": "A new Windows service was registered.",
    },
    "powershell": {
        "name": "Suspicious PowerShell (4688)",
        "explanation": "Encoded PowerShell command observed in process creation.",
    },
    "user_created": {
        "name": "New User Account Created (4720)",
        "explanation": "A new local account was created.",
    },
    "credential_dumping": {
        "name": "Credential Dumping via LSASS Access (4663)",
        "explanation": "A process opened lsass.exe with a memory-read access mask, consistent with credential dumping tools.",
    },
    "lateral_movement": {
        "name": "Lateral Movement - Network Logon Sprawl (4624)",
        "explanation": "Successive Logon Type 3 network logons for one account across multiple hosts in a short window.",
    },
}


EVENT_COUNTS = {
    "brute_force": 10,
    "audit_clear": 1,
    "new_service": 1,
    "powershell": 1,
    "user_created": 1,
    "credential_dumping": 3,
    "lateral_movement": 4,
}


def _pick_agent(db: Session) -> tuple[Agent, Unit]:
    agent = (
        db.query(Agent)
        .join(Unit, Agent.unit_id == Unit.id)
        .filter(Agent.status == "online")
        .order_by(Agent.last_seen_at.desc())
        .first()
    )
    if agent is None:
        agent = db.query(Agent).first()
    if agent is None:
        raise RuntimeError("No agents seeded. Run the demo seed first.")
    unit = db.query(Unit).filter(Unit.id == agent.unit_id).first()
    return agent, unit


def _payload(event_id: int, computer: str, when: datetime, data: dict) -> dict:
    provider = {
        1102: "Microsoft-Windows-Eventlog",
        7045: "Service Control Manager",
    }.get(event_id, "Microsoft-Windows-Security-Auditing")
    return {
        "System": {"EventID": event_id, "Provider": {"Name": provider}, "Computer": computer, "TimeCreated": {"SystemTime": when.isoformat()}},
        "EventData": data,
    }


def run_scenario(db: Session, scenario: str) -> dict:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    agent, unit = _pick_agent(db)
    rng = random.Random()
    now = datetime.now(timezone.utc)
    source_ip = rng.choice(["203.0.113.77", "198.51.100.33", "192.0.2.101"])
    user = rng.choice(["administrator", "s.verma", "a.singh"])
    alert_ids: list[str] = []

    def run(events: list[dict]):
        for ev in events:
            payload = _payload(ev["event_id"], agent.hostname, ev["when"], ev.get("data") or {})
            result = ingest_payload(db, payload, agent=agent, unit=unit)
            alert_ids.extend(result.get("new_alert_ids", []))

    if scenario == "brute_force":
        base = now - timedelta(minutes=2)
        events = [
            {
                "event_id": 4625,
                "when": base + timedelta(seconds=9 * i),
                "data": {
                    "SubjectUserName": user,
                    "IpAddress": source_ip,
                    "Status": "0xC000006A",
                    "SubStatus": "0xC0000064",
                },
            }
            for i in range(10)
        ]
        events.append({
            "event_id": 4624,
            "when": base + timedelta(seconds=100),
            "data": {"SubjectUserName": user, "IpAddress": source_ip, "LogonType": "3"},
        })
        run(events)
    elif scenario == "audit_clear":
        run([{"event_id": 1102, "when": now, "data": {"SubjectUserName": user, "LogName": "Security"}}])
    elif scenario == "new_service":
        run([{
            "event_id": 7045, "when": now,
            "data": {"ServiceName": "RemoteAdminSvc", "ImagePath": "C:\\Windows\\Temp\\remadmin.exe"},
        }])
    elif scenario == "powershell":
        run([{
            "event_id": 4688, "when": now,
            "data": {
                "SubjectUserName": user,
                "NewProcessName": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "CommandLine": "powershell.exe -nop -w hidden -enc SQBFAFgAKAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkA",
            },
        }])
    elif scenario == "user_created":
        run([{
            "event_id": 4720, "when": now,
            "data": {"NewAccountName": "svc_temp", "SubjectUserName": "administrator"},
        }])
    elif scenario == "credential_dumping":
        base = now - timedelta(seconds=30)
        events = [
            {
                "event_id": 4663,
                "when": base + timedelta(seconds=8 * i),
                "data": {
                    "SubjectUserName": user,
                    "ObjectName": "C:\\Windows\\System32\\lsass.exe",
                    "AccessMask": "0x1010",
                    "Process Name": "C:\\Users\\Public\\mimikatz.exe",
                },
            }
            for i in range(3)
        ]
        run(events)
    elif scenario == "lateral_movement":
        base = now - timedelta(minutes=1)
        hosts = ["10.10.4.11", "10.10.4.22", "10.10.7.9", "10.10.12.3"]
        events = [
            {
                "event_id": 4624,
                "when": base + timedelta(seconds=8 * i),
                "data": {"SubjectUserName": user, "IpAddress": ip, "LogonType": "3"},
            }
            for i, ip in enumerate(hosts)
        ]
        run(events)

    return {
        "scenario": scenario,
        "name": SCENARIOS[scenario]["name"],
        "events_ingested": EVENT_COUNTS.get(scenario, 1),
        "alerts_triggered": len(set(alert_ids)),
        "alert_ids": list(dict.fromkeys(alert_ids)),
        "explanation": SCENARIOS[scenario]["explanation"],
        "demo_notice": "DEMO / SYNTHETIC DATA - NO REAL CRPF SYSTEMS",
    }
