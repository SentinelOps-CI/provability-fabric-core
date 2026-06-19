"""Unit tests for observation compiler."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pf_core.compile import compile_observation
from pf_core.deciders import event_safe

ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "pf-core/schemas"
VALID = ROOT / "pf-core/examples/valid"


def test_compile_file_read_observation():
    obs = json.loads((VALID / "file_read_observation.json").read_text())
    event = compile_observation(obs)
    assert event["decision"] == "allowed"
    assert event_safe(event)


def test_compile_downgrades_unsafe_allow():
    obs = json.loads((VALID / "file_read_observation.json").read_text())
    obs["action"]["reads"][0]["tenant_id"] = "tenant-b"
    event = compile_observation(obs)
    assert event["decision"] == "denied"


def test_compile_mcp_sidecar_observation_deterministic():
    obs = json.loads((VALID / "mcp_sidecar_observation.json").read_text())
    first = compile_observation(obs)
    second = compile_observation(obs)
    assert first == second


def test_compile_email_observation():
    obs = json.loads((VALID / "email_send_observation.json").read_text())
    event = compile_observation(obs)
    assert event["decision"] == "allowed"
