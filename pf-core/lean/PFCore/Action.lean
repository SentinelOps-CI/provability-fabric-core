import PFCore.Effect
import PFCore.Capability
import PFCore.Principal

/-!
# PFCore.Action

Actions bundle principal, capability, resource, and effect.
-/

namespace PFCore

structure Action where
  principal : Principal
  capability : Capability
  resource : Resource
  effect : Effect
  deriving Repr, DecidableEq, Inhabited

/-- Action is within tenant and effect-allowed for its capability. -/
def ActionWithinTenant (a : Action) : Prop :=
  SameTenant a.principal a.resource

def actionWithinTenantD (a : Action) : Bool :=
  sameTenantD a.principal a.resource

/--
## Plain-English meaning
`actionWithinTenantD` matches tenant containment for the action.

## Trusted use
Tenant isolation checks in runtime validation.

## Does not imply
Correctness of tenant labels in the identity system.
-/
theorem actionWithinTenantD_sound (a : Action) :
    actionWithinTenantD a = true ↔ ActionWithinTenant a := by
  simp [actionWithinTenantD, ActionWithinTenant, sameTenantD_sound]

/-- Full action authorization: capability, tenant, and effect. -/
def ActionAllowed (a : Action) : Prop :=
  HasCapability a.principal a.capability ∧
  ActionWithinTenant a ∧
  EffectAllowed a.capability a.effect

def actionAllowedD (a : Action) : Bool :=
  hasCapabilityD a.principal a.capability &&
  actionWithinTenantD a &&
  effectAllowedD a.capability a.effect

/--
## Plain-English meaning
`actionAllowedD` is true exactly when capability, tenant, and effect checks pass.

## Trusted use
Core authorization decider for allowed events.

## Does not imply
External systems enforced the denial of unauthorized actions.
-/
theorem actionAllowedD_sound (a : Action) :
    actionAllowedD a = true ↔ ActionAllowed a := by
  constructor <;> simp [actionAllowedD, ActionAllowed, hasCapabilityD_sound,
    actionWithinTenantD_sound, effectAllowedD_sound, Bool.and_eq_true, and_assoc]

end PFCore
