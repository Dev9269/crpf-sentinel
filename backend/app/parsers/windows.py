"""Windows Event Log parser.

Accepts three input shapes:
  - raw XML (Windows Event Log XML / EventRecord)
  - JSON (structured event log)
  - Python dict (structured event log)

The dict shape accepts both the nested Windows layout
(``System.EventID``, ``EventData``) and the flat collector/API layout
(``event_id``, ``provider``, ``time_created``, ``data``).

Extracts the security-relevant fields used by the normalization engine.
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from app.parsers.base import BaseParser, ParsedEvent

_NS = {"w": "http://schemas.microsoft.com/win/2004/08/events/event"}


def _strip_ns(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


class WindowsEventParser(BaseParser):
    format_name: str = "windows"
    version: str = "1.0"

    def parse(self, payload: str | dict) -> ParsedEvent | None:
        if isinstance(payload, str):
            raw = payload
            if raw.lstrip().startswith("<"):
                event = self._parse_xml(raw)
            else:
                event = self._parse_json_text(raw)
        elif isinstance(payload, dict):
            event = self._parse_dict(payload)
        else:
            return None
        if event is None:
            return None
        event.raw = payload if isinstance(payload, str) else json.dumps(payload, default=str)
        return event

    # ── XML ────────────────────────────────────────────────────────────
    def _parse_xml(self, raw: str) -> ParsedEvent | None:
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return None
        ns = {k: v for k, v in _NS.items()}
        event = ParsedEvent()

        def first(path: str) -> str | None:
            node = root.find(path, ns)
            return _text(node.text) if node is not None and node.text else None

        def first_local(tag: str) -> str | None:
            for node in root.iter():
                if _strip_ns(node.tag) == tag and node.text and node.text.strip():
                    return _text(node.text)
            return None

        try:
            event.event_id = int(first_local("EventID") or 0)
        except (ValueError, TypeError):
            event.event_id = None

        def first_attr(tag: str, attr: str, path: str) -> str | None:
            node = root.find(path, ns)
            if node is not None:
                value = node.get(attr) or (node.text or "")
                return _text(value)
            for n in root.iter():
                if _strip_ns(n.tag) == tag:
                    value = n.get(attr) or (n.text or "")
                    return _text(value)
            return None

        event.provider = first_attr("Provider", "Name", ".//w:Provider")
        event.computer = first(".//w:Computer") or first_local("Computer")
        event.time_created = first_attr("TimeCreated", "SystemTime", ".//w:TimeCreated")
        event.user = first_attr("Security", "UserID", ".//w:Security")

        event.event_data = self._collect_event_data(root)
        if event.event_id is None:
            event.event_id = self._int(event.event_data.get("EventID"))
        return event

    def _collect_event_data(self, root: ET.Element) -> dict:
        data: dict = {}
        for node in root.iter():
            if _strip_ns(node.tag) == "Data":
                name = node.get("Name")
                value = _text(node.text)
                if name:
                    data[name] = value
            elif _strip_ns(node.tag) == "EventData":
                continue
        for key in list(data.keys()):
            if key in data and data[key] is None:
                data[key] = None
        return data

    # ── JSON ───────────────────────────────────────────────────────────
    def _parse_json_text(self, raw: str) -> ParsedEvent | None:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return self._parse_dict(obj)

    def _parse_dict(self, obj: dict) -> ParsedEvent | None:
        if not isinstance(obj, dict):
            return None
        system = obj.get("System") if isinstance(obj.get("System"), dict) else obj
        event = ParsedEvent()
        event.event_id = self._int(system.get("EventID"))
        event.provider = self._flat(system.get("Provider"), "Name")
        event.computer = system.get("Computer")
        tc = system.get("TimeCreated")
        event.time_created = self._flat(tc, "SystemTime") if isinstance(tc, dict) else tc
        sec = system.get("Security")
        event.user = self._flat(sec, "UserID") if isinstance(sec, dict) else sec

        event_data = obj.get("EventData", obj.get("Data"))
        if isinstance(event_data, list):
            for item in event_data:
                if isinstance(item, dict):
                    name = item.get("Name") or item.get("_Name")
                    value = item.get("#text") or item.get("value") or item.get("Value")
                    if name:
                        event.event_data[name] = value
        elif isinstance(event_data, dict):
            event.event_data = event_data

        if event.event_id is None:
            event.event_id = self._int(obj.get("event_id"))
            event.provider = event.provider or _text(obj.get("provider"))
            event.computer = event.computer or obj.get("computer")
            if event.time_created is None:
                tc = obj.get("time_created")
                event.time_created = self._flat(tc, "SystemTime") if isinstance(tc, dict) else tc
            if event.user is None:
                event.user = _text(obj.get("user"))
            if not event.event_data:
                event.event_data = obj.get("data") or {}

        if isinstance(event.time_created, datetime):
            event.time_created = event.time_created.isoformat()
        return event

    # ── Shared helpers ─────────────────────────────────────────────────
    @staticmethod
    def _int(value) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _flat(value, key: str) -> str | None:
        if isinstance(value, dict):
            return _text(value.get(key))
        return _text(value)

    # ── High-level extraction for the normalization engine ─────────────
    @staticmethod
    def extract_fields(event: ParsedEvent) -> dict:
        ed = event.event_data
        return {
            "event_id": event.event_id,
            "provider": event.provider,
            "hostname": event.computer,
            "timestamp": event.time_created,
            "user_sid": event.user,
            "username": (
                ed.get("TargetUserName")
                or ed.get("SubjectUserName")
                or ed.get("Account Name")
                or ed.get("NewAccountName")
            ),
            "account_domain": (
                ed.get("TargetDomainName")
                or ed.get("SubjectDomainName")
                or ed.get("Account Domain")
            ),
            "logon_type": ed.get("LogonType") or ed.get("Logon Type"),
            "source_ip": (
                ed.get("IpAddress")
                or ed.get("SourceNetworkAddress")
                or ed.get("Source IP")
            ),
            "destination_ip": ed.get("DestinationIp") or ed.get("Destination IP"),
            "process_name": ed.get("NewProcessName") or ed.get("Process Name"),
            "command_line": (
                ed.get("CommandLine")
                or ed.get("Process Command Line")
                or ed.get("Command line")
            ),
            "status_code": ed.get("Status") or ed.get("SubStatus"),
            "service_name": ed.get("ServiceName"),
            "image_path": ed.get("ImagePath"),
            "target_user": ed.get("TargetUserName"),
            "member_name": ed.get("MemberName"),
            "privileges": ed.get("PrivilegeList"),
            "new_account_name": ed.get("NewAccountName"),
        }
