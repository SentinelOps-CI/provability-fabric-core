# PF-Core Schema Map

Inventory of pinned JSON schemas (all version `pf-core.<kind>.v0`).

## Core authorization types

| Schema | Version | Relationships |
|--------|---------|---------------|
| `principal.schema.json` | `pf-core.principal.v0` | Referenced by `action`, `handoff` |
| `capability.schema.json` | `pf-core.capability.v0` | Referenced by `action`, `handoff`; maps to `effect.kind` |
| `resource.schema.json` | `pf-core.resource.v0` | Referenced by `action`; tenant must match principal |
| `effect.schema.json` | `pf-core.effect.v0` | Referenced by `action`; closed enumeration |
| `action.schema.json` | `pf-core.action.v0` | Bundles principal/capability/resource/effect |
| `decision.schema.json` | `pf-core.decision.v0` | Standalone wrapper; events embed `decision` string |

## Trace artifacts

| Schema | Version | Relationships |
|--------|---------|---------------|
| `event.schema.json` | `pf-core.event.v0` | Legacy: top-level `action` (reference only) |
| `event.v1.schema.json` | `pf-core.event.v1` | `event_kind` discriminator (`action` / `handoff`) + hash-chain |
| `trace.schema.json` | `pf-core.trace.v0` | Ordered `events[]` (v1 items) + `trace_hash` |
| `certificate.schema.json` | `pf-core.certificate.v0` | Binds `trace_hash` + `contract_hash` |

## Policy and adapter

| Schema | Version | Relationships |
|--------|---------|---------------|
| `contract.schema.json` | `pf-core.contract.v0` | Structured `pre`/`post`/`invariant`; hashed into certificates |
| `handoff.schema.json` | `pf-core.handoff.v0` | Bilateral principals + capability |
| `runtime_observation.schema.json` | `pf-core.runtime_observation.v0` | Adapter input; compiles to `event` |
| `claim_classification.schema.json` | `pf-core.claim_classification.v0` | Documentation metadata for claim boundaries |

## Versioning and canonicalization

- Every artifact carries `schema_version` equal to its `$id` suffix.
- `additionalProperties: false` on all object schemas (T2 pinning).
- Hash binding: see `certificate-semantics.md` for `event_hash`, `trace_hash`, and `contract_hash` (canonical JSON, sorted keys, SHA-256 lowercase hex).
- Genesis `previous_event_hash`: 64 ASCII `0` characters.

## Examples in schemas

Each schema file includes at least one valid `examples` entry and documented `x-invalid-examples` (documentation-only; not validated by `schema-check`).
