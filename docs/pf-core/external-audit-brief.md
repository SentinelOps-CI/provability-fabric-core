# PF-Core External Audit Brief (v2)

Prepared for independent Lean / PL / security reviewers. Estimated review time: 2–4 hours.

## Scope

PF-Core is the **trusted kernel** for proof-carrying agentic action traces in the SentinelOps stack. This brief covers the trusted computing base (TCB), theorem boundaries, residual assumptions, adapter bypass scenarios, and Phase 6 operational gates (e2e replay, policy correspondence).

## TCB file list

### Lean (`pf-core/lean/PFCore/`)

| Module | Role |
|--------|------|
| `Basic.lean` | Core aliases, list membership deciders |
| `Principal.lean` | Identity, roles vs explicit capabilities |
| `CapabilityCatalog.lean` | Pinned catalog, role→capability map |
| `Capability.lean` | `HasCapability`, subset predicates |
| `Effect.lean` | Closed effect enumeration |
| `Action.lean` | `ActionAllowed`, multi-effect v1 |
| `Decision.lean` | allowed / denied |
| `EventKind.lean` | action / handoff discriminator |
| `Event.lean` | `EventSafe`, `EventWitness` |
| `Trace.lean` | `TraceSafe`, `EventOccurrence` |
| `Handoff.lean` | `HandoffSafe`, `handoff_does_not_expand_authority` |
| `Certificate.lean` | Evidence-pointer certificate struct |
| `Contract.lean`, `StatefulContract.lean`, `Composition.lean`, `Invariant.lean` | Contract algebra |
| `RuntimeObservation.lean` | Observation types |
| `Assumption.lean`, `ClaimClassification.lean` | Assumption records, T1–T5 |
| `Soundness.lean` | Decider soundness bundle |
| `Examples.lean`, `Replay.lean` | Checked examples, golden Lean replay |

**Scan policy:** no `sorry`, `admit`, `axiom`, or `unsafe` in trusted Lean.

### Schemas (`pf-core/schemas/`)

v0 legacy + v1 primary: `principal`, `action`, `handoff`, `runtime_observation`, `event.v1`, etc. **v1-primary** is normative for trusted golden path (`schema-map.md`).

### Validator (`pf-core/validator/pf_core/`)

`compile.py`, `deciders.py`, `hash_chain.py`, `schemas.py`, `cli.py`, `emitter.py`, `audit.py`

### Untrusted (explicitly excluded from TCB)

- `adapters/` — sidecar normalizers, PCS replay, catalog export
- Parent repos: provability-fabric, pcs-core, post-incident-proofs

## Phase 6 operational gates

### End-to-end replay gate

Blocking CI job `pf-core-e2e` runs the full pipeline on deterministic fixtures:

```
runtime_observation.v1 → compile-observation → validate-event → trace → check-trace → emit-certificate
```

Scenarios: file-read allow/deny, MCP sidecar normalize, handoff subset deny, PCS replay trace, tampered hash failure, Lean `--lean-check` on three golden traces, `validate-handoff` CLI, handoff trace `audit.jsonl` emission.

Scripts: `pf-core/scripts/e2e-replay-gate.sh`, `e2e-replay-gate.ps1`. Makefile: `make pf-core-e2e`.

### Policy correspondence (no TCB expansion)

Parent `Policy.lean` contains `sorry` (non-interference). Alignment is proven via **golden test vectors**, not Lean import:

| Layer | Mechanism |
|-------|-----------|
| Parent `permitD` fragment | 23 vectors in `policy_correspondence_vectors.json` |
| PF-Core `actionAllowedD` / `handoffSafeD` | `test_policy_correspondence.py` |
| Catalog authority | `CapabilityCatalog.lean` = proof authority; JSON export = runtime adapter input (T5) |

See `policy-extraction-map.md` for the correspondence matrix and documented gaps (`LogSpend`, `LogAction`).

### v1-primary migration

Valid fixtures must use `pf-core.runtime_observation.v1`. `audit.py` fails on untagged v0 in trusted path. v0 compile emits deprecation warning.

## Suggested review order

1. **`Handoff.lean`** — verify `handoff_does_not_expand_authority` is subset against source authority, not recipient prior grants.
2. **`CapabilityCatalog.lean` + `Principal.lean`** — roles vs capabilities separation; two-tier catalog model.
3. **`Action.lean` + `Event.lean`** — `ActionAllowed`, audit metadata, `EventWitness` vs `EventOccurrence`.
4. **`Trace.lean` + `Soundness.lean`** — trace safety induction and decider soundness.
5. **`Replay.lean`** — golden trace replay (`file_read`, `handoff`, `lab_release`).
6. **`Certificate.lean`** — certificate does not overclaim (read docstrings "Does not imply").
7. **`hash_chain.py` + `certificate-semantics.md`** — hash binding assumptions (A2).
8. **`claim-boundary.md`** — organizational vs proved claims.
9. **E2E gate output** — run `make pf-core-e2e` and inspect scenario pass/fail boundaries.

