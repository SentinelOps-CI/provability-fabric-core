# Phase 7 PR Spec — post-incident-proofs PR-1/2: Bundle verify + forensic gate

**Repo:** [SentinelOps-CI/post-incident-proofs](https://github.com/SentinelOps-CI/post-incident-proofs)  
**Pin:** `d5f3051b927f2f68cabac1a37c85d5113b9d77ad`

## PR-1: Accept PF-Core five-file bundle

Layout from `emit-artifacts`:

| File | Role |
|------|------|
| `runtime_observation.json` | v1 observation |
| `event.json` | v1 event |
| `trace.json` | v0 trace |
| `certificate.json` | v0 certificate |
| `audit.jsonl` | audit lines |

Binding rules: `certificate.trace_hash` == `trace.trace_hash`, hash chain, audit hash parity.

Reference verifier in-core: `pf core verify-bundle --bundle-dir <dir>`

```bash
pf core emit-artifacts --file pf-core/examples/valid/mcp_sidecar_observation.json --out-dir ./bundle
verify_bundle --bundle-dir ./bundle --pf-core-version 0.6.0
```

## PR-2: Forensic gate in release pipeline

- CI step: emit bundle -> `verify_bundle`
- Block release on `safe: false` or tampered hash chain

## Smoke test

`adapters/post_incident_proofs/smoke_test.sh` — always runs local `pf core verify-bundle` on the emitted bundle.

### SKIP vs RUN (`verify_bundle` in post-incident-proofs clone)

| Condition | Outcome |
|-----------|---------|
| No PIP clone at `/tmp/post-incident-proofs`, `../post-incident-proofs`, or `../../post-incident-proofs` | **SKIP** (exit 0) — documents expected invocation |
| Clone present but `src/VerifyBundle.lean` missing PF-Core markers (`pf-core`, `--bundle-dir`, `--pf-core-version`, `PFCoreArtifacts`) | **SKIP** (exit 0) — pin `d5f3051` pending PR-1 |
| Clone present and `VerifyBundle.lean` contains PF-Core bundle flags **and** `lake exe verify_bundle` accepts `--bundle-dir` | **RUN** — must accept emitted bundle or fail smoke |

Local reference verifier (`pf core verify-bundle`) always **RUN**s and must pass.
