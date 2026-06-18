"""Authorization deciders mirroring Lean PFCore."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from pf_core.event_kind import event_action, event_handoff, parse_event_kind
from pf_core.schemas import EFFECT_KINDS

ROLE_CAPABILITY_MAP: dict[str, list[str]] = {
    "file_reader": ["cap:file-read"],
    "file_admin": ["cap:file-read", "cap:file-write"],
    "network_user": ["cap:network"],
    "email_user": ["cap:email-send"],
    "handoff_delegate": ["cap:handoff"],
    "mcp_user": ["cap:mcp-invoke"],
    "lab_operator": ["cap:lab-release"],
    "agent": ["cap:file-read", "cap:email-send", "cap:handoff", "cap:mcp-invoke"],
}


def _role_capability_ids(role: str) -> list[str]:
    if role in ROLE_CAPABILITY_MAP:
        return list(ROLE_CAPABILITY_MAP[role])
    if role.startswith("cap:"):
        return [role]
    return []


def allowed_capability_ids(principal: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for role in principal.get("roles", []):
        for cap_id in _role_capability_ids(str(role)):
            if cap_id not in ids:
                ids.append(cap_id)
    for cap_id in principal.get("capabilities", []):
        cap_id = str(cap_id)
        if cap_id not in ids:
            ids.append(cap_id)
    return ids


def _principal_has_capability(principal: Mapping[str, Any], capability_id: str) -> bool:
    return capability_id in allowed_capability_ids(principal)


def same_tenant(principal: Mapping[str, Any], resource: Mapping[str, Any]) -> bool:
    return principal.get("tenant_id") == resource.get("tenant_id")


def effect_allowed(capability: Mapping[str, Any], effect: Mapping[str, Any]) -> bool:
    return capability.get("effect_kind") == effect.get("kind")


def _normalize_action(action: Mapping[str, Any]) -> dict[str, Any]:
    if action.get("schema_version") == "pf-core.action.v1":
        return dict(action)
    return {
        "schema_version": "pf-core.action.v1",
        "id": action.get("id", ""),
        "principal": action["principal"],
        "capability": action["capability"],
        "effects": [action["effect"]],
        "reads": [action["resource"]],
        "writes": [],
    }


def action_allowed(action: Mapping[str, Any]) -> bool:
    act = _normalize_action(action)
    principal = act["principal"]
    capability = act["capability"]
    effects = act.get("effects", [])
    reads = act.get("reads", [])
    writes = act.get("writes", [])
    if not effects:
        return False
    if not _principal_has_capability(principal, capability["id"]):
        return False
    for effect in effects:
        if effect.get("kind") not in EFFECT_KINDS:
            return False
        if not effect_allowed(capability, effect):
            return False
    for resource in reads + writes:
        if not same_tenant(principal, resource):
            return False
    return True


def handoff_safe(handoff: Mapping[str, Any]) -> bool:
    version = handoff.get("schema_version", "pf-core.handoff.v0")
    src = handoff["from_principal"]
    dst = handoff["to_principal"]
    if src.get("tenant_id") != dst.get("tenant_id"):
        return False
    if version == "pf-core.handoff.v1":
        allowed = set(allowed_capability_ids(src))
        for cap in handoff.get("delegated_capabilities", []):
            if cap["id"] not in allowed:
                return False
        return bool(handoff.get("delegated_capabilities"))
    cap = handoff["capability"]
    return _principal_has_capability(src, cap["id"]) and _principal_has_capability(dst, cap["id"])


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
    from pf_core.errors import InvalidDecision

    raise InvalidDecision(f"unknown decision status: {decision!r}", "decision")


def trace_safe(trace: Mapping[str, Any]) -> bool:
    return all(event_safe(ev) for ev in trace.get("events", []))


def assert_action_semantics(action: Mapping[str, Any], path: str = "action") -> None:
    from pf_core.errors import InvalidAction, InvalidPrincipal

    act = _normalize_action(action)
    principal = act.get("principal")
    if not isinstance(principal, dict) or not principal.get("id"):
        raise InvalidPrincipal("principal.id required", f"{path}.principal")
    for idx, effect in enumerate(act.get("effects", [])):
        effect_kind = effect.get("kind")
        if effect_kind not in EFFECT_KINDS:
            raise InvalidAction(
                f"unsupported effect kind: {effect_kind}",
                f"{path}.effects[{idx}].kind",
            )
    capability = act.get("capability", {})
    if not _principal_has_capability(principal, capability.get("id", "")):
        raise InvalidAction(
            f"principal lacks capability {capability.get('id')}",
            f"{path}.capability",
        )
