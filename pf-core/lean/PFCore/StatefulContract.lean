import PFCore.Contract

/-!
# PFCore.StatefulContract

Extension of `Contract` with explicit state-transition obligations.
Does not replace the simple contract algebra.
-/

namespace PFCore

/-- Abstract contract state tag for stateful extensions. -/
structure ContractState where
  tag : String
  deriving Repr, DecidableEq, Inhabited

/-- Contract extended with initial-state and step predicates. -/
structure StatefulContract extends Contract where
  stateInit : ContractState → Prop
  stateStep : ContractState → Event → ContractState → Prop

/-- State transition holds when init, event satisfaction, and step post hold. -/
def StatefulContract.satisfiesStateTransition (sc : StatefulContract)
    (s₀ s₁ : ContractState) (ev : Event) : Prop :=
  sc.stateInit s₀ → SatisfiesContract sc.toContract ev → sc.stateStep s₀ ev s₁

/--
## Plain-English meaning
`StatefulContract` embeds the base `Contract` fields without renaming.

## Trusted use
Layering stateful release gates on top of event contracts.

## Does not imply
Runtime state machine enforcement.
-/
theorem stateful_extends_contract (sc : StatefulContract) :
    sc.toContract.name = sc.name ∧
    sc.toContract.pre = sc.pre ∧
    sc.toContract.post = sc.post ∧
    sc.toContract.invariant = sc.invariant :=
  ⟨rfl, rfl, rfl, rfl⟩

/--
## Plain-English meaning
If a state transition is satisfied under a composed base contract event,
each component base contract is satisfied on that event.

## Trusted use
Relating stateful steps to decomposed contract obligations.

## Does not imply
State is tracked or persisted at runtime.
-/
theorem stateful_satisfies_components (sc₁ sc₂ : StatefulContract) (ev : Event)
    (h : SatisfiesContract (sc₁.toContract.seq sc₂.toContract) ev) :
    SatisfiesContract sc₁.toContract ev ∧ SatisfiesContract sc₂.toContract ev :=
  satisfies_contract_of_seq sc₁.toContract sc₂.toContract ev h

end PFCore
