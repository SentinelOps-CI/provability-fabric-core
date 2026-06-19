"""Admission-controller audit line parity vs reference normalizer."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ADAPTER = ROOT / "adapters" / "provability-fabric"
FIXTURES = ADAPTER / "tests" / "fixtures"


def _load_normalize():
    spec = importlib.util.spec_from_file_location(
        "normalize", ADAPTER / "mcp_sidecar" / "normalize.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _canonical(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@pytest.fixture(scope="module")
def normalize_mod():
    return _load_normalize()


def test_normalize_admission_line_matches_file_read_observation(normalize_mod):
    line = json.loads((FIXTURES / "admission_audit_line.json").read_text(encoding="utf-8"))
    obs = normalize_mod.normalize_admission_line(line)
    golden = json.loads(
        (ROOT / "pf-core/examples/valid/file_read_observation.json").read_text(encoding="utf-8")
    )
    assert obs["decision"] == golden["decision"]
    assert obs["action"]["capability"]["id"] == golden["action"]["capability"]["id"]
    assert obs["action"]["effects"][0]["kind"] == golden["action"]["effects"][0]["kind"]
    assert obs["action"]["reads"][0]["uri"] == golden["action"]["reads"][0]["uri"]
    assert obs["principal"]["tenant_id"] == golden["principal"]["tenant_id"]


def test_admission_compile_validate_event(normalize_mod):
    sys.path.insert(0, str(ROOT / "pf-core" / "validator"))
    from pf_core.compile import compile_observation
    from pf_core.deciders import event_safe
    from pf_core.schemas import load_registry, validate_object

    line = json.loads((FIXTURES / "admission_audit_line.json").read_text(encoding="utf-8"))
    obs = normalize_mod.normalize_admission_line(line)
    registry = load_registry(ROOT / "pf-core/schemas")
    validate_object(obs, registry)
    event = compile_observation(obs)
    validate_object(event, registry)
    assert event_safe(event)
