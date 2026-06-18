import PFCore.Basic

/-!
# PFCore.Assumption

Trusted assumption identifiers referenced by certificates and boundary docs.
-/

namespace PFCore

/-- Numbered assumptions from `docs/pf-core/assumptions.md`. -/
inductive AssumptionId where
  | A1 | A2 | A3 | A4 | A6 | A8
  deriving Repr, DecidableEq, Inhabited

structure Assumption where
  id : AssumptionId
  description : String
  deriving Repr, Inhabited

def assumptionA1 : Assumption :=
  { id := .A1, description := "Runtime emitters produce schema-valid JSON before trusted processing" }

def assumptionA2 : Assumption :=
  { id := .A2, description := "SHA-256 digests link previous_event_hash to prior event_hash" }

end PFCore
