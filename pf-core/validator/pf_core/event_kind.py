"""Event kind helpers for v1 events."""

from __future__ import annotations

from typing import Any, Mapping, Tuple


def parse_event_kind(event: Mapping[str, Any]) -> Tuple[str, Mapping[str, Any]]:
    """Return (kind_type, payload) where kind_type is 'action' or 'handoff'."""
    event_kind = event.get("event_kind")
    if isinstance(event_kind, Mapping):
        kind_type = event_kind.get("type")
        if kind_type == "action" and isinstance(event_kind.get("action"), Mapping):
            return "action", event_kind["action"]
        if kind_type == "handoff" and isinstance(event_kind.get("handoff"), Mapping):
            return "handoff", event_kind["handoff"]
    action = event.get("action")
    if isinstance(action, Mapping):
        return "action", action
    raise KeyError("event_kind")


def event_action(event: Mapping[str, Any]) -> Mapping[str, Any]:
    kind_type, payload = parse_event_kind(event)
    if kind_type != "action":
        raise KeyError("action")
    return payload


def event_handoff(event: Mapping[str, Any]) -> Mapping[str, Any] | None:
    try:
        kind_type, payload = parse_event_kind(event)
    except KeyError:
        return None
    if kind_type == "handoff":
        return payload
    return None
