"""Unit tests for audit line formatting (trusted validator)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pf_core.audit_line import AUDIT_SCHEMA_VERSION, format_audit_line, _handoff_audit_capability
from pf_core.emitter import emit_audit_for_trace

ROOT = Path(__file__).resolve().parents[3]

REQUIRED_AUDIT_FIELDS = {
    "schema_version",
    "trace_id",
    "event_id",
    "principal_id",
    "action_id",
    "capability",
    "decision",
    "reason",
    "policy_ref",
    "evidence_ref",
    "event_hash",
    "previous_event_hash",
    "trace_hash",
    "runtime_id",
}


def test_handoff_audit_capability_single():
    handoff = {"delegated_capabilities": [{"id": "cap:handoff"}]}
    assert _handoff_audit_capability(handoff) == "cap:handoff"


def test_handoff_audit_capability_multiple_joined():
    handoff = {
        "delegated_capabilities": [{"id": "cap:a"}, {"id": "cap:b"}],
    }
    assert _handoff_audit_capability(handoff) == "cap:a,cap:b"


def test_handoff_audit_capability_missing_raises():
    with pytest.raises(KeyError, match="delegated_capabilities"):
        _handoff_audit_capability({})


def test_format_audit_line_handoff_trace():
    trace = json.loads((ROOT / "pf-core/examples/valid/handoff_trace.json").read_text())
    event = trace["events"][0]
    handoff = event["event_kind"]["handoff"]
    line = format_audit_line(
        trace_id="trace-handoff-1",
        event=event,
        trace=trace,
        observation={
            "policy_ref": "policy/default.v0",
            "evidence_ref": handoff["evidence_ref"],
        },
        runtime_id="test",
    )
    assert line["schema_version"] == AUDIT_SCHEMA_VERSION
    assert line["capability"] == "cap:handoff"
    assert line["principal_id"] == "agent-1"
    assert line["trace_hash"] == trace["trace_hash"]
    assert line["event_hash"] == event["event_hash"]


def test_emit_audit_for_trace_handoff_writes_valid_lines(tmp_path: Path):
    trace = json.loads((ROOT / "pf-core/examples/valid/handoff_trace.json").read_text())
    handoff = trace["events"][0]["event_kind"]["handoff"]
    out = tmp_path / "audit.jsonl"
    emit_audit_for_trace(
        trace,
        out_path=out,
        trace_id="trace-handoff-1",
        observation={
            "policy_ref": "policy/default.v0",
            "evidence_ref": handoff["evidence_ref"],
        },
        runtime_id="test",
    )
    lines = [json.loads(raw) for raw in out.read_text().strip().splitlines()]
    assert len(lines) == len(trace["events"])
    for line in lines:
        assert line["schema_version"] == AUDIT_SCHEMA_VERSION
        assert REQUIRED_AUDIT_FIELDS <= set(line.keys())
