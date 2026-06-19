# Phase 7 PR Spec — provability-fabric PR-2/3: Schema dep + CLI wrapper

**Repo:** provability-fabric  
**PF-Core tag:** `pf-core-v0.6.0`

## PR-2: Schema dependency

- Submodule or package at `pf-core-v0.6.0`
- CI `schema-check` on every push

```bash
pf core schema-check --schemas vendor/pf-core/schemas
```

## PR-3: CLI wrapper

Thin wrapper over `pf-core-validator`:

- `compile-observation`, `check-trace`, `emit-certificate`, `emit-artifacts`, `verify-bundle`

## Acceptance

- Validator version pin matches PF-Core release
- E2e scenarios equivalent to `make pf-core-e2e` when run from provability-fabric with pinned submodule
