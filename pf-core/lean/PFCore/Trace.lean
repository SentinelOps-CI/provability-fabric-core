import PFCore.Event
import PFCore.Action
import PFCore.Handoff

/-!
# PFCore.Trace

Traces are lists of events; safety is universal quantification.
-/

namespace PFCore

abbrev Trace := List Event

def TraceSafe (tr : Trace) : Prop :=
  ∀ ev ∈ tr, EventSafe ev

def traceSafeD (tr : Trace) : Bool :=
  tr.all eventSafeD

/--
## Plain-English meaning
The empty trace is safe because it contains no failing events.

## Trusted use
Base case for trace safety induction and `traceSafeD` on `[]`.

## Does not imply
Any runtime or deployment safety property.
-/
theorem trace_safe_empty : TraceSafe [] := by
  intro ev h
  cases h

/--
## Plain-English meaning
A trace is safe if its head event is safe and its tail is safe.

## Trusted use
Inductive reasoning over emitted event sequences.

## Does not imply
Hash-chain validity or temporal ordering beyond list structure.
-/
theorem trace_safe_cons (ev : Event) (tr : Trace)
    (hev : EventSafe ev) (htr : TraceSafe tr) :
    TraceSafe (ev :: tr) := by
  intro e he
  simp [List.mem_cons] at he
  rcases he with rfl | he
  · exact hev
  · exact htr e he

/--
## Plain-English meaning
`traceSafeD` returns true exactly when every event in the trace is safe.

## Trusted use
Runtime `check-trace` may rely on this for decidable safety checking.

## Does not imply
JSON parsing correctness or external enforcement of denied events.
-/
theorem traceSafeD_sound (tr : Trace) :
    traceSafeD tr = true ↔ TraceSafe tr := by
  simp [traceSafeD, TraceSafe, List.all_eq_true, eventSafeD_sound]

/--
## Plain-English meaning
In a safe trace, every allowed event has a safe action or handoff payload.

## Trusted use
Linking trace-level safety to per-kind authorization.

## Does not imply
That allowed events were actually executed in the external world.
-/
theorem every_allowed_event_in_safe_trace_is_allowed (tr : Trace) (ht : TraceSafe tr)
    (ev : Event) (hin : ev ∈ tr) (hd : ev.decision = Decision.allowed) :
    EventKindSafe ev.kind := by
  have hev : EventSafe ev := ht ev hin
  simpa [EventSafe, hd] using hev

/--
## Plain-English meaning
In a safe trace, every allowed action event has an allowed action.

## Trusted use
Backward-compatible action-only corollary for contract invariants.

## Does not imply
Handoff events are action-authorized.
-/
theorem every_allowed_action_event_in_safe_trace_is_allowed (tr : Trace) (ht : TraceSafe tr)
    (ev : Event) (a : Action) (hin : ev ∈ tr) (hd : ev.decision = Decision.allowed)
    (hk : ev.kind = EventKind.action a) :
    ActionAllowed a :=
  allowed_event_has_allowed_action ev a hk hd (ht ev hin)

/--
## Plain-English meaning
In a safe trace, every allowed handoff event preserves recipient authority bounds.

## Trusted use
Integrates `handoff_does_not_expand_authority` with trace safety.

## Does not imply
Recipient cannot misuse already-held capability.
-/
theorem every_allowed_handoff_in_safe_trace_preserves_authority (tr : Trace) (ht : TraceSafe tr)
    (ev : Event) (h : Handoff) (hin : ev ∈ tr) (hd : ev.decision = Decision.allowed)
    (hk : ev.kind = EventKind.handoff h) :
    HandoffSafe h ∧
    HasCapability h.toPrincipal h.capability := by
  have hs := allowed_handoff_event_is_safe ev h hk hd (ht ev hin)
  exact ⟨hs, handoff_does_not_expand_authority h hs⟩

end PFCore
