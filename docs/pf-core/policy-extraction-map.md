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
pf-core/lean/PFCore/CapabilityCatalog.lean  (proof authority)
        ↓ manual mirror + drift CI
adapters/provability-fabric/export_catalog.py
        ↓ load_capability_catalog() (optional merge)
adapters/provability-fabric/fixtures/capability_catalog.json
        ↓
pf-core/validator/pf_core/compile.py CAPABILITY_CATALOG
```

Optional sibling read: when `provability-fabric/config/schemas/` is present (CI clone), export verifies capability id set matches Lean before writing JSON. Parent does not ship a standalone capability list at pin `a567c8d`.

**Documented gaps:** `LogSpend` and `LogAction` (parent Policy.lean) have no PF-Core capabilities; golden vectors mark these as `documented_gap` (parent allow, PF deny). See `documented_policy_gaps` in exported catalog JSON.

## Cannot enter TCB

- Non-interference proofs (`sorry` in parent Policy.lean)
- Label lattice / declassification rules
- Solver adapters and runtime sidecar enforcement logic
- Full MCP server semantics

## Acceptance

Catalog pins traceable to provability-fabric commit SHA; PF-Core kernel remains independently auditable with zero `sorry`.

## Correspondence test matrix (extractable fragment)

Executable golden vectors in `adapters/provability-fabric/tests/fixtures/policy_correspondence_vectors.json` (23 vectors, CI via `test_policy_correspondence.py`).

| Parent tool / case | Parent `permitD` input | PF-Core decider | Expected alignment |
|--------------------|------------------------|-----------------|-------------------|
| `FileRead` + `file_user` | role in tool allowlist | `actionAllowedD` + tenant | allow |
| `FileRead` + wrong tenant | role OK, tenant mismatch | `ActionWithinTenant` | deny (PF stricter) |
| `NetworkCall` + `network_user` | role allowlist | `cap:network` | allow |
| `SendEmail` + `email_user` | role allowlist | `cap:email-send` | allow |
| `FileWrite` + `file_writer` | role allowlist | `cap:file-write` via `file_admin` | allow |
| `Custom` (MCP) + admin | role allowlist | `cap:mcp-invoke` | allow |
| Lab release + `lab_operator` | admin maps to operator | `cap:lab-release` | allow |
| Handoff subset | N/A (no `permitD`) | `handoffSafeD` | subset of source caps |
| Handoff expansion | N/A | delegate `cap:network` from agent | deny |
| Cross-tenant handoff | N/A | tenant mismatch | deny |
| `LogSpend` / `LogAction` | parent allow | PF no matching cap | **documented gap** (deny in PF) |

**Catalog sync:** `export_catalog.py` output must match `CapabilityCatalog.lean` (`test_catalog_export_matches_lean`).

**Explicit non-goals:** Label lattices, non-interference, completeness of `permitD` — remain reference-only per extraction log.
