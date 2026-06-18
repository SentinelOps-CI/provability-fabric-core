"""JSON schema loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from pf_core.errors import InvalidSchemaVersion, PFCoreError


SCHEMA_KINDS = {
    "principal": "pf-core.principal.v0",
    "capability": "pf-core.capability.v0",
    "resource": "pf-core.resource.v0",
    "effect": "pf-core.effect.v0",
    "action": "pf-core.action.v0",
    "decision": "pf-core.decision.v0",
    "event": "pf-core.event.v1",
    "trace": "pf-core.trace.v0",
    "contract": "pf-core.contract.v0",
    "handoff": "pf-core.handoff.v0",
    "certificate": "pf-core.certificate.v0",
    "runtime_observation": "pf-core.runtime_observation.v0",
    "claim_classification": "pf-core.claim_classification.v0",
}

EFFECT_KINDS = {
    "file.read",
    "file.write",
    "network.egress",
    "email.send",
    "handoff.delegate",
    "mcp.invoke",
    "lab.release",
}

GENESIS_HASH = "0" * 64


def load_registry(schemas_dir: Path) -> Registry:
    resources: Dict[str, Resource] = {}
    for path in sorted(schemas_dir.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        schema_id = contents.get("$id", path.name)
        resources[schema_id] = Resource.from_contents(contents)
    return Registry().with_resources(resources.items())


def schema_for_kind(registry: Registry, kind: str) -> Draft202012Validator:
    version = SCHEMA_KINDS[kind]
    resource = registry.get(version)
    if resource is None:
        raise PFCoreError("SchemaNotFound", f"no schema for kind {kind}")
    return Draft202012Validator(resource.contents, registry=registry)


def infer_kind(obj: Mapping[str, Any]) -> str:
    version = obj.get("schema_version")
    if not isinstance(version, str):
        raise InvalidSchemaVersion("pf-core.*.v0", str(version))
    if version in {"pf-core.event.v0", "pf-core.event.v1"}:
        return "event"
    for kind, expected in SCHEMA_KINDS.items():
        if version == expected:
            return kind
    raise InvalidSchemaVersion("pf-core.*.v0", version)


def validate_object(obj: Mapping[str, Any], registry: Registry) -> str:
    kind = infer_kind(obj)
    validator = schema_for_kind(registry, kind)
    errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
    if errors:
        err = errors[0]
        path = "/".join(str(p) for p in err.path)
        raise PFCoreError("SchemaValidationError", err.message, path or None)
    return kind


def validate_schema_files(schemas_dir: Path) -> None:
    registry = load_registry(schemas_dir)
    for kind in SCHEMA_KINDS:
        schema_for_kind(registry, kind)
