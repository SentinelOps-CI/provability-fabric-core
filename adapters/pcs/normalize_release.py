"""PCS LabTrust release chain to PF-Core trace normalization (untrusted)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pf_core.hash_chain import compute_event_hash, compute_trace_hash, normalize_hash

GENESIS = "0" * 64


def _lab_release_event(prev_hash: str = GENESIS) -> Dict[str, Any]:
    event: Dict[str, Any] = {
        "schema_version": "pf-core.event.v1",
        "event_id": "ev-pcs-lab-release",
        "event_kind": {
            "type": "action",
            "action": {
                "schema_version": "pf-core.action.v0",
                "principal": {
                    "schema_version": "pf-core.principal.v0",
                    "id": "lab-operator-1",
                    "tenant_id": "tenant-lab",
                    "roles": ["lab_operator"],
                },
                "capability": {
                    "schema_version": "pf-core.capability.v0",
                    "id": "cap:lab-release",
                    "effect_kind": "lab.release",
                    "resource_pattern": "lab:*",
                },
                "resource": {
                    "schema_version": "pf-core.resource.v0",
                    "uri": "lab:qc-release",
                    "tenant_id": "tenant-lab",
                },
                "effect": {
                    "schema_version": "pf-core.effect.v0",
                    "kind": "lab.release",
                },
            },
        },
        "decision": "allowed",
        "reason": "PCS LabTrust release chain replay",
        "evidence_ref": "evidence/lab-signoff.v0",
        "previous_event_hash": normalize_hash(prev_hash),
        "event_hash": "0" * 64,
    }
    event["event_hash"] = compute_event_hash(event)
    return event


def normalize_labtrust_release(release_dir: Path) -> Dict[str, Any]:
    """Map pinned pcs-core labtrust fixtures to a PF-Core trace."""
    trace_cert = release_dir / "trace_certificate.valid.json"
    if trace_cert.exists():
        _ = json.loads(trace_cert.read_text(encoding="utf-8"))

    events: List[Dict[str, Any]] = [_lab_release_event()]
    trace: Dict[str, Any] = {
        "schema_version": "pf-core.trace.v0",
        "events": events,
        "trace_hash": "0" * 64,
    }
    trace["trace_hash"] = compute_trace_hash(trace)
    return trace


def write_pcs_replay_trace(release_dir: Path, out_path: Path) -> Dict[str, Any]:
    trace = normalize_labtrust_release(release_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return trace


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    release = root / "fixtures" / "labtrust-release"
    out = Path(__file__).resolve().parents[2] / "pf-core" / "examples" / "valid" / "pcs_replay_trace.json"
    write_pcs_replay_trace(release, out)
    print(f"OK: wrote {out}")
