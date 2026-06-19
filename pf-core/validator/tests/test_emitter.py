"""Unit tests for artifact emitter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pf_core.emitter import emit_artifacts, emit_certificate, build_trace
from pf_core.errors import PFCoreError
from pf_core.schemas import load_registry, validate_object

ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "pf-core/schemas"


def test_emit_certificate_safe_trace():
    trace = json.loads((ROOT / "pf-core/examples/valid/file_read_allowed_trace.json").read_text())
    contract = {
        "schema_version": "pf-core.contract.v0",
        "name": "trace-safe",
        "pre": {},
        "post": {"require_event_safe": True},
        "invariant": {"require_trace_safe": True},
    }
    cert = emit_certificate(trace, contract)
    assert cert["safe"] is True
    assert cert["trace_hash"] == trace["trace_hash"]


def test_emit_certificate_rejects_forbidden_phrase():
    trace = json.loads((ROOT / "pf-core/examples/valid/file_read_allowed_trace.json").read_text())
    contract = {
        "schema_version": "pf-core.contract.v0",
        "name": "bad-claim",
        "pre": {},
        "post": {},
        "invariant": {},
    }
    with pytest.raises(PFCoreError, match="ForbiddenCertificateClaim"):
        emit_certificate(trace, contract, claim_class="this agent is safe")


def test_build_trace_computes_hash():
    event = json.loads((ROOT / "pf-core/examples/valid/file_read_allowed.json").read_text())
    trace = build_trace([event])
    assert len(trace["trace_hash"]) == 64


def test_emit_artifacts_writes_five_files(tmp_path: Path):
    obs = json.loads((ROOT / "pf-core/examples/valid/mcp_sidecar_observation.json").read_text())
    paths = emit_artifacts(obs, out_dir=tmp_path, schemas_dir=SCHEMAS)
    assert len(paths) == 5
    registry = load_registry(SCHEMAS)
    for name, path in paths.items():
        assert path.is_file()
        if name == "audit":
            lines = [json.loads(raw) for raw in path.read_text().strip().splitlines()]
            assert lines
            continue
        validate_object(json.loads(path.read_text()), registry)
