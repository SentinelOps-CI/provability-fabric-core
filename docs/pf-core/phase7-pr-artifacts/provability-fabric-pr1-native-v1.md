# Phase 7 PR Spec — provability-fabric PR-1: Native v1 emission

**Repo:** [SentinelOps-CI/provability-fabric](https://github.com/SentinelOps-CI/provability-fabric)  
**Pin:** `a567c8dca015fac3890fddbb77dfd254caa720d8`  
**PF-Core tag:** `pf-core-v0.6.0`

## Goal

`runtime/sidecar-watcher` emits `pf-core.runtime_observation.v1` directly (no adapter normalize shim in production).

## Field mapping

See `docs/pf-core/phase7-provability-fabric-checklist.md` PR-1 table and reference `adapters/provability-fabric/mcp_sidecar/normalize.py`.

## Acceptance

- Output validates against `runtime_observation.v1.schema.json`
- Semantic parity with `adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json`
- Denied and ambiguous cases covered

## Reference gate (provability-fabric-core)

```bash
pytest adapters/provability-fabric/tests/test_normalize.py -v
```
