"""Authorization deciders mirroring Lean PFCore."""

from __future__ import annotations

from typing import Any, Mapping

from pf_core.errors import InvalidAction, InvalidDecision, InvalidPrincipal
from pf_core.event_kind import event_action, event_handoff, parse_event_kind
from pf_core.schemas import EFFECT_KINDS


def _principal_has_capability(principal: Mapping[str, Any], capability_id: str) -> bool:
    roles = principal.get("roles", [])
    return capability_id in roles


def same_tenant(principal: Mapping[str, Any], resource: Mapping[str, Any]) -> bool:
    return principal.get("tenant_id") == resource.get("tenant_id")


def effect_allowed(capability: Mapping[str, Any], effect: Mapping[str, Any]) -> bool:
    return capability.get("effect_kind") == effect.get("kind")


def action_allowed(action: Mapping[str, Any]) -> bool:
    principal = action["principal"]
    capability = action["capability"]
    resource = action["resource"]
    effect = action["effect"]
    if effect.get("kind") not in EFFECT_KINDS:
        return False
    return (
        _principal_has_capability(principal, capability["id"])
        and same_tenant(principal, resource)
        and effect_allowed(capability, effect)
    )


def event_safe(event: Mapping[str, Any]) -> bool:
    decision = event.get("decision")
    if decision == "denied":
        return True
    if decision == "allowed":
        try:
            kind_type, payload = parse_event_kind(event)
        except KeyError:
            return False
        if kind_type == "action":
            return action_allowed(payload)
        if kind_type == "handoff":
            return handoff_safe(payload)
    raise InvalidDecision(f"unknown decision status: {decision!r}", "decision")


def trace_safe(trace: Mapping[str, Any]) -> bool:
    return all(event_safe(ev) for ev in trace.get("events", []))


def handoff_safe(handoff: Mapping[str, Any]) -> bool:
    src = handoff["from_principal"]
    dst = handoff["to_principal"]
    cap = handoff["capability"]
    return (
        src.get("tenant_id") == dst.get("tenant_id")
        and _principal_has_capability(src, cap["id"])
        and _principal_has_capability(dst, cap["id"])
    )


def assert_action_semantics(action: Mapping[str, Any], path: str = "action") -> None:
    principal = action.get("principal")
    if not isinstance(principal, dict) or not principal.get("id"):
        raise InvalidPrincipal("principal.id required", f"{path}.principal")
    effect_kind = action.get("effect", {}).get("kind")
    if effect_kind not in EFFECT_KINDS:
        raise InvalidAction(f"unsupported effect kind: {effect_kind}", f"{path}.effect.kind")
    capability = action.get("capability", {})
    if not _principal_has_capability(principal, capability.get("id", "")):
        raise InvalidAction(
            f"principal lacks capability {capability.get('id')}",
            f"{path}.capability",
        )
