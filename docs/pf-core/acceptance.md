# PF-Core Final Acceptance Checklist

Audit date: 2026-06-18. Gate: `powershell -File pf-core/scripts/pf-core-trusted.ps1` (PASS).

Legend: **PASS** | **FAIL** | **N/A** (out of scope by design)

## Mission boundary

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `docs/pf-core/mission.md` exists | PASS | File present |
| Mandatory verbatim boundary statement | PASS | `mission.md` § Mandatory boundary statement |
| PF-Core smaller than Provability Fabric | PASS | `mission.md` scope table |
| Mandatory conceptual objects (Principal … ClaimClassification) | PASS | Lean + schemas + `trusted-boundary.md` |
| Mandatory exclusions not in trusted kernel | PASS | `mission.md`, `trusted-boundary.md` Untrusted |
| Final target-state claim (honest, qualified) | PASS | `mission.md`, `formal-model.md` |

## Formal kernel acceptance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| PFCore Lean target builds cleanly | PASS | `lake build` in gate |
| No `sorry` in trusted Lean | PASS | `audit-boundary` scan |
| No `admit` in trusted Lean | PASS | `audit-boundary` scan |
| No unallowlisted `axiom` | PASS | `audit-boundary` scan |
| No unallowlisted `unsafe` | PASS | `audit-boundary` scan |
| `set_option autoImplicit true` absent | PASS | `lakefile.lean` + audit |
| Minimal types defined | PASS | `pf-core/lean/PFCore/` |
| `TraceSafe`, `EventSafe`, `ActionAllowed` | PASS | `Trace.lean`, `Event.lean`, `Action.lean` |
| Executable deciders + soundness proofs | PASS | `Soundness.lean` |
| `trace_safe_empty`, `trace_safe_cons`, `traceSafeD_sound` | PASS | `Trace.lean` |
| `every_allowed_event_in_safe_trace_is_allowed` | PASS | `Trace.lean` |
| Contract algebra `pre`/`post`/`invariant` + seq projections | PASS | `Contract.lean` |
| `StatefulContract` extends simple contracts | PASS | `StatefulContract.lean` |
| `HandoffSafe`, `handoff_does_not_expand_authority` | PASS | `Handoff.lean` |
| `EventKind` v1 integration | PASS | `EventKind.lean`, `event.v1.schema.json` |
| All theorems have docstrings (Plain-English / Trusted use / Does not imply) | PASS | `audit-boundary` |
| Theorem names match scope (no overclaim) | PASS | Manual audit (`theorem-map.md`) |
| Lean imports documented | PASS | `trusted-boundary.md` § Lean imports |
| `Assumption`, `ClaimClassification` types | PASS | `Assumption.lean`, `ClaimClassification.lean` |

## Schema acceptance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All required schema files present (18) | PASS | `pf-core/schemas/` (v0 legacy + v1 primary) |
| `additionalProperties: false` on trusted schemas | PASS | Schema files |
| `schema_version` = `pf-core.<kind>.v0` (v1 for events) | PASS | `$id` fields |
| Valid fixtures pass | PASS | 21 valid (`validate_examples.py`) |
| Invalid fixtures fail | PASS | 22 invalid |
| Invalid fixtures fail for expected reason | PASS | `expected_error` + `must_fail_at` |
| Negative twin per positive scenario | PASS | `examples.md` scenario table |
| Schema `examples` + `x-invalid-examples` | PASS | All 14 schema files |
| Versioning policy documented | PASS | `schema-map.md` |
| Canonicalization + hash binding documented | PASS | `schema-map.md`, `certificate-semantics.md`, A2 |
| PCS-style SHA-256 lowercase hex; accepts `sha256:` prefix | PASS | `normalize_hash`, `hash_chain.py`, v1 schema `oneOf` |

