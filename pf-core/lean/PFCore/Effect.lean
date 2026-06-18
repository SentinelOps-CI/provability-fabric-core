import PFCore.Basic
import PFCore.Principal
import PFCore.Capability

/-!
# PFCore.Effect

Closed effect enumeration for PF-Core v0.
-/

namespace PFCore

inductive EffectKind where
  | fileRead : EffectKind
  | fileWrite : EffectKind
  | networkEgress : EffectKind
  | emailSend : EffectKind
  | handoffDelegate : EffectKind
  | mcpInvoke : EffectKind
  | labRelease : EffectKind
  deriving Repr, DecidableEq, Inhabited

def effectKindToString : EffectKind → String
  | .fileRead => "file.read"
  | .fileWrite => "file.write"
  | .networkEgress => "network.egress"
  | .emailSend => "email.send"
  | .handoffDelegate => "handoff.delegate"
  | .mcpInvoke => "mcp.invoke"
  | .labRelease => "lab.release"

structure Effect where
  kind : EffectKind
  deriving Repr, DecidableEq, Inhabited

structure Resource where
  uri : ResourceUri
  tenantId : TenantId
  deriving Repr, DecidableEq, Inhabited

/-- Principal and resource share tenant. -/
def SameTenant (p : Principal) (r : Resource) : Prop :=
  p.tenantId = r.tenantId

/-- Tenant equality decider. -/
def sameTenantD (p : Principal) (r : Resource) : Bool :=
  p.tenantId == r.tenantId

/--
## Plain-English meaning
`sameTenantD` returns true when principal and resource tenants match.

## Trusted use
Tenant isolation decider.

## Does not imply
Cross-tenant data cannot leak without OS enforcement.
-/
theorem sameTenantD_sound (p : Principal) (r : Resource) :
    sameTenantD p r = true ↔ SameTenant p r := by
  simp [sameTenantD, SameTenant, beq_iff_eq]

/-- Effect `e` is on the closed allowlist for capability `c`. -/
def EffectAllowed (c : Capability) (e : Effect) : Prop :=
  effectKindToString e.kind = c.effectKind

def effectAllowedD (c : Capability) (e : Effect) : Bool :=
  effectKindToString e.kind == c.effectKind

/--
## Plain-English meaning
`effectAllowedD` matches effect kind string equality with capability.

## Trusted use
Effect allowlisting in action authorization.

## Does not imply
The effect enumeration covers all real-world tool behaviors.
-/
theorem effectAllowedD_sound (c : Capability) (e : Effect) :
    effectAllowedD c e = true ↔ EffectAllowed c e := by
  simp [effectAllowedD, EffectAllowed, beq_iff_eq]

end PFCore
