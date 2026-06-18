import PFCore.Basic

/-!
# PFCore.Principal

Principal records and role authorization.
-/

namespace PFCore

structure Principal where
  id : PrincipalId
  tenantId : TenantId
  roles : List Role
  deriving Repr, DecidableEq, Inhabited

/-- Principal `p` has role `r`. -/
def HasRole (p : Principal) (r : Role) : Prop :=
  Mem r p.roles

/-- Role membership decider. -/
def hasRoleD (p : Principal) (r : Role) : Bool :=
  memD r p.roles

/--
## Plain-English meaning
`hasRoleD` returns true exactly when the principal has the role.

## Trusted use
Role checks in authorization pipelines.

## Does not imply
IAM system assigned roles correctly.
-/
theorem hasRoleD_sound (p : Principal) (r : Role) :
    hasRoleD p r = true ↔ HasRole p r := by
  simp [hasRoleD, HasRole, memD_sound]

end PFCore
