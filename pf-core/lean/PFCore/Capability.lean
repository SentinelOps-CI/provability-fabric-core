import PFCore.Basic
import PFCore.Principal

/-!
# PFCore.Capability

Capability identifiers and principal capability grants.
-/

namespace PFCore

structure Capability where
  id : CapabilityId
  effectKind : String
  resourcePattern : String
  deriving Repr, DecidableEq, Inhabited

/-- Principal `p` is granted capability `c`. -/
def HasCapability (p : Principal) (c : Capability) : Prop :=
  Mem c.id (p.roles)

/-- Capability grant decider (capability id listed in principal roles). -/
def hasCapabilityD (p : Principal) (c : Capability) : Bool :=
  memD c.id p.roles

/--
## Plain-English meaning
`hasCapabilityD` returns true when the principal's roles include the capability id.

## Trusted use
Capability authorization decider.

## Does not imply
The capability catalog is complete for production tools.
-/
theorem hasCapabilityD_sound (p : Principal) (c : Capability) :
    hasCapabilityD p c = true ↔ HasCapability p c := by
  simp [hasCapabilityD, HasCapability, memD_sound]

end PFCore
