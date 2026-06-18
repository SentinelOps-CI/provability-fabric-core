"""Contract satisfaction deciders mirroring Lean PFCore.Contract."""

from __future__ import annotations

from typing import Any, Mapping

from pf_core.deciders import action_allowed, event_safe, trace_safe
from pf_core.errors import ContractPreconditionFailed, ContractPostconditionFailed, PFCoreError
from pf_core.event_kind import event_action
from pf_core.schemas import EFFECT_KINDS


def _check_pre(contract: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
    pre = contract.get("pre") or {}
    try:
        action = event_action(event)
    except KeyError:
        return True
    principal = action["principal"]
    capability = action["capability"]
    resource = action["resource"]
    effect = action["effect"]

    cap_req = pre.get("require_capability")
    if cap_req and cap_req not in principal.get("roles", []):
        return False

    role_req = pre.get("require_role")
    if role_req and role_req not in principal.get("roles", []):
        return False

    effect_req = pre.get("require_effect")
    if effect_req:
        if effect_req not in EFFECT_KINDS:
            return False
        if effect.get("kind") != effect_req:
            return False

    if pre.get("require_tenant_match") and principal.get("tenant_id") != resource.get("tenant_id"):
        return False

    return True


def _check_post(contract: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
    post = contract.get("post") or {}
    decision_req = post.get("require_decision")
    if decision_req and event.get("decision") != decision_req:
        return False
    if post.get("require_event_safe") and not event_safe(event):
        return False
    return True


def satisfies_contract_pre(contract: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
    return _check_pre(contract, event)


def satisfies_contract_post(contract: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
    return _check_pre(contract, event) and _check_post(contract, event)


def satisfies_contract_event(contract: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
    return satisfies_contract_post(contract, event)


def trace_satisfies_contract(contract: Mapping[str, Any], trace: Mapping[str, Any]) -> bool:
    events = trace.get("events", [])
    return all(satisfies_contract_event(contract, ev) for ev in events)


def contract_invariant_holds(contract: Mapping[str, Any], trace: Mapping[str, Any]) -> bool:
    inv = contract.get("invariant") or {}
    if inv.get("require_trace_safe"):
        return trace_safe(trace)
    return True


def assert_contract_event(
    contract: Mapping[str, Any],
    event: Mapping[str, Any],
    *,
    path: str = "event",
) -> None:
    if not _check_pre(contract, event):
        raise ContractPreconditionFailed(
            f"contract pre failed for {contract.get('name', 'unnamed')}",
            path,
        )
    if not _check_post(contract, event):
        raise ContractPostconditionFailed(
            f"contract post failed for {contract.get('name', 'unnamed')}",
            path,
        )


def observation_satisfies_contract_pre(
    contract: Mapping[str, Any], observation: Mapping[str, Any]
) -> bool:
    """Check observation-level pre fields (policy_ref, evidence_ref)."""
    pre = contract.get("pre") or {}
    policy = pre.get("require_policy_ref")
    if policy and observation.get("policy_ref") != policy:
        return False
    evidence = pre.get("require_evidence_ref")
    if evidence and observation.get("evidence_ref") != evidence:
        return False
    return True


def assert_observation_contract_pre(
    contract: Mapping[str, Any], observation: Mapping[str, Any]
) -> None:
    if not observation_satisfies_contract_pre(contract, observation):
        raise ContractPreconditionFailed(
            f"observation failed contract pre for {contract.get('name', 'unnamed')}",
            "observation",
        )


def assert_trace_satisfies_contract(
    contract: Mapping[str, Any],
    trace: Mapping[str, Any],
) -> None:
    inv = contract.get("invariant") or {}
    if inv.get("require_trace_safe") and not trace_safe(trace):
        raise PFCoreError("ContractInvariantFailed", "trace_safe invariant failed")
    for idx, ev in enumerate(trace.get("events", [])):
        assert_contract_event(contract, ev, path=f"events[{idx}]")
