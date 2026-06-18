"""Tests for provability-fabric sidecar normalization (untrusted adapter zone)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pf-core" / "validator"))

_normalize_path = ROOT / "adapters" / "provability-fabric" / "mcp_sidecar" / "normalize.py"
_spec = importlib.util.spec_from_file_location("pf_sidecar_normalize", _normalize_path)
assert _spec and _spec.loader
_normalize = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_normalize)

from pf_core.compile import compile_observation  # noqa: E402
from pf_core.schemas import load_registry, validate_object  # noqa: E402


def test_sidecar_golden_line_compiles():
    fixture = Path(__file__).parent / "fixtures" / "sidecar_audit_line.json"
    line = json.loads(fixture.read_text(encoding="utf-8"))
    obs = _normalize.normalize_sidecar_line(line)
    assert obs["schema_version"] == "pf-core.runtime_observation.v1"
    assert obs["principal"]["roles"] == ["mcp_user", "agent"]
    registry = load_registry(ROOT / "pf-core" / "schemas")
    validate_object(obs, registry)
    event = compile_observation(obs)
    validate_object(event, registry)
    assert event["decision"] == "allowed"


def test_sidecar_denied_line_compiles():
    fixture = Path(__file__).parent / "fixtures" / "sidecar_denied_audit_line.json"
    line = json.loads(fixture.read_text(encoding="utf-8"))
    obs = _normalize.normalize_sidecar_line(line)
    assert obs["decision"] == "denied"
    registry = load_registry(ROOT / "pf-core" / "schemas")
    validate_object(obs, registry)
    event = compile_observation(obs)
    validate_object(event, registry)
    assert event["decision"] == "denied"


def test_sidecar_missing_capability_hint_is_ambiguous():
    line = {
        "request_id": "obs-mcp-ambiguous",
        "agent_id": "agent-1",
        "tenant": "tenant-a",
        "tool_effect": "mcp.invoke",
        "resource": "mcp:filesystem/read",
        "policy_decision": "allowed",
    }
    with pytest.raises(ValueError, match="capability_hint required"):
        _normalize.normalize_sidecar_line(line)
