# PF-Core Ecosystem Inventory (Reference Only)

PF-Core is a greenfield trusted kernel in this repository. Provability Fabric parent components are **not** imported into the Lean TCB. This document records what **would** connect at the adapter boundary.

## Soundness split

| Component | Zone | Connection |
|-----------|------|------------|
| PF-Core Lean kernel | Trusted | This repo |
| PF-Core validator | Trusted | `pf-core/validator/` |
| Provability Fabric runtime | Untrusted | Future adapter source |
| MCP sidecars | Untrusted | Observations only |
| Policy.lean (parent) | Untrusted reference | Not compiled into PF-Core |

## Would-connect components

| External artifact | PF-Core entry point | Notes |
|-------------------|---------------------|-------|
| MCP sidecar `audit.jsonl` line | `runtime_observation.v0` | See adapter-contract MCP mapping |
| Lab release gate log | `runtime_observation.v0` | `lab_release_observation.json` fixture |
| PCS hash-chain emitter | `event_hash` / `trace_hash` | Same canonical JSON rules |
| Parent `Policy.lean` | None (reference) | Capability catalog must be pinned separately (A4) |
| Evidence graph / PCS bundle | `evidence_ref` string | Content not verified in kernel |

## MCP sidecar audit line to runtime_observation

Reference mapping (documented example, not live sidecar code):

| MCP audit field (example) | `runtime_observation` field |
|---------------------------|----------------------------|
| `request_id` | `observation_id` |
| `agent_id` | `principal_id` |
| `tenant` | `tenant_id` |
| `tool_effect` | `effect_kind` |
| `resource` | `resource_uri` |
| `policy_decision` | `decision` (`allowed` / `denied`) |
| `prev_hash` | `previous_event_hash` |
| `policy_bundle` | `policy_ref` |
| `audit_bundle` | `evidence_ref` |
| `capability_hint` | `capability_id` (required when ambiguous) |

Example compile path:

```bash
pf core compile-observation --file pf-core/examples/valid/mcp_sidecar_observation.json
```

## Honest status

No external Policy.lean or MCP sidecar ships in this repository. Adapters must normalize untrusted logs into pinned schemas before PF-Core validation.
