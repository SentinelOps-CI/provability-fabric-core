"""Normalize provability-fabric sidecar audit lines to runtime_observation.v1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

# Sidecar audit field names (provability-fabric runtime/sidecar-watcher patterns).
_SIDEcar_TO_OBS: Dict[str, str] = {
    "request_id": "observation_id",
    "agent_id": "principal_id",
    "tenant": "tenant_id",
    "tool_effect": "effect_kind",
    "resource": "resource_uri",
    "policy_decision": "decision",
    "prev_hash": "previous_event_hash",
    "policy_bundle": "policy_ref",
    "audit_bundle": "evidence_ref",
    "capability_hint": "capability_id",
    "trace_id": "trace_id",
    "event_id": "event_id",
    "runtime_ref": "runtime_ref",
    "timestamp": "timestamp",
    "reason": "reason",
}

_CATALOG_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "capability_catalog.json"
_CATALOG_CACHE: Dict[str, Any] | None = None


def _load_catalog() -> Dict[str, Any]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is None:
        _CATALOG_CACHE = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    return _CATALOG_CACHE


def _map_decision(value: Any) -> str:
    text = str(value).lower()
    if text in {"allow", "allowed", "permit", "permitted"}:
        return "allowed"
    if text in {"deny", "denied", "block", "blocked"}:
        return "denied"
    return text


def _resolve_capability_id(effect_kind: str, capability_id: str | None) -> str:
    catalog = _load_catalog()
    capabilities = catalog.get("capabilities", [])
    matches = [c for c in capabilities if c.get("effect_kind") == effect_kind]
    if capability_id:
        return capability_id
    if len(matches) == 1:
        return str(matches[0]["id"])
    if len(matches) > 1:
        raise ValueError(
            f"capability_hint required for effect {effect_kind}; "
            f"matches {[c['id'] for c in matches]}"
        )
    raise ValueError(f"no catalog capability for effect {effect_kind}")


def _roles_for_capability(capability_id: str) -> List[str]:
    catalog = _load_catalog()
    role_map = catalog.get("principal_roles_by_capability", {})
    roles = role_map.get(capability_id)
    if isinstance(roles, list) and roles:
        return [str(r) for r in roles]
    return ["mcp_user"]


def normalize_sidecar_line(line: Mapping[str, Any]) -> Dict[str, Any]:
    """Map a sidecar audit JSON line to pf-core.runtime_observation.v1."""
    flat: Dict[str, Any] = {}
    for src, dst in _SIDEcar_TO_OBS.items():
        if src in line:
            flat[dst] = line[src]

    observation_id = flat.get("observation_id") or flat.get("event_id") or "obs-unknown"
    trace_id = flat.get("trace_id") or f"trace-{observation_id}"
    event_id = flat.get("event_id") or observation_id
    principal_id = flat.get("principal_id", "unknown-agent")
    tenant_id = flat.get("tenant_id", "unknown-tenant")
    effect_kind = flat.get("effect_kind", "mcp.invoke")
    resource_uri = flat.get("resource_uri", "mcp:unknown")
    decision = _map_decision(flat.get("decision", "denied"))
    prev_hash = flat.get("previous_event_hash", "0" * 64)

    capability_id = _resolve_capability_id(effect_kind, flat.get("capability_id"))
    roles = _roles_for_capability(capability_id)
    cap_entry = {
        "schema_version": "pf-core.capability.v0",
        "id": capability_id,
        "effect_kind": effect_kind,
        "resource_pattern": "mcp:*",
    }

    principal = {
        "schema_version": "pf-core.principal.v1",
        "id": principal_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "capabilities": [capability_id],
    }

    action: Dict[str, Any] = {
        "schema_version": "pf-core.action.v1",
        "id": f"act-{observation_id}",
        "capability": cap_entry,
        "effects": [{"schema_version": "pf-core.effect.v0", "kind": effect_kind}],
        "reads": [
            {
                "schema_version": "pf-core.resource.v0",
                "uri": resource_uri,
                "tenant_id": tenant_id,
            }
        ],
        "writes": [],
        "principal": principal,
    }

    obs: Dict[str, Any] = {
        "schema_version": "pf-core.runtime_observation.v1",
        "trace_id": trace_id,
        "event_id": event_id,
        "observation_id": observation_id,
        "principal": principal,
        "action": action,
        "decision": decision,
        "reason": flat.get("reason", "sidecar audit line"),
        "policy_ref": flat.get("policy_ref", "policy/default.v0"),
        "evidence_ref": flat.get("evidence_ref", "evidence/mcp-audit.v0"),
        "runtime_ref": flat.get("runtime_ref", "provability-fabric/sidecar-watcher"),
        "timestamp": flat.get("timestamp", "2026-06-18T00:00:00Z"),
        "previous_event_hash": prev_hash,
        "hash": "0" * 64,
    }
    return obs


def normalize_sidecar_jsonl(text: str) -> list[Dict[str, Any]]:
    observations: list[Dict[str, Any]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        observations.append(normalize_sidecar_line(json.loads(line)))
    return observations


# Admission-controller audit field names (provability-fabric runtime/admission-controller).
_ADMISSION_TO_OBS: Dict[str, str] = {
    "admission_id": "observation_id",
    "request_uid": "observation_id",
    "trace_id": "trace_id",
    "event_id": "event_id",
    "principal_id": "principal_id",
    "namespace": "tenant_id",
    "effect_kind": "effect_kind",
    "target_resource": "resource_uri",
    "verdict": "decision",
    "prev_hash": "previous_event_hash",
    "policy_bundle": "policy_ref",
    "evidence_bundle": "evidence_ref",
    "capability": "capability_id",
    "runtime_ref": "runtime_ref",
    "timestamp": "timestamp",
    "reason": "reason",
}


def normalize_admission_line(line: Mapping[str, Any]) -> Dict[str, Any]:
    """Map an admission-controller audit JSON line to runtime_observation.v1."""
    flat: Dict[str, Any] = {}
    for src, dst in _ADMISSION_TO_OBS.items():
        if src in line:
            flat[dst] = line[src]

    observation_id = flat.get("observation_id") or flat.get("event_id") or "obs-admission-unknown"
    trace_id = flat.get("trace_id") or f"trace-{observation_id}"
    event_id = flat.get("event_id") or observation_id
    principal_id = flat.get("principal_id", "unknown-agent")
    tenant_id = flat.get("tenant_id", "default")
    effect_kind = flat.get("effect_kind", "file.read")
    resource_uri = flat.get("resource_uri", "/data/unknown")
    decision = _map_decision(flat.get("decision", "denied"))
    prev_hash = flat.get("previous_event_hash", "0" * 64)

    capability_id = _resolve_capability_id(effect_kind, flat.get("capability_id"))
    roles = _roles_for_capability(capability_id)
    cap_entry = next(
        c for c in _load_catalog()["capabilities"] if c["id"] == capability_id
    )
    capability = {
        "schema_version": "pf-core.capability.v0",
        "id": capability_id,
        "effect_kind": effect_kind,
        "resource_pattern": cap_entry.get("resource_pattern", "*"),
    }

    principal = {
        "schema_version": "pf-core.principal.v1",
        "id": principal_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "capabilities": [capability_id],
    }

    action: Dict[str, Any] = {
        "schema_version": "pf-core.action.v1",
        "id": f"act-{observation_id}",
        "capability": capability,
        "effects": [{"schema_version": "pf-core.effect.v0", "kind": effect_kind}],
        "reads": [
            {
                "schema_version": "pf-core.resource.v0",
                "uri": resource_uri,
                "tenant_id": tenant_id,
            }
        ],
        "writes": [],
        "principal": principal,
    }

    return {
        "schema_version": "pf-core.runtime_observation.v1",
        "trace_id": trace_id,
        "event_id": event_id,
        "observation_id": observation_id,
        "principal": principal,
        "action": action,
        "decision": decision,
        "reason": flat.get("reason", "admission controller audit line"),
        "policy_ref": flat.get("policy_ref", "policy/default.v0"),
        "evidence_ref": flat.get("evidence_ref", ""),
        "runtime_ref": flat.get("runtime_ref", "provability-fabric/admission-controller"),
        "timestamp": flat.get("timestamp", "2026-06-18T00:00:00Z"),
        "previous_event_hash": prev_hash,
        "hash": "0" * 64,
    }
