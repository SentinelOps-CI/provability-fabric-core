import Lake
open Lake DSL

package «pf-core» where
  leanOptions := #[
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩
  ]

@[default_target]
lean_lib PFCore where
  roots := #[`PFCore]