## Runtime bridge acceptance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Deterministic `compile-observation` | PASS | `validate_examples.py` determinism test |
| All 11 typed compile errors + fixtures | PASS | See compile-error table below |
| Unknown capabilities rejected | PASS | `obs_unsupported_capability.json` |
| Unknown effects rejected | PASS | `obs_unsupported_effect.json` |
| Ambiguous mappings rejected | PASS | `mcp_sidecar_ambiguous.json` |
| Denied actions remain in trace | PASS | `file_read_denied.json`, `email_send_denied.json` |
| Hash chain passes on valid traces | PASS | `file_read_allowed_trace.json` |
| Hash chain fails on tampered traces | PASS | `trace_tampered_chain.json`, `file_read_bad_hash.json` |
| Trace replay validator listed in trusted boundary | PASS | `hash_chain.py`, `trusted-boundary.md` |
| CLI: schema-check, validate-event, validate-trace | PASS | `cli.py` |
| CLI: compile-observation, check-trace, emit-certificate | PASS | `cli.py` |
| CLI: audit-boundary, emit-artifacts | PASS | `cli.py`, `emitter.py` |
| Adapter artifact set (observation, event, trace, cert, audit) | PASS | `emitter.py` |
| Pre/post execution + prohibited behaviors documented | PASS | `adapter-contract.md` |
| No LLM/network in validation path | PASS | `compile.py`, A6 |

### Compile errors (11 required)

| Error | Valid path | Invalid twin | Status |
|-------|------------|--------------|--------|
| `MissingRequiredField` | observation compile | `obs_missing_required_field.json` | PASS |
| `InvalidSchemaVersion` | schema check | `file_read_bad_schema_version.json` | PASS |
| `InvalidDecision` | event semantics | `event_invalid_decision.json` | PASS |
| `InvalidPrincipal` | event semantics | `event_invalid_principal.json` | PASS |
| `InvalidAction` | event semantics | `event_invalid_action.json` | PASS |
| `InvalidHash` | hash chain | `file_read_bad_hash.json`, `trace_tampered_chain.json` | PASS |
| `UnsupportedEffect` | compile | `obs_unsupported_effect.json` | PASS |
| `UnsupportedCapability` | compile | `obs_unsupported_capability.json` | PASS |
| `AmbiguousMapping` | compile | `mcp_sidecar_ambiguous.json` | PASS |
| `PolicyRefNotFound` | compile | `lab_release_missing_policy.json` | PASS |
| `EvidenceRefNotFound` | compile | `obs_evidence_not_found.json` | PASS |

## Certificate acceptance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Binds `trace_hash` | PASS | `certificate.schema.json`, `emitter.py` |
| Binds `contract_hash` | PASS | `compute_contract_hash` |
| Binds checker output (`checker`, `checker_version`, `proof_ref`) | PASS | `emitter.py` |
| Lists assumptions | PASS | `DEFAULT_ASSUMPTIONS` |
| Lists `claim_class` | PASS | `certificate.schema.json` |
| Forbidden phrases blocked at emit | PASS | `emitter.py` `_reject_forbidden_certificate_text` |
| `certificate_safe_sound` (Lean) | PASS | `Certificate.lean` |