## Theorem map highlights (does not imply)

| Theorem | Does **not** imply |
|---------|-------------------|
| `traceSafeD_sound` | JSON parsing correctness, OS enforcement |
| `handoff_does_not_expand_authority` | Recipient honors delegation |
| `certificate_safe_sound` | Downstream verifier acceptance without policy |
| `certificate_claim_bounded` | Global agent safety, model alignment |
| `eventOccurrence_iff_mem` | Temporal ordering beyond list structure |

Full index: `pf-core/docs/theorem-map.md`.

## Residual assumptions

Documented in `docs/pf-core/assumptions.md`:

- **A1** — observation fidelity (emitters produce honest JSON)
- **A2** — SHA-256 hash chain integrity
- **A3** — tenant label correctness
- **A4** — capability catalog completeness for mapped effects
- **A6** — compile determinism
- **A8** — static policy_ref resolution

## Adapter bypass scenarios

From `pf-core/docs/threat-model.md`:

1. **Malicious adapter** — emits schema-valid but semantically false observations (mitigated: organizational trust in adapter; kernel checks deciders only).
2. **Catalog poisoning** — untrusted `capability_catalog.json` merged at compile time (mitigated: Lean catalog is proof authority; drift CI fails on mismatch).
3. **Hash prefix confusion** — `sha256:` vs hex64 (mitigated: `normalize_hash` accepts both; storage is hex64).
4. **Certificate overclaim** — forbidden phrases blocked in `emitter.py` and `audit.py`.

## Pins (adapter extraction)

| Repo | Pin |
|------|-----|
| provability-fabric | `a567c8d` |
| pcs-core | `v0.1.0` / `280bbea` |
| post-incident-proofs | `d5f3051` |
| provability-fabric-core | **`pf-core-v0.6.0`** |

See `docs/pf-core/extraction-log.md` for file-by-file classification.

## Phase 7 handoff

Native parent-repo emitters are **not** in TCB. Ready-to-execute PR specs: `docs/pf-core/phase7-handoff.md` and `docs/pf-core/phase7-pr-artifacts/`.

## Ready for scheduling

In-repo gates required before booking an external review are **PASS** as of 2026-06-19:

- Trusted kernel: `make pf-core-trusted` / `pf-core-trusted.ps1` (schema, fixtures, audit-boundary, Lean build)
- E2E replay: `make pf-core-e2e` on Linux CI (`lake` required for `--lean-check` scenarios)
- Adapters: `adapters-ci` workflow (catalog drift, PCS hash vectors, PIP smoke guard, verify-bundle reference)
- Phase 7 in-repo reference: `bundle_verify.py`, admission parity tests, cross-repo smoke Step 1

**Not blocking scheduling:** parent-repo Phase 7 PRs (Steps 2–5 in `phase7-cross-repo-verification.md`) — audit scope is TCB + operational gates in this repo.

**Blocking production claims beyond TCB:** completed external review with findings triaged.

## External audit scheduling checklist

Schedule before organizational production claims beyond TCB gates:

| Step | Action | Owner | Target |
|------|--------|-------|--------|
| 1 | Share `external-audit-brief.md` v2 + pin table with reviewer | PF-Core maintainer | T-4 weeks |
| 2 | Provide `make pf-core-trusted` + `make pf-core-e2e` output artifacts | PF-Core maintainer | T-3 weeks |
| 3 | Reviewer completes Lean TCB pass (suggested order in brief) | External reviewer | T-2 weeks |
| 4 | Reviewer signs off or files findings; triage in-repo | PF-Core maintainer | T-1 week |
| 5 | Update `acceptance.md` and `extraction-log.md` pins post-review | PF-Core maintainer | Before release claim |

Blocking gates for scheduling: Phase 6 PASS, Phase 7 in-repo reference deliverables PASS (`phase7-status.md`).

## Gates

| Gate | Command | Blocking on `main` |
|------|---------|-------------------|
| Trusted kernel | `make pf-core-trusted` | yes |
| E2E replay | `make pf-core-e2e` | yes |
| Adapters | `adapters-ci` workflow | yes (pinned SHAs, catalog drift) |

Release version: `pf-core/VERSION`. Checklist: `docs/pf-core/release-checklist.md`.
