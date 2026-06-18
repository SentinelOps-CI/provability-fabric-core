# Phase 7 — pcs-core Execution Checklist

Executable PR checklist for [SentinelOps-CI/pcs-core](https://github.com/SentinelOps-CI/pcs-core). Reference adapter and hash vectors live in **provability-fabric-core** at tag `pf-core-v0.6.0`.

**Pin:** `280bbea4bf3bf3e45004b6254bc72b603030f179` (tag `v0.1.0`)

## Prerequisites

- [ ] Read [`adapters/pcs/normalize_release.py`](../../adapters/pcs/normalize_release.py)
- [ ] Fixture: [`adapters/pcs/fixtures/labtrust-release/trace_certificate.valid.json`](../../adapters/pcs/fixtures/labtrust-release/trace_certificate.valid.json)
- [ ] PF-Core certificate semantics: [`pf-core/docs/certificate-semantics.md`](../../pf-core/docs/certificate-semantics.md)

---

## PR-1: PF-Core trace ↔ PCS `trace_certificate` mapping

**Target:** Add `docs/pf-core-trace-mapping.md` in pcs-core documenting field correspondence.

### PCS `trace_certificate` (v0) vs PF-Core artifacts

PCS and PF-Core use **different certificate schemas**. Phase 7 documents mapping; it does not unify schemas.

| PCS `trace_certificate` field | PF-Core equivalent | Notes |
|------------------------------|-------------------|-------|
| `certificate_id` | `certificate.certificate_id` | Different naming convention (`cert-*` vs generated) |
| `schema_version` | `certificate.schema_version` | PCS `v0` vs PF-Core `pf-core.certificate.v0` |
| `trace_hash` | `trace.trace_hash`, `certificate.trace_hash` | PCS uses `sha256:` prefix; PF-Core stores hex64 (normalize at boundary) |
| `spec_hash` | `certificate.contract_hash` | PCS spec hash ↔ PF-Core contract hash binding |
| `property_id` | (none) | PCS property identifier; map to `policy_ref` or contract id in docs |
| `checker` | `certificate.checker` | PCS `certifyedge` vs PF-Core `lean4` |
| `checker_version` | `certificate.checker_version` | Version strings differ by design |
| `status` | `certificate.safe` | `CertificateChecked` + `safe: true` equivalence documented |
| `counterexample_ref` | (none) | PCS-only; out of PF-Core scope |
| `created_at` | (none) | Organizational metadata |
| `producer` / `producer_version` | `certificate.created_by` | Optional PF-Core field |
| `source_repo` / `source_commit` | `certificate.proof_ref` | Different semantics; document cross-ref |
| `signature_or_digest` | (none) | PCS bundle integrity; PIP layer |

### Event / trace hash rules (shared)

Both repos must agree on:

1. Genesis `previous_event_hash`: 64 ASCII `0` characters
2. Canonical JSON: sorted keys, minimal separators
3. `event_hash = sha256(payload)` as lowercase hex (accept `sha256:` prefix at validation)
4. `trace_hash = sha256(canonical_json(trace \\ {trace_hash}))`

Reference: [`pf-core/docs/certificate-semantics.md`](../../pf-core/docs/certificate-semantics.md) § Hash chain.

### LabTrust replay path

[`normalize_release.py`](../../adapters/pcs/normalize_release.py) maps pinned `labtrust-release/` fixtures to `pcs_replay_trace.json`. Document how PCS release dir fields feed PF-Core events.

### Acceptance

- [ ] Field-by-field table in pcs-core `docs/pf-core-trace-mapping.md`
- [ ] Cross-reference to `pf-core/docs/certificate-semantics.md`
- [ ] No semantic drift vs `normalize_release.py` output
- [ ] `check-trace` passes on generated trace in pf-core repo:

```bash
PYTHONPATH=pf-core/validator python -m pf_core.cli core check-trace \
  --schemas pf-core/schemas \
  --file pf-core/examples/valid/pcs_replay_trace.json
```

---

## PR-2: Shared hash vector CI

**Target:** PCS and PF-Core share identical hash vector regression files.

### Vector location (authoritative in provability-fabric-core)

```
adapters/pcs/tests/fixtures/hash_vectors/TraceCertificate.v0/
```

### Acceptance commands

```bash
# In provability-fabric-core
PYTHONPATH=pf-core/validator pytest adapters/pcs/tests/ -v

# In pcs-core (after PR-2)
pytest tests/hash_vectors/ -v   # identical vector files
```

- [ ] CI job in pcs-core imports or mirrors vector files from pf-core tag
- [ ] Fails on canonical JSON or `sha256:` prefix handling drift
- [ ] Both repos pass with identical vector file contents

---

## Reference files (provability-fabric-core)

| File | Purpose |
|------|---------|
| `adapters/pcs/normalize_release.py` | LabTrust → PF-Core trace |
| `pf-core/examples/valid/pcs_replay_trace.json` | Golden replay trace |
| `adapters/pcs/tests/fixtures/hash_vectors/` | Shared hash vectors |
| `pf-core/docs/certificate-semantics.md` | Hash and certificate rules |
