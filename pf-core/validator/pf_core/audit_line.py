"""Audit line formatting for adapter outputs."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from pf_core.event_kind import event_action, event_handoff

AUDIT_SCHEMA_VERSION = "pf-core.audit_line.v0"


def _handoff_audit_capability(handoff: Mapping[str, Any]) -> str:
    delegated = handoff.get("delegated_capabilities")
    if not isinstance(delegated, list) or not delegated:
        raise KeyError("delegated_capabilities")
    ids = [
        cap["id"]
        for cap in delegated
        if isinstance(cap, Mapping) and cap.get("id")
    ]
    if not ids:
        raise KeyError("delegated_capabilities")
    if len(ids) == 1:
        return str(ids[0])
    return ",".join(str(cap_id) for cap_id in ids)


def format_audit_line(
    *,
    trace_id: str,
    event: Mapping[str, Any],
    trace: Mapping[str, Any],
    observation: Mapping[str, Any],
    runtime_id: str,
    reason: str = "adapter_compile",
) -> Dict[str, Any]:
    handoff = event_handoff(event)
    if handoff is not None:
        principal_id = handoff["from_principal"]["id"]
        capability = _handoff_audit_capability(handoff)
    else:
        action = event_action(event)
        principal_id = action["principal"]["id"]
        capability = action["capability"]["id"]
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "trace_id": trace_id,
        "event_id": event["event_id"],
        "principal_id": principal_id,
        "action_id": event["event_id"],
        "capability": capability,
        "decision": event["decision"],
        "reason": reason,
        "policy_ref": observation.get("policy_ref", ""),
        "evidence_ref": observation.get("evidence_ref", ""),
        "event_hash": event["event_hash"],
        "previous_event_hash": event["previous_event_hash"],
        "trace_hash": trace["trace_hash"],
        "runtime_id": runtime_id,
    }
