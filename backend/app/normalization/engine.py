"""Normalization engine: converts parser output into the common event schema.

Modular: an event gets a category/action/severity from the mapping tables
below. Additional log sources are added by extending these maps and the
parser registry — no changes to the ingestion pipeline are required.
"""

import ipaddress
from datetime import datetime, timezone
from typing import Any

from app.parsers.base import ParsedEvent
from app.parsers.windows import WindowsEventParser

EVENT_CLASSIFICATION: dict[int, tuple[str, str, str]] = {
    4624: ("authentication", "login_success", "low"),
    4625: ("authentication", "login_failed", "medium"),
    4648: ("credential_usage", "explicit_credential_use", "medium"),
    4672: ("privilege_assignment", "special_privileges_assigned", "medium"),
    4688: ("process_creation", "process_created", "low"),
    4720: ("account_management", "user_created", "high"),
    4728: ("account_management", "member_added_privileged_group", "high"),
    4732: ("account_management", "member_added_privileged_group", "high"),
    1102: ("security_audit", "audit_log_cleared", "critical"),
    7045: ("service_installation", "service_installed", "high"),
}

PRIVILEGED_USERS = {
    "administrator",
    "admin",
    "root",
    "system",
    "domain\\admin",
    "krbtgt",
    "nt authority\\system",
}

BLACKHOLE_IPS = {"127.0.0.1", "::1", "-", "", "0.0.0.0"}
PRIVATE_RANGES = [
    "10.",
    "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
    "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
    "172.26.", "172.27.", "172.28.", "172.29.", "172.30.",
    "172.31.",
    "192.168.",
]


def _clean_ip(value: Any) -> str | None:
    if not value:
        return None
    ip = str(value).strip().lower()
    if ip in BLACKHOLE_IPS or ip.startswith("%"):
        return None
    if ip.startswith("fe80:"):
        return None
    try:
        return str(ipaddress.ip_address(ip.split("%")[0]))
    except ValueError:
        return ip[:45]


def _clean_username(value: Any) -> str | None:
    if not value:
        return None
    username = str(value).strip().lower()
    if username in {"-", "anonymous logon", "n\\a", "none", "null"}:
        return None
    return username


def parse_timestamp(value: str | datetime | None) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    value = value.strip()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def normalize_event(
    parsed: ParsedEvent,
    unit_id: str | None,
    agent_id: str | None,
    parser_version: str = "1.0",
) -> dict[str, Any] | None:
    if parsed.event_id is None:
        return None

    fields = WindowsEventParser.extract_fields(parsed)
    category, action, default_severity = EVENT_CLASSIFICATION.get(
        parsed.event_id, ("unknown", "observed", "informational")
    )

    username = _clean_username(fields["username"])
    source_ip = _clean_ip(fields["source_ip"])
    destination_ip = _clean_ip(fields["destination_ip"])
    timestamp = parse_timestamp(fields["timestamp"])

    severity = default_severity
    if parsed.event_id == 4672:
        privileged = username and username.lower() in PRIVILEGED_USERS
        severity = "high" if privileged else "medium"
    if parsed.event_id == 4688:
        severity = _process_creation_severity(fields["command_line"])

    event = {
        "timestamp": timestamp or datetime.now(timezone.utc),
        "unit_id": unit_id,
        "agent_id": agent_id,
        "hostname": fields["hostname"] or None,
        "event_id": parsed.event_id,
        "provider": parsed.provider or None,
        "category": category,
        "action": action,
        "username": username,
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "process_name": fields["process_name"] or None,
        "command_line": fields["command_line"] or None,
        "logon_type": fields["logon_type"] or None,
        "status_code": fields["status_code"] or None,
        "severity": severity,
        "parser_version": parser_version,
        "is_suspicious": False,
        "extra": {
            "account_domain": fields["account_domain"],
            "service_name": fields["service_name"],
            "image_path": fields["image_path"],
            "member_name": fields["member_name"],
            "privileges": fields["privileges"],
            "user_sid": fields["user_sid"],
        },
    }
    return event


def _process_creation_severity(command_line: str | None) -> str:
    """Process creation is informational unless a suspicious pattern matches."""
    if not command_line:
        return "low"
    lowered = command_line.lower()
    indicators = [
        "-enc", "-encodedcommand", "-nop", "-windowstyle hidden",
        "invoke-webrequest", "iwr", "downloadstring", "net.webclient",
        "frombase64string", "iisreset", "wscript", "cscript",
    ]
    if any(ind in lowered for ind in indicators):
        return "medium"
    return "low"


def is_public_ip(ip: str | None) -> bool:
    if not ip:
        return False
    return not any(ip.startswith(p) for p in PRIVATE_RANGES)


def is_privileged_user(username: str | None) -> bool:
    if not username:
        return False
    return username.lower() in PRIVILEGED_USERS or username.lower().endswith("\\administrator")
