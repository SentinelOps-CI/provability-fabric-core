# Phase 7 Status — provability-fabric-core

Last updated: 2026-06-19

## Recovery

| Item | Status |
|------|--------|
| `git checkout HEAD -- .` | Completed — `cli.py` restored (~9KB) |
| Prior untracked work | Re-implemented (see below) |

## In-repo deliverables (this repo)

| Deliverable | Status | Path |
|-------------|--------|------|
| Five-file bundle verifier | DONE | `pf-core/validator/pf_core/bundle_verify.py` |
| CLI `verify-bundle` | DONE | `pf-core/validator/pf_core/cli.py` |
| Bundle verify tests | DONE | `pf-core/validator/tests/test_bundle_verify.py` |
| smoke_test.sh local verify | DONE | `adapters/post_incident_proofs/smoke_test.sh` |
| Parent probe scripts | DONE | `scripts/phase7-parent-probe.sh`, `.ps1` |
| Cross-repo smoke Step 1 | DONE | `scripts/phase7-cross-repo-smoke.sh`, `.ps1` |
| Admission parity | DONE | `normalize_admission_line()`, `test_admission_parity.py` |
| PR spec artifacts (5) | DONE | `docs/pf-core/phase7-pr-artifacts/` |
| Validator unit tests (8 modules) | DONE | `pf-core/validator/tests/test_*.py` |
| Email/network fixtures + e2e | DONE | `pf-core/examples/`, `e2e-replay-gate.*` |
| Assumption.lean A1–A10 | DONE | `pf-core/lean/PFCore/Assumption.lean` |
| PCS trace mapping doc | DONE | `pf-core/docs/pf-core-trace-mapping.md` |
| adapters-ci guards | DONE | `.github/workflows/adapters-ci.yml` (smoke integrity + verify-bundle) |
| Shell scripts LF line endings | DONE | `smoke_test.sh`, `e2e-replay-gate.sh`, phase7 scripts |

## Parent-repo work (blocked)

| PR | Repo | Status |
|----|------|--------|
| PR-1 Native v1 emission | provability-fabric | PENDING |
| PR-2 Schema dependency | provability-fabric | PENDING |
| PR-3 CLI wrapper | provability-fabric | PENDING |
| PR-4 Admission parity | provability-fabric | PENDING |
| PR-1 Trace mapping | pcs-core | PENDING |
| PR-2 Hash vector CI | pcs-core | PENDING |
| PR-1 Bundle verify | post-incident-proofs | PENDING |
| PR-2 Forensic gate | post-incident-proofs | PENDING |

## Local verification (2026-06-19)

| Gate | Windows (local) | Notes |
|------|-----------------|-------|
| `schema-check` | PASS | 18 schemas |
| `validate_examples.py` | PASS | 21 valid, 22 invalid |
| `audit-boundary` | PASS | |
| pytest (adapters + validator) | PASS | 81 tests |
| `emit-artifacts` + `verify-bundle` | PASS | PowerShell / `PYTHONPATH=pf-core/validator` |
| `e2e-replay-gate.ps1` | **Partial** | Fails at `--lean-check` without `lake` on PATH |
| `e2e-replay-gate.sh` via WSL bash | **Partial** | Use Linux CI or Git Bash + Windows `PYTHON` for smoke |
| `lake build` / Lean replay | **Requires Linux CI** | Not available on typical Windows dev shell |

## Requires Linux CI / `lake`

These gates run fully on **ubuntu-latest** GitHub Actions only:

| Gate | Workflow / script | Why |
|------|-------------------|-----|
| Lean trusted build | `pf-core-trusted.yml`, `make pf-core-trusted` | `lake build` in `pf-core/lean` |
| E2E `--lean-check` | `pf-core-e2e.yml`, `e2e-replay-gate.sh` | Invokes `lake build PFCore.Replay` |
| Full adapters-ci | `adapters-ci.yml` | Clones sibling repos at pinned SHAs, bash smoke |
| PIP `verify_bundle` RUN path | `smoke_test.sh` | Requires merged PIP PR-1 + local PIP clone with Lean |

Windows developers: use `pf-core-trusted.ps1` for schema/fixtures/audit; use `PYTHONPATH=pf-core/validator pytest ...` for Python gates; defer `--lean-check` and full bash smoke to CI or WSL with matching Python + `lake`.

## Verification commands

```bash
export PYTHONPATH=pf-core/validator
python -m pf_core.cli core schema-check --schemas pf-core/schemas
python pf-core/scripts/validate_examples.py
python -m pf_core.cli core audit-boundary --root .
pytest adapters/provability-fabric/tests adapters/pcs/tests pf-core/validator/tests -v
bash adapters/post_incident_proofs/smoke_test.sh   # Linux CI / Git Bash + PYTHON=python
bash scripts/phase7-cross-repo-smoke.sh            # full Step 1 on Linux
```

```powershell
$env:PYTHONPATH = "pf-core\validator"
powershell -NoProfile -File pf-core/scripts/pf-core-trusted.ps1
python -m pytest adapters/provability-fabric/tests adapters/pcs/tests pf-core/validator/tests -v
```

## Cross-repo verification

| Step | Status |
|------|--------|
| Step 1 (in-repo gates) | **PASS** — see [`phase7-cross-repo-verification.md`](phase7-cross-repo-verification.md) |
| Steps 2–5 (parent repos) | **BLOCKED** until PRs merge |

## External audit

Prepared per `docs/pf-core/external-audit-brief.md` — **ready for scheduling** (in-repo gates PASS); execution not yet completed.
