"""Unit tests for authorization deciders."""

from __future__ import annotations

import json
from pathlib import Path

from pf_core.deciders import action_allowed, event_safe, handoff_safe, trace_safe
from pf_core.event_kind import event_action

ROOT = Path(__file__).resolve().parents[3]
VALID = ROOT / "pf-core/examples/valid"
INVALID = ROOT / "pf-core/examples/invalid"


def test_file_read_allowed_event_safe():
    event = json.loads((VALID / "file_read_allowed.json").read_text())
    assert event_safe(event)


def test_network_denied_event_not_action_allowed():
    event = json.loads((VALID / "network_denied.json").read_text())
    assert event_safe(event)
    action = event_action(event)
    assert not action_allowed(action)


def test_handoff_trace_safe():
    trace = json.loads((VALID / "handoff_trace.json").read_text())
    assert trace_safe(trace)


def test_handoff_unsafe_trace_fails():
    trace = json.loads((INVALID / "handoff_trace_unsafe.json").read_text())
    assert not trace_safe(trace)


def test_handoff_json_safe():
    handoff = json.loads((VALID / "handoff.json").read_text())
    assert handoff_safe(handoff)


def test_action_allowed_requires_capability():
    event = json.loads((VALID / "email_send.json").read_text())
    action = event_action(event)
    assert action_allowed(action)
