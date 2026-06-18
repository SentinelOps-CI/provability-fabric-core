# PF-Core Documentation Index

PF-Core is the minimal trusted kernel for proof-carrying agentic actions. Start here.

## What PF-Core is

PF-Core is the mathematical and schema-level nucleus for proof-carrying agentic actions, contracted tool calls, handoffs, and trace-level safety preservation. It provides a no-sorry Lean kernel, pinned JSON schemas, a deterministic runtime-to-trace compiler, hash-chain replay validation, and certificates whose claims are bounded by theorem statements and explicit assumptions.

## What PF-Core is not

PF-Core is not Provability Fabric, not a second agent runtime, not an MCP implementation, not a PCS standard, and not a policy authoring UI. It does not prove LLM semantics, external tool honesty, OS security, or end-to-end deployment safety without adapter contracts and organizational controls. See [mission.md](mission.md).

## Where the Lean files live

`pf-core/lean/PFCore/` — namespace `PFCore`, built with `lake build` from `pf-core/lean/`. File inventory in [trusted-boundary.md](trusted-boundary.md).

## Where schemas live

`pf-core/schemas/` — all artifacts use `pf-core.<kind>.v0` (events use `pf-core.event.v1`). See [schema map](../pf-core/docs/schema-map.md).

## How to inspect assumptions

Read [assumptions.md](assumptions.md) (A1–A10). Certificates list assumption IDs they depend on. Run `pf core audit-boundary --root .` to list trusted files and scan for boundary violations.

## How to add a new contract

1. Define structured `pre` / `post` / `invariant` fields in `pf-core/schemas/contract.schema.json` (or extend with a new schema version if breaking).
2. Add decider logic in `pf-core/validator/pf_core/contracts.py` if new fields need runtime checking.
3. If the contract maps to Lean predicates, add a `Contract` instance or extension in `pf-core/lean/PFCore/Contract.lean` with proved projection theorems.
4. Add valid/invalid fixtures under `pf-core/examples/` and register in `gen_fixtures.py` if generated.
5. Document the contract in [examples.md](../pf-core/docs/examples.md).

## How to add a new adapter mapping

1. Normalize runtime output to `pf-core.runtime_observation.v0` (see [adapter-contract.md](../pf-core/docs/adapter-contract.md)).
2. Register capability and policy catalogs in `pf-core/validator/pf_core/compile.py` (or a dedicated adapter module).
3. Add `valid/` and `invalid/` fixtures with `expected_error` and `must_fail_at` on negatives.
4. Map audit fields in [ecosystem-inventory.md](ecosystem-inventory.md) (reference only).
5. Run `make pf-core-trusted` to verify schema, compile, decider, and boundary gates.

## Boundary documents

| Document | Purpose |
|----------|---------|
| [mission.md](mission.md) | What PF-Core proves and does not prove |
| [trusted-boundary.md](trusted-boundary.md) | Trusted / untrusted / assumed / unproved |
| [claim-boundary.md](claim-boundary.md) | Claim classification (T1–T5) |
| [tutorial.md](tutorial.md) | Non-Lean engineer quick start |
| [ecosystem-inventory.md](ecosystem-inventory.md) | Reference adapter connections |
| [acceptance.md](acceptance.md) | Final mission acceptance checklist |
| [assumptions.md](assumptions.md) | Numbered assumptions (A1–A10) |

## Formal and operational docs

| Document | Location |
|----------|----------|
| Formal model | [pf-core/docs/formal-model.md](../pf-core/docs/formal-model.md) |
| Theorem map | [pf-core/docs/theorem-map.md](../pf-core/docs/theorem-map.md) |
| Schema map | [pf-core/docs/schema-map.md](../pf-core/docs/schema-map.md) |
| Runtime mapping | [pf-core/docs/runtime-mapping.md](../pf-core/docs/runtime-mapping.md) |
| Trusted rings | [pf-core/docs/trusted-rings.md](../pf-core/docs/trusted-rings.md) |
| Threat model | [pf-core/docs/threat-model.md](../pf-core/docs/threat-model.md) |
| Examples | [pf-core/docs/examples.md](../pf-core/docs/examples.md) |
| Adapter contract | [pf-core/docs/adapter-contract.md](../pf-core/docs/adapter-contract.md) |
| Certificate semantics | [pf-core/docs/certificate-semantics.md](../pf-core/docs/certificate-semantics.md) |
| Validator | [pf-core/validator/README.md](../pf-core/validator/README.md) |

