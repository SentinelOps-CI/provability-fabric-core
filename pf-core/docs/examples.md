# PF-Core Examples

Fixtures live in `pf-core/examples/valid/` and `pf-core/examples/invalid/`. Regenerate with `python pf-core/scripts/gen_fixtures.py`.

## Scenarios

| Scenario | Valid | Invalid twin | Error | Stage |
|----------|-------|--------------|-------|-------|
| File read allowed | `file_read_allowed.json` | `file_read_allowed_wrong_tenant.json` | `UnsafeEvent` | decider_check |
| File read denied | `file_read_denied.json` | — | — | — |
| Network denied | `network_denied.json` | `network_allowed_without_cap.json` | `UnsafeEvent` | decider_check |
| Email send | `email_send.json` | `email_send_missing_capability.json` | `UnsafeEvent` | decider_check |
| Email denied | `email_send_denied.json` | — | — | — |
| Handoff trace (v1) | `handoff_trace.json` | `handoff_trace_unsafe.json` | `UnsafeTrace` | decider_check |
| Handoff document | `handoff.json` | `handoff_cross_tenant.json` | `UnsafeHandoff` | decider_check |
| Handoff expansion | — | `handoff_authority_expansion.json` | `UnsafeHandoff` | decider_check |
| Lab release gate | `lab_release_gate.json`, `lab_release_observation.json` | `lab_release_missing_policy.json` | `PolicyRefNotFound` | runtime_to_trace |
| Email observation | `email_send_observation.json` | `email_send_missing_capability_obs.json` | `UnsupportedCapability` / downgrade | runtime_to_trace |
| Network observation | `network_denied_observation.json` | `network_denied_obs.json` | `DecisionDowngraded` | compile_downgrade |
| Certificate | `certificate.json` | `certificate_overclaim.json` | `ForbiddenCertificateClaim` | certificate_overclaim |
| Claim classification | `claim_classification.json` | — | — | — |
| MCP sidecar | `mcp_sidecar_allowed.json`, `mcp_sidecar_observation.json` | `mcp_sidecar_denied.json`, `mcp_sidecar_ambiguous.json` | `AmbiguousMapping` | runtime_to_trace |
| Hash integrity | — | `file_read_bad_hash.json`, `trace_tampered_chain.json` | `InvalidHash` | decider_check |
| Schema version | — | `file_read_bad_schema_version.json` | `InvalidSchemaVersion` | schema_validation |
| Missing field | — | `obs_missing_required_field.json` | `MissingRequiredField` | runtime_to_trace |
| Unsupported capability | — | `obs_unsupported_capability.json` | `UnsupportedCapability` | runtime_to_trace |
| Unsupported effect | — | `obs_unsupported_effect.json` | `UnsupportedEffect` | runtime_to_trace |
| Evidence ref | — | `obs_evidence_not_found.json` | `EvidenceRefNotFound` | runtime_to_trace |
| Invalid principal | — | `event_invalid_principal.json` | `InvalidPrincipal` | action_semantics |
| Invalid action | — | `event_invalid_action.json` | `InvalidAction` | action_semantics |

## Emit full artifact set

```bash
pip install -e pf-core/validator
pf core emit-artifacts \
  --file pf-core/examples/valid/mcp_sidecar_observation.json \
  --out-dir ./artifacts
```

## Validate

```bash
make pf-core-trusted
```
