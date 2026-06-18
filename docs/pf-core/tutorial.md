# PF-Core Tutorial (Non-Lean Engineers)

This tutorial explains PF-Core without requiring Lean. For formal details see [formal-model.md](../pf-core/docs/formal-model.md).

## Soundness split

| Layer | What it does |
|-------|----------------|
| **Lean proves** | If JSON is modeled correctly, deciders match safety predicates |
| **Runtime validates** | Schema, hash chains, compile determinism |
| **Assumptions** | Emitters are honest enough to produce valid JSON and tenant labels |

## Core artifacts

1. **Runtime observation** — what an adapter saw (MCP audit line, lab gate, etc.)
2. **Event** — normalized record with `event_kind` (`action` or `handoff`), `decision`, and hash-chain fields
3. **Trace** — ordered events with `trace_hash`
4. **Certificate** — summary bit `safe` over a trace hash

## Quick start

```bash
pip install -e pf-core/validator
pf core schema-check --schemas pf-core/schemas
pf core compile-observation --file pf-core/examples/valid/mcp_sidecar_observation.json
pf core check-trace --file pf-core/examples/valid/file_read_allowed_trace.json
pf core emit-artifacts --file pf-core/examples/valid/mcp_sidecar_observation.json --out-dir ./artifacts
```

Windows: `powershell -File pf-core/scripts/pf-core-trusted.ps1`

## Event kinds (v1)

| Kind | Meaning | Safety check |
|------|---------|--------------|
| `action` | Tool call / effect attempt | Capability + tenant + effect |
| `handoff` | Authority transfer between principals | Same tenant + bilateral capability |

Handoff trace example: `pf-core/examples/valid/handoff_trace.json`

## What PF-Core does not do

- Does not prove LLM outputs are correct
- Does not sandbox MCP servers or OS calls
- Does not guarantee recipients honor handoffs

See [claim-boundary.md](claim-boundary.md) for allowed wording.

## Next steps

- [Adapter contract](../pf-core/docs/adapter-contract.md) — map your runtime to observations
- [Ecosystem inventory](ecosystem-inventory.md) — how PF-Core relates to Provability Fabric
- [Examples](../pf-core/docs/examples.md) — valid/invalid fixture catalog
