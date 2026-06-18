import PFCore.Effect
import PFCore.Capability
import PFCore.Principal

/-!
# PFCore.Action

Actions bundle principal, capability, and multi-effect read/write resource lists (v1).
-/

namespace PFCore

abbrev ActionId := String

structure Action where
  id : ActionId
  principal : Principal
  capability : Capability
  effects : List Effect
  reads : List Resource
  writes : List Resource
  deriving Repr, DecidableEq, Inhabited

/-- First effect in the action list (legacy v0 compatibility). -/
def Action.primaryEffect (a : Action) : Effect :=
  match a.effects with
  | e :: _ => e
  | [] => { kind := .fileRead }

/-- First read resource (legacy v0 compatibility). -/
def Action.primaryResource (a : Action) : Resource :=
  match a.reads with
  | r :: _ => r
  | [] => { uri := "", tenantId := "" }

def Action.ofLegacy (principal : Principal) (capability : Capability) (resource : Resource)
    (effect : Effect) : Action :=
  { id := ""
    principal := principal
    capability := capability
    effects := [effect]
    reads := [resource]
    writes := [] }

def allResourcesSameTenantD (p : Principal) (rs : List Resource) : Bool :=
  rs.all (sameTenantD p)

/--
## Plain-English meaning
`allResourcesSameTenantD` matches tenant containment for every resource in the list.

## Trusted use
Multi-resource tenant checks in action authorization.

## Does not imply
Correctness of tenant labels in the identity system.
-/
theorem allResourcesSameTenantD_sound (p : Principal) (rs : List Resource) :
    allResourcesSameTenantD p rs = true ↔ ∀ r, r ∈ rs → SameTenant p r := by
  simp [allResourcesSameTenantD, List.all_eq_true, sameTenantD_sound]

def actionWithinTenantD (a : Action) : Bool :=
  allResourcesSameTenantD a.principal a.reads &&
  allResourcesSameTenantD a.principal a.writes

/-- Action is within tenant for all touched resources. -/
def ActionWithinTenant (a : Action) : Prop :=
  (∀ r, r ∈ a.reads → SameTenant a.principal r) ∧
  (∀ r, r ∈ a.writes → SameTenant a.principal r)

/--
## Plain-English meaning
`actionWithinTenantD` matches tenant containment for all read and write resources.

## Trusted use
Tenant isolation checks in runtime validation.

## Does not imply
Correctness of tenant labels in the identity system.
-/
theorem actionWithinTenantD_sound (a : Action) :
    actionWithinTenantD a = true ↔ ActionWithinTenant a := by
  simp [actionWithinTenantD, ActionWithinTenant, allResourcesSameTenantD_sound, Bool.and_eq_true,
    and_assoc]

def AllEffectsAllowed (c : Capability) (es : List Effect) : Prop :=
  ∀ e, e ∈ es → EffectAllowed c e

def allEffectsAllowedD (c : Capability) (es : List Effect) : Bool :=
  es.all (effectAllowedD c)

/--
## Plain-English meaning
`allEffectsAllowedD` matches effect allowlisting for every effect in the list.

## Trusted use
Multi-effect action authorization.

## Does not imply
The effect enumeration covers all real-world tool behaviors.
-/
theorem allEffectsAllowedD_sound (c : Capability) (es : List Effect) :
    allEffectsAllowedD c es = true ↔ AllEffectsAllowed c es := by
  simp [allEffectsAllowedD, AllEffectsAllowed, List.all_eq_true, effectAllowedD_sound]

/-- Full action authorization: capability, tenant, and all effects. -/
def ActionAllowed (a : Action) : Prop :=
  HasCapability a.principal a.capability ∧
  ActionWithinTenant a ∧
  AllEffectsAllowed a.capability a.effects

def actionAllowedD (a : Action) : Bool :=
  hasCapabilityD a.principal a.capability &&
  actionWithinTenantD a &&
  allEffectsAllowedD a.capability a.effects

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
    actionWithinTenantD_sound, allEffectsAllowedD_sound, Bool.and_eq_true, and_assoc]

end PFCore
