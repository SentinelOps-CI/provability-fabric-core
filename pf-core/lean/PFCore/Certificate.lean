import PFCore.Trace

/-!
# PFCore.Certificate

Certificate structure summarizing a safe trace.
-/

namespace PFCore

structure Certificate where
  schemaVersion : String
  traceHash : Hash
  eventCount : Nat
  safe : Bool
  deriving Repr, DecidableEq, Inhabited

def genesisHash : Hash :=
  String.mk (List.replicate 64 '0')

def certificateFromTrace (tr : Trace) (traceHash : Hash) : Certificate :=
  { schemaVersion := "pf-core.certificate.v0"
    traceHash := traceHash
    eventCount := tr.length
    safe := traceSafeD tr }

/--
## Plain-English meaning
Certificate `safe` flag matches trace safety decider.

## Trusted use
`emit-certificate` output semantics.

## Does not imply
Downstream verifiers accept the certificate without their own policy.
-/
theorem certificate_safe_sound (tr : Trace) (traceHash : Hash)
    (c : Certificate) (hc : c = certificateFromTrace tr traceHash) :
    c.safe = true ↔ TraceSafe tr := by
  subst hc
  simp [certificateFromTrace, traceSafeD_sound]

end PFCore
