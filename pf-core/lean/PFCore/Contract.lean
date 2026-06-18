import PFCore.Event
import PFCore.Trace
import PFCore.Effect

/-!
# PFCore.Contract

Contract algebra: named pre/post/invariant predicates over events and traces.

Effect-pair encodings live in `EffectPairEncoding` as adapter convenience only.
-/

namespace PFCore

/-- Named contract with per-event pre/post and trace-level invariant. -/
structure Contract where
  name : String
  pre : Principal → Action → Prop
  post : Principal → Action → Event → Prop
  invariant : Trace → Prop

/-- Single event satisfies contract when pre/post hold for actions; handoffs require event safety. -/
def SatisfiesContract (c : Contract) (ev : Event) : Prop :=
  match ev.kind with
  | .action a => c.pre a.principal a ∧ c.post a.principal a ev
  | .handoff _ => EventSafe ev

/-- Trace satisfies contract when every event satisfies it (empty trace is trivial). -/
def TraceSatisfiesContract (c : Contract) : Trace → Prop
  | [] => True
  | ev :: tr => TraceSatisfiesContract c tr ∧ SatisfiesContract c ev

/-- Sequential composition: conjunction of pre/post/invariant obligations. -/
def Contract.seq (c₁ c₂ : Contract) : Contract :=
  { name := c₁.name ++ ";" ++ c₂.name
    pre := fun p a => c₁.pre p a ∧ c₂.pre p a
    post := fun p a e => c₁.post p a e ∧ c₂.post p a e
    invariant := fun tr => c₁.invariant tr ∧ c₂.invariant tr }

/--
## Plain-English meaning
Composed contract satisfaction on one event implies each component contract holds.

## Trusted use
Decomposing sequential policy obligations per event.

## Does not imply
Temporal ordering beyond list structure in the trace.
-/
theorem satisfies_contract_of_seq (c₁ c₂ : Contract) (ev : Event)
    (h : SatisfiesContract (c₁.seq c₂) ev) :
    SatisfiesContract c₁ ev ∧ SatisfiesContract c₂ ev := by
  cases hev : ev.kind with
  | action a =>
    simp [SatisfiesContract, hev] at h
    rcases h with ⟨hpre, hpost⟩
    simp [SatisfiesContract, hev]
    exact ⟨⟨hpre.1, hpost.1⟩, ⟨hpre.2, hpost.2⟩⟩
  | handoff hnd =>
    simp only [SatisfiesContract, hev, Contract.seq] at h ⊢
    exact And.intro h h

/--
## Plain-English meaning
If a trace satisfies a composed contract, it satisfies the left component.

## Trusted use
Extracting first-stage obligations from composed adapter policies.

## Does not imply
The left contract was checked before the right at runtime.
-/
theorem seq_contract_satisfaction_left (c₁ c₂ : Contract) (tr : Trace)
    (h : TraceSatisfiesContract (c₁.seq c₂) tr) :
    TraceSatisfiesContract c₁ tr := by
  induction tr with
  | nil => exact trivial
  | cons ev tr ih =>
    rcases h with ⟨hrest, hsat⟩
    exact ⟨ih hrest, (satisfies_contract_of_seq c₁ c₂ ev hsat).1⟩

/--
## Plain-English meaning
If a trace satisfies a composed contract, it satisfies the right component.

## Trusted use
Extracting second-stage obligations from composed adapter policies.

## Does not imply
The right contract subsumes all runtime policy checks.
-/
theorem seq_contract_satisfaction_right (c₁ c₂ : Contract) (tr : Trace)
    (h : TraceSatisfiesContract (c₁.seq c₂) tr) :
    TraceSatisfiesContract c₂ tr := by
  induction tr with
  | nil => exact trivial
  | cons ev tr ih =>
    rcases h with ⟨hrest, hsat⟩
    exact ⟨ih hrest, (satisfies_contract_of_seq c₁ c₂ ev hsat).2⟩

/--
## Plain-English meaning
Sequential composition preserves invariants as a conjunction of component invariants.

## Trusted use
Composing trace-level invariants in policy bundles.

