/-!
# PFCore.Basic

Core identifiers and list membership helpers used across PF-Core.
-/

namespace PFCore

abbrev TenantId := String
abbrev PrincipalId := String
abbrev Role := String
abbrev CapabilityId := String
abbrev ResourceUri := String
abbrev EventId := String
abbrev Hash := String

/-- List membership as a proposition. -/
def Mem {α : Type} [BEq α] (x : α) (xs : List α) : Prop :=
  x ∈ xs

/-- Decidable list membership decider. -/
def memD {α : Type} [BEq α] : α → List α → Bool
  | _, [] => false
  | x, y :: ys => (x == y) || memD x ys

/--
## Plain-English meaning
`memD` returns true exactly when the element is in the list.

## Trusted use
Foundation for role and capability deciders.

## Does not imply
Semantic correctness of role strings in production IAM.
-/
theorem memD_sound {α : Type} [BEq α] [LawfulBEq α] (x : α) (xs : List α) :
    memD x xs = true ↔ Mem x xs := by
  induction xs with
  | nil => simp [memD, Mem]
  | cons y ys ih =>
    simp only [memD, Mem, List.mem_cons, Bool.or_eq_true]
    constructor
    · rintro (hxy | htail)
      · exact Or.inl ((beq_iff_eq (a := x) (b := y)).mp hxy)
      · exact Or.inr (ih.mp htail)
    · rintro (heq | htail)
      · subst heq
        exact Or.inl ((beq_iff_eq (a := x) (b := x)).mpr rfl)
      · exact Or.inr (ih.mpr htail)

end PFCore
