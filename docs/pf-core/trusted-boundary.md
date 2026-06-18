# PF-Core Trusted Boundary

This document partitions PF-Core into four zones. Artifacts in the **Trusted** zone are subject to Lean verification, schema pinning, fixture gates, and CI job `pf-core-trusted`.

## Soundness split

| Layer | Responsibility |
|-------|----------------|
| **Lean proves** | Decider soundness, event/trace safety, contract projections, handoff subset |
| **Runtime validates** | JSON schema, hash chains, compile determinism, adapter catalogs |
| **Assumptions** | Observation fidelity, tenant labels, SHA-256 chaining (see `assumptions.md`) |

## Trusted

### Lean kernel (`pf-core/lean/PFCore/`)

- `Basic.lean` — core aliases and helpers
- `Principal.lean` — `Principal`, `HasRole`, `hasRoleD`
- `CapabilityCatalog.lean` — pinned catalog, `AllowedCapabilities`, role map
- `Capability.lean` — `HasCapability`, `CapabilitySubset`
- `Effect.lean` — closed `EffectKind` enumeration
- `Action.lean` — `Action`, `ActionAllowed`, `actionAllowedD`
- `Decision.lean` — `allowed` / `denied`
- `EventKind.lean` — `EventKind` (`action` / `handoff`)
- `Event.lean` — `Event`, `EventSafe`, `EventWitness`
- `Trace.lean` — `Trace`, `TraceSafe`, `EventOccurrence`, `traceSafeD`
- `Contract.lean` — contract algebra (`SatisfiesContract`, `TraceSatisfiesContract`, `seq`)
- `StatefulContract.lean` — stateful extension over `Contract`
- `Invariant.lean` — `AllowedEventsAuthorized`
- `Composition.lean` — trace append safety
- `Handoff.lean` — `HandoffSafe`, `handoff_does_not_expand_authority`
- `Certificate.lean` — certificate structure and `certificate_safe_sound`
- `RuntimeObservation.lean` — observation types
- `Assumption.lean` — numbered assumption records
- `ClaimClassification.lean` — T1–T5 claim categories
- `Soundness.lean` — decider soundness theorems
- `Examples.lean` — checked examples
- `Replay.lean` — optional Lean replay (`--lean-check`)

### JSON schemas (`pf-core/schemas/`)

- `principal.schema.json` — `pf-core.principal.v0`
- `principal.v1.schema.json` — `pf-core.principal.v1`
- `capability.schema.json` — `pf-core.capability.v0`
- `resource.schema.json` — `pf-core.resource.v0`
- `effect.schema.json` — `pf-core.effect.v0`
- `action.schema.json` — `pf-core.action.v0`
- `action.v1.schema.json` — `pf-core.action.v1`
- `decision.schema.json` — `pf-core.decision.v0`
- `event.schema.json` — `pf-core.event.v0` (legacy reference)
- `event.v1.schema.json` — `pf-core.event.v1` (action/handoff discriminator)
- `trace.schema.json` — `pf-core.trace.v0`
- `contract.schema.json` — `pf-core.contract.v0`
- `handoff.schema.json` — `pf-core.handoff.v0`
- `handoff.v1.schema.json` — `pf-core.handoff.v1`
- `certificate.schema.json` — `pf-core.certificate.v0`
- `runtime_observation.schema.json` — `pf-core.runtime_observation.v0`
- `runtime_observation.v1.schema.json` — `pf-core.runtime_observation.v1`
- `claim_classification.schema.json` — `pf-core.claim_classification.v0`

### Canonical hash specification

Documented in `pf-core/docs/certificate-semantics.md`:

- Genesis `previous_event_hash`: 64 ASCII `0` characters
- `event_hash = sha256(canonical_json(event \\ {event_hash}))` lowercase hex
- `trace_hash = sha256(canonical_json(trace \\ {trace_hash}))` lowercase hex
- PCS-style canonical JSON: sorted keys, minimal separators

### Trace replay validator (`pf-core/validator/pf_core/`)

- `compile.py` — deterministic `compile-observation`
- `hash_chain.py` — `event_hash` / `previous_event_hash` / `trace_hash` validation
- `deciders.py` — executable safety deciders mirroring Lean
- `contracts.py` — contract satisfaction deciders
- `schemas.py` — JSON Schema loading and validation
- `cli.py` — `pf core` commands
- `emitter.py` — full adapter artifact emission
- `audit_line.py` — `audit.jsonl` line format
- `event_kind.py` — v1 event kind parsing
- `audit.py` — trusted-boundary audit for CI
- `errors.py` — typed compiler/validator errors