## Does not imply
Either invariant holds without trace satisfaction.
-/
theorem seq_invariant_preservation (c₁ c₂ : Contract) (tr : Trace) :
    (c₁.seq c₂).invariant tr ↔ c₁.invariant tr ∧ c₂.invariant tr :=
  Iff.rfl

/-- Standard trace-safety contract: post requires `EventSafe`, invariant is `TraceSafe`. -/
def traceSafeContract : Contract :=
  { name := "trace-safe"
    pre := fun _ _ => True
    post := fun _ _ ev => EventSafe ev
    invariant := TraceSafe }

/--
## Plain-English meaning
`traceSafeContract` trace satisfaction is equivalent to `TraceSafe`.

## Trusted use
Linking contract algebra to existing trace safety theorems.

## Does not imply
Hash-chain integrity or external enforcement.
-/
theorem trace_satisfies_trace_safe_contract (tr : Trace) :
    TraceSatisfiesContract traceSafeContract tr ↔ TraceSafe tr := by
  constructor
  · intro h
    induction tr with
    | nil => intro ev hin; cases hin
    | cons ev tr ih =>
      rcases h with ⟨hrest, hsat⟩
      intro e he
      simp [List.mem_cons] at he
      rcases he with rfl | he
      · cases hk : e.kind with
        | action a =>
          rw [SatisfiesContract, hk] at hsat
          rcases hsat with ⟨_, hpost⟩
          simpa [traceSafeContract] using hpost
        | handoff hnd =>
          rw [SatisfiesContract, hk] at hsat
          exact hsat
      · exact ih hrest e he
  · intro h
    induction tr with
    | nil => exact trivial
    | cons ev tr ih =>
      have hev : EventSafe ev := h ev (by simp)
      refine ⟨ih fun e he => h e (by simp [he]), ?_⟩
      cases hk : ev.kind with
      | action a =>
        rw [SatisfiesContract, hk, traceSafeContract]
        exact ⟨trivial, hev⟩
      | handoff hnd =>
        rw [SatisfiesContract, hk]
        exact hev

/-!
## Effect-pair convenience (adapter encoding, not trusted contract core)
-/

/-- Adapter convenience: required/target effect pair without arbitrary `Prop` fields. -/
structure EffectPairEncoding where
  requiredEffect : EffectKind
  targetEffect : EffectKind
  deriving Repr, DecidableEq, Inhabited

/-- Lift effect-pair encoding to a `Contract` with decidable pre on effect kind. -/
def EffectPairEncoding.toContract (ep : EffectPairEncoding) : Contract :=
  { name := s!"effect-pair:{effectKindToString ep.requiredEffect}"
    pre := fun _ a =>
      effectKindToString a.primaryEffect.kind = effectKindToString ep.requiredEffect
    post := fun _ a ev =>
      effectKindToString a.primaryEffect.kind = effectKindToString ep.targetEffect ∧ EventSafe ev
    invariant := fun _ => True }

/-- Build contract from effect kinds (adapter shorthand). -/
def Contract.ofEffectPair (required target : EffectKind) : Contract :=
  (EffectPairEncoding.mk required target).toContract

/-- Sequential composition of effect-pair encodings (adapter shorthand). -/
def EffectPairEncoding.seq (c1 c2 : EffectPairEncoding) : EffectPairEncoding :=
  { requiredEffect := c1.requiredEffect, targetEffect := c2.targetEffect }

/--
## Plain-English meaning
Effect-pair `seq` projects the second target effect.

## Trusted use
Adapter policy translation for effect chains.

## Does not imply
Runtime enforcement of prerequisite effects.
-/
theorem effect_pair_seq_target (c1 c2 : EffectPairEncoding) :
    (c1.seq c2).targetEffect = c2.targetEffect := rfl

/--
## Plain-English meaning
Effect-pair `seq` keeps the first required effect.

## Trusted use
Adapter policy translation for effect chains.

## Does not imply
The prerequisite effect was observed in a trace.
-/
theorem effect_pair_seq_required (c1 c2 : EffectPairEncoding) :
    (c1.seq c2).requiredEffect = c1.requiredEffect := rfl

end PFCore
