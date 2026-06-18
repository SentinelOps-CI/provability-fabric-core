# PF-Core Trusted Rings

Partition of the PF-Core stack by proof and enforcement status.

```mermaid
flowchart TB
  subgraph trusted [Trusted — Lean + pinned schemas + validator]
    LEAN[Lean kernel PFCore]
    SCH[JSON schemas v0]
    DEC[Deciders + contracts.py]
    FIX[Example fixtures gate]
  end

  subgraph operational [Operationally checked — T4]
    CLI[pf core CLI]
    HASH[hash_chain.py]
    EMIT[emitter.py / audit.jsonl]
  end

  subgraph assumed [Assumed — A1-A10]
    OBSF[Observation fidelity]
    TENANT[Tenant label assignment]
    SHA[SHA-256 chain integrity]
    CAT[Adapter catalogs]
  end

  subgraph unproved [Explicitly unproved]
    LLM[LLM / planner outputs]
    OS[OS / network enforcement]
    ORG[Organizational policy content]
    DOWN[Downstream certificate acceptance]
  end

  LEAN --> DEC
  SCH --> CLI
  DEC --> CLI
  HASH --> EMIT
  assumed --> operational
  operational --> trusted
  unproved -.->|outside boundary| trusted
```

## Ring definitions

| Ring | Contents | Evidence |
|------|----------|----------|
| **Trusted** | Lean theorems, schemas, decider soundness, contract algebra | `lake build`, `make pf-core-trusted` |
| **Operationally checked** | CLI commands, hash validation, compile determinism | Validator modules, fixture tests |
| **Assumed** | Emitter honesty, hash linking, tenant labels, catalogs | `docs/pf-core/assumptions.md` |
| **Unproved** | External systems, semantic policy, deployment safety | `mission.md`, `claim-boundary.md` |

## Lean vs runtime contract split

- **Lean `Contract`**: arbitrary `Prop` pre/post/invariant; proved algebra (`seq`, satisfaction).
- **JSON `contract`**: conservative structured fields executable by `contracts.py`.
- **Gap**: JSON contracts do not encode arbitrary Lean `Prop`; mapping is intentional and documented.