### Example fixtures (`pf-core/examples/`)

- `valid/` — positive scenarios with negative twins
- `invalid/` — `expected_error` + `must_fail_at` on every invalid fixture

### Boundary documentation

- `docs/pf-core/mission.md`
- `docs/pf-core/trusted-boundary.md` (this file)
- `docs/pf-core/claim-boundary.md`
- `docs/pf-core/assumptions.md`
- `docs/pf-core/README.md`
- `docs/pf-core/tutorial.md`
- `docs/pf-core/ecosystem-inventory.md`
- `docs/pf-core/acceptance.md`
- `pf-core/docs/formal-model.md`
- `pf-core/docs/threat-model.md`
- `pf-core/docs/examples.md`
- `pf-core/docs/adapter-contract.md`
- `pf-core/docs/certificate-semantics.md`
- `pf-core/docs/theorem-map.md`
- `pf-core/docs/schema-map.md`
- `pf-core/docs/runtime-mapping.md`
- `pf-core/docs/trusted-rings.md`

### Makefile targets and CI

- `make pf-core-lean`, `pf-core-schema`, `pf-core-examples`, `pf-core-audit`, `pf-core-trusted`
- GitHub Actions workflow `.github/workflows/pf-core-trusted.yml`
- Non-blocking adapter workflow `.github/workflows/adapters-ci.yml`

### Untrusted adapters (`adapters/`)

- `adapters/provability-fabric/` — sidecar normalize, catalog export, Policy.lean reference
- `adapters/pcs/` — LabTrust replay, PCS hash vector parity tests
- `adapters/post_incident_proofs/` — forensic cross-check documentation

### Lean imports (allowlisted)

PF-Core trusted Lean files import only Mathlib-free standard library modules and other `PFCore.*` modules. No `sorry`, `admit`, `axiom`, or `unsafe` in trusted files. Dependency graph (leaves → roots):

| Module | Imports |
|--------|---------|
| `Basic.lean` | (stdlib only) |
| `Principal.lean` | `Basic` |
| `CapabilityCatalog.lean` | `Basic`, `Principal` |
| `Capability.lean` | `Basic`, `Principal`, `CapabilityCatalog` |
| `Effect.lean` | `Basic`, `Principal`, `Capability` |
| `Decision.lean` | `Basic` |
| `Action.lean` | `Effect`, `Capability`, `Principal` |
| `Handoff.lean` | `Action`, `Principal`, `Capability` |
| `EventKind.lean` | `Action`, `Handoff` |
| `Event.lean` | `Action`, `Decision`, `EventKind`, `Handoff` |
| `Trace.lean` | `Event`, `Action`, `Handoff` |
| `Contract.lean` | `Event`, `Trace`, `Effect` |
| `Invariant.lean` | `Trace`, `Contract` |
| `Composition.lean` | `Trace`, `Contract` |
| `StatefulContract.lean` | `Contract` |
| `Certificate.lean` | `Trace` |
| `RuntimeObservation.lean` | `Basic`, `Principal`, `Capability`, `Effect`, `Decision`, `Event` |
| `Assumption.lean` | `Basic` |
| `ClaimClassification.lean` | `Basic` |
| `Soundness.lean` | `Principal` … `Handoff` (decider soundness bundle) |
| `Replay.lean` | `Examples`, `Trace` |

Toolchain: `pf-core/lean/lean-toolchain` (via elan). `set_option autoImplicit false` in `lakefile.lean`.

## Untrusted

- Agent prompts, model outputs, planner logic
- MCP servers, sidecars, third-party tools (except normalized observations)
- Policy documents outside pinned `policy_ref` catalogs
- Evidence blob contents referenced by `evidence_ref`
- Deployment configuration (Kubernetes, IAM, secrets managers)
- Parent Provability Fabric runtime and PCS emitters

## Assumed

- Runtime emitters produce schema-valid JSON before trusted processing (A1)
- SHA-256 digests link `previous_event_hash` to prior `event_hash` (A2)
- `tenant_id` labels are assigned correctly by organizational process (A3)
- Adapter capability catalog is complete for mapped effects (A4)
- `compile-observation` is pure and deterministic (A6)
- `policy_ref` resolves to static adapter bundles (A8)

## Explicitly unproved

- Safe trace implies real-world safety
- Denied events were blocked at the host OS
- Handoff recipients honor received authority
- Lab release gates or MCP audits cover all attack surfaces
- Certificate acceptance by downstream verifiers without their own policy
- Completeness of effect/capability enumeration vs production tools
