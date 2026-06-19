# Phase 7 — post-incident-proofs Execution Checklist

Executable PR checklist for [SentinelOps-CI/post-incident-proofs](https://github.com/SentinelOps-CI/post-incident-proofs). Bundle layout reference and smoke test live in **provability-fabric-core** at tag `pf-core-v0.6.0`.

**Pin:** `d5f3051b927f2f68cabac1a37c85d5113b9d77ad`

## Prerequisites

- [ ] Read [`adapters/post_incident_proofs/README.md`](../../adapters/post_incident_proofs/README.md)
- [ ] Smoke script: [`adapters/post_incident_proofs/smoke_test.sh`](../../adapters/post_incident_proofs/smoke_test.sh)
- [ ] PF-Core artifact emitter: `pf core emit-artifacts`

---

## Expected bundle layout

`emit-artifacts` produces a directory with exactly these files:

| File | Schema / role |
|------|---------------|
| `runtime_observation.json` | `pf-core.runtime_observation.v1` |
| `event.json` | `pf-core.event.v1` |
| `trace.json` | `pf-core.trace.v0` |
| `certificate.json` | `pf-core.certificate.v0` |
| `audit.jsonl` | One line per event (`pf-core.audit_line.v0`) |

### Binding rules PIP must verify

1. **`certificate.trace_hash`** equals **`trace.trace_hash`**
2. **`certificate.safe`** is `true` for passing bundles
3. **Hash chain:** each event's `previous_event_hash` chains to prior `event_hash`; genesis is 64 zeros
4. **Audit line:** `trace_hash` and `event_hash` match trace/event artifacts

Reference: [`pf-core/docs/certificate-semantics.md`](../../pf-core/docs/certificate-semantics.md)

---

## PR-1: Accept PF-Core `emit-artifacts` bundle layout

**Target:** Extend `verify_bundle` to accept PF-Core artifact directory layout.

### Generate test bundle

```bash
cd provability-fabric-core
python -m pip install -e pf-core/validator
export PYTHONPATH=pf-core/validator

pf core emit-artifacts \
  --schemas pf-core/schemas \
  --file pf-core/examples/valid/mcp_sidecar_observation.json \
  --out-dir ./bundle
```

Handoff bundle (optional second fixture):

```bash
pf core emit-artifacts \
  --schemas pf-core/schemas \
  --file pf-core/examples/valid/handoff_trace.json \
  --out-dir ./bundle-handoff
```

Note: handoff path uses trace-as-input if supported; otherwise assemble from `handoff_trace.json` via e2e `emit_audit_for_trace` pattern.

### Expected PIP invocation

```bash
verify_bundle --bundle-dir ./bundle --pf-core-version 0.6.0
```

Or Lean entrypoint at pinned SHA:

```bash
cd post-incident-proofs
lake exe verify_bundle -- ./bundle
```

### Acceptance

- [ ] `verify_bundle` accepts all five artifact files
- [ ] Rejects bundle when `certificate.safe: false`
- [ ] Rejects bundle when `trace_hash` tampered
- [ ] Rejects bundle when hash chain broken
- [ ] Unit test uses bundle from `smoke_test.sh` layout

---

## PR-2: Forensic gate in release pipeline

**Target:** Release pipeline runs PIP verify on PF-Core artifact bundles.

### Pipeline step (after PCS/lab release)

```bash
# Emit bundle from release observation
pf core emit-artifacts --file <release_observation.json> --out-dir ./release-bundle

# Forensic gate
verify_bundle --bundle-dir ./release-bundle --pf-core-version $(cat pf-core/VERSION)
```

### Acceptance

- [ ] CI step added to release workflow
- [ ] Release **fails** when `certificate.safe: false`
- [ ] Release **fails** when hash chain tampered (use `trace_tampered_chain.json` pattern)
- [ ] Release **passes** on golden MCP sidecar bundle

---

## Smoke test (provability-fabric-core)

Run locally before opening PIP PR:

```bash
bash adapters/post_incident_proofs/smoke_test.sh
# Or: bash scripts/phase7-cross-repo-smoke.sh (full in-repo harness)
```

Expected output: `OK: PF-Core artifact bundle at ...` plus `verify_bundle` invocation or SKIP until PIP PR-1 lands.

When PIP is cloned at extraction-log pin paths (`/tmp/post-incident-proofs`, sibling `../post-incident-proofs`), smoke test probes `verify_bundle` and runs it when PF-Core layout support is detected in `VerifyBundle.lean`.

---

## Assurance boundary

| Layer | Claim class |
|-------|-------------|
| PF-Core `safe: true` | T1 (Lean-proved) + T4 (runtime deciders) |
| PIP `verify_bundle` | T5 organizational / forensic gate |

PIP does **not** expand PF-Core TCB. See [`claim-boundary.md`](claim-boundary.md).
