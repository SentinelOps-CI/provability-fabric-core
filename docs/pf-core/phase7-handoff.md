# Phase 7 Handoff — Parent Repository PR Specs

Phase 6 delivers PF-Core operational credibility inside `provability-fabric-core`. Phase 7 implements native emitters and shared CI in parent repos. Each PR below references:

- **PF-Core release tag:** `pf-core-v$(cat pf-core/VERSION)` (e.g. `pf-core-v0.6.0`)
- **Extraction pins:** `docs/pf-core/extraction-log.md`

## Execution checklists

| Repo | Checklist |
|------|-----------|
| provability-fabric | [`phase7-provability-fabric-checklist.md`](phase7-provability-fabric-checklist.md) |
| pcs-core | [`phase7-pcs-checklist.md`](phase7-pcs-checklist.md) |
| post-incident-proofs | [`phase7-pip-checklist.md`](phase7-pip-checklist.md) |
| Cross-repo verification | [`phase7-cross-repo-verification.md`](phase7-cross-repo-verification.md) |

---

## provability-fabric ([SentinelOps-CI/provability-fabric](https://github.com/SentinelOps-CI/provability-fabric))

**Pin:** `a567c8dca015fac3890fddbb77dfd254caa720d8`

### PR-1: Native `runtime_observation.v1` emission

**Goal:** `runtime/sidecar-watcher` emits `pf-core.runtime_observation.v1` directly (no adapter normalize shim).

**Changes:**

- Map sidecar audit fields to v1 shape per `docs/pf-core/ecosystem-inventory.md`
- Include `trace_id`, `event_id`, `principal` (v1), `action` (v1 multi-effect), hash-chain fields
- Unit test: output validates against `pf-core/schemas/runtime_observation.v1.schema.json`

**Acceptance:** Golden sidecar line → schema-valid v1 observation matching `adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json` semantics.

### PR-2: PF-Core schema dependency

**Goal:** Depend on PF-Core schemas via git submodule or published JSON Schema package.

**Changes:**

- Submodule or npm/pypi package pointing at `pf-core-v0.6.0` tag
- CI `schema-check` against pinned schemas on every push

**Acceptance:** Sidecar output passes `pf core schema-check` with pinned schema path.

### PR-3: `pf core` CLI wrapper

**Goal:** Thin wrapper delegates to `pf-core-validator` CLI.

**Changes:**

- `pf core compile-observation`, `check-trace`, `emit-certificate` invoke installed validator
- Version pin in `pyproject.toml` / `requirements.txt` matches PF-Core release

**Acceptance:** Wrapper passes `make pf-core-e2e` scenarios when run from provability-fabric repo with submodule.

### PR-4: Admission-controller audit line compatibility

**Goal:** Admission-controller audit lines compile through PF-Core path.

**Changes:**

- Fixture test: admission audit JSON → `compile-observation` → `validate-event`
- Document field mapping in repo README

**Acceptance:** No regression vs `adapters/provability-fabric/mcp_sidecar/normalize.py` output on golden fixtures.

---

## pcs-core ([SentinelOps-CI/pcs-core](https://github.com/SentinelOps-CI/pcs-core))

**Pin:** `280bbea4bf3bf3e45004b6254bc72b603030f179` (tag `v0.1.0`)

### PR-1: PF-Core trace ↔ PCS `trace_certificate` mapping

**Goal:** Document field mapping between PCS release artifacts and PF-Core traces.

**Changes:**

- Add `docs/pf-core-trace-mapping.md` in pcs-core
- Map `trace_hash`, `event_hash`, canonical JSON rules to PCS `trace_certificate` fields
- Cross-reference `pf-core/docs/certificate-semantics.md`

**Acceptance:** `adapters/pcs/normalize_release.py` output documented field-by-field; no semantic drift.

### PR-2: Shared hash vector CI

**Goal:** PCS and PF-Core share hash vector regression gate.

**Changes:**

- CI job imports `adapters/pcs/tests/fixtures/hash_vectors/` parity tests
- Fails on canonical JSON or `sha256:` prefix handling drift

**Acceptance:** `pytest adapters/pcs/tests/` passes in both repos with identical vector files.

---

## post-incident-proofs ([SentinelOps-CI/post-incident-proofs](https://github.com/SentinelOps-CI/post-incident-proofs))

**Pin:** `d5f3051b927f2f68cabac1a37c85d5113b9d77ad`

### PR-1: Accept PF-Core `emit-artifacts` bundle layout

**Goal:** `verify_bundle` accepts PF-Core artifact directory layout.

**Changes:**

- Accept bundle containing: `runtime_observation.json`, `event.json`, `trace.json`, `certificate.json`, `audit.jsonl`
- Validate `certificate.safe` and `trace_hash` binding
- Reference `adapters/post_incident_proofs/smoke_test.sh` expected invocation

**Acceptance:**

```bash
pf core emit-artifacts --file <observation> --out-dir ./bundle
verify_bundle --bundle-dir ./bundle --pf-core-version $(cat pf-core/VERSION)
```

### PR-2: Forensic gate in release pipeline

**Goal:** Release pipeline runs PIP verify on PF-Core artifact bundles.

**Changes:**

- Add CI step after PCS/lab release: emit PF-Core bundle → `verify_bundle`
- Gate blocks release on bundle verification failure

**Acceptance:** Release workflow fails when certificate `safe: false` or hash chain tampered.

---

## Cross-repo coordination

| Dependency | Owner | Phase 7 PR |
|------------|-------|------------|
| v1 observation shape | provability-fabric | PR-1 |
| Schema package | provability-fabric | PR-2 |
| Hash vectors | pcs-core | PR-2 |
| Bundle verify | post-incident-proofs | PR-1, PR-2 |
| E2E proof (reference) | provability-fabric-core | `make pf-core-e2e` (Phase 6 complete) |

## Non-goals (remain in PF-Core reference only)

- Importing parent `Policy.lean` sorry-bearing theorems into TCB
- Native MCP server or second runtime inside pf-core
- Global non-interference proofs
