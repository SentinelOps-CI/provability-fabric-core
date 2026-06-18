"""Mechanical uplift of v0 PF-Core fixtures to v1 schemas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def migrate_principal_v0_to_v1(obj: Dict[str, Any]) -> Dict[str, Any]:
    if obj.get("schema_version") != "pf-core.principal.v0":
        return obj
    return {
        "schema_version": "pf-core.principal.v1",
        "id": obj["id"],
        "tenant_id": obj["tenant_id"],
        "roles": obj.get("roles", []),
        "capabilities": [
            r for r in obj.get("roles", []) if str(r).startswith("cap:")
        ],
    }


def migrate_handoff_v0_to_v1(obj: Dict[str, Any]) -> Dict[str, Any]:
    if obj.get("schema_version") != "pf-core.handoff.v0":
        return obj
    cap = obj.get("capability")
    delegated = [cap] if cap else []
    return {
        "schema_version": "pf-core.handoff.v1",
        "from_principal": migrate_principal_v0_to_v1(obj["from_principal"]),
        "to_principal": migrate_principal_v0_to_v1(obj["to_principal"]),
        "delegated_capabilities": delegated,
        "reason": obj.get("reason", "migrated handoff"),
        "evidence_ref": obj.get("evidence_ref", "evidence/handoff.v0"),
    }


def migrate_action_v0_to_v1(obj: Dict[str, Any]) -> Dict[str, Any]:
    if obj.get("schema_version") != "pf-core.action.v0":
        return obj
    effect = obj.get("effect", {})
    resource = obj.get("resource")
    reads = [resource] if resource else []
    return {
        "schema_version": "pf-core.action.v1",
        "id": obj.get("id", "act-migrated"),
        "principal": migrate_principal_v0_to_v1(obj["principal"]),
        "capability": obj["capability"],
        "effects": [effect] if effect else [],
        "reads": reads,
        "writes": [],
    }


def migrate_observation_v0_to_v1(obj: Dict[str, Any]) -> Dict[str, Any]:
    if obj.get("schema_version") != "pf-core.runtime_observation.v0":
        return obj
    principal = migrate_principal_v0_to_v1(
        {
            "schema_version": "pf-core.principal.v0",
            "id": obj["principal_id"],
            "tenant_id": obj["tenant_id"],
            "roles": [obj.get("capability_id", "cap:file-read")],
        }
    )
    action = migrate_action_v0_to_v1(
        {
            "schema_version": "pf-core.action.v0",
            "id": f"act-{obj['observation_id']}",
            "principal": principal,
            "capability": {
                "schema_version": "pf-core.capability.v0",
                "id": obj.get("capability_id", "cap:file-read"),
                "effect_kind": obj["effect_kind"],
                "resource_pattern": "/data/*",
            },
            "resource": {
                "schema_version": "pf-core.resource.v0",
                "uri": obj["resource_uri"],
                "tenant_id": obj["tenant_id"],
            },
            "effect": {
                "schema_version": "pf-core.effect.v0",
                "kind": obj["effect_kind"],
            },
        }
    )
    return {
        "schema_version": "pf-core.runtime_observation.v1",
        "trace_id": f"trace-{obj['observation_id']}",
        "event_id": obj["observation_id"],
        "observation_id": obj["observation_id"],
        "principal": principal,
        "action": action,
        "decision": obj["decision"],
        "policy_ref": obj.get("policy_ref", "policy/default.v0"),
        "evidence_ref": obj.get("evidence_ref", ""),
        "runtime_ref": "migrated/v0",
        "timestamp": "2026-06-18T00:00:00Z",
        "previous_event_hash": obj.get("previous_event_hash", "0" * 64),
        "hash": "0" * 64,
    }


def migrate_file(path: Path, out: Path | None) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("schema_version", "")
    if version == "pf-core.principal.v0":
        migrated = migrate_principal_v0_to_v1(data)
    elif version == "pf-core.handoff.v0":
        migrated = migrate_handoff_v0_to_v1(data)
    elif version == "pf-core.action.v0":
        migrated = migrate_action_v0_to_v1(data)
    elif version == "pf-core.runtime_observation.v0":
        migrated = migrate_observation_v0_to_v1(data)
    else:
        migrated = data
    target = out or path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(migrated, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate PF-Core v0 fixtures to v1")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="output path (default: overwrite input)")
    args = parser.parse_args()
    migrate_file(args.input, args.output)
    print(f"OK: migrated {args.input}")


if __name__ == "__main__":
    main()
