import PFCore.Basic

/-!
# PFCore.ClaimClassification

Minimal trusted classification for README and boundary claims (T1–T5).
-/

namespace PFCore

inductive ClaimCategory where
  | T1 | T2 | T3 | T4 | T5
  deriving Repr, DecidableEq, Inhabited

structure ClaimClassification where
  claim : String
  category : ClaimCategory
  deriving Repr, Inhabited

def traceSafeClaim : ClaimClassification :=
  { claim := "Trace safety decider matches Lean TraceSafe", category := .T1 }

end PFCore
