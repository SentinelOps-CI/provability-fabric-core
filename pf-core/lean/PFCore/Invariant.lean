import PFCore.Trace
import PFCore.Contract

/-!
# PFCore.Invariant

Trace invariants: allowed decisions imply safe actions; contract invariants link to safety.
-/

namespace PFCore

/-- Invariant: every allowed event in trace has safe action or handoff payload. -/
def AllowedEventsAuthorized (tr : Trace) : Prop :=
  ∀ ev ∈ tr, ev.decision = Decision.allowed → EventKindSafe ev.kind

/--
## Plain-English meaning
Trace safety implies every allowed event has a safe action or handoff payload.

## Trusted use
Audit invariants over agent traces.

## Does not imply
Denied events were blocked externally.
-/
theorem trace_safe_implies_allowed_authorized (tr : Trace) (h : TraceSafe tr) :
    AllowedEventsAuthorized tr :=
  fun ev hin hd => every_allowed_event_in_safe_trace_is_allowed tr h ev hin hd

/--
## Plain-English meaning
When `traceSafeContract` invariant holds, the trace is safe.

## Trusted use
Connecting contract invariants to `TraceSafe` for standard policies.

## Does not imply
Custom contracts with weaker invariants imply safety.
-/
theorem trace_safe_contract_invariant (tr : Trace) (h : traceSafeContract.invariant tr) :
    TraceSafe tr := by
  simpa [traceSafeContract] using h

/--
## Plain-English meaning
Trace satisfying `traceSafeContract` implies its invariant.

## Trusted use
Bidirectional link between contract satisfaction and safety invariant.

## Does not imply
Arbitrary contract invariants imply `TraceSafe`.
-/
theorem trace_satisfies_implies_invariant (tr : Trace)
    (h : TraceSatisfiesContract traceSafeContract tr) :
    traceSafeContract.invariant tr :=
  (trace_satisfies_trace_safe_contract tr).mp h

end PFCore
