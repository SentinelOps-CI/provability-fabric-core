import PFCore.Action
import PFCore.Handoff

/-!
# PFCore.EventKind

Discriminated event payload: action execution or authority handoff.
-/

namespace PFCore

inductive EventKind where
  | action (a : Action) : EventKind
  | handoff (h : Handoff) : EventKind
  deriving Repr, DecidableEq, Inhabited

/-- Event kind is safe when its action or handoff payload passes authorization. -/
def EventKindSafe (k : EventKind) : Prop :=
  match k with
  | .action a => ActionAllowed a
  | .handoff h => HandoffSafe h

def eventKindSafeD (k : EventKind) : Bool :=
  match k with
  | .action a => actionAllowedD a
  | .handoff h => handoffSafeD h

/--
## Plain-English meaning
`eventKindSafeD` matches action authorization or handoff safety for the payload.

## Trusted use
Per-event kind check inside trace validation.

## Does not imply
External systems enforced denials or honored handoffs.
-/
theorem eventKindSafeD_sound (k : EventKind) :
    eventKindSafeD k = true ↔ EventKindSafe k := by
  cases k <;> simp [eventKindSafeD, EventKindSafe, actionAllowedD_sound, handoffSafeD_sound,
    Bool.and_eq_true, and_assoc]

end PFCore
