"""Unit tests for trusted boundary audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pf_core.audit import FORBIDDEN_PHRASES, audit_boundary, audit_v1_primary_fixtures
from pf_core.errors import PFCoreError

ROOT = Path(__file__).resolve().parents[3]


def test_audit_boundary_passes_on_repo_root():
    audit_boundary(ROOT)


def test_audit_boundary_fails_on_missing_doc(tmp_path: Path):
    with pytest.raises(PFCoreError):
        audit_boundary(tmp_path)


def test_audit_v1_primary_rejects_v0_in_valid_path(tmp_path: Path):
    examples = tmp_path / "pf-core" / "examples" / "valid"
    examples.mkdir(parents=True)
    (examples / "legacy_obs.json").write_text(
        json.dumps({"schema_version": "pf-core.runtime_observation.v0"}),
        encoding="utf-8",
    )
    with pytest.raises(PFCoreError, match="LegacyFixtureInTrustedPath"):
        audit_v1_primary_fixtures(tmp_path)


def test_forbidden_phrases_list_non_empty():
    assert len(FORBIDDEN_PHRASES) >= 10
