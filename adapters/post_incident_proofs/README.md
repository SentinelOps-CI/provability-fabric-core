# Post-incident-proofs forensic cross-check (untrusted organizational gate)

PF-Core proves **trace-level authorization** under pinned schemas and Lean deciders.
[post-incident-proofs](https://github.com/SentinelOps-CI/post-incident-proofs) validates **evidence bundle integrity** after incidents.

## Two-layer assurance

| Layer | Repo | Claim |
|-------|------|-------|
| Authorization trace kernel | provability-fabric-core (PF-Core) | Allowed events satisfy `ActionAllowed` / `HandoffSafe` |
| Forensic non-forgery | post-incident-proofs (PIP) | Bundles and logs cannot be forged post-hoc |

PIP code is **not** in the PF-Core TCB.

## Optional workflow

1. Emit PF-Core artifacts:

```bash
pf core emit-artifacts \
  --file pf-core/examples/valid/mcp_sidecar_observation.json \
  --out-dir ./artifacts
```

2. Package `trace.json`, `certificate.json`, and audit lines for organizational review.

3. When PIP is available at pinned SHA (`d5f3051b927f2f68cabac1a37c85d5113b9d77ad`):

```bash
cd ../post-incident-proofs
lake exe verify_bundle -- <path-to-bundle>
```

4. Treat PIP verification as an **organizational gate** (T5), not a Lean theorem.

## Assurance mapping

See `docs/pf-core/claim-boundary.md` for PF-Core T1–T5 ↔ spec 10-category map.
PIP `docs/ASSURANCE_MATRIX.md` rows for bundle integrity map to **Cryptographic assumption (T3-A2)** and **Replay validation (T4)** when used as a cross-check fixture tagged `must_fail_at: replay_validation`.

## Pin

| Repository | SHA |
|------------|-----|
| post-incident-proofs | `d5f3051b927f2f68cabac1a37c85d5113b9d77ad` |
