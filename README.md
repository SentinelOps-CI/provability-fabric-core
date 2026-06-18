# Provability Fabric Core

Minimal trusted kernel repository for **PF-Core** — proof-carrying agentic actions, contracted tool calls, handoffs, and trace-level safety preservation.

PF-Core is intentionally smaller than Provability Fabric: it is not a second runtime, CLI surface, or evidence standard.

## PF-Core documentation

- [PF-Core index](docs/pf-core/README.md)
- [Trusted kernel (Lean)](pf-core/lean/PFCore/)
- [Mission and boundary](docs/pf-core/mission.md)
- [Trusted boundary](docs/pf-core/trusted-boundary.md)
- [Claim boundary](docs/pf-core/claim-boundary.md)
- [Formal model](pf-core/docs/formal-model.md)
- [Examples](pf-core/docs/examples.md)
- [Theorem map](pf-core/docs/theorem-map.md)
- [Schema map](pf-core/docs/schema-map.md)
- [Runtime mapping](pf-core/docs/runtime-mapping.md)
- [Trusted rings](pf-core/docs/trusted-rings.md)
- [Validator](pf-core/validator/README.md)

## Verify locally

```bash
make pf-core-trusted
```

On Windows (PowerShell):

```powershell
powershell -File pf-core/scripts/pf-core-trusted.ps1
```

Requires [Lean 4](https://leanprover.github.io/) (via `elan`) and Python 3.10+.

## Layout

```
pf-core/
  lean/PFCore/     # Formal kernel (Lean 4)
  schemas/         # JSON schemas (pf-core.*.v0)
  examples/        # Valid/invalid fixtures
  validator/       # Runtime bridge + CLI
docs/pf-core/      # Boundary documentation
```
