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
  { id := "agent-1"
    tenantId := "tenant-a"
    roles := ["agent"]
    capabilities := [] }

def readerCapability : Capability :=
  { id := "cap:file-read", effectKind := "file.read", resourcePattern := "/data/*" }

def dataResource : Resource :=
  { uri := "/data/report.txt", tenantId := "tenant-a" }

def fileReadEffect : Effect := { kind := .fileRead }

def fileReadAction : Action :=
  Action.ofLegacy agentPrincipal readerCapability dataResource fileReadEffect

example : actionAllowedD fileReadAction = true := by native_decide

example : ActionAllowed fileReadAction :=
  (actionAllowedD_sound fileReadAction).1 (by native_decide)

def deniedNetworkCapability : Capability :=
  { id := "cap:network", effectKind := "network.egress", resourcePattern := "*" }

def networkEffect : Effect := { kind := .networkEgress }

def networkAction : Action :=
  Action.ofLegacy agentPrincipal deniedNetworkCapability dataResource networkEffect

example : actionAllowedD networkAction = false := by native_decide

example : ¬ ActionAllowed networkAction := fun h => by
  have ht := (actionAllowedD_sound networkAction).2 h
  rw [show actionAllowedD networkAction = false by native_decide] at ht
  cases ht

def safeFileReadEvent : Event :=
  { eventId := "ev-1", kind := .action fileReadAction, decision := .allowed,
    reason := "", evidenceRef := "", prevHash := genesisHash, hash := "abc" }

example : eventSafeD safeFileReadEvent = true := by native_decide

example : EventSafe safeFileReadEvent :=
  (eventSafeD_sound safeFileReadEvent).1 (by native_decide)

example : TraceSafe [safeFileReadEvent] :=
  trace_safe_cons _ _ ((eventSafeD_sound safeFileReadEvent).1 (by native_decide)) trace_safe_empty

def fileReadContract : Contract :=
  { name := "file-read"
    pre := fun p a => HasCapability p a.capability ∧ ActionWithinTenant a
    post := fun _ _ ev => EventSafe ev
    invariant := TraceSafe }

example : SatisfiesContract fileReadContract safeFileReadEvent := by
  simp [SatisfiesContract, fileReadContract, safeFileReadEvent]
  constructor
  · have h := (actionAllowedD_sound fileReadAction).1 (by native_decide)
    rcases h with ⟨hc, ht, _⟩
    exact ⟨hc, ht⟩
  · exact (eventSafeD_sound safeFileReadEvent).1 (by native_decide)

example : TraceSatisfiesContract fileReadContract [safeFileReadEvent] := by
  simp only [TraceSatisfiesContract]
  simp [SatisfiesContract, fileReadContract, safeFileReadEvent]
  constructor
  · have h := (actionAllowedD_sound fileReadAction).1 (by native_decide)
    rcases h with ⟨hc, ht, _⟩
    exact ⟨hc, ht⟩
  · exact (eventSafeD_sound safeFileReadEvent).1 (by native_decide)

def labReleaseCapability : Capability :=
  { id := "cap:lab-release", effectKind := "lab.release", resourcePattern := "lab:*" }

def labReleaseAgent : Principal :=
  { id := "agent-1", tenantId := "tenant-a", roles := ["lab_operator"], capabilities := [] }

def labResource : Resource :=
  { uri := "lab:experiment-42", tenantId := "tenant-a" }

def labReleaseEffect : Effect := { kind := .labRelease }

def labReleaseAction : Action :=
  Action.ofLegacy labReleaseAgent labReleaseCapability labResource labReleaseEffect

def labReleaseEvent : Event :=
  { eventId := "ev-lab-release", kind := .action labReleaseAction, decision := .allowed,
    reason := "", evidenceRef := "", prevHash := genesisHash, hash := "lab" }

def labReleaseContract : Contract :=
  { name := "lab-release-gate"
    pre := fun p a =>
      HasCapability p labReleaseCapability ∧
      effectKindToString a.primaryEffect.kind = "lab.release"
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

example : actionAllowedD labReleaseAction = true := by native_decide

example : EventSafe labReleaseEvent :=
  (eventSafeD_sound labReleaseEvent).1 (by native_decide)

end PFCore.Examples
