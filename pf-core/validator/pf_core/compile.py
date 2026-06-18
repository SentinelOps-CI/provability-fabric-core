"""Deterministic runtime-observation to trace compiler."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from pf_core.deciders import action_allowed
from pf_core.errors import (
    AmbiguousMapping,
    EvidenceRefNotFound,
    InvalidSchemaVersion,
    MissingRequiredField,
    PolicyRefNotFound,
    UnsupportedCapability,
    UnsupportedEffect,
)
from pf_core.hash_chain import compute_event_hash, normalize_hash
from pf_core.schemas import EFFECT_KINDS, GENESIS_HASH, SCHEMA_KINDS

CAPABILITY_CATALOG: Dict[str, Dict[str, str]] = {
    "cap:file-read": {
        "id": "cap:file-read",
        "effect_kind": "file.read",
        "resource_pattern": "/data/*",
    },
    "cap:file-write": {
        "id": "cap:file-write",
        "effect_kind": "file.write",
        "resource_pattern": "/data/*",
    },
    "cap:network": {
        "id": "cap:network",
        "effect_kind": "network.egress",
        "resource_pattern": "*",
    },
    "cap:email-send": {
        "id": "cap:email-send",
        "effect_kind": "email.send",
        "resource_pattern": "mailto:*",
    },
    "cap:handoff": {
        "id": "cap:handoff",
        "effect_kind": "handoff.delegate",
        "resource_pattern": "agent:*",
    },
    "cap:mcp-invoke": {
        "id": "cap:mcp-invoke",
        "effect_kind": "mcp.invoke",
        "resource_pattern": "mcp:*",
    },
    "cap:mcp-alt": {
        "id": "cap:mcp-alt",
        "effect_kind": "mcp.invoke",
        "resource_pattern": "mcp:alt/*",
    },
    "cap:lab-release": {
        "id": "cap:lab-release",
        "effect_kind": "lab.release",
        "resource_pattern": "lab:*",
    },
}

POLICY_CATALOG = {"policy/default.v0", "policy/lab-gate.v0"}
EVIDENCE_CATALOG = {
    "evidence/mcp-audit.v0",
    "evidence/lab-signoff.v0",
    "evidence/handoff.v0",
}


def load_capability_catalog(root: Optional[Path] = None) -> None:
    """Merge adapter-exported catalog when present (untrusted input)."""
    global CAPABILITY_CATALOG
    path = (root or Path(".")) / "adapters/provability-fabric/fixtures/capability_catalog.json"
    if not path.exists():
        return
    exported = json.loads(path.read_text(encoding="utf-8"))
    for entry in exported.get("capabilities", []):
        CAPABILITY_CATALOG[entry["id"]] = entry


def _check_schema_version(obs: Mapping[str, Any]) -> str:
    version = obs.get("schema_version")
    if version in {"pf-core.runtime_observation.v0", "pf-core.runtime_observation.v1"}:
        return str(version)
    expected = SCHEMA_KINDS["runtime_observation"]
    raise InvalidSchemaVersion(expected, str(version))


def _resolve_capability(obs: Mapping[str, Any]) -> Dict[str, str]:
    effect_kind = obs.get("effect_kind")
    if effect_kind not in EFFECT_KINDS:
        raise UnsupportedEffect(str(effect_kind), "effect_kind")

    cap_id = obs.get("capability_id")
    if cap_id:
        if cap_id not in CAPABILITY_CATALOG:
            raise UnsupportedCapability(str(cap_id), "capability_id")
        cap = CAPABILITY_CATALOG[cap_id]
        if cap["effect_kind"] != effect_kind:
            raise AmbiguousMapping(
                f"capability_id {cap_id} maps to {cap['effect_kind']}, not {effect_kind}",
                "capability_id",
            )
        return {
            "schema_version": "pf-core.capability.v0",
            "id": cap["id"],
            "effect_kind": cap["effect_kind"],
            "resource_pattern": cap["resource_pattern"],
        }

    matches = [c for c in CAPABILITY_CATALOG.values() if c["effect_kind"] == effect_kind]
    if len(matches) == 0:
        raise UnsupportedCapability(f"no capability for effect {effect_kind}", "effect_kind")
    if len(matches) > 1:
        raise AmbiguousMapping(
            f"multiple capabilities for effect {effect_kind}; set capability_id",
            "effect_kind",
        )
    cap = matches[0]
    return {
        "schema_version": "pf-core.capability.v0",
        "id": cap["id"],
        "effect_kind": cap["effect_kind"],
        "resource_pattern": cap["resource_pattern"],
    }


def compile_observation_v1(obs: Mapping[str, Any]) -> Dict[str, Any]:
    for field in (
        "trace_id",
        "event_id",
        "observation_id",
        "principal",
        "action",
        "decision",
        "policy_ref",
        "evidence_ref",
        "runtime_ref",
        "timestamp",
        "previous_event_hash",
        "hash",
    ):
        if field not in obs:
            raise MissingRequiredField(field)

    policy_ref = obs.get("policy_ref")
    if policy_ref and policy_ref not in POLICY_CATALOG:
        raise PolicyRefNotFound(str(policy_ref), "policy_ref")

    evidence_ref = obs.get("evidence_ref")
    if evidence_ref and evidence_ref not in EVIDENCE_CATALOG:
        raise EvidenceRefNotFound(str(evidence_ref), "evidence_ref")

    action = dict(obs["action"])
    decision = obs["decision"]
    if decision == "allowed" and not action_allowed(action):
        decision = "denied"

    prev_hash = normalize_hash(str(obs["previous_event_hash"]))
    event: Dict[str, Any] = {
        "schema_version": "pf-core.event.v1",
        "event_id": obs["event_id"],
        "event_kind": {"type": "action", "action": action},
        "decision": decision,
        "reason": obs.get("reason", ""),
        "evidence_ref": obs.get("evidence_ref", ""),
        "previous_event_hash": prev_hash,
        "event_hash": "0" * 64,
    }
    event["event_hash"] = compute_event_hash(event)
    return event


def compile_observation(
    obs: Mapping[str, Any],
    *,
    principal_roles: Optional[list[str]] = None,
) -> Dict[str, Any]:
    version = _check_schema_version(obs)
    if version == "pf-core.runtime_observation.v1":
        return compile_observation_v1(obs)

    warnings.warn(
        "pf-core.runtime_observation.v0 is deprecated; use pf-core.runtime_observation.v1 "
        "(see pf-core/scripts/migrate-v0-to-v1.py)",
        DeprecationWarning,
        stacklevel=2,
    )

    for field in (
        "observation_id",
        "principal_id",
        "tenant_id",
        "effect_kind",
        "resource_uri",
        "decision",
        "previous_event_hash",
    ):
        if field not in obs:
            raise MissingRequiredField(field)

    policy_ref = obs.get("policy_ref")
    if policy_ref and policy_ref not in POLICY_CATALOG:
        raise PolicyRefNotFound(str(policy_ref), "policy_ref")

    evidence_ref = obs.get("evidence_ref")
    if evidence_ref and evidence_ref not in EVIDENCE_CATALOG:
        raise EvidenceRefNotFound(str(evidence_ref), "evidence_ref")

    capability = _resolve_capability(obs)
    roles = principal_roles or [capability["id"]]
    if obs.get("decision") == "allowed" and capability["id"] not in roles:
        roles = list(roles) + [capability["id"]]

    principal = {
        "schema_version": "pf-core.principal.v0",
        "id": obs["principal_id"],
        "tenant_id": obs["tenant_id"],
        "roles": roles,
    }
    resource = {
        "schema_version": "pf-core.resource.v0",
        "uri": obs["resource_uri"],
        "tenant_id": obs["tenant_id"],
    }
    effect = {
        "schema_version": "pf-core.effect.v0",
        "kind": obs["effect_kind"],
    }
    action = {
        "schema_version": "pf-core.action.v0",
        "principal": principal,
        "capability": capability,
        "resource": resource,
        "effect": effect,
    }

    decision = obs["decision"]
    if decision == "allowed" and not action_allowed(action):
        decision = "denied"

    event: Dict[str, Any] = {
        "schema_version": "pf-core.event.v1",
        "event_id": obs["observation_id"],
        "event_kind": {"type": "action", "action": action},
        "decision": decision,
        "previous_event_hash": obs.get("previous_event_hash", GENESIS_HASH),
        "event_hash": "0" * 64,
    }
    event["event_hash"] = compute_event_hash(event)
    return event
