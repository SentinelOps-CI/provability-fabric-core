# PF-Core Adapter Contract

Adapters map runtime observations to PF-Core events without LLM or network calls in the trusted compile path.

## Soundness split

- **Lean proves:** safety predicates over compiled events
- **Runtime validates:** schema, compile errors, hash chain, deciders
- **Assumptions:** A4 (capability catalog), A6 (determinism), A8 (policy refs)

## Input

`runtime_observation` JSON (`pf-core.runtime_observation.v1` is normative; v0 is legacy reference only).

Required v1 fields: `trace_id`, `event_id`, `observation_id`, nested `principal`, nested `action`, `decision`, `policy_ref`, `evidence_ref`, `runtime_ref`, `timestamp`, `previous_event_hash`, `hash`.

Nested shapes:

| Object | Schema | Key fields |
|--------|--------|------------|
| `principal` | `pf-core.principal.v1` | `id`, `tenant_id`, `roles[]`, `capabilities[]` |
| `action` | `pf-core.action.v1` | `id`, `principal`, `capability`, `effects[]`, `reads[]`, `writes[]` |
| `action.capability` | `pf-core.capability.v0` | `id`, `effect_kind`, `resource_pattern` |

Handoff events are authored as `pf-core.event.v1` with `event_kind.type = "handoff"` (see `handoff.v1.schema.json`); they are not produced by the observation compile path today.

## Output artifact set

Every adapter run must emit:

| File | Description |
|------|-------------|
| `runtime_observation.json` | Normalized observation |
| `event.json` | Compiled event with `event_hash` |
| `trace.json` | Append-only trace with `trace_hash` |
| `certificate.json` | When trace is checkable |
| `audit.jsonl` | One audit line per event (append-only) |

CLI:

```bash
pf core emit-artifacts \
  --file pf-core/examples/valid/mcp_sidecar_observation.json \
  --out-dir ./artifacts

pf core validate-handoff \
  --file pf-core/examples/valid/handoff.json
```

## Compile requirements

1. **Determinism** — `compile(input) == compile(input)` (tested in `validate_examples.py`)
2. **Capability resolution** — set `action.capability.id` when multiple capabilities share an `effect_kind`
3. **Policy refs** — must exist in `POLICY_CATALOG` or `PolicyRefNotFound`
4. **Evidence refs** — if present, must exist in `EVIDENCE_CATALOG` or `EvidenceRefNotFound`
5. **Decision coherence** — unauthorized `allowed` downgrades to `denied`
6. **Hash chain** — `previous_event_hash` from observation; `event_hash` computed per `certificate-semantics.md`

## Typed compile errors

| Error | Stage |
|-------|-------|
| `MissingRequiredField` | `runtime_to_trace` |
| `InvalidSchemaVersion` | `runtime_to_trace` / `schema_validation` |
| `UnsupportedEffect` | `runtime_to_trace` |
| `UnsupportedCapability` | `runtime_to_trace` |
| `AmbiguousMapping` | `runtime_to_trace` |
| `PolicyRefNotFound` | `runtime_to_trace` |
| `EvidenceRefNotFound` | `runtime_to_trace` |

## Adapter mappings (examples)

| Domain | Valid | Invalid twin |
|--------|-------|--------------|
| MCP sidecar | `mcp_sidecar_allowed.json` | `mcp_sidecar_denied.json`, `mcp_sidecar_ambiguous.json` |
| LabTrust gate | `lab_release_gate.json` | `lab_release_missing_policy.json` |
| File read | `file_read_allowed.json` | `file_read_denied.json`, `file_read_allowed_wrong_tenant.json` |
| Email send | `email_send.json` | `email_send_denied.json`, `email_send_missing_capability.json` |
| Handoff | `handoff.json`, `handoff_trace.json` | `handoff_cross_tenant.json`, `handoff_authority_expansion.json`, `handoff_trace_unsafe.json` |

## MCP sidecar reference mapping

See [ecosystem-inventory.md](../../docs/pf-core/ecosystem-inventory.md) for audit-line field mapping (reference only).

| MCP audit field (example) | `runtime_observation.v1` field |
|---------------------------|--------------------------------|
| `request_id` | `observation_id` |
| `trace_id` | `trace_id` |
| `event_id` | `event_id` |
| `agent_id` | `principal.id` |
| `tenant` | `principal.tenant_id` |
| `tool_effect` | `action.effects[].kind` |
| `resource` | `action.reads[].uri` |
| `policy_decision` | `decision` |
| `prev_hash` | `previous_event_hash` |
| `policy_bundle` | `policy_ref` |
| `audit_bundle` | `evidence_ref` |
| `capability_hint` | `action.capability.id` (required when effect is ambiguous) |
| `runtime_ref` | `runtime_ref` |
| `timestamp` | `timestamp` |
| `reason` | `reason` |

Sidecar principal roles are resolved from `adapters/provability-fabric/fixtures/capability_catalog.json` (`principal_roles_by_capability`), not hardcoded in the normalizer.

Compiled action observations use `pf-core.event.v1` with `event_kind.type = "action"`.

## Live path: provability-fabric sidecar

Untrusted adapter: `adapters/provability-fabric/mcp_sidecar/normalize.py`

1. Sidecar emits audit JSON line (see field map in `docs/pf-core/ecosystem-inventory.md`).
2. Adapter normalizes to `pf-core.runtime_observation.v1`.
3. Trusted compile path: `pf core compile-observation` → `pf core check-trace`.

Golden tests: `adapters/provability-fabric/tests/test_normalize.py` (not in blocking `pf-core-trusted`).

v0 flat observations remain supported for migration reference; use `pf-core/scripts/migrate-v0-to-v1.py` for mechanical uplift.

## Pre-execution behavior

Before a tool call, the adapter must:

1. Load pinned policy and contract references.
2. Validate principal and requested action against capability catalog.
3. Compute allow/deny decision; if deny, block execution and emit a denied observation (denied events remain in the trace).
4. If allow, execute only the declared tool/effect.
5. Emit an allowed observation with evidence and policy references.

## Post-execution behavior

After a tool call, the adapter must:

1. Capture result metadata (exit status, resource changes when available).
2. Validate executable postconditions where defined in the contract.
3. Attach `evidence_ref` and update hash chain (`event_hash`, `trace_hash`).
4. Append an audit line to `audit.jsonl` (append-only; no in-place edits).

Handoff audit lines use `delegated_capabilities[].id` (comma-joined when multiple) for the `capability` field, not a legacy single `capability` object.

## Prohibited adapter behavior

Adapters must not:

- Silently allow unknown actions or coerce unknown capabilities.
- Silently ignore schema validation errors or drop denied events.
- Silently drop failed postcondition checks.
- Rewrite traces or audit lines after emission.
- Claim Lean verification when only runtime validation occurred.
- Call an LLM or depend on network access during deterministic validation (`compile-observation`, `check-trace`, `schema-check`).

## Audit line fields

`schema_version`, `trace_id`, `event_id`, `principal_id`, `action_id`, `capability`, `decision`, `reason`, `policy_ref`, `evidence_ref`, `event_hash`, `previous_event_hash`, `trace_hash`, `runtime_id`. No secrets or raw tokens.
