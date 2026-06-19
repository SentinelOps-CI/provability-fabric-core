<div align="center">

# Provability Fabric Core

**Machine-checked safety for AI agent actions — from runtime logs to verifiable certificates.**

<br/>

[![pf-core-trusted](https://github.com/SentinelOps-CI/provability-fabric-core/actions/workflows/pf-core-trusted.yml/badge.svg)](https://github.com/SentinelOps-CI/provability-fabric-core/actions/workflows/pf-core-trusted.yml)
[![Lean 4](https://img.shields.io/badge/Lean-4-2C3E50?style=flat-square)](https://leanprover.github.io/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.6.0-6C757D?style=flat-square)](pf-core/VERSION)

<br/>

[Quick Start](#quick-start) · [How It Works](#how-it-works) · [Contributing](#contributing) · [Documentation](#documentation)

</div>

---

## What is this?

When an AI agent reads a file, sends an email, or hands work to another agent — **was that action allowed?** Can you prove it later, from logs alone?

**Provability Fabric Core** is a small, auditable foundation for answering those questions. It gives you:

| | |
|---|---|
| **Structured records** | A common format for agent actions, handoffs between agents, and the traces they form |
| **Safety checks** | Rules that verify capabilities, tenant boundaries, and allowed effects on every step |
| **Proofs you can replay** | Lean 4 theorems linked to a Python validator, so certificates mean what they claim |

This repository is the **trusted kernel** — schemas, proofs, and a reference validator. It is not a full agent runtime, policy editor, or deployment platform.

> **In one sentence:** turn runtime observations into ordered traces, check them against formal safety rules, and emit certificates backed by machine-checked proofs.

---

## How it works

```mermaid
flowchart LR
  A["Runtime log"] --> B["Adapter"]
  B --> C["Observation"]
  C --> D["Trace events"]
  D --> E["Safety checks"]
  E --> F["Certificate"]

  style A fill:#f8f9fa,stroke:#dee2e6
  style B fill:#e7f1ff,stroke:#0d6efd
  style C fill:#e7f1ff,stroke:#0d6efd
  style D fill:#fff3cd,stroke:#ffc107
  style E fill:#d1e7dd,stroke:#198754
  style F fill:#d1e7dd,stroke:#198754
```

| Component | Location | What it does |
|-----------|----------|--------------|
| **Schemas** | `pf-core/schemas/` | JSON formats for observations, events, traces, and certificates |
| **Validator** | `pf-core/validator/` | CLI that compiles, validates, checks safety, and emits artifacts |
| **Lean proofs** | `pf-core/lean/PFCore/` | Machine-checked theorems: runtime checks match the formal model |
| **Examples** | `pf-core/examples/` | Paired valid and invalid fixtures — every success has a failure twin |
| **Adapters** | `adapters/` | Optional bridges from real runtime logs into core formats |

Every safety predicate in the formal model has a matching runtime decider, with a soundness proof connecting the two.

---

## Quick start

### Prerequisites

- [Lean 4](https://leanprover.github.io/) via [elan](https://github.com/leanprover/elan)
- Python 3.10+

### Run the full verification gate

This runs Lean proofs, schema validation, example fixtures, a boundary audit, and unit tests.

**Linux / macOS**

```bash
make pf-core-trusted
```

**Windows (PowerShell)**

```powershell
powershell -File pf-core/scripts/pf-core-trusted.ps1
```

### Try the CLI

```bash
pip install -e pf-core/validator

# Validate schema files
pf core schema-check --schemas pf-core/schemas

# Compile a runtime observation into a trace event
pf core compile-observation \
  --file pf-core/examples/valid/mcp_sidecar_observation.json

# Check an entire trace for safety violations
pf core check-trace \
  --file pf-core/examples/valid/file_read_allowed_trace.json

# Emit a certificate for a safe trace
pf core emit-certificate \
  --trace pf-core/examples/valid/file_read_allowed_trace.json
```

New to the project? The [hands-on tutorial](docs/pf-core/tutorial.md) walks through the pipeline without requiring Lean.

---

## Repository layout

```
provability-fabric-core/
├── pf-core/
│   ├── lean/PFCore/       Formal model and proofs (Lean 4)
│   ├── schemas/           JSON schema definitions
│   ├── examples/          Valid and invalid test fixtures
│   ├── validator/         Python CLI and runtime bridge
│   └── docs/              Technical deep-dives
├── adapters/              Reference log normalizers (outside trusted core)
├── docs/pf-core/          Guides, tutorials, and boundary documentation
└── scripts/               CI helpers and cross-repo smoke tests
```
