import PFCore.Basic

/-!
# PFCore.Assumption

Trusted assumption identifiers referenced by certificates and boundary docs.
Full prose in `docs/pf-core/assumptions.md` (A1–A10).
-/

namespace PFCore

/-- Numbered assumptions from `docs/pf-core/assumptions.md`. -/
inductive AssumptionId where
  | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9 | A10
  deriving Repr, DecidableEq, Inhabited

structure Assumption where
  id : AssumptionId
  description : String
  deriving Repr, Inhabited

def assumptionA1 : Assumption :=
  { id := .A1, description := "Runtime emitters produce schema-valid JSON before trusted processing" }

def assumptionA2 : Assumption :=
  { id := .A2, description := "SHA-256 digests link previous_event_hash to prior event_hash" }

def assumptionA3 : Assumption :=
  { id := .A3, description := "Tenant labels are compared for equality, not provenance" }

def assumptionA4 : Assumption :=
  { id := .A4, description := "Capabilities exist in the adapter catalog at validation time" }

def assumptionA5 : Assumption :=
  { id := .A5, description := "Effects are drawn from the closed enumeration in Effect.lean" }

def assumptionA6 : Assumption :=
  { id := .A6, description := "compile-observation is pure and deterministic" }

def assumptionA7 : Assumption :=
  { id := .A7, description := "Allowed handoff recipients are modeled in the same tenant" }

def assumptionA8 : Assumption :=
  { id := .A8, description := "policy_ref resolves to static policy bundles shipped with the adapter" }

def assumptionA9 : Assumption :=
  { id := .A9, description := "evidence_ref presence is checked; content is not validated" }

def assumptionA10 : Assumption :=
  { id := .A10, description := "Trace order matches emission order; no temporal causality proof" }

def allAssumptions : List Assumption :=
  [assumptionA1, assumptionA2, assumptionA3, assumptionA4, assumptionA5,
   assumptionA6, assumptionA7, assumptionA8, assumptionA9, assumptionA10]

end PFCore
