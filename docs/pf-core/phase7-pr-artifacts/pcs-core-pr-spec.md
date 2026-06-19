# Phase 7 PR Spec — pcs-core PR-1/2: Trace mapping + hash vectors

**Repo:** [SentinelOps-CI/pcs-core](https://github.com/SentinelOps-CI/pcs-core)  
**Pin:** `280bbea4bf3bf3e45004b6254bc72b603030f179`

## PR-1: trace_certificate mapping

- Add `docs/pf-core-trace-mapping.md` in pcs-core (mirror `pf-core/docs/pf-core-trace-mapping.md`)
- Document `trace_hash`, `spec_hash`, canonical JSON rules

Reference: `adapters/pcs/normalize_release.py`, `adapters/pcs/tests/test_trace_certificate_mapping.py`

## PR-2: Shared hash vector CI

- Import `adapters/pcs/tests/fixtures/hash_vectors/` parity tests
- Fail on canonical JSON or `sha256:` prefix drift

## Acceptance

```bash
pytest adapters/pcs/tests/ -v   # identical vectors in both repos
pf core check-trace --file pf-core/examples/valid/pcs_replay_trace.json
```
