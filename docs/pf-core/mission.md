# PF-Core Mission

PF-Core is the minimal trusted kernel for proof-carrying agentic actions, contracted tool calls, handoffs, and trace-level safety preservation. It is intentionally smaller than Provability Fabric: it is not a second runtime, CLI surface, or evidence standard.

## Mandatory boundary statement

PF-Core proves preservation properties over abstract traces. It does not prove that arbitrary LLM outputs are semantically correct, that external tools are honest, that operating systems are secure, that timestamps are reliable, that cryptographic hashes cannot collide except as an assumption, or that runtime instrumentation is complete unless separately attested.

**PF-Core proves:** Given explicitly modeled principals, capabilities, effects, resources, actions, decisions, events, and traces—and given stated assumptions about hash-chain integrity and schema conformance—whether each event in a trace satisfies tenant isolation, capability authorization, and effect allowlisting, and whether handoffs preserve authority within declared bounds.

**PF-Core does not prove:** Correctness of external systems (LLMs, MCP servers, operating systems, networks), honesty of runtime emitters, completeness of policy catalogs, cryptographic collision resistance beyond stated hash assumptions, semantic equivalence between runtime observations and formal models, or end-to-end safety of an agent deployment without adapter contracts and organizational controls.

## Soundness split

| Layer | Responsibility |
|-------|----------------|
| Lean proves | Decider soundness, event/trace safety, contract algebra, handoff subset |
| Runtime validates | Schema conformance, hash chains, compile determinism, adapter catalogs |
| Assumptions | Observation fidelity, tenant labels, SHA-256 chaining (`assumptions.md`) |

## Scope

| In scope | Out of scope |
|----------|--------------|
| Formal authorization predicates and deciders | Full evidence graph / PCS packaging |
| Trace safety composition | Agent orchestration runtime |
| Contract algebra (sequence, projection) | Policy authoring UI |
| Handoff authority preservation | Network sandbox enforcement |
| Certificate structure over safe traces | Lean proof of external tool behavior |

## Design principles

1. **Minimal trusted computing base** — Few types, few theorems, no `sorry`.
2. **Decidable runtime bridge** — Every trusted predicate has a Boolean decider with a soundness proof.
3. **Explicit assumptions** — Hash chains, tenant labels, and adapter mappings are assumed, not proved.
4. **Negative fixtures** — Every positive example has a negative twin with `expected_error`.
