# PF-Core Claim Boundary

Claims about PF-Core must use classification categories below. CI `audit-boundary` rejects forbidden phrases in trusted paths.

## Soundness split (required in all major docs)

- **Lean proves:** decider soundness, trace/event safety, contract projections, handoff subset
- **Runtime validates:** schema conformance, hash chains, compile determinism, adapter catalogs
- **Assumptions:** observation fidelity, tenant labels, SHA-256 chaining (`assumptions.md`)

## Classification categories (T1–T5)

| ID | Name | Meaning |
|----|------|---------|
| T1 | Lean-proved | Theorem in `pf-core/lean/PFCore/` with docstring |
| T2 | Schema-guaranteed | Pinned JSON schema + `additionalProperties: false` |
| T3 | Assumed | Documented in `assumptions.md` |
| T4 | Operationally checked | Validator CLI / deciders, not Lean-proved |
| T5 | Organizational | Process, deployment, human review |

## Spec 10-category map (Phase 5)

| Spec category | PF-Core mapping | Evidence |
|---------------|-----------------|----------|
| Lean-proved | **T1** | `pf-core/lean/PFCore/`, `Soundness.lean` |
| Lean-stated but untrusted | **T1b** (doc-only) | Parent Policy.lean reference; not in TCB |
| Executable runtime check | **T4** | `deciders.py`, `pf core check-trace` |
| Schema validation | **T2** | `pf-core/schemas/`, `schema-check` |
| Replay validation | **T4** + fixture tag `must_fail_at: replay_validation` | `pcs_replay_trace.json`, adapters |
| Cryptographic assumption | **T3 (A2)** | `hash_chain.py`, `assumptions.md` A2 |
| Infrastructure assumption | **T3 (A1, A3, …)** | `assumptions.md` |
| Empirical benchmark result | **Out of scope** | — |
| Documentation-only claim | **T5** | Runbooks, adapter READMEs |
| Out of scope | **N/A** | `mission.md` exclusions |

## Root README claim classification

| README claim | Class | Evidence |
|--------------|-------|----------|
| "Minimal trusted kernel for proof-carrying agentic actions" | T1 + T4 | `TraceSafe`, `compile-observation` |
| "Contracted tool calls, handoffs, trace-level safety preservation" | T1 | `EventSafe`, `HandoffSafe`, `trace_safe_cons`, `seq_contract_satisfaction_left` |
| "Contract algebra with pre/post/invariant" | T1 | `Contract.lean`, `TraceSatisfiesContract` |
| "Structured JSON contracts for runtime" | T2 + T4 | `contract.schema.json`, `contracts.py` |
| "Intentionally smaller than Provability Fabric" | T5 | Scope boundary in `mission.md` |
| "Not a second runtime, CLI surface, or evidence standard" | T5 | `mission.md` exclusions |
| "`make pf-core-trusted`" verifies trusted build | T4 | Makefile + CI workflow |
| Layout lists Lean/schemas/examples/validator | T2 + T5 | Directory inventory |

## pf-core/docs claim classification

| Doc claim | Class | Evidence |
|-----------|-------|----------|
| Formal model types and predicates | T1 | `pf-core/lean/PFCore/` |
| EventKind v1 migration table | T2 + T5 | `event.v1.schema.json`, `formal-model.md` |
| Theorem map index | T1 | `theorem-map.md` ↔ Lean theorems |
| Schema map versions | T2 | `pf-core/schemas/` |
| Runtime mapping pipeline | T4 + T3 | `runtime-mapping.md`, validator |
| Adapter contract emit set | T4 | `emitter.py`, `adapter-contract.md` |
| Certificate hash semantics | T3 + T4 | `certificate-semantics.md`, `hash_chain.py` |
| Threat model mitigations | T1 + T4 | Theorem map + deciders |
| Examples fixture catalog | T4 | `validate_examples.py` |
| Trusted rings layering | T5 | `trusted-rings.md` |

## Allowed claim phrases

- PF-Core proves trace-level safety preservation under stated assumptions.
- PF-Core checks that allowed events satisfy declared action predicates.
- PF-Core validates runtime observations against pinned schemas.
- PF-Core links runtime evidence to formal trace artifacts.
- PF-Core does not prove semantic correctness of LLM outputs.
- PF-Core does not prove external tools are honest.

## Forbidden without T1–T4 backing

- "fully secure", "provably safe in production", "guarantees no data exfiltration"
- "trustless", "zero trust" (unqualified)
- "proves the LLM cannot …"
- "cryptographically proves"
- "PF-Core verifies agents"
- "PF-Core guarantees AI safety"
- "PF-Core proves model alignment"
- "PF-Core proves the runtime is secure"
- "PF-Core proves non-interference for the whole platform"
- "PF-Core proves all Provability Fabric claims"

## Mapping claims to evidence

| Category | Evidence location |
|----------|-------------------|
| T1 | Lean theorem + `Soundness.lean` |
| T2 | Schema file + `pf core schema-check` |
| T3 | `assumptions.md` section ID |
| T4 | Validator module + CLI command |
| T5 | External runbook (not in repo) |
