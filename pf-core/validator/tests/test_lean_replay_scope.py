"""Guardrails for intentional --lean-check golden-only scope."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

E2E_GOLDENS = {
    "file_read_allowed_trace.json",
    "handoff_trace.json",
    "pcs_replay_trace.json",
}


def test_e2e_lean_check_uses_release_goldens_only():
    script = (ROOT / "pf-core/scripts/e2e-replay-gate.sh").read_text(encoding="utf-8")
    match = re.search(r'GOLDEN_TRACES=\((.*?)\)', script, re.DOTALL)
    assert match, "GOLDEN_TRACES not found in e2e-replay-gate.sh"
    block = match.group(1)
    names = {Path(line.strip().strip('"')).name for line in block.splitlines() if ".json" in line}
    assert names == E2E_GOLDENS


def test_replay_lean_documents_golden_only_gate():
    replay = (ROOT / "pf-core/lean/PFCore/Replay.lean").read_text(encoding="utf-8")
    assert "golden" in replay.lower()
    assert "file read" in replay.lower() or "safeFileReadEvent" in replay
    assert "handoff" in replay.lower()
    assert "lab" in replay.lower() or "labReleaseEvent" in replay


def test_certificate_semantics_documents_lean_check_intent():
    doc = (ROOT / "pf-core/docs/certificate-semantics.md").read_text(encoding="utf-8")
    assert "--lean-check" in doc
    assert "three release golden traces" in doc.lower() or "three" in doc
    assert "without deserializing arbitrary trace JSON" in doc
