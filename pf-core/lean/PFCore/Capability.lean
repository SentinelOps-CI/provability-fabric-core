import PFCore.Basic
import PFCore.Principal
import PFCore.CapabilityCatalog

/-!
# PFCore.Capability

Principal authorization and capability subset predicates.
-/

namespace PFCore

/-- Delegated capability ids must be subset of source allowed ids. -/
def CapabilitySubset (xs ys : List Capability) : Prop :=
  ∀ c, c ∈ xs → c.id ∈ capabilityIds ys

def capabilitySubsetD (xs ys : List Capability) : Bool :=
  xs.all fun c => memD c.id (capabilityIds ys)

/--
## Plain-English meaning
`capabilitySubsetD` returns true when every delegated capability id appears in the allow-list.

## Trusted use
Handoff delegation subset checks.

## Does not imply
Recipient will honor delegated authority.
-/
theorem capabilitySubsetD_sound (xs ys : List Capability) :
    capabilitySubsetD xs ys = true ↔ CapabilitySubset xs ys := by
  simp [capabilitySubsetD, CapabilitySubset, capabilityIds, List.all_eq_true, memD_sound, Mem]

/-- Principal `p` may exercise capability `c` when its id is in the allowed set. -/
def HasCapability (p : Principal) (c : Capability) : Prop :=
  Mem c.id (allowedCapabilityIds p)

def hasCapabilityD (p : Principal) (c : Capability) : Bool :=
  memD c.id (allowedCapabilityIds p)

/--
## Plain-English meaning
`hasCapabilityD` returns true when the capability id is in the principal's allowed set.

## Trusted use
Capability authorization decider.

## Does not imply
The capability catalog is complete for production tools.
-/
theorem hasCapabilityD_sound (p : Principal) (c : Capability) :
    hasCapabilityD p c = true ↔ HasCapability p c := by
  simp [hasCapabilityD, HasCapability, memD_sound]

end PFCore
