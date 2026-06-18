# PF-Core Release Checklist

Use this checklist when tagging a PF-Core release (`pf-core/VERSION` semver).

## Pre-release gates

- [ ] `make pf-core-trusted` passes locally
- [ ] `make pf-core-e2e` passes locally (or `powershell -File pf-core/scripts/e2e-replay-gate.ps1`)
- [ ] `adapters-ci` passes on `main` (pinned SHAs, catalog drift, policy correspondence)
- [ ] `docs/pf-core/acceptance.md` Phase 6 rows are PASS
- [ ] No `sorry` / `admit` / `axiom` / `unsafe` in `pf-core/lean/PFCore/`

## Version and schema policy

- [ ] Bump `pf-core/VERSION` (semver: MAJOR for breaking schema/kernel changes, MINOR for Phase features, PATCH for fixes)
- [ ] Update `pf-core/docs/schema-map.md` if schema status changes (v1-primary vs legacy)
- [ ] Regenerate fixtures if examples changed: `python pf-core/scripts/gen_fixtures.py`
- [ ] Update `docs/pf-core/extraction-log.md` pins if sibling repos change

## Tag and publish

- [ ] Git tag: `pf-core-vX.Y.Z` pointing at the release commit
- [ ] Release notes cite: e2e gate, policy correspondence vector count, Lean replay goldens
- [ ] `phase7-handoff.md` parent PR specs reference this tag and extraction-log SHAs

## Post-release

- [ ] Parent-repo handoff PRs (provability-fabric, pcs-core, post-incident-proofs) updated to depend on new tag
- [ ] `external-audit-brief.md` pin table updated if SHAs change

## Artifact bundle (adapter smoke)

```bash
pf core emit-artifacts --file pf-core/examples/valid/mcp_sidecar_observation.json --out-dir ./release-bundle
```

Expected files: `runtime_observation.json`, `event.json`, `trace.json`, `certificate.json`, `audit.jsonl`.
