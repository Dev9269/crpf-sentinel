"""Time-window correlation: count rules and failure→success sequences.

These queries run against the database so they scale to high event volumes
and stay consistent across ingestion workers.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.detection.matcher import event_matches
from app.models.event import NormalizedEvent
from app.models.rule import DetectionRule

KEY_FIELDS = {
    "source_ip", "destination_ip", "username", "hostname", "unit_id", "agent_id",
}

_ROW_COLUMNS = (
    "id", "timestamp", "event_id", "username", "hostname", "source_ip",
    "destination_ip", "process_name", "command_line", "logon_type", "status_code",
)


def _window_start(seconds: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


def _rule_event_ids(rule: DetectionRule) -> list[int]:
    ids = rule.event_id if isinstance(rule.event_id, list) else [rule.event_id]
    return [i for i in ids if i is not None]


def _collect_matching(
    db: Session,
    rule: DetectionRule,
    event: dict,
    *,
    event_ids: list[int] | None = None,
    before_ts: datetime | None = None,
    after_ts: datetime | None = None,
) -> tuple[list[dict], int]:
    """Return (matched_event_dicts, total_match_count) in the time window.

    Unlike a bare COUNT query, rows are fetched and passed through the rule's
    conditions (e.g. logon_type eq "3") and scoped to the correlation key, so
    correlation matches respect the full rule definition.
    """
    start = _window_start(rule.time_window_seconds)
    query = db.query(*[getattr(NormalizedEvent, c) for c in _ROW_COLUMNS]).filter(
        NormalizedEvent.timestamp >= start,
        NormalizedEvent.timestamp <= datetime.now(timezone.utc),
    )
    ids = event_ids if event_ids is not None else _rule_event_ids(rule)
    if ids:
        query = query.filter(NormalizedEvent.event_id.in_(ids))
    if before_ts is not None:
        query = query.filter(NormalizedEvent.timestamp < before_ts)
    if after_ts is not None:
        query = query.filter(NormalizedEvent.timestamp >= after_ts)

    key_field = rule.correlation_key or "source_ip"
    key_value = event.get(key_field)
    if key_field in KEY_FIELDS and key_value:
        query = query.filter(getattr(NormalizedEvent, key_field) == key_value)

    rows = query.order_by(NormalizedEvent.timestamp.asc()).limit(20000).all()

    matched: list[dict] = []
    for row in rows:
        candidate = dict(zip(_ROW_COLUMNS, row))
        if event_matches(candidate, rule):
            matched.append(candidate)
    return matched, len(matched)


def evaluate_count_rule(
    db: Session, rule: DetectionRule, event: dict
) -> tuple[bool, int]:
    """Count condition-matching events in the window grouped by correlation key."""
    key_field = rule.correlation_key or "source_ip"
    key_value = event.get(key_field)
    if not key_value:
        return False, 0
    _, count = _collect_matching(db, rule, event)
    return count >= rule.threshold, count


def evaluate_sequence_rule(
    db: Session, rule: DetectionRule, event: dict
) -> tuple[bool, int, str]:
    """Failure(s) followed by success within the window for the same subject.

    Both legs are scoped to the correlation key (e.g. username) and the rule's
    conditions, so failures from other accounts cannot satisfy the threshold.
    """
    window_seconds = (rule.conditions or {}).get("window", rule.time_window_seconds)
    start = _window_start(window_seconds)
    ets = event["timestamp"]

    failures, _ = _collect_matching(
        db, rule, event,
        event_ids=[4625],
        before_ts=ets,
    )
    failure_count = len(failures)

    if failure_count < rule.threshold:
        return False, failure_count, "below failure threshold"

    successes, _ = _collect_matching(
        db, rule, event,
        event_ids=[4624],
        after_ts=ets - timedelta(seconds=120),
    )
    success_exists = len(successes) > 0

    matched = success_exists or event["event_id"] == 4624
    reason = (
        f"{failure_count} failed logons followed by success" if matched else "no success yet"
    )
    return matched, failure_count, reason