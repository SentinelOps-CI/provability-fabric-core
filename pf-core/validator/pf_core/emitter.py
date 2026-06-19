"""Adapter artifact emission (observation, event, trace, certificate, audit)."""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from pf_core.audit_line import format_audit_line
from pf_core.event_kind import event_action
from pf_core.compile import compile_observation
from pf_core.contracts import assert_observation_contract_pre, primary_action_effect_kind
from pf_core.deciders import trace_safe
from pf_core.errors import PFCoreError
from pf_core.hash_chain import compute_trace_hash, validate_trace_hashes
from pf_core.schemas import load_registry, validate_object

CHECKER = "lean4"
CHECKER_VERSION = "4.14.0"
PROOF_REF = "pf-core/lean/PFCore/Soundness.lean"
DEFAULT_ASSUMPTIONS = ["A1", "A2", "A3", "A4", "A6", "A8"]

FORBIDDEN_CERTIFICATE_PHRASES = [
    "this agent is safe",
    "this tool is secure",
    "this workflow is verified",
    "this model is aligned",
    "this runtime is formally verified",
    "verified agent",
]


def _reject_forbidden_certificate_text(obj: Mapping[str, Any]) -> None:
    blob = json.dumps(obj, sort_keys=True).lower()
    for phrase in FORBIDDEN_CERTIFICATE_PHRASES:
        if phrase in blob:
            raise PFCoreError(
                "ForbiddenCertificateClaim",
                f"certificate text must not contain forbidden phrase: {phrase!r}",
            )


def compute_contract_hash(contract: Mapping[str, Any]) -> str:
    payload = json.dumps(contract, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_trace(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    trace: Dict[str, Any] = {
        "schema_version": "pf-core.trace.v0",
        "events": events,
        "trace_hash": "0" * 64,
    }
    trace["trace_hash"] = compute_trace_hash(trace)
    return trace


def emit_certificate(
    trace: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    certificate_id: Optional[str] = None,
    claim_class: str = "Lean-proved",
    assumptions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    events = list(trace["events"])
    safe = trace_safe(trace)
    cert = {
        "schema_version": "pf-core.certificate.v0",
        "certificate_id": certificate_id or f"cert-{uuid.uuid4().hex[:12]}",
        "trace_hash": trace["trace_hash"],
        "contract_hash": compute_contract_hash(contract),
        "proof_ref": PROOF_REF,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "claim_class": claim_class,
        "assumptions": assumptions or DEFAULT_ASSUMPTIONS,
        "event_count": len(events),
        "safe": safe,
        "created_by": "pf-core-validator",
    }
    _reject_forbidden_certificate_text(cert)
    return cert


def emit_artifacts(
    observation: Mapping[str, Any],
    *,
    out_dir: Path,
    schemas_dir: Path,
    contract: Optional[Mapping[str, Any]] = None,
    trace_id: Optional[str] = None,
    runtime_id: str = "pf-core-adapter",
    prior_events: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Path]:
    registry = load_registry(schemas_dir)
    validate_object(observation, registry)

    event = compile_observation(observation)
    validate_object(event, registry)

    events = list(prior_events or [])
    events.append(event)
    trace = build_trace(events)
    validate_trace_hashes(trace)
    validate_object(trace, registry)

    contract_obj = contract or {
        "schema_version": "pf-core.contract.v0",
        "name": "default-effect",
        "pre": {"require_effect": primary_action_effect_kind(event_action(event))},
        "post": {"require_event_safe": True},
        "invariant": {"require_trace_safe": True},
    }
    validate_object(contract_obj, registry)
    assert_observation_contract_pre(contract_obj, observation)

    certificate = emit_certificate(trace, contract_obj)
    validate_object(certificate, registry)

    tid = trace_id or f"trace-{observation['observation_id']}"
    audit_line = format_audit_line(
        trace_id=tid,
        event=event,
        trace=trace,
        observation=observation,
        runtime_id=runtime_id,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "runtime_observation": out_dir / "runtime_observation.json",
        "event": out_dir / "event.json",
        "trace": out_dir / "trace.json",
        "certificate": out_dir / "certificate.json",
        "audit": out_dir / "audit.jsonl",
    }

    for key, path in paths.items():
        if key == "audit":
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(audit_line, sort_keys=True) + "\n")
        else:
            obj = {
                "runtime_observation": observation,
                "event": event,
                "trace": trace,
                "certificate": certificate,
            }[key]
            path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return paths


def emit_audit_for_trace(
    trace: Mapping[str, Any],
    *,
    out_path: Path,
    trace_id: str,
    observation: Mapping[str, Any],
    runtime_id: str = "pf-core-adapter",
    reason: str = "adapter_compile",
) -> Path:
    """Write audit.jsonl lines for each event in an existing trace."""
    events = trace.get("events")
    if not isinstance(events, list) or not events:
        raise PFCoreError("EmptyTrace", "trace has no events for audit emission")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for event in events:
            audit_line = format_audit_line(
                trace_id=trace_id,
                event=event,
                trace=trace,
                observation=observation,
                runtime_id=runtime_id,
                reason=reason,
            )
            fh.write(json.dumps(audit_line, sort_keys=True) + "\n")
    return out_path
