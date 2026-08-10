"""Stateless condition matcher for a single normalized event.

Supported conditions (JSON stored on the DetectionRule):
  - event_id: int or list[int]                    exact match on event id
  - field: {"field": "username", "mode": "field"} match non-null field value
  - contains: {"command_line": {"contains": "powershell"}}
  - contains_any: {"command_line": {"contains_any": ["-enc", "iwr "]}}
  - eq: {"severity": {"eq": "high"}} or {"category": "authentication"}
"""

from typing import Any


def _field_value(event: dict[str, Any], field: str) -> Any:
    return event.get(field)


def _value_contains(value: Any, needle: str, case_sensitive: bool = False) -> bool:
    if value is None:
        return False
    text = str(value)
    if not case_sensitive:
        text = text.lower()
        needle = needle.lower()
    return needle in text


def _matches_condition(event: dict[str, Any], key: str, value: Any) -> bool:
    if key == "event_id":
        event_ids = value if isinstance(value, list) else [value]
        return event.get("event_id") in event_ids

    if key in ("field", "mode", "sequence", "window"):
        # Rule metadata / correlation-level constructs — evaluated by the engine.
        if key == "field":
            field = value.get("field") if isinstance(value, dict) else value
            if not field:
                return True
            return _field_value(event, field) is not None
        return True

    # Field-keyed conditions: {"command_line": {"contains_any": [...]}}
    field_value = _field_value(event, key)

    if isinstance(value, dict):
        if "contains_any" in value:
            return any(
                _value_contains(field_value, needle)
                for needle in value["contains_any"]
                if needle
            )
        if "contains" in value:
            return _value_contains(field_value, value["contains"])
        if "eq" in value:
            return field_value == value["eq"]
        if "ne" in value:
            return field_value != value["ne"]
        if "regex" in value:
            import re

            try:
                return bool(re.search(value["regex"], str(field_value or ""), re.IGNORECASE))
            except re.error:
                return False
        return True

    # Plain equality
    if value is None:
        return field_value is None
    return str(field_value).lower() == str(value).lower()


def evaluate_conditions(event: dict[str, Any], conditions: dict[str, Any]) -> tuple[bool, str]:
    if not conditions:
        return True, "no conditions"
    reasons: list[str] = []
    for key, value in conditions.items():
        if not _matches_condition(event, key, value):
            return False, ""
        reasons.append(key)
    return True, ", ".join(reasons)


def event_matches(event: dict[str, Any], rule: Any) -> tuple[bool, str]:
    """Return (matched, reason). event_id list is checked first for cheap rejection."""
    rule_event_ids = rule.event_id if isinstance(rule.event_id, list) else [rule.event_id]
    if rule_event_ids and event.get("event_id") not in rule_event_ids:
        return False, ""
    return evaluate_conditions(event, rule.conditions or {})
