# provability-fabric adapter (untrusted reference)

Reference normalizers for provability-fabric runtime audit lines. Not part of PF-Core TCB.

## Sidecar audit line mapping

See `mcp_sidecar/normalize.py` — `normalize_sidecar_line()` maps sidecar-watcher fields to `pf-core.runtime_observation.v1`.

Golden fixtures: `tests/fixtures/sidecar_audit_line.json`, `sidecar_denied_audit_line.json`, `sidecar_ambiguous_audit_line.json`.

## Admission-controller audit line mapping

`normalize_admission_line()` maps admission-controller audit JSON to `pf-core.runtime_observation.v1`.

| Admission field | PF-Core v1 field |
|-----------------|------------------|
| `admission_id` / `request_uid` | `observation_id` |
| `trace_id` | `trace_id` |
| `event_id` | `event_id` |
| `principal_id` | `principal.id` |
| `namespace` | `principal.tenant_id` |
| `effect_kind` | `action.effects[].kind` |
| `target_resource` | `action.reads[].uri` |
| `verdict` | `decision` |
| `prev_hash` | `previous_event_hash` |
| `policy_bundle` | `policy_ref` |
| `evidence_bundle` | `evidence_ref` |
| `capability` | `action.capability.id` |
| `runtime_ref` | `runtime_ref` |
| `timestamp` | `timestamp` |
| `reason` | `reason` |

Golden fixture: `tests/fixtures/admission_audit_line.json`. Parity tests: `tests/test_admission_parity.py`.

## Tests

```bash
PYTHONPATH=pf-core/validator pytest adapters/provability-fabric/tests/ -v
```
