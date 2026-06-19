"""PCS trace_certificate field mapping vs PF-Core artifacts (Phase 7 PR-1 guard)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pf-core" / "validator"))

from pf_core.hash_chain import normalize_hash  # noqa: E402

LABTRUST = ROOT / "adapters/pcs/fixtures/labtrust-release"
PCS_CERT = LABTRUST / "trace_certificate.valid.json"
PCS_REPLAY = ROOT / "pf-core/examples/valid/pcs_replay_trace.json"

# Authoritative mapping table from docs/pf-core/phase7-pcs-checklist.md
PCS_TO_PF_CORE_FIELDS = {
    "certificate_id": "certificate.certificate_id",
    "schema_version": "certificate.schema_version",
    "trace_hash": "trace.trace_hash / certificate.trace_hash",
    "spec_hash": "certificate.contract_hash",
    "property_id": "(none — PCS-only; map to policy_ref in pcs-core docs)",
    "checker": "certificate.checker",
    "checker_version": "certificate.checker_version",
    "status": "certificate.safe (CertificateChecked + safe: true)",
    "counterexample_ref": "(none — PCS-only)",
    "created_at": "(none — organizational metadata)",
    "producer": "certificate.created_by (optional)",
    "producer_version": "(organizational metadata)",
    "source_repo": "certificate.proof_ref (different semantics; document cross-ref)",
    "source_commit": "(document cross-ref to proof_ref)",
    "signature_or_digest": "(none — PIP bundle integrity layer)",
}


def test_pcs_trace_certificate_fixture_has_mapping_fields():
    cert = json.loads(PCS_CERT.read_text(encoding="utf-8"))
    for pcs_field in PCS_TO_PF_CORE_FIELDS:
        assert pcs_field in cert, f"missing PCS field {pcs_field!r} in fixture"


def test_pcs_trace_hash_normalizes_to_hex64():
    cert = json.loads(PCS_CERT.read_text(encoding="utf-8"))
    normalized = normalize_hash(cert["trace_hash"])
    assert len(normalized) == 64
    assert all(c in "0123456789abcdef" for c in normalized)


def test_pcs_replay_trace_passes_check_trace():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "pf-core/validator")}
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pf_core.cli",
            "core",
            "check-trace",
            "--schemas",
            str(ROOT / "pf-core/schemas"),
            "--file",
            str(PCS_REPLAY),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_normalize_release_reads_trace_certificate():
    """normalize_release.py must load trace_certificate when present (mapping hook)."""
    source = (ROOT / "adapters/pcs/normalize_release.py").read_text(encoding="utf-8")
    assert "trace_certificate.valid.json" in source
    assert "trace_cert.exists()" in source
