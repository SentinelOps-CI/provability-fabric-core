import PFCore.Basic

/-!
# PFCore.Decision

Runtime allow/deny decisions on actions.
-/

namespace PFCore

inductive Decision where
  | allowed : Decision
  | denied : Decision
  deriving Repr, DecidableEq, Inhabited

def decisionAllowedD (d : Decision) : Bool :=
  match d with | .allowed => true | .denied => false

def DecisionAllowed (d : Decision) : Prop :=
  d = Decision.allowed

/--
## Plain-English meaning
`decisionAllowedD` is true only for allowed decisions.

## Trusted use
Classifying decision labels in event analysis.

## Does not imply
The action was executed because the decision was allowed.
-/
theorem decisionAllowedD_sound (d : Decision) :
    decisionAllowedD d = true ↔ DecisionAllowed d := by
  cases d <;> simp [decisionAllowedD, DecisionAllowed]

end PFCore
