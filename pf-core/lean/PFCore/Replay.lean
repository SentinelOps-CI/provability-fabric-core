import PFCore.Examples
import PFCore.Trace

/-!
# PFCore.Replay

Optional Lean replay path for golden trace fixtures (used by `--lean-check`).
-/

namespace PFCore.Replay

example : traceSafeD [PFCore.Examples.safeFileReadEvent] = true := by native_decide

example : TraceSafe [PFCore.Examples.safeFileReadEvent] :=
  (traceSafeD_sound [PFCore.Examples.safeFileReadEvent]).1 (by native_decide)

end PFCore.Replay
