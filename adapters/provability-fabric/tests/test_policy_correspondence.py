"""Golden vectors: parent Policy.lean permitD fragment vs PF-Core actionAllowedD."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys_path = ROOT / "pf-core" / "validator"
import sys

sys.path.insert(0, str(sys_path))

from pf_core.deciders import action_allowed, handoff_safe  # noqa: E402

VECTORS = Path(__file__).parent / "fixtures" / "policy_correspondence_vectors.json"
CATALOG_LEAN = ROOT / "pf-core" / "lean" / "PFCore" / "CapabilityCatalog.lean"
CATALOG_JSON = ROOT / "adapters" / "provability-fabric" / "fixtures" / "capability_catalog.json"

TOOL_ROLES: dict[str, list[str]] = {
    "SendEmail": ["email_user", "admin"],
    "LogSpend": ["finance_user", "admin"],
    "LogAction": ["logger", "admin"],
    "NetworkCall": ["network_user", "admin"],
    "FileRead": ["file_user", "admin"],
    "FileWrite": ["file_writer", "admin"],
    "Custom": ["admin"],
}

TOOL_PF: dict[str, tuple[str, str, str]] = {
    "SendEmail": ("cap:email-send", "email.send", "email_user"),
    "LogSpend": ("cap:file-read", "file.read", "file_reader"),
    "LogAction": ("cap:file-read", "file.read", "file_reader"),
    "NetworkCall": ("cap:network", "network.egress", "network_user"),
    "FileRead": ("cap:file-read", "file.read", "file_reader"),
    "FileWrite": ("cap:file-write", "file.write", "file_admin"),
    "Custom": ("cap:mcp-invoke", "mcp.invoke", "mcp_user"),
}

CAP_PATTERNS: dict[str, str] = {
    "cap:file-read": "/data/*",
    "cap:file-write": "/data/*",
    "cap:network": "*",
    "cap:email-send": "mailto:*",
    "cap:handoff": "agent:*",
    "cap:mcp-invoke": "mcp:*",
    "cap:lab-release": "lab:*",
}


def parent_permit_call(roles: list[str], tool: str) -> bool:
    allowed = TOOL_ROLES.get(tool, [])
    return any(r in roles for r in allowed)


def pf_core_action(
    *,
    role: str,
    tenant_id: str,
    resource_uri: str,
    capability_id: str,
    effect_kind: str,
    resource_tenant: str | None = None,
) -> dict:
    rt = resource_tenant or tenant_id
    return {
        "schema_version": "pf-core.action.v1",
        "id": "act-correspondence",
        "principal": {
            "schema_version": "pf-core.principal.v1",
            "id": "agent-test",
            "tenant_id": tenant_id,
            "roles": [role],
            "capabilities": [],
        },
        "capability": {
            "schema_version": "pf-core.capability.v0",
            "id": capability_id,
            "effect_kind": effect_kind,
            "resource_pattern": CAP_PATTERNS.get(capability_id, "*"),
        },
        "effects": [{"schema_version": "pf-core.effect.v0", "kind": effect_kind}],
        "reads": [
            {
                "schema_version": "pf-core.resource.v0",
                "uri": resource_uri,
                "tenant_id": rt,
            }
        ],
        "writes": [],
    }


def pf_core_handoff(
    *,
    from_roles: list[str],
    to_roles: list[str],
    tenant_id: str,
    to_tenant: str | None,
    delegated_capability: str,
) -> dict:
    cap = {
        "schema_version": "pf-core.capability.v0",
        "id": delegated_capability,
        "effect_kind": "handoff.delegate" if delegated_capability == "cap:handoff" else "network.egress",
        "resource_pattern": CAP_PATTERNS.get(delegated_capability, "*"),
    }
    if delegated_capability == "cap:network":
        cap["effect_kind"] = "network.egress"
    return {
        "schema_version": "pf-core.handoff.v1",
        "from_principal": {
            "schema_version": "pf-core.principal.v1",
            "id": "agent-1",
            "tenant_id": tenant_id,
            "roles": from_roles,
            "capabilities": [],
        },
        "to_principal": {
            "schema_version": "pf-core.principal.v1",
            "id": "agent-2",
            "tenant_id": to_tenant or tenant_id,
            "roles": to_roles,
            "capabilities": [],
        },
        "delegated_capabilities": [cap],
        "reason": "correspondence test",
        "evidence_ref": "evidence/handoff.v0",
    }


def load_vectors() -> list[dict]:
    return json.loads(VECTORS.read_text(encoding="utf-8"))


def parse_lean_catalog() -> list[dict]:
    text = CATALOG_LEAN.read_text(encoding="utf-8")
    entries = []
    for block in re.finditer(
        r'\{ id := "([^"]+)", effectKind := "([^"]+)", resourcePattern := "([^"]+)" \}',
        text,
    ):
        entries.append(
            {
                "id": block.group(1),
                "effect_kind": block.group(2),
                "resource_pattern": block.group(3),
            }
        )
    return entries


@pytest.mark.parametrize("vector", load_vectors(), ids=lambda v: v["id"])
def test_policy_correspondence_vector(vector: dict) -> None:
    if vector.get("vector_kind") == "handoff":
        handoff = pf_core_handoff(
            from_roles=vector["from_roles"],
            to_roles=vector["to_roles"],
            tenant_id=vector["tenant_id"],
            to_tenant=vector.get("to_tenant"),
            delegated_capability=vector["delegated_capability"],
        )
        assert handoff_safe(handoff) == vector["expected_pf_core_handoff_safe"]
        return

    parent_ok = parent_permit_call(vector["parent_roles"], vector["parent_tool"])
    assert parent_ok == vector["expected_parent_permit"]

    cap_id, effect, default_role = TOOL_PF[vector["parent_tool"]]
    cap_id = vector.get("pf_core_capability", cap_id)
    effect = vector.get("pf_core_effect", effect)
    role = vector.get("pf_core_role", default_role)

    action = pf_core_action(
        role=role,
        tenant_id=vector["tenant_id"],
        resource_uri=vector["resource_uri"],
        capability_id=cap_id,
        effect_kind=effect,
        resource_tenant=vector.get("resource_tenant"),
    )
    pf_ok = action_allowed(action)
    assert pf_ok == vector["expected_pf_core_allowed"]

    if vector.get("documented_gap"):
        assert parent_ok != pf_ok
        return

    if vector["expected_parent_permit"] == vector["expected_pf_core_allowed"]:
        assert parent_ok == pf_ok, (
            f"alignment mismatch for {vector['id']}: parent={parent_ok} pf={pf_ok}"
        )


def test_catalog_export_matches_lean() -> None:
    lean_caps = parse_lean_catalog()
    exported = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    assert exported["capabilities"] == lean_caps
    assert len(lean_caps) >= 8


def test_vector_count() -> None:
    assert len(load_vectors()) >= 20
