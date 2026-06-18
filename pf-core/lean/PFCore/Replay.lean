import PFCore.Certificate
import PFCore.Examples
import PFCore.Handoff
import PFCore.Trace

/-!
# PFCore.Replay

Optional Lean replay path for golden trace fixtures (used by `--lean-check`).
Covers release goldens: file read, handoff subset, PCS lab-release replay.
-/

namespace PFCore.Replay

example : traceSafeD [PFCore.Examples.safeFileReadEvent] = true := by native_decide

example : TraceSafe [PFCore.Examples.safeFileReadEvent] :=
  (traceSafeD_sound [PFCore.Examples.safeFileReadEvent]).1 (by native_decide)

def handoffPrincipalFrom : Principal :=
  { id := "agent-1", tenantId := "tenant-a", roles := ["agent"], capabilities := [] }

def handoffPrincipalTo : Principal :=
  { id := "agent-2", tenantId := "tenant-a", roles := ["handoff_delegate"], capabilities := [] }

def handoffCapability : Capability :=
  { id := "cap:handoff", effectKind := "handoff.delegate", resourcePattern := "agent:*" }

def goldenHandoff : Handoff :=
  { fromPrincipal := handoffPrincipalFrom
    toPrincipal := handoffPrincipalTo
    delegatedCapabilities := [handoffCapability]
    reason := "delegate handoff authority to agent-2"
    evidenceRef := "evidence/handoff.v0" }

def safeHandoffEvent : Event :=
  { eventId := "ev-handoff-1", kind := .handoff goldenHandoff, decision := .allowed,
    reason := "delegate handoff authority to agent-2", evidenceRef := "evidence/handoff.v0",
    prevHash := genesisHash, hash := "handoff" }

example : handoffSafeD goldenHandoff = true := by native_decide

example : traceSafeD [safeHandoffEvent] = true := by native_decide

example : TraceSafe [safeHandoffEvent] :=
  (traceSafeD_sound [safeHandoffEvent]).1 (by native_decide)

example : traceSafeD [PFCore.Examples.labReleaseEvent] = true := by native_decide

example : TraceSafe [PFCore.Examples.labReleaseEvent] :=
  (traceSafeD_sound [PFCore.Examples.labReleaseEvent]).1 (by native_decide)

end PFCore.Replay
