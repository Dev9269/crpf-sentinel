"""MITRE ATT&CK mappings used by built-in detection rules.

Deliberately conservative: techniques are mapped only where technically
appropriate. This is not a claim of full ATT&CK coverage.
"""

MITRE_MAP: dict[str, dict[str, str]] = {
    "T1110": {"name": "Brute Force", "sub": ""},
    "T1070.001": {"name": "Clear Windows Event Logs", "sub": "Indicator Removal"},
    "T1543.003": {"name": "Windows Service", "sub": "Create or Modify System Process"},
    "T1059.001": {"name": "PowerShell", "sub": "Command and Scripting Interpreter"},
    "T1136.001": {"name": "Local Account", "sub": "Create Account"},
    "T1098": {"name": "Account Manipulation", "sub": "Account Manipulation"},
    "T1078": {"name": "Valid Accounts", "sub": "Valid Accounts"},
    "T1134": {"name": "Access Token Manipulation", "sub": "Access Token Manipulation"},
}

EVENT_MITRE: dict[int, str] = {
    4625: "T1110",
    4624: "T1078",
    1102: "T1070.001",
    7045: "T1543.003",
    4688: "T1059.001",
    4720: "T1136.001",
    4728: "T1098",
    4732: "T1098",
    4672: "T1134",
    4648: "T1078",
}


def mitre_for(event_id: int) -> tuple[str | None, str | None]:
    technique = EVENT_MITRE.get(event_id)
    if technique is None:
        return None, None
    entry = MITRE_MAP.get(technique)
    if entry is None:
        return technique, None
    return technique, entry["name"]
