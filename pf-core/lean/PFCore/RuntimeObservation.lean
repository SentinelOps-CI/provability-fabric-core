import PFCore.Basic
import PFCore.Principal
import PFCore.Capability
import PFCore.Effect
import PFCore.Decision
import PFCore.Event

/-!
# PFCore.RuntimeObservation

Types for mapping runtime observations to events (adapter layer).
-/

namespace PFCore

structure RuntimeObservation where
  observationId : String
  principalId : PrincipalId
  tenantId : TenantId
  effectKind : String
  resourceUri : ResourceUri
  decision : Decision
  prevHash : Hash
  deriving Repr, DecidableEq, Inhabited

/-- Observation compiles to event when principal and capability are modeled. -/
structure CompiledObservation where
  observation : RuntimeObservation
  event : Event
  deriving Repr, Inhabited

def observationMatchesEvent (obs : RuntimeObservation) (ev : Event) : Prop :=
  ∃ a, ev.kind = EventKind.action a ∧
    a.principal.id = obs.principalId ∧
    a.principal.tenantId = obs.tenantId ∧
    effectKindToString a.effect.kind = obs.effectKind ∧
    a.resource.uri = obs.resourceUri ∧
    ev.decision = obs.decision ∧
    ev.prevHash = obs.prevHash

end PFCore