## How to build and verify

```bash
# Full trusted gate (Lean + schemas + examples + audit)
make pf-core-trusted

# Individual targets
make pf-core-lean
make pf-core-schema
make pf-core-examples
make pf-core-audit
```

Windows (PowerShell):

```powershell
powershell -File pf-core/scripts/pf-core-trusted.ps1
```

## How to validate runtime artifacts

```bash
# Install validator (from repo root)
pip install -e pf-core/validator

# Schema check
pf core schema-check --schemas pf-core/schemas

# Validate a single event
pf core validate-event --file pf-core/examples/valid/file_read_allowed.json

# Validate a trace
pf core validate-trace --file pf-core/examples/valid/handoff_trace.json

# Compile runtime observation to trace events
pf core compile-observation --file pf-core/examples/valid/mcp_sidecar_observation.json

# Check trace safety (deciders)
pf core check-trace --file pf-core/examples/valid/file_read_allowed_trace.json

# Emit certificate over safe trace
pf core emit-certificate --trace pf-core/examples/valid/file_read_allowed_trace.json

# Emit full adapter artifact set
pf core emit-artifacts --file pf-core/examples/valid/mcp_sidecar_observation.json --out-dir ./artifacts

# Audit trusted boundary (docstrings, forbidden claims)
pf core audit-boundary --root .
```

## Repository inventory (initial)

### Lean files

| Path | Status |
|------|--------|
| `pf-core/lean/PFCore/Basic.lean` | Core aliases and helpers |
| `pf-core/lean/PFCore/Principal.lean` | Principal type, HasRole |
| `pf-core/lean/PFCore/Capability.lean` | Capability type |
| `pf-core/lean/PFCore/Effect.lean` | Effect kinds |
| `pf-core/lean/PFCore/Action.lean` | Action, ActionAllowed |
| `pf-core/lean/PFCore/Decision.lean` | Allowed / Denied |
| `pf-core/lean/PFCore/Event.lean` | Event, EventSafe, EventIn |
| `pf-core/lean/PFCore/Trace.lean` | Trace, TraceSafe |
| `pf-core/lean/PFCore/Contract.lean` | Contract algebra (pre/post/invariant, seq) |
| `pf-core/lean/PFCore/StatefulContract.lean` | Stateful contract extension |
| `pf-core/lean/PFCore/Invariant.lean` | Trace invariants |
| `pf-core/lean/PFCore/Composition.lean` | Sequential composition |
| `pf-core/lean/PFCore/Handoff.lean` | HandoffSafe |
| `pf-core/lean/PFCore/Certificate.lean` | Certificate structure |
| `pf-core/lean/PFCore/RuntimeObservation.lean` | Observation mapping types |
| `pf-core/lean/PFCore/Soundness.lean` | Decider soundness theorems |
| `pf-core/lean/PFCore/Examples.lean` | Checked examples |

*No pre-existing Lean files were present in the repository; PF-Core is greenfield.*

### Schemas

All under `pf-core/schemas/` with versions `pf-core.<kind>.v0`.

### Runtime emitters

Adapter contract in `pf-core/docs/adapter-contract.md`. Validator compiles observations deterministically.

### PCS / hash conventions

PF-Core uses SHA-256 lowercase hex over canonical JSON (field `hash`, chain via `prev_hash`), aligned with common PCS hash-chain patterns. Genesis sentinel: `0` repeated 64 times.

### MCP sidecar patterns

Example fixtures: `mcp_sidecar_allowed.json`, `mcp_sidecar_denied.json`, and observation compile example.
