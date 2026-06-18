import PFCore.Action
import PFCore.Principal
import PFCore.Capability

/-!
# PFCore.Handoff

Authority-preserving handoffs: delegated capabilities must be a subset of source authority.
-/

namespace PFCore

structure Handoff where
  fromPrincipal : Principal
  toPrincipal : Principal
  delegatedCapabilities : List Capability
  reason : String
  evidenceRef : String
  deriving Repr, DecidableEq, Inhabited

def HandoffSafe (h : Handoff) : Prop :=
  h.fromPrincipal.tenantId = h.toPrincipal.tenantId ∧
  ∀ c, c ∈ h.delegatedCapabilities → Mem c.id (allowedCapabilityIds h.fromPrincipal)

def handoffSafeD (h : Handoff) : Bool :=
  (h.fromPrincipal.tenantId == h.toPrincipal.tenantId) &&
  h.delegatedCapabilities.all fun c => memD c.id (allowedCapabilityIds h.fromPrincipal)

/--
## Plain-English meaning
`handoffSafeD` matches tenant equality and delegated-capability subset against source authority.

## Trusted use
Handoff validation in trace compilation.

## Does not imply
Recipient will honor delegated authority.
-/
theorem handoffSafeD_sound (h : Handoff) :
    handoffSafeD h = true ↔ HandoffSafe h := by
  constructor <;> simp [handoffSafeD, HandoffSafe, beq_iff_eq, List.all_eq_true, memD_sound,
    Bool.and_eq_true, and_assoc]

/--
## Plain-English meaning
Safe handoffs delegate only capabilities the source principal was already allowed to exercise.

## Trusted use
Authority preservation argument for handoff events.

## Does not imply
Recipient cannot misuse already-held capability.
-/
theorem handoff_does_not_expand_authority (h : Handoff) (hs : HandoffSafe h) (c : Capability)
    (hc : c ∈ h.delegatedCapabilities) :
    Mem c.id (allowedCapabilityIds h.fromPrincipal) :=
  hs.2 c hc

end PFCore
