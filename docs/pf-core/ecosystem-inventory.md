# PF-Core Ecosystem Inventory

PF-Core is the **trusted kernel** in provability-fabric-core. Parent SentinelOps repos supply untrusted emitters, reference policy, and evidence formats. Adapters under `adapters/` normalize parent artifacts into pinned PF-Core schemas.

## Pin table

| Repository | Pin | SHA |
|------------|-----|-----|
| provability-fabric-core | `main` | this repo |
| provability-fabric | `main` | `a567c8dca015fac3890fddbb77dfd254caa720d8` |
| pcs-core | tag `v0.1.0` | `280bbea4bf3bf3e45004b6254bc72b603030f179` |
| post-incident-proofs | `main` | `d5f3051b927f2f68cabac1a37c85d5113b9d77ad` |

File-by-file classification: [`extraction-log.md`](extraction-log.md).

## Soundness split

| Component | Zone | Connection |
|-----------|------|------------|
| PF-Core Lean kernel | Trusted | `pf-core/lean/PFCore/` |
| PF-Core validator | Trusted | `pf-core/validator/` |
| `adapters/` | Untrusted | Normalizers only; not in TCB |
| Provability Fabric runtime | Untrusted | Sidecar audit lines → `runtime_observation.v1` |
| PCS emitters | Untrusted | Hash rules + LabTrust fixtures |
| post-incident-proofs | Untrusted | Forensic bundle cross-check |
| Parent `Policy.lean` | Reference | Catalog export; contains `sorry` |

## Adapter paths (Phase 5)

| Adapter | Input | Output | Tests |
|---------|-------|--------|-------|
| `adapters/provability-fabric/mcp_sidecar/normalize.py` | Sidecar audit JSON line | `runtime_observation.v1` | `adapters/provability-fabric/tests/` |
| `adapters/provability-fabric/export_catalog.py` | Pinned catalog | `fixtures/capability_catalog.json` | manual + CI export step |
| `adapters/pcs/normalize_release.py` | `fixtures/labtrust-release/` | `pcs_replay_trace.json` | `adapters/pcs/tests/` |
| `adapters/post_incident_proofs/` | PF-Core emit set | PIP `verify_bundle` (optional) | documented workflow |

## Sidecar audit line → runtime_observation.v1

Field names from provability-fabric `runtime/sidecar-watcher` patterns:

| Sidecar field | PF-Core v1 field |
|---------------|------------------|
| `request_id` | `observation_id` |
| `trace_id` | `trace_id` |
| `event_id` | `event_id` |
| `agent_id` | `principal.id` (nested) |
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

Example:

```bash
python adapters/provability-fabric/mcp_sidecar/normalize.py  # via tests
pf core compile-observation --file <normalized-observation.json>
pf core check-trace --file pf-core/examples/valid/pcs_replay_trace.json
```

## PCS LabTrust replay

pcs-core `examples/labtrust/` fixtures vendored at `adapters/pcs/fixtures/labtrust-release/`.
Normalized golden trace: `pf-core/examples/valid/pcs_replay_trace.json`.

## Policy catalog

See [`policy-extraction-map.md`](policy-extraction-map.md). Lean authoritative catalog: `CapabilityCatalog.lean`.

## Two-layer forensics

- **PF-Core:** authorization trace safety (T1/T4)
- **post-incident-proofs:** bundle/log integrity (organizational T5 gate)

See `adapters/post_incident_proofs/README.md`.
