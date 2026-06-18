# PF-Core External Audit Brief

Prepared for independent Lean / PL / security reviewers. Estimated review time: 2–4 hours.

## Scope

PF-Core is the **trusted kernel** for proof-carrying agentic action traces in the SentinelOps stack. This brief covers the trusted computing base (TCB), theorem boundaries, residual assumptions, and adapter bypass scenarios.

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
| `Examples.lean`, `Replay.lean` | Checked examples, optional replay |

**Scan policy:** no `sorry`, `admit`, `axiom`, or `unsafe` in trusted Lean.

### Schemas (`pf-core/schemas/`)

v0 legacy + v1 primary: `principal`, `action`, `handoff`, `runtime_observation`, `event.v1`, etc.

### Validator (`pf-core/validator/pf_core/`)

`compile.py`, `deciders.py`, `hash_chain.py`, `schemas.py`, `cli.py`, `emitter.py`, `audit.py`

### Untrusted (explicitly excluded from TCB)

- `adapters/` — sidecar normalizers, PCS replay, catalog export
- Parent repos: provability-fabric, pcs-core, post-incident-proofs

## Suggested review order

1. **`Handoff.lean`** — verify `handoff_does_not_expand_authority` is subset against source authority, not recipient prior grants.
2. **`CapabilityCatalog.lean` + `Principal.lean`** — roles vs capabilities separation.
3. **`Action.lean` + `Event.lean`** — `ActionAllowed`, audit metadata, `EventWitness` vs `EventOccurrence`.
4. **`Trace.lean` + `Soundness.lean`** — trace safety induction and decider soundness.
5. **`Certificate.lean`** — certificate does not overclaim (read docstrings "Does not imply").
6. **`hash_chain.py` + `certificate-semantics.md`** — hash binding assumptions (A2).
7. **`claim-boundary.md`** — organizational vs proved claims.

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
2. **Catalog poisoning** — untrusted `capability_catalog.json` merged at compile time (mitigated: catalog is organizational T5; kernel catalog in Lean is authoritative for proofs).
3. **Hash prefix confusion** — `sha256:` vs hex64 (mitigated: `normalize_hash` accepts both; storage is hex64).
4. **Certificate overclaim** — forbidden phrases blocked in `emitter.py` and `audit.py`.

## Pins (adapter extraction)

| Repo | Pin |
|------|-----|
| provability-fabric | `a567c8d` |
| pcs-core | `v0.1.0` / `280bbea` |
| post-incident-proofs | `d5f3051` |

See `docs/pf-core/extraction-log.md` for file-by-file classification.

## Gate

Trusted CI: `powershell -File pf-core/scripts/pf-core-trusted.ps1` or `make pf-core-trusted`.

Adapter CI (non-blocking): `.github/workflows/adapters-ci.yml`.
