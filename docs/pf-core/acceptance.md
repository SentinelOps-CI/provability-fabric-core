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
| All required schema files present (14) | PASS | `pf-core/schemas/` |
| `additionalProperties: false` on trusted schemas | PASS | Schema files |
| `schema_version` = `pf-core.<kind>.v0` (v1 for events) | PASS | `$id` fields |
| Valid fixtures pass | PASS | 15 valid (`validate_examples.py`) |
| Invalid fixtures fail | PASS | 19 invalid |
| Invalid fixtures fail for expected reason | PASS | `expected_error` + `must_fail_at` |
| Negative twin per positive scenario | PASS | `examples.md` scenario table |
| Schema `examples` + `x-invalid-examples` | PASS | All 14 schema files |
| Versioning policy documented | PASS | `schema-map.md` |
| Canonicalization + hash binding documented | PASS | `schema-map.md`, `certificate-semantics.md`, A2 |
| PCS-style SHA-256 lowercase hex (not `sha256:` prefix) | PASS | `hash_chain.py`, schemas `pattern: ^[0-9a-f]{64}$` |

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
| Ecosystem inventory (honest, no live PF wiring) | PASS | `ecosystem-inventory.md` |
| Non-Lean tutorial | PASS | `tutorial.md` |
| Theorem / schema / runtime maps | PASS | `theorem-map.md`, `schema-map.md`, `runtime-mapping.md` |
| Trusted rings diagram doc | PASS | `trusted-rings.md` |

## CI acceptance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Job `pf-core-trusted` in GitHub Actions | PASS | `.github/workflows/pf-core-trusted.yml` |
| Matches Makefile gate (`make pf-core-trusted`) | PASS | Workflow runs `make pf-core-trusted` |
| Fails on sorry/admit/axiom/unsafe | PASS | `audit.py` |
| Fails on schema/fixture regression | PASS | `schema-check`, `validate_examples.py` |
| Fails on missing theorem docstring | PASS | `audit.py` |
| Fails on forbidden claim phrase | PASS | `audit.py` `FORBIDDEN_PHRASES` |
| Fails on undocumented trusted file | PASS | `audit.py` boundary check |

## Must-not-do (hard prohibitions)

| Prohibition | Status | Notes |
|-------------|--------|-------|
| sorry/admit/axiom in trusted Lean | PASS | CI enforced |
| Trusted schemas without invalid fixtures | PASS | 19 invalid fixtures |
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
| Live Provability Fabric repo integration | N/A (`ecosystem-inventory.md`) |
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
| Documentation | 15 | 0 | 0 |
| CI | 7 | 0 | 0 |
| Must-not-do | 9 | 0 | 0 |
| Out of scope | 0 | 0 | 7 |
| **Total** | **90** | **0** | **7** |

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

- Hash digests use 64-char lowercase hex (PCS-style canonical JSON); the `sha256:` URI prefix from some PCS examples is not used — policy is documented consistently.
- `pf-core.event.v0` is legacy reference; fixtures use `pf-core.event.v1`.
- Claim classification uses T1–T5 shorthand; maps to the spec's finer categories in `claim-boundary.md`.
- Parent Provability Fabric Policy.lean is reference-only; not imported into trusted kernel.
