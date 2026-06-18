# PF-Core Phase 5 Extraction Log

Pinned sibling repositories for adapter extraction (local dev layout: sibling clones under `../`).

| Repository | Pin | SHA |
|------------|-----|-----|
| provability-fabric-core | release **`pf-core-v0.6.0`** | tag at release |
| provability-fabric | `main` | `a567c8dca015fac3890fddbb77dfd254caa720d8` |
| pcs-core | tag **`v0.1.0`** | `280bbea4bf3bf3e45004b6254bc72b603030f179` |
| post-incident-proofs | `main` | `d5f3051b927f2f68cabac1a37c85d5113b9d77ad` |

## provability-fabric (`a567c8d`)

| Path | Classification | PF-Core touchpoint | sorry/admit |
|------|----------------|-------------------|-------------|
| `Policy.lean` | reference-only | `ActionAllowed` predicate mapping | contains `sorry` (non-interference); not in TCB |
| `config/schemas/` | reusable (catalog export) | `CAPABILITY_CATALOG` via `export_catalog.py` | n/a |
| `config/specifications/spec.yaml` | reference-only | capability naming | n/a |
| `runtime/admission-controller/` | out-of-scope | K8s admission | n/a |
| `runtime/sidecar-watcher/` | extractable (patterns) | `runtime_observation.v1` via sidecar adapter | n/a |
| `adapters/pcs/` | reference-only | PCS bridge patterns | n/a |
| `adapters/fastapi_cert_middleware/` | out-of-scope | HTTP middleware | n/a |

## pcs-core v0.1.0 (`280bbea`)

| Path | Classification | PF-Core touchpoint | sorry/admit |
|------|----------------|-------------------|-------------|
| `python/pcs_core/hash.py` | reusable | `normalize_hash` / canonical JSON | n/a |
| `docs/hash-canonicalization.md` | reference | `sha256:` prefix rule | n/a |
| `python/tests/hash_vectors/` | reusable fixtures | `adapters/pcs/tests/` parity | n/a |
| `examples/labtrust/` | reusable fixtures | `pcs_replay_trace.json` | n/a |
| `schemas/` | reference-only | diff against PF-Core schemas; no wholesale merge | n/a |
| `lean/PCS/` | reference-only | trace certificate semantics | scan: no sorry in hash path |

## post-incident-proofs (`d5f3051`)

| Path | Classification | PF-Core touchpoint | sorry/admit |
|------|----------------|-------------------|-------------|
| `src/` | forensic cross-check | optional `verify_bundle` gate | Lean scan required before import |
| `docs/ASSURANCE_MATRIX.md` | reference | claim map D1 | n/a |

## adapters/ (untrusted, Phase 5)

| Path | Classification | Notes |
|------|----------------|-------|
| `provability-fabric/mcp_sidecar/normalize.py` | extractable | Sidecar → observation v1 |
| `provability-fabric/export_catalog.py` | reusable | Catalog JSON export |
| `provability-fabric/reference/Policy.lean` | reference-only | Pin `a567c8d`; contains `sorry` |
| `provability-fabric/fixtures/capability_catalog.json` | reusable | Feeds compile.py optionally |
| `pcs/normalize_release.py` | extractable | LabTrust → trace |
| `pcs/tests/fixtures/hash_vectors/` | reusable | PCS v0.1.0 parity |
| `post_incident_proofs/README.md` | reference | Forensic gate workflow |

## provability-fabric-core (trusted TCB)

| Path | Classification | Notes |
|------|----------------|-------|
| `pf-core/lean/PFCore/` | **trusted** | no sorry/admit/axiom/unsafe |
| `pf-core/schemas/` | **trusted** | v0 legacy + v1 primary |
| `pf-core/validator/pf_core/` | **trusted** | deciders + compile |
| `adapters/` | **untrusted** | normalizers only |

