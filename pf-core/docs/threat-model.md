# PF-Core Threat Model

## Adversary capabilities (untrusted zone)

- Control agent prompts, planner, and tool arguments
- Operate arbitrary MCP servers and sidecars
- Emit malformed or malicious JSON observations
- Replay or reorder events outside adapter control
- Spoof network, filesystem, or email side effects

## Mitigations in PF-Core (trusted zone)

| Threat | Mitigation | Category |
|--------|------------|----------|
| Unauthorized allowed label | `ActionAllowed` / `EventKindSafe` + `EventSafe` | T1 |
| Unsafe handoff in trace | `HandoffSafe` via `event_kind.handoff` | T1 |
| Cross-tenant access in model | `SameTenant` / `ActionWithinTenant` | T1 |
| Schema injection | `additionalProperties: false` | T2 |
| Ambiguous effect mapping | `AmbiguousMapping` error | T4 |
| Hash tampering | `InvalidHash` chain check | T4 |

## Out of scope attacks

- OS sandbox escape
- LLM prompt injection leading to unlogged actions
- Collisions in SHA-256 (assumed in A2)
- Recipient misuse after safe handoff
- Forged organizational tenant labels (A3)

## MCP sidecar

Sidecar observations compile through `compile-observation`. Safety depends on adapter mapping (A4, A6) and static capability catalog. Sidecar code is untrusted; only compiled events enter the trusted trace.
