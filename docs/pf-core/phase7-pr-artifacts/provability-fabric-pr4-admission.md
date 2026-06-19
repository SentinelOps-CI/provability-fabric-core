# Phase 7 PR Spec — provability-fabric PR-4: Admission parity

**Repo:** provability-fabric  
**Reference:** `adapters/provability-fabric/mcp_sidecar/normalize.py` — `normalize_admission_line()`

## Goal

Admission-controller audit lines compile through PF-Core path without regression vs reference normalizer.

## Fixture

`adapters/provability-fabric/tests/fixtures/admission_audit_line.json`

## Acceptance

```bash
# admission audit JSON -> compile-observation -> validate-event
pytest adapters/provability-fabric/tests/test_admission_parity.py -v
```

- Field mapping documented in `adapters/provability-fabric/README.md`
- No regression vs reference `normalize_admission_line()` on golden fixtures
