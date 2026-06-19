<div align="center">

# Provability Fabric Core

**Machine-checked safety for AI agent actions — from runtime logs to verifiable certificates.**

<br/>

[![pf-core-trusted](https://github.com/SentinelOps-CI/provability-fabric-core/actions/workflows/pf-core-trusted.yml/badge.svg)](https://github.com/SentinelOps-CI/provability-fabric-core/actions/workflows/pf-core-trusted.yml)
[![Lean 4](https://img.shields.io/badge/Lean-4-2C3E50?style=flat-square)](https://leanprover.github.io/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.6.0-6C757D?style=flat-square)](pf-core/VERSION)

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

## Verify locally

```bash
make pf-core-trusted
```

On Windows (PowerShell):

```powershell
powershell -File pf-core/scripts/pf-core-trusted.ps1
```

Requires [Lean 4](https://leanprover.github.io/) (via `elan`) and Python 3.10+.

## Layout

```
pf-core/
  lean/PFCore/     # Formal kernel (Lean 4)
  schemas/         # JSON schemas (pf-core.*.v0)
  examples/        # Valid/invalid fixtures
  validator/       # Runtime bridge + CLI
docs/pf-core/      # Boundary documentation
```
