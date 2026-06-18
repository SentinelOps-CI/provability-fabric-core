# PF-Core Policy Extraction Map (Reference Only)

Maps provability-fabric `Policy.lean` predicates to PF-Core trusted kernel shapes.
Parent Policy.lean is **reference-only** (contains `sorry` for non-interference); nothing imports into `pf-core/lean/` without full no-sorry review.

**Pin:** provability-fabric @ `a567c8dca015fac3890fddbb77dfd254caa720d8`
**Vendored copy:** `adapters/provability-fabric/reference/Policy.lean`

## Predicate mapping

| Parent (Policy.lean) | PF-Core trusted | Notes |
|----------------------|-----------------|-------|
| `Permit p a` | `ActionAllowed a` | Same-tenant resource + capability membership |
| `permitD p a` | `actionAllowedD a` | Decidable mirror |
| `Principal.roles` | `Principal.roles` | RBAC role names |
| `Principal.org` | `Principal.tenantId` | Tenant isolation |
| Tool / effect enumeration | `EffectKind` + catalog | Pinned in `CapabilityCatalog.lean` |
| Label lattice / NI | — | **Out of scope**; parent theorems with `sorry` |

## Catalog export path

```
provability-fabric/config/schemas/  (reference)
        ↓ export_catalog.py (untrusted)
adapters/provability-fabric/fixtures/capability_catalog.json
        ↓ load_capability_catalog() (optional merge)
pf-core/validator/pf_core/compile.py CAPABILITY_CATALOG
        ↓ mirrors
pf-core/lean/PFCore/CapabilityCatalog.lean catalogCapabilities
```

## Cannot enter TCB

- Non-interference proofs (`sorry` in parent Policy.lean)
- Label lattice / declassification rules
- Solver adapters and runtime sidecar enforcement logic
- Full MCP server semantics

## Acceptance

Catalog pins traceable to provability-fabric commit SHA; PF-Core kernel remains independently auditable with zero `sorry`.