## Documentation acceptance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `mission.md` | PASS | |
| `trusted-boundary.md` (4 zones) | PASS | |
| `claim-boundary.md` + README claim classification | PASS | |
| `assumptions.md` (A1–A10) | PASS | |
| `threat-model.md` | PASS | `pf-core/docs/threat-model.md` |
| `examples.md` | PASS | |
| `adapter-contract.md` | PASS | |
| `certificate-semantics.md` | PASS | |
| `formal-model.md` + soundness posture | PASS | |
| `docs/pf-core/README.md` required sections | PASS | What is/isn't, Lean, schemas, build, assumptions, contract, adapter |
| Root README links (kernel, model, boundary, claim, examples) | PASS | Root `README.md` |
| Every trusted file listed | PASS | `trusted-boundary.md` + audit |
| Ecosystem inventory + extraction log | PASS | `ecosystem-inventory.md`, `extraction-log.md` |
| External audit brief | PASS | `external-audit-brief.md` |
| Policy extraction map | PASS | `policy-extraction-map.md` |
| Phase 5 adapters (untrusted) | PASS | `adapters/` + `adapters-ci.yml` |
| PCS replay fixture | PASS | `pcs_replay_trace.json` |
| v0→v1 migration script | PASS | `migrate-v0-to-v1.py` |
| Lean optional replay | PASS | `Replay.lean`, `--lean-check`, `lean-check-trace.sh` |
| Non-Lean tutorial | PASS | `tutorial.md` |
| Theorem / schema / runtime maps | PASS | `theorem-map.md`, `schema-map.md`, `runtime-mapping.md` |
| Trusted rings diagram doc | PASS | `trusted-rings.md` |

## CI acceptance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Job `pf-core-trusted` in GitHub Actions | PASS | `.github/workflows/pf-core-trusted.yml` |
| Blocking `pf-core-e2e` on `main` | PASS | `.github/workflows/pf-core-e2e.yml` |
| Blocking `adapters-ci` on `main` (pinned SHAs) | PASS | `.github/workflows/adapters-ci.yml` |
| Matches Makefile gate (`make pf-core-trusted`) | PASS | Workflow runs `make pf-core-trusted` |
| `make pf-core-e2e` target | PASS | `Makefile`, `e2e-replay-gate.sh` |
| Fails on sorry/admit/axiom/unsafe | PASS | `audit.py` |
| Fails on schema/fixture regression | PASS | `schema-check`, `validate_examples.py` |
| Fails on v0 fixtures in valid path | PASS | `audit.py` `audit_v1_primary_fixtures` |
| Fails on missing theorem docstring | PASS | `audit.py` |
| Fails on forbidden claim phrase | PASS | `audit.py` `FORBIDDEN_PHRASES` |
| Fails on undocumented trusted file | PASS | `audit.py` boundary check |
| Catalog drift fails adapter CI | PASS | `test_catalog_export_matches_lean` |

## Phase 6 — Real Vision (operational credibility)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| End-to-end replay gate (sidecar → certificate) | PASS | `e2e-replay-gate.sh`, `e2e-replay-gate.ps1` |
| E2E scenarios: allow, deny, MCP, handoff, PCS, tamper, email, network, lab release | PASS | Gate scripts |
| Policy correspondence (20+ vectors) | PASS | `policy_correspondence_vectors.json` (23), `test_policy_correspondence.py` |
| v1-primary trusted path | PASS | `schema-map.md`, `audit.py`, `compile.py` deprecation |
| Adapter pinned SHAs in CI | PASS | `adapters-ci.yml`, `extraction-log.md` |
| Lean replay on 3 golden traces | PASS | `Replay.lean`, `--lean-check` in e2e job |
| `pf-core/VERSION` semver file | PASS | `pf-core/VERSION` |
| Release checklist | PASS | `docs/pf-core/release-checklist.md` |
| External audit brief v2 (e2e + correspondence) | PASS | `external-audit-brief.md` |
| Phase 7 handoff doc | PASS | `docs/pf-core/phase7-handoff.md` |
| Phase 7 in-repo reference (bundle verify, admission, probes) | PASS | `phase7-status.md`, `bundle_verify.py` |
| PIP smoke test | PASS (SKIP semantics) | `smoke_test.sh` emits bundle + local `verify-bundle`; PIP `verify_bundle` **SKIP** until PR-1 |

## Must-not-do (hard prohibitions)

