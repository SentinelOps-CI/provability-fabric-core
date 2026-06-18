# PF-Core Runtime Validator

Deterministic, pure bridge between runtime observations and PF-Core traces.

## Commands

Install from repository root:

```bash
pip install -e pf-core/validator
```

| Command | Purpose |
|---------|---------|
| `pf core schema-check --schemas pf-core/schemas` | Validate schema files |
| `pf core validate-event --file <event.json>` | Schema + hash + safety |
| `pf core validate-trace --file <trace.json>` | Schema + hash chain |
| `pf core compile-observation --file <obs.json>` | Compile to event JSON |
| `pf core check-trace --file <trace.json>` | Safety deciders on trace |
| `pf core check-trace --lean-check` | Optional Lean replay (`PFCore.Replay`) |
| `pf core emit-certificate --trace <trace.json>` | Emit certificate |
| `pf core audit-boundary --root .` | Audit trusted boundary |

## Typed errors

- `MissingRequiredField`
- `InvalidSchemaVersion`
- `InvalidDecision`
- `InvalidPrincipal`
- `InvalidAction`
- `InvalidHash`
- `UnsupportedEffect`
- `UnsupportedCapability`
- `AmbiguousMapping`
- `PolicyRefNotFound`
- `EvidenceRefNotFound`

## Hash chain

SHA-256 lowercase hex over canonical JSON (sorted keys) of the event object excluding `event_hash`. Genesis `previous_event_hash` is 64 ASCII `0` digits. Accepts `sha256:` URI prefix via `normalize_hash` (PCS v0.1.0 interop); internal storage remains hex64.

## Windows editable install

If `pip install -e pf-core/validator` fails on Windows, use:

```powershell
$env:PYTHONPATH = "pf-core/validator"
python -m pf_core.cli core schema-check --schemas pf-core/schemas
```

CI uses both editable install and `PYTHONPATH` fallback (`pf-core-trusted.ps1`).

## Design constraints

- No LLM or network calls in the compile/validate path
- Adapter capability catalog is static in `pf_core/compile.py` (organizational catalogs are T5)
