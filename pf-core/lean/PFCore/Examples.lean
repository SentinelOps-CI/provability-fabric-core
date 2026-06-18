import PFCore.Action
import PFCore.Event
import PFCore.Trace
import PFCore.Contract
import PFCore.StatefulContract
import PFCore.Certificate

/-!
# PFCore.Examples

Checked example scenarios mirroring JSON fixtures.
-/

namespace PFCore.Examples

def agentPrincipal : Principal :=
  { id := "agent-1", tenantId := "tenant-a", roles := ["cap:file-read", "cap:email-send"] }

def readerCapability : Capability :=
  { id := "cap:file-read", effectKind := "file.read", resourcePattern := "/data/*" }

def dataResource : Resource :=
  { uri := "/data/report.txt", tenantId := "tenant-a" }

def fileReadEffect : Effect := { kind := .fileRead }

def fileReadAction : Action :=
  { principal := agentPrincipal, capability := readerCapability,
    resource := dataResource, effect := fileReadEffect }

example : ActionAllowed fileReadAction := by
  simp [ActionAllowed, fileReadAction, agentPrincipal, readerCapability,
    dataResource, fileReadEffect, HasCapability, HasRole, Mem, EffectAllowed,
    ActionWithinTenant, SameTenant, effectKindToString]

def deniedNetworkCapability : Capability :=
  { id := "cap:network", effectKind := "network.egress", resourcePattern := "*" }

def networkEffect : Effect := { kind := .networkEgress }

def networkAction : Action :=
  { principal := agentPrincipal, capability := deniedNetworkCapability,
    resource := dataResource, effect := networkEffect }

example : ¬ ActionAllowed networkAction := by
  intro h
  rcases h with ⟨hc, _, _⟩
  simp [networkAction, agentPrincipal, deniedNetworkCapability, HasCapability, Mem] at hc

def safeFileReadEvent : Event :=
  { eventId := "ev-1", kind := .action fileReadAction, decision := .allowed,
    prevHash := genesisHash, hash := "abc" }

example : EventSafe safeFileReadEvent := by
  simp [EventSafe, EventKindSafe, safeFileReadEvent, ActionAllowed, fileReadAction,
    agentPrincipal, readerCapability, dataResource, fileReadEffect,
    HasCapability, Mem, EffectAllowed, ActionWithinTenant, SameTenant, effectKindToString]

example : TraceSafe [safeFileReadEvent] :=
  trace_safe_cons _ _ (by simp [EventSafe, EventKindSafe, safeFileReadEvent, ActionAllowed, fileReadAction,
    agentPrincipal, readerCapability, dataResource, fileReadEffect,
    HasCapability, Mem, EffectAllowed, ActionWithinTenant, SameTenant, effectKindToString]) trace_safe_empty

def fileReadContract : Contract :=
  { name := "file-read"
    pre := fun p a => HasCapability p a.capability ∧ ActionWithinTenant a
    post := fun _ _ ev => EventSafe ev
    invariant := TraceSafe }

example : SatisfiesContract fileReadContract safeFileReadEvent := by
  simp [SatisfiesContract, fileReadContract, safeFileReadEvent, EventSafe, EventKindSafe, fileReadAction,
    agentPrincipal, readerCapability, dataResource, fileReadEffect, ActionAllowed,
    HasCapability, Mem, EffectAllowed, ActionWithinTenant, SameTenant, effectKindToString]

example : TraceSatisfiesContract fileReadContract [safeFileReadEvent] := by
  simp only [TraceSatisfiesContract]
  simp [SatisfiesContract, fileReadContract, safeFileReadEvent, EventSafe, EventKindSafe, fileReadAction,
    agentPrincipal, readerCapability, dataResource, fileReadEffect, ActionAllowed,
    HasCapability, Mem, EffectAllowed, ActionWithinTenant, SameTenant, effectKindToString]

def labReleaseCapability : Capability :=
  { id := "cap:lab-release", effectKind := "lab.release", resourcePattern := "lab:*" }

def labReleaseAgent : Principal :=
  { id := "agent-1", tenantId := "tenant-a", roles := ["cap:lab-release"] }

def labResource : Resource :=
  { uri := "lab:experiment-42", tenantId := "tenant-a" }

def labReleaseEffect : Effect := { kind := .labRelease }

def labReleaseAction : Action :=
  { principal := labReleaseAgent, capability := labReleaseCapability,
    resource := labResource, effect := labReleaseEffect }

def labReleaseEvent : Event :=
  { eventId := "ev-lab-release", kind := .action labReleaseAction, decision := .allowed,
    prevHash := genesisHash, hash := "lab" }

def labReleaseContract : Contract :=
  { name := "lab-release-gate"
    pre := fun p a =>
      HasCapability p labReleaseCapability ∧
      effectKindToString a.effect.kind = "lab.release"
    post := fun _ _ ev => ev.decision = Decision.allowed ∧ EventSafe ev
    invariant := TraceSafe }

def labReleaseStateful : StatefulContract :=
  { name := "lab-release-gate"
    pre := labReleaseContract.pre
    post := labReleaseContract.post
    invariant := labReleaseContract.invariant
    stateInit := fun s => s.tag = "qc-passed"
    stateStep := fun s₀ ev s₁ =>
      s₀.tag = "qc-passed" → ev.decision = Decision.allowed → s₁.tag = "released" }

example : SatisfiesContract labReleaseContract labReleaseEvent := by
  simp [SatisfiesContract, labReleaseContract, labReleaseEvent, EventSafe, EventKindSafe, labReleaseAction,
    labReleaseAgent, labReleaseCapability, labResource, labReleaseEffect, ActionAllowed,
    HasCapability, Mem, EffectAllowed, ActionWithinTenant, SameTenant, effectKindToString]

end PFCore.Examples