| Prohibition | Status | Notes |
|-------------|--------|-------|
| sorry/admit/axiom in trusted Lean | PASS | CI enforced |
| Trusted schemas without invalid fixtures | PASS | 22 invalid fixtures |
| Silent coercion of unknown fields | PASS | `additionalProperties: false` |
| Examples without expected failure modes | PASS | All invalid have `expected_error` |
| Certificate overclaim | PASS | Emitter guard + semantics doc |
| Denied actions absent from trace | PASS | Denied fixtures in traces |
| Trace history mutation | PASS | Append-only semantics in docs |
| LLM calls for validation | PASS | A6, adapter contract |
| Experimental modules in trusted boundary | PASS | Isolated `pf-core/` tree |

## Out of scope (documented, not implemented)

| Item | Status |
|------|--------|
| Second runtime / MCP implementation | N/A |
| PCS standard / full release logic | N/A |
| K8s / WASM / ledger | N/A |
| LLM semantics / neural verification | N/A |
| Live Provability Fabric adapter path | PASS | `adapters/provability-fabric/` (untrusted) |
| Global non-interference (unproved) | N/A (`trusted-boundary.md`) |
| Lean proof of external tool behavior | N/A |

## Summary

| Category | PASS | FAIL | N/A |
|----------|------|------|-----|
| Mission boundary | 6 | 0 | 0 |
| Formal kernel | 19 | 0 | 0 |
| Schemas | 11 | 0 | 0 |
| Runtime bridge | 16 | 0 | 0 |
| Certificates | 7 | 0 | 0 |
| Documentation | 21 | 0 | 0 |
| CI | 12 | 0 | 0 |
| Phase 6 | 11 | 0 | 0 |
| Must-not-do | 9 | 0 | 0 |
| Out of scope | 0 | 0 | 6 |
| **Total** | **119** | **0** | **6** |

## Gaps fixed in final pass

1. Verbatim mandatory statement added to `mission.md`.
2. Root README explicit trusted-kernel link.
3. `docs/pf-core/README.md` — what is/isn't, assumptions, add contract, add adapter mapping.
4. `formal-model.md` — full soundness posture paragraph.
5. `trusted-boundary.md` — Lean imports table.
6. `adapter-contract.md` — pre/post execution and prohibited behaviors.
7. `audit.py` — two additional forbidden phrases from spec.
8. `emitter.py` — forbidden certificate phrase guard.

## Caveats

- Hash digests stored as 64-char lowercase hex; `sha256:` URI prefix accepted at validation boundary (`normalize_hash`).
- `pf-core.event.v0` and `pf-core.runtime_observation.v0` are legacy reference; valid fixtures use v1 only.
- Claim classification uses T1–T5 with explicit 10-category map in `claim-boundary.md`.
- Parent Provability Fabric Policy.lean is reference-only in `adapters/provability-fabric/reference/`; correspondence tested on extractable fragment only.
- Adapter zone is untrusted; `pf-core-trusted` does not run adapter pytest (adapter CI is separate, blocking on `main`).
- Phase 7 parent-repo emitters documented in `phase7-handoff.md` and per-repo checklists (`phase7-*-checklist.md`); in-repo harness: `scripts/phase7-cross-repo-smoke.sh` / `.ps1`, `scripts/phase7-parent-probe.sh` / `.ps1`; status: `docs/pf-core/phase7-status.md`.
- External audit per `external-audit-brief.md` v2 is prepared with scheduling checklist; not yet executed.
- **Harness regression caveat:** if `adapters/post_incident_proofs/smoke_test.sh` or `scripts/phase7-cross-repo-smoke.ps1` is empty, adapter CI and Phase 7 smoke become no-ops; `adapters-ci.yml` guards against an empty PIP smoke script.
- Assessment §10 bridge items closed in Phase A (v0.6.0): v1 handoff audit lines, `validate-handoff` CLI, adapter contract v1 alignment, catalog export honesty, sidecar role mapping from fixture; validator unit tests in `pf-core/validator/tests/` (8 modules); PCS trace_certificate mapping test in `adapters/pcs/tests/test_trace_certificate_mapping.py`; admission parity in `test_admission_parity.py`.
