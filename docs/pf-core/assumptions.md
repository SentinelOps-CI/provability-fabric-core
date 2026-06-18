# PF-Core Assumptions

Each assumption has an ID for reference from certificates and audits.

## A1 — Schema conformance

Runtime observations and events are UTF-8 JSON objects that validate against the pinned PF-Core schemas before trusted processing.

## A2 — Hash chain integrity

Each event's `previous_event_hash` equals the `event_hash` of the prior event (or the genesis sentinel for the first event). Hashes are lowercase hex SHA-256 digests of the canonical JSON payload excluding the `event_hash` field. `trace_hash` is SHA-256 over the canonical trace object excluding `trace_hash`.

## A3 — Tenant labeling

`principal.tenant_id` and `resource.tenant_id` are assigned by an organizational identity system. PF-Core checks equality, not provenance of labels.

## A4 — Capability catalog

Capabilities referenced in actions exist in the adapter's capability table. Unknown capabilities cause `UnsupportedCapability` at validation time.

## A5 — Effect enumeration

Effects are drawn from the closed set: `file.read`, `file.write`, `network.egress`, `email.send`, `handoff.delegate`, `mcp.invoke`, `lab.release`. Extensions require schema version bump.

## A6 — Adapter determinism

`compile-observation` is pure: identical input yields identical trace events. No LLM or network calls in the trusted validator path.

## A7 — Handoff recipient

When a handoff is marked allowed, the recipient principal is modeled in the same tenant. Cross-tenant handoff is always denied unless explicitly extended in a future schema version.

## A8 — Policy references

`policy_ref` strings resolve to static policy bundles shipped with the adapter. Missing references yield `PolicyRefNotFound`.

## A9 — Evidence references

`evidence_ref` strings are opaque to PF-Core. Presence is checked; content is not validated (T5 organizational).

## A10 — Clock and ordering

Trace order matches emission order. PF-Core does not reorder events or prove temporal causality.
