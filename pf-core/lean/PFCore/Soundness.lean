import PFCore.Principal
import PFCore.Capability
import PFCore.Effect
import PFCore.Action
import PFCore.Event
import PFCore.Trace
import PFCore.EventKind
import PFCore.Handoff

/-!
# PFCore.Soundness

Central soundness theorems for deciders.

## Plain-English meaning
Boolean deciders agree with their Prop counterparts.

## Trusted use
Runtime `check-trace` may use deciders when soundness theorems apply.

## Does not imply
Correctness of JSON parsing, hash chains, or external enforcement.
-/

namespace PFCore

theorem hasRoleD_soundness (p : Principal) (r : Role) :
    hasRoleD p r = true ↔ HasRole p r :=
  hasRoleD_sound p r

theorem hasCapabilityD_soundness (p : Principal) (c : Capability) :
    hasCapabilityD p c = true ↔ HasCapability p c :=
  hasCapabilityD_sound p c

theorem sameTenantD_soundness (p : Principal) (r : Resource) :
    sameTenantD p r = true ↔ SameTenant p r :=
  sameTenantD_sound p r

theorem effectAllowedD_soundness (c : Capability) (e : Effect) :
    effectAllowedD c e = true ↔ EffectAllowed c e :=
  effectAllowedD_sound c e

theorem actionAllowedD_soundness (a : Action) :
    actionAllowedD a = true ↔ ActionAllowed a :=
  actionAllowedD_sound a

theorem eventKindSafeD_soundness (k : EventKind) :
    eventKindSafeD k = true ↔ EventKindSafe k :=
  eventKindSafeD_sound k

theorem eventSafeD_soundness (ev : Event) :
    eventSafeD ev = true ↔ EventSafe ev :=
  eventSafeD_sound ev

theorem traceSafeD_soundness (tr : Trace) :
    traceSafeD tr = true ↔ TraceSafe tr :=
  traceSafeD_sound tr

theorem handoffSafeD_soundness (h : Handoff) :
    handoffSafeD h = true ↔ HandoffSafe h :=
  handoffSafeD_sound h

end PFCore
