# Phase 7 — Cross-Repo Verification

Run after parent-repo Phase 7 PRs merge. PF-Core reference gate remains unchanged in **provability-fabric-core**; this document defines the cross-repo acceptance criteria for the "real vision" exit.

**PF-Core pin:** `pf-core-v0.6.0` (see [`pf-core/VERSION`](../../pf-core/VERSION))

---

## Step 1: PF-Core reference gate (unchanged)

In `provability-fabric-core` at tag `pf-core-v0.6.0`:

```bash
make pf-core-trusted
make pf-core-e2e
PYTHONPATH=pf-core/validator pytest adapters/provability-fabric/tests adapters/pcs/tests -v
bash adapters/post_incident_proofs/smoke_test.sh
```

All must pass. This gate does not depend on parent repo changes.

---

## Step 2: provability-fabric native path

After PR-1 through PR-4 merge in provability-fabric:

```bash
# Sidecar emits v1 observation natively
sidecar-watcher emit-test --golden sidecar_audit_line.json > /tmp/obs.json

pf core schema-check --schemas vendor/pf-core/schemas
pf core compile-observation --schemas vendor/pf-core/schemas --file /tmp/obs.json
pf core check-trace --schemas vendor/pf-core/schemas --file trace.json --lean-check
pf core emit-certificate --schemas vendor/pf-core/schemas --trace trace.json
```

### Pass criteria

- [ ] Native v1 observation validates without normalize shim
- [ ] Compile + check-trace + certificate match pf-core e2e mcp-sidecar scenario
- [ ] Admission-controller audit lines compile with parity vs reference normalize.py
- [ ] CI runs schema-check on every push with pinned pf-core tag

---

## Step 3: pcs-core hash parity

After PR-1 and PR-2 merge in pcs-core:

```bash
# Both repos
pytest adapters/pcs/tests/ -v   # or pcs-core equivalent path
```

### Pass criteria

- [ ] `docs/pf-core-trace-mapping.md` exists in pcs-core
- [ ] Hash vector files identical to `adapters/pcs/tests/fixtures/hash_vectors/`
- [ ] `check-trace` passes on PCS-derived trace in pf-core repo
- [ ] No drift in canonical JSON or `sha256:` prefix handling

---

## Step 4: post-incident-proofs bundle verify

After PR-1 and PR-2 merge in post-incident-proofs:

```bash
pf core emit-artifacts \
  --schemas pf-core/schemas \
  --file pf-core/examples/valid/mcp_sidecar_observation.json \
  --out-dir ./bundle

verify_bundle --bundle-dir ./bundle --pf-core-version 0.6.0
```

### Pass criteria

- [ ] `verify_bundle` accepts PF-Core five-file layout
- [ ] Rejects tampered `trace_hash` and broken hash chain
- [ ] Release pipeline includes forensic gate step
- [ ] Release fails on `safe: false` certificate

---

## Step 5: End-to-end real vision path

Full stack scenario (manual or CI):

```
Sidecar (provability-fabric)
  → runtime_observation.v1
  → compile-observation
  → check-trace
  → emit-artifacts
  → verify_bundle (post-incident-proofs)
```

Optional PCS branch:

```
LabTrust release (pcs-core)
  → PF-Core trace
  → emit-certificate
  → field mapping verified per pcs-core docs
```

### Real vision exit criteria

- [ ] Runtime observations emitted natively from provability-fabric sidecar (not shim-only)
- [ ] PCS release artifacts documented and hash-gated against PF-Core
- [ ] Forensic bundle verification in release pipeline
- [ ] Policy alignment remains vector-tested (no sorry import into TCB)
- [ ] Independent external audit scheduled or completed (see [`external-audit-brief.md`](external-audit-brief.md))

---

## Pin updates

After cross-repo verification passes:

1. Update [`extraction-log.md`](extraction-log.md) with new parent SHAs
2. Update [`external-audit-brief.md`](external-audit-brief.md) pin table
3. Bump `pf-core/VERSION` only if kernel/schema breaking changes required; otherwise parent repos bump dependency pin only

---

## Checklist index

| Parent repo | Checklist |
|-------------|-----------|
| provability-fabric | [`phase7-provability-fabric-checklist.md`](phase7-provability-fabric-checklist.md) |
| pcs-core | [`phase7-pcs-checklist.md`](phase7-pcs-checklist.md) |
| post-incident-proofs | [`phase7-pip-checklist.md`](phase7-pip-checklist.md) |
| Overview | [`phase7-handoff.md`](phase7-handoff.md) |
