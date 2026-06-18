"""Export pinned capability catalog for compile.py (untrusted organizational input)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

PIN_SHA = "a567c8dca015fac3890fddbb77dfd254caa720d8"
SOURCE_REPO = "provability-fabric"

# Manual mirror of pf-core/lean/PFCore/CapabilityCatalog.lean (proof authority).
# Parent config/schemas/ does not ship a machine-readable capability list at the pin;
# CI clones the sibling repo for pin verification only. Drift is gated by
# test_catalog_export_matches_lean (Lean wins on conflict).
CAPABILITIES: List[Dict[str, str]] = [
    {
        "id": "cap:file-read",
        "effect_kind": "file.read",
        "resource_pattern": "/data/*",
    },
    {
        "id": "cap:file-write",
        "effect_kind": "file.write",
        "resource_pattern": "/data/*",
    },
    {
        "id": "cap:network",
        "effect_kind": "network.egress",
        "resource_pattern": "*",
    },
    {
        "id": "cap:email-send",
        "effect_kind": "email.send",
        "resource_pattern": "mailto:*",
    },
    {
        "id": "cap:handoff",
        "effect_kind": "handoff.delegate",
        "resource_pattern": "agent:*",
    },
    {
        "id": "cap:mcp-invoke",
        "effect_kind": "mcp.invoke",
        "resource_pattern": "mcp:*",
    },
    {
        "id": "cap:mcp-alt",
        "effect_kind": "mcp.invoke",
        "resource_pattern": "mcp:alt/*",
    },
    {
        "id": "cap:lab-release",
        "effect_kind": "lab.release",
        "resource_pattern": "lab:*",
    },
]

# Mirrors CapabilityCatalog.lean role→capability map (sidecar adapter uses cap→roles).
PRINCIPAL_ROLES_BY_CAPABILITY: Dict[str, List[str]] = {
    "cap:file-read": ["file_reader", "file_admin", "agent"],
    "cap:file-write": ["file_admin"],
    "cap:network": ["network_user"],
    "cap:email-send": ["email_user", "agent"],
    "cap:handoff": ["handoff_delegate", "agent"],
    "cap:mcp-invoke": ["mcp_user", "agent"],
    "cap:mcp-alt": ["mcp_user"],
    "cap:lab-release": ["lab_operator"],
}

# Parent Policy.lean tools with no PF-Core catalog entry; explicit deny in PF (see vectors).
DOCUMENTED_POLICY_GAPS = [
    {
        "parent_tool": "LogSpend",
        "pf_core_behavior": "deny",
        "reason": "no matching capability in CapabilityCatalog.lean",
        "vector_ids": ["log_spend_allow_finance"],
    },
    {
        "parent_tool": "LogAction",
        "pf_core_behavior": "deny",
        "reason": "no matching capability in CapabilityCatalog.lean",
        "vector_ids": ["log_action_allow_logger"],
    },
]


def _parent_schema_roots() -> List[Path]:
    here = Path(__file__).resolve().parent
    candidates = [
        here.parents[1] / "provability-fabric" / "config" / "schemas",
        Path("/tmp/provability-fabric/config/schemas"),
        here.parents[2].parent / "provability-fabric" / "config" / "schemas",
    ]
    return [p for p in candidates if p.is_dir()]


def _try_load_parent_capabilities(root: Path) -> Optional[List[Dict[str, str]]]:
    """Best-effort read when sibling clone is present; returns None if not parseable."""
    for pattern in ("capabilities.json", "capability_catalog.json"):
        path = root / pattern
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        caps = data.get("capabilities") if isinstance(data, Mapping) else data
        if isinstance(caps, list) and caps and all("id" in c for c in caps):
            return caps
    return None


def export_catalog(out: Path) -> None:
    parent_roots = _parent_schema_roots()
    parent_caps = None
    parent_path = None
    for root in parent_roots:
        parent_caps = _try_load_parent_capabilities(root)
        if parent_caps is not None:
            parent_path = str(root)
            break

    capabilities = CAPABILITIES
    source_mode = "manual_mirror_of_lean_catalog"
    if parent_caps is not None:
        lean_ids = {c["id"] for c in CAPABILITIES}
        parent_ids = {c["id"] for c in parent_caps}
        if parent_ids != lean_ids:
            raise SystemExit(
                "catalog drift: parent export capability ids differ from Lean mirror; "
                f"parent={sorted(parent_ids)} lean={sorted(lean_ids)}"
            )
        source_mode = "parent_schemas_verified_against_lean"

    payload = {
        "source_repo": SOURCE_REPO,
        "source_sha": PIN_SHA,
        "source_mode": source_mode,
        "source_paths": [
            "pf-core/lean/PFCore/CapabilityCatalog.lean (proof authority)",
            "provability-fabric/config/schemas/ (reference; optional sibling read)",
            "Policy.lean (reference-only; LogSpend/LogAction not in TCB)",
        ],
        "parent_schema_path": parent_path,
        "capabilities": capabilities,
        "principal_roles_by_capability": PRINCIPAL_ROLES_BY_CAPABILITY,
        "documented_policy_gaps": DOCUMENTED_POLICY_GAPS,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    export_catalog(root / "fixtures" / "capability_catalog.json")
    print(f"OK: wrote {root / 'fixtures' / 'capability_catalog.json'}")
