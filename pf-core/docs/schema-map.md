# PF-Core Schema Map

Inventory of pinned JSON schemas. **v1-primary** artifacts are normative for the trusted golden path; **legacy** v0 schemas remain for reference and backward-compatible compile tests only.

## v1-primary (normative)

| Schema | Version | Relationships |
|--------|---------|---------------|
| `principal.v1.schema.json` | `pf-core.principal.v1` | Roles + explicit `capabilities[]` |
| `action.v1.schema.json` | `pf-core.action.v1` | Multi-effect `reads`/`writes` |
| `event.v1.schema.json` | `pf-core.event.v1` | `event_kind` discriminator (`action` / `handoff`) + hash-chain |
| `handoff.v1.schema.json` | `pf-core.handoff.v1` | `delegated_capabilities[]` subset model |
| `runtime_observation.v1.schema.json` | `pf-core.runtime_observation.v1` | Adapter input; compiles to `event.v1` |

## Core authorization types (legacy reference)

| Schema | Version | Status |
|--------|---------|--------|
| `principal.schema.json` | `pf-core.principal.v0` | legacy — embedded in v0 actions/events |
| `capability.schema.json` | `pf-core.capability.v0` | legacy — still referenced by v1 actions |
| `resource.schema.json` | `pf-core.resource.v0` | legacy |
| `effect.schema.json` | `pf-core.effect.v0` | legacy |
| `action.schema.json` | `pf-core.action.v0` | legacy — use `action.v1` for new fixtures |
| `decision.schema.json` | `pf-core.decision.v0` | legacy wrapper |

## Trace artifacts

| Schema | Version | Status |
|--------|---------|--------|
| `event.schema.json` | `pf-core.event.v0` | legacy reference only |
| `trace.schema.json` | `pf-core.trace.v0` | active — ordered `events[]` (v1 items) + `trace_hash` |
| `certificate.schema.json` | `pf-core.certificate.v0` | active — binds `trace_hash` + `contract_hash` |

## Policy and adapter

| Schema | Version | Status |
|--------|---------|--------|
| `contract.schema.json` | `pf-core.contract.v0` | active |
| `handoff.schema.json` | `pf-core.handoff.v0` | legacy — use `handoff.v1` |
| `runtime_observation.schema.json` | `pf-core.runtime_observation.v0` | legacy — compile emits deprecation warning |
| `claim_classification.schema.json` | `pf-core.claim_classification.v0` | active |

## Versioning and canonicalization

- Every artifact carries `schema_version` equal to its `$id` suffix.
- Trusted CI (`pf-core-trusted`) validates **v1-primary** observations in `examples/valid/`; v0 observations require `"legacy": true` in invalid fixtures.
- `additionalProperties: false` on all object schemas (T2 pinning).
- Hash binding: see `certificate-semantics.md` for `event_hash`, `trace_hash`, and `contract_hash` (canonical JSON, sorted keys, SHA-256 lowercase hex).
- Genesis `previous_event_hash`: 64 ASCII `0` characters.

## Examples in schemas

Each schema file includes at least one valid `examples` entry and documented `x-invalid-examples` (documentation-only; not validated by `schema-check`).
