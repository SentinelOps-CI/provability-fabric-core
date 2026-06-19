"""PCS LabTrust release chain to PF-Core trace normalization (untrusted)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pf_core.hash_chain import compute_event_hash, compute_trace_hash, normalize_hash

GENESIS = "0" * 64

# Field mapping table: PCS trace_certificate -> PF-Core (see pf-core/docs/pf-core-trace-mapping.md)
PCS_CERTIFICATE_FIELD_MAP = {
    "certificate_id": "certificate.certificate_id",
    "schema_version": "certificate.schema_version",
    "trace_hash": "trace.trace_hash / certificate.trace_hash",
    "spec_hash": "certificate.contract_hash",
    "checker": "certificate.checker",
    "checker_version": "certificate.checker_version",
    "status": "certificate.safe",
    "producer": "certificate.created_by",
    "source_repo": "certificate.proof_ref",
}


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_trace_certificate(release_dir: Path) -> Optional[Dict[str, Any]]:
    return _read_json(release_dir / "trace_certificate.valid.json")


def _read_verification_result(release_dir: Path) -> Optional[Dict[str, Any]]:
    return _read_json(release_dir / "verification_result.valid.json")


def _read_science_claim_bundle(release_dir: Path) -> Optional[Dict[str, Any]]:
    return _read_json(release_dir / "science_claim_bundle.certified.valid.json")


def _policy_ref_from_property(property_id: Optional[str]) -> str:
    if property_id:
        return f"policy/{property_id}.v0"
    return "policy/lab-gate.v0"


def _evidence_ref_from_bundle(bundle: Optional[Dict[str, Any]]) -> str:
    if bundle and bundle.get("bundle_id"):
        return f"evidence/{bundle['bundle_id']}"
    return "evidence/lab-signoff.v0"


def _qc_gate_event(
    *,
    prev_hash: str = GENESIS,
    evidence_ref: str,
    policy_ref: str,
    reason: str,
) -> Dict[str, Any]:
    event: Dict[str, Any] = {
        "schema_version": "pf-core.event.v1",
        "event_id": "ev-pcs-qc-gate",
        "event_kind": {
            "type": "action",
            "action": {
                "schema_version": "pf-core.action.v0",
                "principal": {
                    "schema_version": "pf-core.principal.v0",
                    "id": "lab-operator-1",
                    "tenant_id": "tenant-lab",
                    "roles": ["lab_operator", "cap:file-read"],
                },
                "capability": {
                    "schema_version": "pf-core.capability.v0",
                    "id": "cap:file-read",
                    "effect_kind": "file.read",
                    "resource_pattern": "lab:*",
                },
                "resource": {
                    "schema_version": "pf-core.resource.v0",
                    "uri": "lab:qc-evidence",
                    "tenant_id": "tenant-lab",
                },
                "effect": {
                    "schema_version": "pf-core.effect.v0",
                    "kind": "file.read",
                },
            },
        },
        "decision": "allowed",
        "reason": f"{reason} (QC gate; policy_ref={policy_ref})",
        "evidence_ref": evidence_ref,
        "previous_event_hash": normalize_hash(prev_hash),
        "event_hash": "0" * 64,
    }
    event["event_hash"] = compute_event_hash(event)
    return event


def _lab_release_event(
    *,
    prev_hash: str = GENESIS,
    reason: str = "PCS LabTrust release chain replay",
    evidence_ref: str = "evidence/lab-signoff.v0",
    policy_ref: str = "policy/lab-gate.v0",
    spec_hash: Optional[str] = None,
) -> Dict[str, Any]:
    release_reason = reason
    if spec_hash:
        release_reason = f"{reason} (spec_hash={normalize_hash(spec_hash)}; policy_ref={policy_ref})"
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
        "reason": release_reason,
        "evidence_ref": evidence_ref,
        "previous_event_hash": normalize_hash(prev_hash),
        "event_hash": "0" * 64,
    }
    event["event_hash"] = compute_event_hash(event)
    return event


def normalize_labtrust_release(release_dir: Path) -> Dict[str, Any]:
    """Map pinned pcs-core labtrust fixtures to a PF-Core trace."""
    pcs_cert = _read_trace_certificate(release_dir)
    verification = _read_verification_result(release_dir)
    science_bundle = _read_science_claim_bundle(release_dir)

    property_id = pcs_cert.get("property_id") if pcs_cert else None
    spec_hash = pcs_cert.get("spec_hash") if pcs_cert else None
    trace_hash_hint = pcs_cert.get("trace_hash") if pcs_cert else None
    policy_ref = _policy_ref_from_property(property_id)
    evidence_ref = _evidence_ref_from_bundle(science_bundle)

    reason = "PCS LabTrust release chain replay"
    if pcs_cert and pcs_cert.get("producer"):
        reason = f"{reason} (producer={pcs_cert['producer']})"

    qc_passed = verification is None or verification.get("status") == "ProofChecked"
    events: List[Dict[str, Any]] = []
    prev = GENESIS

    if qc_passed:
        qc_event = _qc_gate_event(
            prev_hash=prev,
            evidence_ref=evidence_ref,
            policy_ref=policy_ref,
            reason=reason,
        )
        events.append(qc_event)
        prev = qc_event["event_hash"]

    release_event = _lab_release_event(
        prev_hash=prev,
        reason=reason,
        evidence_ref=evidence_ref,
        policy_ref=policy_ref,
        spec_hash=spec_hash,
    )
    events.append(release_event)

    trace: Dict[str, Any] = {
        "schema_version": "pf-core.trace.v0",
        "events": events,
        "trace_hash": "0" * 64,
    }
    trace["trace_hash"] = compute_trace_hash(trace)

    if trace_hash_hint:
        trace["pcs_trace_hash_hint"] = normalize_hash(str(trace_hash_hint))
    if spec_hash:
        trace["pcs_spec_hash_hint"] = normalize_hash(str(spec_hash))
    if property_id:
        trace["pcs_policy_ref"] = policy_ref

    return trace


def write_pcs_replay_trace(release_dir: Path, out_path: Path) -> Dict[str, Any]:
    trace = normalize_labtrust_release(release_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Strip non-schema hints before writing fixture consumed by schema validation.
    out_obj = {
        k: v
        for k, v in trace.items()
        if k not in {"pcs_trace_hash_hint", "pcs_spec_hash_hint", "pcs_policy_ref"}
    }
    out_path.write_text(json.dumps(out_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return trace


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    release = root / "fixtures" / "labtrust-release"
    out = Path(__file__).resolve().parents[2] / "pf-core" / "examples" / "valid" / "pcs_replay_trace.json"
    write_pcs_replay_trace(release, out)
    print(f"OK: wrote {out}")
