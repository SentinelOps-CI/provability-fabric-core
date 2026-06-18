import PFCore.Action
import PFCore.Decision
import PFCore.EventKind
import PFCore.Handoff

/-!
# PFCore.Event

Events record a discriminated kind (action or handoff), decision, audit metadata, and hash-chain fields.
-/

namespace PFCore

structure Event where
  eventId : EventId
  kind : EventKind
  decision : Decision
  reason : String
  evidenceRef : String
  prevHash : Hash
  hash : Hash
  deriving Repr, DecidableEq, Inhabited

/-- Event is safe when allowed decisions match kind-level authorization. -/
def EventSafe (ev : Event) : Prop :=
  match ev.decision with
  | .allowed => EventKindSafe ev.kind
  | .denied => True

def eventSafeD (ev : Event) : Bool :=
  match ev.decision with
  | .allowed => eventKindSafeD ev.kind
  | .denied => true

/--
## Plain-English meaning
`eventSafeD` is true when allowed events have safe action or handoff payloads; denied events are structurally safe.

## Trusted use
Per-event safety check in trace validation.

## Does not imply
Denied events were blocked at runtime.
-/
theorem eventSafeD_sound (ev : Event) :
    eventSafeD ev = true ↔ EventSafe ev := by
  cases h : ev.decision
  · simp [eventSafeD, EventSafe, h, eventKindSafeD_sound]
  · simp [eventSafeD, EventSafe, h, iff_true]

/-- Packaging witness for compiling observations into events (not trace membership). -/
inductive EventWitness where
  | allowed (k : EventKind) : EventWitness
  | denied (k : EventKind) : EventWitness

def EventWitness.toEvent (ei : EventWitness) (eventId reason evidenceRef prevHash hash : String) : Event :=
  match ei with
  | .allowed k =>
    { eventId, kind := k, decision := .allowed, reason, evidenceRef, prevHash, hash }
  | .denied k =>
    { eventId, kind := k, decision := .denied, reason, evidenceRef, prevHash, hash }

/--
## Plain-English meaning
Denied decisions are not classified as allowed.

## Trusted use
Distinguishing audit denials from executions.

## Does not imply
OS-level enforcement of denials.
-/
theorem denied_event_not_executed (ev : Event) (h : ev.decision = Decision.denied) :
    ¬ DecisionAllowed ev.decision := by
  simp [DecisionAllowed, h]

/--
## Plain-English meaning
Allowed action events in safe traces have authorized actions.

## Trusted use
Linking decision labels to action authorization proofs.

## Does not imply
The action was executed successfully externally.
-/
theorem allowed_event_has_allowed_action (ev : Event) (a : Action)
    (hk : ev.kind = EventKind.action a) (h : ev.decision = Decision.allowed) (hs : EventSafe ev) :
    ActionAllowed a := by
  simp [EventSafe, h, hk] at hs
  simpa [EventKindSafe, hk] using hs

/--
## Plain-English meaning
Allowed handoff events in safe traces satisfy handoff safety.

## Trusted use
Linking trace safety to `handoff_does_not_expand_authority`.

## Does not imply
Recipient will honor delegated authority.
-/
theorem allowed_handoff_event_is_safe (ev : Event) (h : Handoff)
    (hk : ev.kind = EventKind.handoff h) (hd : ev.decision = Decision.allowed) (hs : EventSafe ev) :
    HandoffSafe h := by
  simp [EventSafe, hd, hk] at hs
  simpa [EventKindSafe, hk] using hs

end PFCore
