#!/usr/bin/env python3
"""Generate PF-Core example fixtures with valid hash chains."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validator"))

from pf_core.hash_chain import compute_event_hash, compute_trace_hash

OUT = ROOT / "examples"
GENESIS = "0" * 64

AGENT = {
    "schema_version": "pf-core.principal.v0",
    "id": "agent-1",
    "tenant_id": "tenant-a",
    "roles": ["cap:file-read", "cap:email-send", "cap:handoff", "cap:mcp-invoke"],
}

AGENT_NO_NETWORK = {
    **AGENT,
    "roles": ["cap:file-read", "cap:email-send"],
}

AGENT_NO_EMAIL = {
    **AGENT,
    "roles": ["cap:file-read", "cap:handoff", "cap:mcp-invoke"],
}

RECIPIENT = {
    "schema_version": "pf-core.principal.v0",
    "id": "agent-2",
    "tenant_id": "tenant-a",
    "roles": ["cap:handoff"],
}

CAP_FILE_READ = {
    "schema_version": "pf-core.capability.v0",
    "id": "cap:file-read",
    "effect_kind": "file.read",
    "resource_pattern": "/data/*",
}

CAP_NETWORK = {
    "schema_version": "pf-core.capability.v0",
    "id": "cap:network",
    "effect_kind": "network.egress",
    "resource_pattern": "*",
}

CAP_EMAIL = {
    "schema_version": "pf-core.capability.v0",
    "id": "cap:email-send",
    "effect_kind": "email.send",
    "resource_pattern": "mailto:*",
}

CAP_HANDOFF = {
    "schema_version": "pf-core.capability.v0",
    "id": "cap:handoff",
    "effect_kind": "handoff.delegate",
    "resource_pattern": "agent:*",
}

CAP_MCP = {
    "schema_version": "pf-core.capability.v0",
    "id": "cap:mcp-invoke",
    "effect_kind": "mcp.invoke",
    "resource_pattern": "mcp:*",
}

CAP_LAB = {
    "schema_version": "pf-core.capability.v0",
    "id": "cap:lab-release",
    "effect_kind": "lab.release",
    "resource_pattern": "lab:*",
}


def resource(uri: str, tenant: str = "tenant-a") -> dict:
    return {
        "schema_version": "pf-core.resource.v0",
        "uri": uri,
        "tenant_id": tenant,
    }


def effect(kind: str) -> dict:
    return {"schema_version": "pf-core.effect.v0", "kind": kind}


def action(principal, capability, uri: str, kind: str, tenant: str = "tenant-a") -> dict:
    return {
        "schema_version": "pf-core.action.v0",
        "principal": principal,
        "capability": capability,
        "resource": resource(uri, tenant),
        "effect": effect(kind),
    }


def make_event(event_id: str, act: dict, decision: str, previous_event_hash: str) -> dict:
    ev = {
        "schema_version": "pf-core.event.v1",
        "event_id": event_id,
        "event_kind": {"type": "action", "action": act},
        "decision": decision,
        "previous_event_hash": previous_event_hash,
        "event_hash": "0" * 64,
    }
    ev["event_hash"] = compute_event_hash(ev)
    return ev


def make_handoff_event(
    event_id: str, handoff_doc: dict, decision: str, previous_event_hash: str
) -> dict:
    ev = {
        "schema_version": "pf-core.event.v1",
        "event_id": event_id,
        "event_kind": {"type": "handoff", "handoff": handoff_doc},
        "decision": decision,
        "previous_event_hash": previous_event_hash,
        "event_hash": "0" * 64,
    }
    ev["event_hash"] = compute_event_hash(ev)
    return ev


def make_trace(events: list[dict]) -> dict:
    trace = {"schema_version": "pf-core.trace.v0", "events": events, "trace_hash": "0" * 64}
    trace["trace_hash"] = compute_trace_hash(trace)
    return trace


def chain_events(specs: list[tuple[str, dict, str]]) -> list[dict]:
    prev = GENESIS
    out = []
    for eid, act, decision in specs:
        ev = make_event(eid, act, decision, prev)
        out.append(ev)
        prev = ev["event_hash"]
    return out


def write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def write_invalid(path: Path, obj: dict, expected_error: str, must_fail_at: str) -> None:
    write(path, {**obj, "expected_error": expected_error, "must_fail_at": must_fail_at})


def main() -> None:
    file_read_act = action(AGENT, CAP_FILE_READ, "/data/report.txt", "file.read")
    file_read_ev = make_event("ev-file-read-1", file_read_act, "allowed", GENESIS)
    write(OUT / "valid/file_read_allowed.json", file_read_ev)
    write(OUT / "valid/file_read_allowed_trace.json", make_trace([file_read_ev]))

    file_read_bad = action(AGENT, CAP_FILE_READ, "/data/report.txt", "file.read", "tenant-b")
    file_read_denied_ev = make_event("ev-file-read-denied", file_read_bad, "denied", GENESIS)
    write(OUT / "valid/file_read_denied.json", file_read_denied_ev)

    write_invalid(
        OUT / "invalid/file_read_allowed_wrong_tenant.json",
        make_event("ev-file-read-bad", file_read_bad, "allowed", GENESIS),
        "UnsafeEvent",
        "decider_check",
    )

    net_act = action(AGENT_NO_NETWORK, CAP_NETWORK, "https://example.com", "network.egress")
    net_ev = make_event("ev-net-denied", net_act, "denied", GENESIS)
    write(OUT / "valid/network_denied.json", net_ev)
    write_invalid(
        OUT / "invalid/network_allowed_without_cap.json",
        make_event("ev-net-bad", net_act, "allowed", GENESIS),
        "UnsafeEvent",
        "decider_check",
    )

    email_act = action(AGENT, CAP_EMAIL, "mailto:user@example.com", "email.send")
    email_ev = make_event("ev-email-1", email_act, "allowed", GENESIS)
    write(OUT / "valid/email_send.json", email_ev)
    write(OUT / "valid/email_send_trace.json", make_trace([email_ev]))

    email_denied_act = action(AGENT_NO_EMAIL, CAP_EMAIL, "mailto:user@example.com", "email.send")
    email_denied_ev = make_event("ev-email-denied", email_denied_act, "denied", GENESIS)
    write(OUT / "valid/email_send_denied.json", email_denied_ev)
    write_invalid(
        OUT / "invalid/email_send_missing_capability.json",
        make_event("ev-email-bad", email_denied_act, "allowed", GENESIS),
        "UnsafeEvent",
        "decider_check",
    )

    handoff_doc = {
        "schema_version": "pf-core.handoff.v0",
        "from_principal": AGENT,
        "to_principal": RECIPIENT,
        "capability": CAP_HANDOFF,
    }
    write(OUT / "valid/handoff.json", handoff_doc)

    handoff_events = [make_handoff_event("ev-handoff-1", handoff_doc, "allowed", GENESIS)]
    write(OUT / "valid/handoff_trace.json", make_trace(handoff_events))

    write_invalid(
        OUT / "invalid/handoff_cross_tenant.json",
        {**handoff_doc, "to_principal": {**RECIPIENT, "tenant_id": "tenant-b"}},
        "UnsafeHandoff",
        "decider_check",
    )

    handoff_expand = {
        **handoff_doc,
        "capability": CAP_NETWORK,
        "to_principal": {**RECIPIENT, "roles": ["cap:network", "cap:handoff"]},
    }
    write_invalid(
        OUT / "invalid/handoff_authority_expansion.json",
        handoff_expand,
        "UnsafeHandoff",
        "decider_check",
    )

    write_invalid(
        OUT / "invalid/handoff_trace_unsafe.json",
        make_trace(
            [
                make_handoff_event(
                    "ev-handoff-bad",
                    {**handoff_doc, "to_principal": {**RECIPIENT, "tenant_id": "tenant-b"}},
                    "allowed",
                    GENESIS,
                )
            ]
        ),
        "UnsafeTrace",
        "decider_check",
    )

    lab_agent = {**AGENT, "roles": ["cap:lab-release"]}
    lab_act = action(lab_agent, CAP_LAB, "lab:experiment-42", "lab.release")
    lab_ev = make_event("ev-lab-release", lab_act, "allowed", GENESIS)
    write(OUT / "valid/lab_release_gate.json", lab_ev)

    lab_contract = {
        "schema_version": "pf-core.contract.v0",
        "name": "lab-release-gate",
        "pre": {
            "require_capability": "cap:lab-release",
            "require_effect": "lab.release",
            "require_policy_ref": "policy/lab-gate.v0",
            "require_evidence_ref": "evidence/lab-signoff.v0",
        },
        "post": {"require_decision": "allowed", "require_event_safe": True},
        "invariant": {"require_trace_safe": True},
    }
    write(OUT / "valid/lab_release_contract.json", lab_contract)

    lab_obs = {
        "schema_version": "pf-core.runtime_observation.v0",
        "observation_id": "obs-lab-release",
        "principal_id": "agent-1",
        "tenant_id": "tenant-a",
        "effect_kind": "lab.release",
        "resource_uri": "lab:experiment-42",
        "decision": "allowed",
        "previous_event_hash": GENESIS,
        "capability_id": "cap:lab-release",
        "policy_ref": "policy/lab-gate.v0",
        "evidence_ref": "evidence/lab-signoff.v0",
    }
    write(OUT / "valid/lab_release_observation.json", lab_obs)

    write_invalid(
        OUT / "invalid/contract_missing_name.json",
        {
            "schema_version": "pf-core.contract.v0",
            "pre": {"require_effect": "file.read"},
            "post": {"require_event_safe": True},
            "invariant": {"require_trace_safe": True},
        },
        "SchemaValidationError",
        "schema_validation",
    )

    write_invalid(
        OUT / "invalid/lab_release_missing_policy.json",
        {
            "schema_version": "pf-core.runtime_observation.v0",
            "observation_id": "obs-lab-bad",
            "principal_id": "agent-1",
            "tenant_id": "tenant-a",
            "effect_kind": "lab.release",
            "resource_uri": "lab:experiment-42",
            "decision": "allowed",
            "previous_event_hash": GENESIS,
            "policy_ref": "policy/unknown.v0",
        },
        "PolicyRefNotFound",
        "runtime_to_trace",
    )

    mcp_act = action(AGENT, CAP_MCP, "mcp:filesystem/read", "mcp.invoke")
    mcp_ev = make_event("ev-mcp-1", mcp_act, "allowed", GENESIS)
    write(OUT / "valid/mcp_sidecar_allowed.json", mcp_ev)

    mcp_denied_act = action(AGENT_NO_NETWORK, CAP_MCP, "mcp:network/fetch", "mcp.invoke")
    mcp_denied_ev = make_event("ev-mcp-denied", mcp_denied_act, "denied", GENESIS)
    write(OUT / "valid/mcp_sidecar_denied.json", mcp_denied_ev)

    mcp_obs = {
        "schema_version": "pf-core.runtime_observation.v0",
        "observation_id": "obs-mcp-1",
        "principal_id": "agent-1",
        "tenant_id": "tenant-a",
        "effect_kind": "mcp.invoke",
        "resource_uri": "mcp:filesystem/read",
        "decision": "allowed",
        "previous_event_hash": GENESIS,
        "capability_id": "cap:mcp-invoke",
        "policy_ref": "policy/default.v0",
        "evidence_ref": "evidence/mcp-audit.v0",
    }
    write(OUT / "valid/mcp_sidecar_observation.json", mcp_obs)

    mcp_ambiguous = dict(mcp_obs)
    mcp_ambiguous["observation_id"] = "obs-mcp-ambiguous"
    mcp_ambiguous.pop("capability_id")
    write_invalid(
        OUT / "invalid/mcp_sidecar_ambiguous.json",
        mcp_ambiguous,
        "AmbiguousMapping",
        "runtime_to_trace",
    )

    write_invalid(
        OUT / "invalid/obs_missing_required_field.json",
        {
            "schema_version": "pf-core.runtime_observation.v0",
            "observation_id": "obs-missing",
            "tenant_id": "tenant-a",
            "effect_kind": "file.read",
            "resource_uri": "/data/x",
            "decision": "allowed",
            "previous_event_hash": GENESIS,
        },
        "MissingRequiredField",
        "runtime_to_trace",
    )

    write_invalid(
        OUT / "invalid/obs_unsupported_capability.json",
        {
            "schema_version": "pf-core.runtime_observation.v0",
            "observation_id": "obs-bad-cap",
            "principal_id": "agent-1",
            "tenant_id": "tenant-a",
            "effect_kind": "file.read",
            "resource_uri": "/data/x",
            "decision": "allowed",
            "previous_event_hash": GENESIS,
            "capability_id": "cap:unknown",
        },
        "UnsupportedCapability",
        "runtime_to_trace",
    )

    write_invalid(
        OUT / "invalid/obs_evidence_not_found.json",
        {
            "schema_version": "pf-core.runtime_observation.v0",
            "observation_id": "obs-bad-evidence",
            "principal_id": "agent-1",
            "tenant_id": "tenant-a",
            "effect_kind": "file.read",
            "resource_uri": "/data/x",
            "decision": "allowed",
            "previous_event_hash": GENESIS,
            "evidence_ref": "evidence/missing.v0",
        },
        "EvidenceRefNotFound",
        "runtime_to_trace",
    )

    write_invalid(
        OUT / "invalid/obs_unsupported_effect.json",
        {
            "schema_version": "pf-core.runtime_observation.v0",
            "observation_id": "obs-bad-effect",
            "principal_id": "agent-1",
            "tenant_id": "tenant-a",
            "effect_kind": "custom.unknown",
            "resource_uri": "/data/x",
            "decision": "allowed",
            "previous_event_hash": GENESIS,
        },
        "UnsupportedEffect",
        "runtime_to_trace",
    )

    bad_hash_ev = dict(file_read_ev)
    bad_hash_ev["event_hash"] = "f" * 64
    write_invalid(
        OUT / "invalid/file_read_bad_hash.json",
        bad_hash_ev,
        "InvalidHash",
        "decider_check",
    )

    bad_schema = dict(file_read_ev)
    bad_schema["schema_version"] = "pf-core.event.v2"
    write_invalid(
        OUT / "invalid/file_read_bad_schema_version.json",
        bad_schema,
        "InvalidSchemaVersion",
        "schema_validation",
    )

    tampered_trace = make_trace([file_read_ev, file_read_denied_ev])
    tampered_trace["events"][1]["previous_event_hash"] = "f" * 64
    write_invalid(
        OUT / "invalid/trace_tampered_chain.json",
        tampered_trace,
        "InvalidHash",
        "decider_check",
    )

    bad_principal_act = action(
        {**AGENT, "id": ""},
        CAP_FILE_READ,
        "/data/report.txt",
        "file.read",
    )
    write_invalid(
        OUT / "invalid/event_invalid_principal.json",
        make_event("ev-bad-principal", bad_principal_act, "allowed", GENESIS),
        "InvalidPrincipal",
        "action_semantics",
    )

    bad_action = action(
        {**AGENT, "roles": []},
        CAP_FILE_READ,
        "/data/report.txt",
        "file.read",
    )
    write_invalid(
        OUT / "invalid/event_invalid_action.json",
        make_event("ev-bad-action", bad_action, "allowed", GENESIS),
        "InvalidAction",
        "action_semantics",
    )

    bad_decision_ev = dict(file_read_ev)
    bad_decision_ev["decision"] = "maybe"
    write_invalid(
        OUT / "invalid/event_invalid_decision.json",
        bad_decision_ev,
        "InvalidDecision",
        "decision_check",
    )

    print(f"Wrote fixtures under {OUT}")


if __name__ == "__main__":
    main()
