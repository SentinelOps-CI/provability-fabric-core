# PF-Core Certificate Semantics

## Soundness split

- **Lean proves:** `certificate_safe_sound` — `safe` bit matches `TraceSafe`
- **Runtime validates:** schema, hash chain, decider replay
- **Assumptions:** A1 (schema), A2 (hash chain), A6 (deterministic compile)

## Structure

Certificates follow `pf-core.certificate.v0`:

| Field | Meaning |
|-------|---------|
| `certificate_id` | Unique certificate identifier |
| `trace_hash` | SHA-256 of canonical trace payload (excluding `trace_hash`) |
| `contract_hash` | SHA-256 of canonical contract JSON |
| `proof_ref` | Lean proof artifact path |
| `checker` / `checker_version` | Checker identity (e.g. `lean4`) |
| `claim_class` | T1–T5 classification label |
| `assumptions` | Assumption IDs (e.g. `A1`, `A2`) |
| `event_count` | Number of events in trace |
| `safe` | Result of `trace_safe` decider |

## Hash chain (events)

1. Genesis `previous_event_hash`: 64 ASCII `0` characters.
2. Canonical payload: event object with `event_hash` field removed, JSON serialized with sorted keys and minimal separators (PCS-style).
3. `event_hash = sha256(payload)` as lowercase hex.
4. `previous_event_hash` of event *n* must equal `event_hash` of event *n-1*.
5. `trace_hash = sha256(canonical_json(trace \\ {trace_hash}))`.

## Emission

```bash
pf core emit-certificate \
  --trace pf-core/examples/valid/file_read_allowed_trace.json \
  --contract pf-core/schemas/contract.schema.json

pf core emit-artifacts \
  --file pf-core/examples/valid/mcp_sidecar_observation.json \
  --out-dir /tmp/pf-core-artifacts
```

## Trusted claims (T1 + T4)

- If `safe` is true and deciders match Lean, every allowed event has `ActionAllowed` action.
- Hash chain validity is T4 (validator), not Lean-proved.

## Non-claims

- Certificate does not prove external execution or PCS bundle validity.
- Forbidden certificate text: "This agent is safe", "This tool is secure", "This workflow is verified".
