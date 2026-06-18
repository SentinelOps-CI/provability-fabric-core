import PFCore.Trace
import PFCore.Contract

/-!
# PFCore.Composition

Composing safe traces preserves safety; contract satisfaction distributes over append.
-/

namespace PFCore

/--
## Plain-English meaning
Appending safe traces yields a safe combined trace.

## Trusted use
Composing sub-traces from tool calls and handoffs.

## Does not imply
Hash-chain integrity of appended segments.
-/
theorem trace_safe_append (t1 t2 : Trace) (h1 : TraceSafe t1) (h2 : TraceSafe t2) :
    TraceSafe (t1 ++ t2) := by
  intro ev he
  rcases List.mem_append.mp he with he1 | he2
  · exact h1 ev he1
  · exact h2 ev he2

/--
## Plain-English meaning
`traceSafeD` on append matches conjunction of deciders on parts.

## Trusted use
Incremental trace safety checking.

## Does not imply
Decider soundness without `traceSafeD_sound`.
-/
theorem traceSafeD_append (t1 t2 : Trace) :
    traceSafeD (t1 ++ t2) = (traceSafeD t1 && traceSafeD t2) := by
  induction t1 with
  | nil => simp [traceSafeD]
  | cons ev t1 ih =>
    simp [traceSafeD, List.all_cons, ih, Bool.and_assoc, Bool.and_left_comm, Bool.and_comm]

/--
## Plain-English meaning
If two traces each satisfy a contract, their append satisfies the contract.

## Trusted use
Composing trace segments under a shared policy contract.

## Does not imply
Contracts are checked incrementally at runtime without full trace replay.
-/
theorem trace_satisfies_contract_append (c : Contract) (t1 t2 : Trace)
    (h1 : TraceSatisfiesContract c t1) (h2 : TraceSatisfiesContract c t2) :
    TraceSatisfiesContract c (t1 ++ t2) := by
  induction t1 generalizing t2 with
  | nil => simpa using h2
  | cons ev tr ih =>
    rcases h1 with ⟨htr, hsat⟩
    exact ⟨ih t2 htr h2, hsat⟩

end PFCore
