"""Export pinned capability catalog for compile.py (untrusted organizational input)."""

from __future__ import annotations

import json
from pathlib import Path

PIN_SHA = "a567c8dca015fac3890fddbb77dfd254caa720d8"

CAPABILITIES = [
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


def export_catalog(out: Path) -> None:
    payload = {
        "source_repo": "provability-fabric",
        "source_sha": PIN_SHA,
        "source_paths": ["config/schemas/", "Policy.lean (reference-only)"],
        "capabilities": CAPABILITIES,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    export_catalog(root / "fixtures" / "capability_catalog.json")
    print(f"OK: wrote {root / 'fixtures' / 'capability_catalog.json'}")
