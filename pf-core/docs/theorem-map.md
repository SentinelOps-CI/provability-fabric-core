# PF-Core Theorem Map

One-page index of proved theorems, what they justify, and what they do not.

## Contract algebra (`Contract.lean`)

| Theorem | Justifies | Does not imply |
|---------|-----------|----------------|
| `satisfies_contract_of_seq` | Composed per-event obligations decompose | Temporal ordering beyond list structure |
| `seq_contract_satisfaction_left` | Left policy stage holds on satisfied composed traces | Left stage ran first at runtime |
| `seq_contract_satisfaction_right` | Right policy stage holds on satisfied composed traces | Full runtime policy coverage |
| `seq_invariant_preservation` | `seq` invariant is conjunction of component invariants | Invariants hold without satisfaction |
| `trace_satisfies_trace_safe_contract` | `traceSafeContract` aligns with `TraceSafe` | Hash-chain integrity |
| `effect_pair_seq_target` / `effect_pair_seq_required` | Adapter effect-pair chaining projections | Prerequisite effects observed |

## Stateful extension (`StatefulContract.lean`)

| Theorem | Justifies | Does not imply |
|---------|-----------|----------------|
| `stateful_extends_contract` | Stateful layer embeds base contract fields | Runtime state machine enforcement |
| `stateful_satisfies_components` | Stateful events decompose under `seq` | Persisted state tracking |

## Trace and event (`Trace.lean`, `Event.lean`)

| Theorem | Justifies | Does not imply |
|---------|-----------|----------------|
| `trace_safe_empty` / `trace_safe_cons` | Inductive trace safety reasoning | External deployment safety |
| `traceSafeD_sound` | Runtime `check-trace` decider soundness | JSON parsing correctness |
| `eventSafeD_sound` | Per-event decider soundness | OS-level denial enforcement |
| `eventKindSafeD_sound` | Action/handoff kind decider soundness | Handoff honored at runtime |
| `denied_event_not_executed` | Denied decisions are not "allowed" | Host blocked the action |
| `allowed_event_has_allowed_action` | Allowed action events imply authorization | Successful external execution |
| `allowed_handoff_event_is_safe` | Allowed handoff events satisfy `HandoffSafe` | Recipient honors delegation |
| `every_allowed_event_in_safe_trace_is_allowed` | Safe traces yield `EventKindSafe` payloads | Execution in external world |
| `every_allowed_handoff_in_safe_trace_preserves_authority` | Handoff trace integration with `handoff_does_not_expand_authority` | Recipient misuse prevention |

## Composition (`Composition.lean`)

| Theorem | Justifies | Does not imply |
|---------|-----------|----------------|
| `trace_safe_append` | Safe sub-traces compose | Hash-chain across segments |
| `traceSafeD_append` | Incremental decider on append | Decider completeness alone |
| `trace_satisfies_contract_append` | Contract satisfaction on append | Incremental contract checking without replay |

## Invariants (`Invariant.lean`)

| Theorem | Justifies | Does not imply |
|---------|-----------|----------------|
| `trace_safe_implies_allowed_authorized` | Allowed events in safe traces are authorized | Denied events were blocked |
| `trace_safe_contract_invariant` | Standard contract invariant implies `TraceSafe` | Arbitrary contract invariants imply safety |
| `trace_satisfies_implies_invariant` | Satisfying `traceSafeContract` yields invariant | Custom contracts imply safety |

## Handoff (`Handoff.lean`)

| Theorem | Justifies | Does not imply |
|---------|-----------|----------------|
| `handoffSafeD_sound` | Handoff decider soundness | Recipient honors delegation |
| `handoff_does_not_expand_authority` | Safe handoff requires recipient already has capability | Recipient cannot misuse capability |

## Soundness hub (`Soundness.lean`)

Aggregates decider soundness theorems for principals, capabilities, effects, actions, events, traces, and handoffs. Does not prove adapter catalogs, hash chains, or external honesty.

## Certificate (`Certificate.lean`)

| Theorem | Justifies | Does not imply |
|---------|-----------|----------------|
| `certificate_safe_sound` | Certificate `safe` bit matches `TraceSafe` | Downstream acceptance without verifier policy |
