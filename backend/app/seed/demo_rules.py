"""Seed the built-in detection rules into PostgreSQL."""

import uuid

from sqlalchemy.orm import Session

from app.detection.rules import BUILTIN_RULES
from app.models.rule import DetectionRule
from app.models.user import User


def seed_rules(db: Session, created_by: User | None = None) -> int:
    """Upsert the built-in rules so definitions stay in sync with code."""
    count = 0
    existing = {r.rule_id: r for r in db.query(DetectionRule).all()}
    for definition in BUILTIN_RULES:
        rule = existing.get(definition["rule_id"])
        if rule is None:
            rule = DetectionRule(
                id=uuid.uuid4().hex[:16],
                created_by=created_by.id if created_by else None,
                **definition,
            )
            db.add(rule)
            count += 1
        else:
            # Refresh definition fields while preserving match statistics.
            for key, value in definition.items():
                if key != "rule_id":
                    setattr(rule, key, value)
            db.add(rule)
            count += 1
    db.commit()
    return count
