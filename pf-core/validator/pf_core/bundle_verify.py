"""Five-file PF-Core artifact bundle verifier (Phase 7 reference implementation)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from pf_core.audit_line import AUDIT_SCHEMA_VERSION
from pf_core.errors import PFCoreError
from pf_core.hash_chain import validate_trace_hashes
from pf_core.schemas import load_registry, validate_object

BUNDLE_FILES = (
    "runtime_observation.json",
    "event.json",
    "trace.json",
    "certificate.json",
    "audit.jsonl",
)

_REQUIRED_AUDIT_FIELDS = {
    "schema_version",
    "trace_id",
    "event_id",
    "principal_id",
    "action_id",
    "capability",
    "decision",
    "reason",
    "policy_ref",
    "evidence_ref",
    "event_hash",
    "previous_event_hash",
    "trace_hash",
    "runtime_id",
}


def _validate_audit_line(line: Mapping[str, Any], index: int) -> None:
    if line.get("schema_version") != AUDIT_SCHEMA_VERSION:
        raise PFCoreError(
            "InvalidAuditLine",
            f"audit line {index}: expected {AUDIT_SCHEMA_VERSION}",
        )
    missing = _REQUIRED_AUDIT_FIELDS - set(line.keys())
    if missing:
        raise PFCoreError(
            "InvalidAuditLine",
            f"audit line {index}: missing fields {sorted(missing)}",
        )


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_audit_lines(path: Path) -> List[Dict[str, Any]]:
    lines: List[Dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line:
            lines.append(json.loads(line))
    return lines


def verify_bundle(
    bundle_dir: Path,
    *,
    schemas_dir: Path,
    pf_core_version: Optional[str] = None,
    require_safe: bool = True,
) -> Dict[str, Any]:
    """Verify PF-Core emit-artifacts five-file bundle layout and bindings."""
    bundle_dir = Path(bundle_dir)
    if not bundle_dir.is_dir():
        raise PFCoreError("BundleNotFound", f"bundle directory not found: {bundle_dir}")

    missing = [name for name in BUNDLE_FILES if not (bundle_dir / name).is_file()]
    if missing:
        raise PFCoreError("BundleIncomplete", f"missing bundle files: {', '.join(missing)}")

    registry = load_registry(schemas_dir)
    observation = _load_json(bundle_dir / "runtime_observation.json")
    event = _load_json(bundle_dir / "event.json")
    trace = _load_json(bundle_dir / "trace.json")
    certificate = _load_json(bundle_dir / "certificate.json")
    audit_lines = _load_audit_lines(bundle_dir / "audit.jsonl")

    validate_object(observation, registry)
    validate_object(event, registry)
    validate_object(trace, registry)
    validate_object(certificate, registry)
    for idx, line in enumerate(audit_lines):
        _validate_audit_line(line, idx)

    validate_trace_hashes(trace)

    trace_hash = trace.get("trace_hash")
    if certificate.get("trace_hash") != trace_hash:
        raise PFCoreError(
            "CertificateTraceHashMismatch",
            "certificate.trace_hash does not match trace.trace_hash",
        )

    if require_safe and certificate.get("safe") is not True:
        raise PFCoreError("UnsafeCertificate", "certificate.safe must be true")

    events = trace.get("events", [])
    if not events:
        raise PFCoreError("EmptyTrace", "trace has no events")
    if events[-1] != event and events[-1].get("event_hash") != event.get("event_hash"):
        raise PFCoreError("EventTraceMismatch", "event.json does not match final trace event")

    if certificate.get("event_count") != len(events):
        raise PFCoreError(
            "CertificateEventCountMismatch",
            f"certificate.event_count {certificate.get('event_count')} != {len(events)}",
        )

    if len(audit_lines) != len(events):
        raise PFCoreError(
            "AuditLineCountMismatch",
            f"audit.jsonl lines {len(audit_lines)} != trace events {len(events)}",
        )

    for idx, (audit_line, trace_event) in enumerate(zip(audit_lines, events)):
        if audit_line.get("trace_hash") != trace_hash:
            raise PFCoreError(
                "AuditTraceHashMismatch",
                f"audit line {idx} trace_hash mismatch",
            )
        if audit_line.get("event_hash") != trace_event.get("event_hash"):
            raise PFCoreError(
                "AuditEventHashMismatch",
                f"audit line {idx} event_hash mismatch",
            )
        if audit_line.get("event_id") != trace_event.get("event_id"):
            raise PFCoreError(
                "AuditEventIdMismatch",
                f"audit line {idx} event_id mismatch",
            )

    if pf_core_version:
        version_path = schemas_dir.parent / "VERSION"
        if version_path.is_file():
            pinned = version_path.read_text(encoding="utf-8").strip()
            if pinned != pf_core_version:
                raise PFCoreError(
                    "PfCoreVersionMismatch",
                    f"expected pf-core version {pf_core_version}, got {pinned}",
                )

    return {
        "valid": True,
        "trace_hash": trace_hash,
        "event_count": len(events),
        "safe": certificate.get("safe"),
        "bundle_dir": str(bundle_dir),
    }
