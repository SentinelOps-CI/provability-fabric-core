"""Tests for five-file PF-Core bundle verification."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from pf_core.bundle_verify import BUNDLE_FILES, verify_bundle
from pf_core.emitter import emit_artifacts
from pf_core.errors import PFCoreError

ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "pf-core/schemas"
OBS = ROOT / "pf-core/examples/valid/mcp_sidecar_observation.json"


@pytest.fixture
def bundle_dir(tmp_path: Path) -> Path:
    obs = json.loads(OBS.read_text(encoding="utf-8"))
    emit_artifacts(
        obs,
        out_dir=tmp_path,
        schemas_dir=SCHEMAS,
        runtime_id="test-bundle",
    )
    return tmp_path


def test_verify_bundle_accepts_emit_artifacts_layout(bundle_dir: Path):
    result = verify_bundle(bundle_dir, schemas_dir=SCHEMAS)
    assert result["valid"] is True
    assert result["safe"] is True
    assert len(result["trace_hash"]) == 64


def test_verify_bundle_requires_all_files(bundle_dir: Path):
    (bundle_dir / "certificate.json").unlink()
    with pytest.raises(PFCoreError, match="BundleIncomplete"):
        verify_bundle(bundle_dir, schemas_dir=SCHEMAS)


def test_verify_bundle_rejects_tampered_trace_hash(bundle_dir: Path):
    trace_path = bundle_dir / "trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["trace_hash"] = "f" * 64
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(PFCoreError):
        verify_bundle(bundle_dir, schemas_dir=SCHEMAS)


def test_verify_bundle_rejects_certificate_trace_hash_mismatch(bundle_dir: Path):
    cert_path = bundle_dir / "certificate.json"
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    cert["trace_hash"] = "a" * 64
    cert_path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(PFCoreError, match="CertificateTraceHashMismatch"):
        verify_bundle(bundle_dir, schemas_dir=SCHEMAS)


def test_verify_bundle_rejects_unsafe_certificate(bundle_dir: Path):
    cert_path = bundle_dir / "certificate.json"
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    cert["safe"] = False
    cert_path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(PFCoreError, match="UnsafeCertificate"):
        verify_bundle(bundle_dir, schemas_dir=SCHEMAS)


def test_bundle_files_constant_matches_emit_artifacts():
    assert set(BUNDLE_FILES) == {
        "runtime_observation.json",
        "event.json",
        "trace.json",
        "certificate.json",
        "audit.jsonl",
    }
