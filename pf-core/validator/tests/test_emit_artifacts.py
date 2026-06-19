"""Unit tests for emit-artifacts integration."""

from __future__ import annotations

import json
from pathlib import Path

from pf_core.bundle_verify import verify_bundle
from pf_core.emitter import emit_artifacts

ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "pf-core/schemas"


def test_emit_artifacts_bundle_verifies(tmp_path: Path):
    obs = json.loads((ROOT / "pf-core/examples/valid/mcp_sidecar_observation.json").read_text())
    emit_artifacts(obs, out_dir=tmp_path, schemas_dir=SCHEMAS, runtime_id="emit-test")
    result = verify_bundle(tmp_path, schemas_dir=SCHEMAS)
    assert result["valid"] is True
    assert result["event_count"] == 1


def test_emit_artifacts_email_bundle(tmp_path: Path):
    obs = json.loads((ROOT / "pf-core/examples/valid/email_send_observation.json").read_text())
    emit_artifacts(obs, out_dir=tmp_path, schemas_dir=SCHEMAS)
    result = verify_bundle(tmp_path, schemas_dir=SCHEMAS)
    assert result["safe"] is True
