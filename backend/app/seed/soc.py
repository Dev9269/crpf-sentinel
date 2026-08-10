"""Seed demo incidents and IOC library entries.

ALL DATA IS SYNTHETIC. No real CRPF operational information is used.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.incident import Incident, IncidentAlert, IncidentNote
from app.models.ioc import IocEntry
from app.models.rule import DetectionRule
from app.models.unit import Unit
from app.models.user import User


def seed_iocs(db: Session) -> int:
    """Seed a small demonstration IOC library. Returns count of new entries."""
    admin = db.query(User).filter(User.username == "admin").first()
    creator = admin.id if admin else None

    demo_iocs = [
        {"ioc_type": "ip", "value": "203.0.113.14", "description": "Known scanning source observed in demo feed", "source": "demo-feed", "severity": "high", "threat_type": "scanner"},
        {"ioc_type": "ip", "value": "198.51.100.7", "description": "Historical brute-force source", "source": "demo-feed", "severity": "high", "threat_type": "brute_force"},
        {"ioc_type": "ip", "value": "192.0.2.55", "description": "Suspicious inbound source", "source": "demo-feed", "severity": "medium", "threat_type": "suspicious"},
        {"ioc_type": "domain", "value": "payload.delivery.example", "description": "C2 delivery domain (synthetic)", "source": "demo-feed", "severity": "high", "threat_type": "c2"},
        {"ioc_type": "command", "value": "powershell.exe -nop -w hidden -enc", "description": "Encoded PowerShell download cradle pattern", "source": "demo-feed", "severity": "high", "threat_type": "execution"},
        {"ioc_type": "hash", "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "description": "Synthetic file hash (empty payload)", "source": "manual", "severity": "low", "threat_type": "hash"},
        {"ioc_type": "url", "value": "http://malicious.download.example/bob.exe", "description": "Synthetic malware download URL", "source": "demo-feed", "severity": "high", "threat_type": "download"},
    ]

    created = 0
    for spec in demo_iocs:
        exists = (
            db.query(IocEntry)
            .filter(IocEntry.ioc_type == spec["ioc_type"], IocEntry.value == spec["value"])
            .first()
        )
        if exists:
            continue
        db.add(
            IocEntry(
                id=uuid.uuid4().hex[:16],
                ioc_id=f"IOC-DEMO-{created + 1:03d}",
                created_by=creator,
                **spec,
            )
        )
        created += 1
    db.commit()
    return created


def seed_demo_incidents(db: Session) -> int:
    """Create demo incidents grouping open alerts. Returns number created."""
    existing = db.query(Incident).first()
    if existing:
        return 0

    units = {u.id: u for u in db.query(Unit).all()}
    admin = db.query(User).filter(User.username == "admin").first()
    created_by = admin.id if admin else None
    now = datetime.now(timezone.utc)

    rules_by_id = {r.id: r for r in db.query(DetectionRule).all()}

    groups = [
        {
            "title": "Brute Force Attack on Delhi Unit",
            "category": "authentication",
            "rule_substring": "RULE-AUTH-001",
            "severity": "high",
        },
        {
            "title": "Security Audit Log Tampering",
            "category": "security_audit",
            "rule_substring": "RULE-AUDIT-001",
            "severity": "critical",
        },
        {
            "title": "Unexpected Service Installation",
            "category": "service_installation",
            "rule_substring": "RULE-SVC-001",
            "severity": "high",
        },
    ]

    created = 0
    for spec in groups:
        rule_ids = [r.id for rid, r in rules_by_id.items() if spec["rule_substring"] in (r.rule_id or "")]
        alerts = (
            db.query(Alert)
            .filter(Alert.rule_id.in_(rule_ids) if rule_ids else False)
            .order_by(Alert.last_seen.desc())
            .limit(8)
            .all()
        )
        if not alerts:
            continue

        first = alerts[-1]
        last = alerts[0]
        created_by_user = None

        incident = Incident(
            id=uuid.uuid4().hex[:16],
            incident_id=f"INC-DEMO-{created + 1:03d}",
            title=spec["title"],
            description=(
                f"Multiple related alerts indicate {spec['category'].replace('_', ' ')} "
                "activity across the monitored estate. Synthetic demonstration incident."
            ),
            severity=spec["severity"],
            status="investigating",
            category=spec["category"],
            source="correlation",
            unit_id=first.unit_id,
            hostname=first.hostname,
            source_ip=first.source_ip,
            username=first.username,
            mitre_technique=first.mitre_technique,
            mitre_name=first.mitre_name,
            alert_count=len(alerts),
            event_count=sum(a.event_count or 0 for a in alerts),
            risk_score=max(a.risk_score or 0 for a in alerts),
            assigned_to=created_by,
            created_by=created_by,
            first_seen=first.first_seen,
            last_seen=last.last_seen,
        )
        db.add(incident)
        db.flush()
        for a in alerts:
            db.add(IncidentAlert(incident_id=incident.id, alert_id=a.id, timestamp=now))
        db.add(
            IncidentNote(
                incident_id=incident.id,
                user_id=created_by,
                username=admin.username if admin else "system",
                content="Incident auto-created during demo seeding. Review linked alerts and timeline.",
                timestamp=now,
            )
        )
        created += 1

    db.commit()
    return created
