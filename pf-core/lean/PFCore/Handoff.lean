import PFCore.Action
import PFCore.Principal
import PFCore.Capability

/-!
# PFCore.Handoff

Authority-preserving handoffs between principals in the same tenant.
-/

namespace PFCore

structure Handoff where
  fromPrincipal : Principal
  toPrincipal : Principal
  capability : Capability
  deriving Repr, DecidableEq, Inhabited

/-- Handoff is safe when both principals share tenant and both have capability. -/
def HandoffSafe (h : Handoff) : Prop :=
  h.fromPrincipal.tenantId = h.toPrincipal.tenantId ∧
  HasCapability h.fromPrincipal h.capability ∧
  HasCapability h.toPrincipal h.capability

def handoffSafeD (h : Handoff) : Bool :=
  (h.fromPrincipal.tenantId == h.toPrincipal.tenantId) &&
  hasCapabilityD h.fromPrincipal h.capability &&
  hasCapabilityD h.toPrincipal h.capability

/--
## Plain-English meaning
`handoffSafeD` matches tenant equality and bilateral capability grants.

## Trusted use
Handoff validation in trace compilation.

## Does not imply
Recipient will honor delegated authority.
-/
theorem handoffSafeD_sound (h : Handoff) :
    handoffSafeD h = true ↔ HandoffSafe h := by
  constructor <;> simp [handoffSafeD, HandoffSafe, beq_iff_eq, hasCapabilityD_sound,
    Bool.and_eq_true, and_assoc]

/--
## Plain-English meaning
Safe handoffs do not grant capabilities the recipient lacked.

## Trusted use
Authority preservation argument for handoff events.

## Does not imply
Recipient cannot misuse already-held capability.
-/
theorem handoff_does_not_expand_authority (h : Handoff) (hs : HandoffSafe h) :
    HasCapability h.toPrincipal h.capability := by
  rcases hs with ⟨_, _, htgt⟩
  exact htgt

end PFCore
