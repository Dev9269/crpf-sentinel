"""Time-window correlation: count rules and failure→success sequences.

These queries run against the database so they scale to high event volumes
and stay consistent across ingestion workers.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.event import NormalizedEvent
from app.models.rule import DetectionRule


def _window_start(seconds: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


def evaluate_count_rule(
    db: Session, rule: DetectionRule, event: dict
) -> tuple[bool, int]:
    """Count matching events in the time window grouped by correlation_key."""
    key_field = rule.correlation_key or "source_ip"
    key_value = event.get(key_field)
    if not key_value:
        return False, 0

    start = _window_start(rule.time_window_seconds)
    query = db.query(func.count(NormalizedEvent.id)).filter(
        NormalizedEvent.timestamp >= start,
        NormalizedEvent.timestamp <= datetime.now(timezone.utc),
        NormalizedEvent.event_id.in_(rule.event_id or [event["event_id"]]),
    )
    # Match the correlation key field to the same value
    if key_field in {"source_ip", "destination_ip", "username", "hostname", "unit_id", "agent_id"}:
        query = query.filter(getattr(NormalizedEvent, key_field) == key_value)

    count = query.scalar() or 0
    return count >= rule.threshold, count


def evaluate_sequence_rule(
    db: Session, rule: DetectionRule, event: dict
) -> tuple[bool, int, str]:
    """Failure(s) followed by success within the window for the same subject."""
    window_seconds = (rule.conditions or {}).get("window", rule.time_window_seconds)
    start = _window_start(window_seconds)
    subject = event.get(rule.correlation_key or "username")

    failure_count = (
        db.query(func.count(NormalizedEvent.id))
        .filter(
            NormalizedEvent.timestamp >= start,
            NormalizedEvent.event_id == 4625,
            NormalizedEvent.timestamp < event["timestamp"],
        )
        .scalar()
        or 0
    )

    if failure_count < rule.threshold:
        return False, failure_count, "below failure threshold"

    success_exists = (
        db.query(func.count(NormalizedEvent.id))
        .filter(
            NormalizedEvent.timestamp >= start,
            NormalizedEvent.event_id == 4624,
            NormalizedEvent.timestamp >= event["timestamp"] - timedelta(seconds=120),
        )
        .scalar()
        or 0
    ) > 0

    matched = success_exists or event["event_id"] == 4624
    reason = (
        f"{failure_count} failed logons followed by success" if matched else "no success yet"
    )
    return matched, failure_count, reason
