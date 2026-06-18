# PF-Core Formal Model



PF-Core models a minimal authorization kernel. Types live in namespace `PFCore` under `pf-core/lean/PFCore/`.



## Types



| Type | Description |

|------|-------------|

| `Principal` | Agent identity with tenant and role/capability ids |

| `Capability` | Effect kind + resource pattern |

| `Effect` | Closed `EffectKind` enumeration |

| `Resource` | URI + tenant |

| `Action` | Principal attempting capability on resource with effect |

| `Decision` | `allowed` or `denied` |

| `Event` | Discriminated `EventKind` + decision + hash-chain fields |
| `EventKind` | `action` or `handoff` payload |

| `Trace` | `List Event` |

| `Contract` | Named `pre`/`post`/`invariant` predicates |

| `StatefulContract` | `Contract` + `stateInit`/`stateStep` |

| `EffectPairEncoding` | Adapter convenience (not trusted contract core) |

| `Handoff` | Bilateral principal capability transfer |

| `Certificate` | Summary over trace hash and safety bit |

| `RuntimeObservation` | Adapter input before compilation |
| `Assumption` | Numbered trusted assumption record |
| `ClaimClassification` | T1–T5 claim category record |



## Predicates



- `HasRole`, `HasCapability`, `SameTenant`

- `ActionWithinTenant`, `EffectAllowed`, `ActionAllowed`

- `EventSafe`, `TraceSafe`, `EventKindSafe`, `HandoffSafe`

- `SatisfiesContract`, `TraceSatisfiesContract`



## Deciders



Each predicate has a `*D` decider with a soundness theorem (see `Soundness.lean`). JSON contracts use structured fields checked by `contracts.py` (T4).



## Key theorems



- `trace_safe_empty`, `trace_safe_cons`, `traceSafeD_sound`

- `seq_contract_satisfaction_left`, `seq_contract_satisfaction_right`, `seq_invariant_preservation`

- `trace_satisfies_trace_safe_contract`

- `denied_event_not_executed`, `allowed_event_has_allowed_action`, `allowed_handoff_event_is_safe`
- `every_allowed_event_in_safe_trace_is_allowed`, `every_allowed_handoff_in_safe_trace_preserves_authority`
- `handoff_does_not_expand_authority`



See `theorem-map.md` for the full index.



## EventIn



`EventIn` is an inductive witness for allowed/denied actions before event packaging.



## EventKind (v1)

```lean
inductive EventKind where
  | action : Action → EventKind
  | handoff : Handoff → EventKind
```

`Event` carries `kind : EventKind`. Runtime schema: `pf-core.event.v1` with `event_kind.type` discriminator.

### Migration from v0

| v0 (`pf-core.event.v0`) | v1 (`pf-core.event.v1`) |
|-------------------------|-------------------------|
| Top-level `action` | `event_kind: { type: "action", action: ... }` |
| Handoff via `handoff.delegate` action | `event_kind: { type: "handoff", handoff: ... }` |

Hash canonicalization is unchanged: `event_hash = sha256(canonical_json(event \\ {event_hash}))`. Fixtures and trace schema now use v1 events. v0 schema file remains for reference only.



## Relation to JSON



Runtime artifacts validate against `pf-core/schemas/` and are checked by deciders in `pf-core/validator/`. See `schema-map.md` and `runtime-mapping.md`.



## Soundness posture

If the trace is constructed from schema-valid runtime observations, each observation compiles deterministically into a PF-Core event, the executable decider accepts each event, the decider is sound with respect to the Lean predicate, and the trace replay validator preserves event order and hash chains, then every allowed event in the trace satisfies the declared PF-Core action-safety predicate (and handoff events satisfy the handoff subset predicate).

The proof is split: Lean proves decider soundness, event/trace safety, contract algebra projections, and handoff authority subset; the runtime validates JSON schema conformance, hash-chain integrity, compile determinism, and adapter catalogs; assumptions cover observation fidelity, hash collision resistance, tenant labeling, and external infrastructure (see `docs/pf-core/assumptions.md`).

## Soundness split



| Layer | Responsibility |

|-------|----------------|

| Lean proves | Decider soundness, trace/event safety, contract algebra, handoff subset |

| Runtime validates | Schema conformance, hash chains, compile determinism, contract deciders |

| Assumptions | Observation fidelity, tenant labels, SHA-256 chaining (`docs/pf-core/assumptions.md`) |

