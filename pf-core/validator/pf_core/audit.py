"""Trusted boundary audit for PF-Core."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pf_core.errors import PFCoreError

V0_OBSERVATION = "pf-core.runtime_observation.v0"

FORBIDDEN_PHRASES = [
    "fully secure",
    "provably safe in production",
    "guarantees no data exfiltration",
    "trustless",
    "zero trust",
    "proves the llm cannot",
    "cryptographically proves",
    "pf-core verifies agents",
    "pf-core guarantees ai safety",
    "pf-core proves model alignment",
    "pf-core proves the runtime is secure",
    "pf-core proves non-interference for the whole platform",
    "pf-core proves all provability fabric claims",
]

SORRY_PATTERN = re.compile(r"\b(sorry|admit)\b")
AXIOM_PATTERN = re.compile(r"\baxiom\b")
UNSAFE_PATTERN = re.compile(r"\bunsafe\b")
AUTO_IMPLICIT_PATTERN = re.compile(r"set_option\s+autoImplicit\s+true")

TRUSTED_PATHS = [
    "pf-core/lean/PFCore",
    "pf-core/schemas",
    "pf-core/examples",
    "pf-core/validator/pf_core",
    "docs/pf-core",
    "pf-core/docs",
]

REQUIRED_DOCS = [
    "docs/pf-core/mission.md",
    "docs/pf-core/trusted-boundary.md",
    "docs/pf-core/claim-boundary.md",
    "docs/pf-core/assumptions.md",
    "docs/pf-core/README.md",
    "docs/pf-core/tutorial.md",
    "docs/pf-core/ecosystem-inventory.md",
    "docs/pf-core/acceptance.md",
    "pf-core/docs/formal-model.md",
    "pf-core/docs/threat-model.md",
    "pf-core/docs/examples.md",
    "pf-core/docs/adapter-contract.md",
    "pf-core/docs/certificate-semantics.md",
]

TRUSTED_BOUNDARY_DOC = "docs/pf-core/trusted-boundary.md"

LEAN_FILES = [
    "pf-core/lean/PFCore/Basic.lean",
    "pf-core/lean/PFCore/Principal.lean",
    "pf-core/lean/PFCore/CapabilityCatalog.lean",
    "pf-core/lean/PFCore/Capability.lean",
    "pf-core/lean/PFCore/Effect.lean",
    "pf-core/lean/PFCore/Action.lean",
    "pf-core/lean/PFCore/Decision.lean",
    "pf-core/lean/PFCore/EventKind.lean",
    "pf-core/lean/PFCore/Event.lean",
    "pf-core/lean/PFCore/Trace.lean",
    "pf-core/lean/PFCore/Contract.lean",
    "pf-core/lean/PFCore/StatefulContract.lean",
    "pf-core/lean/PFCore/Invariant.lean",
    "pf-core/lean/PFCore/Composition.lean",
    "pf-core/lean/PFCore/Handoff.lean",
    "pf-core/lean/PFCore/Certificate.lean",
    "pf-core/lean/PFCore/RuntimeObservation.lean",
    "pf-core/lean/PFCore/Assumption.lean",
    "pf-core/lean/PFCore/ClaimClassification.lean",
    "pf-core/lean/PFCore/Soundness.lean",
    "pf-core/lean/PFCore/Examples.lean",
    "pf-core/lean/PFCore/Replay.lean",
]

SCHEMA_FILES = [
    "pf-core/schemas/principal.schema.json",
    "pf-core/schemas/principal.v1.schema.json",
    "pf-core/schemas/capability.schema.json",
    "pf-core/schemas/resource.schema.json",
    "pf-core/schemas/effect.schema.json",
    "pf-core/schemas/action.schema.json",
    "pf-core/schemas/action.v1.schema.json",
    "pf-core/schemas/decision.schema.json",
    "pf-core/schemas/event.schema.json",
    "pf-core/schemas/event.v1.schema.json",
    "pf-core/schemas/trace.schema.json",
    "pf-core/schemas/contract.schema.json",
    "pf-core/schemas/handoff.schema.json",
    "pf-core/schemas/handoff.v1.schema.json",
    "pf-core/schemas/certificate.schema.json",
    "pf-core/schemas/runtime_observation.schema.json",
    "pf-core/schemas/runtime_observation.v1.schema.json",
    "pf-core/schemas/claim_classification.schema.json",
]

THEOREM_DOC_PATTERN = re.compile(
    r"/--\s*\n(?:.*\n)*?## Plain-English meaning",
    re.MULTILINE,
)


def _iter_trusted_files(root: Path):
    for rel in TRUSTED_PATHS:
        base = root / rel
        if not base.exists():
            continue
        if base.is_file():
            yield base
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {
                ".lean",
                ".md",
                ".py",
                ".json",
            }:
                yield path


def _check_documented_in_boundary(root: Path, rel_path: str) -> None:
    boundary = (root / TRUSTED_BOUNDARY_DOC).read_text(encoding="utf-8")
    name = Path(rel_path).name
    if name not in boundary and rel_path not in boundary:
        raise PFCoreError(
            "UndocumentedTrustedFile",
            f"{rel_path} not listed in {TRUSTED_BOUNDARY_DOC}",
        )


def audit_v1_primary_fixtures(root: Path) -> None:
    """Fail if trusted valid fixtures use v0 observations without legacy tagging."""
    examples = root / "pf-core" / "examples"
    if not examples.exists():
        return
    for path in sorted(examples.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != V0_OBSERVATION:
            continue
        rel = path.relative_to(examples).as_posix()
        if rel.startswith("valid/"):
            raise PFCoreError(
                "LegacyFixtureInTrustedPath",
                f"{rel} uses {V0_OBSERVATION}; valid fixtures must be v1-primary",
            )
        if not data.get("legacy"):
            raise PFCoreError(
                "LegacyFixtureUntagged",
                f"{rel} uses {V0_OBSERVATION} without \"legacy\": true",
            )


def audit_boundary(root: Path) -> None:
    lean_theorems_missing_docs: list[str] = []

    audit_v1_primary_fixtures(root)

    for doc in REQUIRED_DOCS:
        if not (root / doc).exists():
            raise PFCoreError("UndocumentedTrustedFile", f"missing required doc: {doc}")

    for rel in LEAN_FILES + SCHEMA_FILES:
        if not (root / rel).exists():
            raise PFCoreError("UndocumentedTrustedFile", f"missing trusted file: {rel}")
        _check_documented_in_boundary(root, rel)

    validator_modules = [
        "pf-core/validator/pf_core/compile.py",
        "pf-core/validator/pf_core/hash_chain.py",
        "pf-core/validator/pf_core/deciders.py",
        "pf-core/validator/pf_core/contracts.py",
        "pf-core/validator/pf_core/schemas.py",
        "pf-core/validator/pf_core/cli.py",
        "pf-core/validator/pf_core/emitter.py",
        "pf-core/validator/pf_core/audit_line.py",
        "pf-core/validator/pf_core/event_kind.py",
        "pf-core/validator/pf_core/audit.py",
        "pf-core/validator/pf_core/bundle_verify.py",
    ]
    for rel in validator_modules:
        if not (root / rel).exists():
            raise PFCoreError("UndocumentedTrustedFile", f"missing validator module: {rel}")

    for path in _iter_trusted_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()

        for phrase in FORBIDDEN_PHRASES:
            if phrase in lower and "forbidden" not in lower:
                rel = path.relative_to(root)
                if rel.as_posix() == "docs/pf-core/claim-boundary.md":
                    continue
                raise PFCoreError(
                    "ForbiddenClaimPhrase",
                    f"forbidden phrase {phrase!r} in {rel}",
                )

        if path.suffix == ".lean":
            if SORRY_PATTERN.search(text):
                raise PFCoreError("SorryFound", f"sorry/admit in {path}")
            if AXIOM_PATTERN.search(text):
                raise PFCoreError("AxiomFound", f"axiom in {path}")
            if UNSAFE_PATTERN.search(text):
                raise PFCoreError("UnsafeFound", f"unsafe in {path}")
            if AUTO_IMPLICIT_PATTERN.search(text):
                raise PFCoreError("AutoImplicitFound", f"autoImplicit true in {path}")

            if path.name == "Soundness.lean":
                continue

            for match in re.finditer(r"^theorem\s+(\w+)", text, re.MULTILINE):
                name = match.group(1)
                start = match.start()
                prefix = text[max(0, start - 800) : start]
                if "/--" not in prefix or "## Plain-English meaning" not in prefix:
                    lean_theorems_missing_docs.append(f"{path}:{name}")

    if lean_theorems_missing_docs:
        raise PFCoreError(
            "MissingTheoremDocstring",
            "theorems missing docstrings: " + ", ".join(lean_theorems_missing_docs[:10]),
        )
