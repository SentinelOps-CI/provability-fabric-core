# Phase 7 — provability-fabric Execution Checklist

Executable PR checklist for [SentinelOps-CI/provability-fabric](https://github.com/SentinelOps-CI/provability-fabric). Reference implementation and golden fixtures live in **provability-fabric-core** at tag `pf-core-v0.6.0`.

**Pin:** `a567c8dca015fac3890fddbb77dfd254caa720d8` (see [`extraction-log.md`](extraction-log.md))

## Prerequisites

- [ ] PF-Core tag `pf-core-v0.6.0` checked out or submodule pinned
- [ ] Read reference adapter: [`adapters/provability-fabric/mcp_sidecar/normalize.py`](../../adapters/provability-fabric/mcp_sidecar/normalize.py)
- [ ] Golden sidecar line: [`adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json`](../../adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json)

---

## PR-1: Native `runtime_observation.v1` emission

**Target:** `runtime/sidecar-watcher/` emits v1 directly (no normalize shim in production path).

### Field mapping

Use [`ecosystem-inventory.md`](ecosystem-inventory.md) § Sidecar audit line → runtime_observation.v1.

| Sidecar field | PF-Core v1 field |
|---------------|------------------|
| `request_id` | `observation_id` |
| `trace_id` | `trace_id` |
| `event_id` | `event_id` |
| `agent_id` | `principal.id` |
| `tenant` | `principal.tenant_id` |
| `tool_effect` | `action.effects[].kind` |
| `resource` | `action.reads[].uri` |
| `policy_decision` | `decision` |
| `prev_hash` | `previous_event_hash` |
| `policy_bundle` | `policy_ref` |
| `audit_bundle` | `evidence_ref` |
| `capability_hint` | `action.capability.id` |
| `runtime_ref` | `runtime_ref` |
| `timestamp` | `timestamp` |
| `reason` | `reason` |

Roles: resolve from `capability_catalog.json` `principal_roles_by_capability` (see normalize.py), not hardcoded.

### Acceptance commands

```bash
# From provability-fabric-core (reference)
PYTHONPATH=pf-core/validator pytest adapters/provability-fabric/tests/test_normalize.py -v

# After PR-1 in provability-fabric
python -m pf_core.cli core schema-check --schemas <path-to-pf-core/schemas>
# Sidecar unit test: emitted observation validates against runtime_observation.v1.schema.json
# Semantic parity with sidecar_audit_line.json golden
```

- [ ] Output validates against `pf-core/schemas/runtime_observation.v1.schema.json`
- [ ] Semantics match golden sidecar fixture (allowed MCP invoke)
- [ ] Denied and ambiguous cases covered (missing `capability_hint` → compile error)

---

## PR-2: PF-Core schema dependency

**Target:** Pin schemas from `pf-core-v0.6.0` via submodule or published package.

### Acceptance commands

```bash
pf core schema-check --schemas vendor/pf-core/schemas
# CI job on every push
```

- [ ] Submodule or package points at `pf-core-v0.6.0`
- [ ] CI fails on schema drift vs pinned tag

---

## PR-3: `pf core` CLI wrapper

**Target:** Thin wrapper delegates to installed `pf-core-validator`.

### Commands to wrap

```bash
pf core compile-observation --file <obs.json>
pf core check-trace --file <trace.json> [--lean-check]
pf core emit-certificate --trace <trace.json>
pf core emit-artifacts --file <obs.json> --out-dir ./bundle
```

### Acceptance

```bash
# Equivalent scenarios to provability-fabric-core gate
make pf-core-e2e   # or run e2e-replay-gate from pinned pf-core submodule
```

- [ ] `pyproject.toml` / `requirements.txt` pins validator version matching `pf-core-v0.6.0`
- [ ] Wrapper passes mcp-sidecar, file-read-allow/deny, handoff scenarios

---

## PR-4: Admission-controller audit line compatibility

**Target:** Admission-controller audit JSON compiles through PF-Core path.

### Acceptance

```bash
# admission audit JSON → compile-observation → validate-event
# Output must match normalize.py on golden fixtures (byte-level or canonical JSON parity)
diff <(normalize golden) <(native emitter golden)
```

- [ ] Fixture test in provability-fabric CI
- [ ] Field mapping documented in repo README
- [ ] No regression vs reference normalize.py on golden fixtures

---

## Reference files (provability-fabric-core)

| File | Purpose |
|------|---------|
| `adapters/provability-fabric/mcp_sidecar/normalize.py` | Reference normalizer |
| `adapters/provability-fabric/tests/test_normalize.py` | Adapter tests (32 vectors) |
| `adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json` | Allowed golden |
| `adapters/provability-fabric/tests/fixtures/sidecar_denied_audit_line.json` | Denied golden |
| `adapters/provability-fabric/tests/fixtures/sidecar_ambiguous_audit_line.json` | Missing capability_hint (compile error) |
| `pf-core/examples/valid/mcp_sidecar_observation.json` | Pre-built v1 observation |
| `pf-core/scripts/e2e-replay-gate.sh` | Full pipeline gate |

## Non-goals

- Do not import parent `Policy.lean` sorry-theorems into PF-Core TCB
- Policy alignment stays at golden vectors in `test_policy_correspondence.py`
