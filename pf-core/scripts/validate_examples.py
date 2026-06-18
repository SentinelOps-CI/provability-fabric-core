"""Validate PF-Core example fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validator"))

from pf_core.compile import compile_observation
from pf_core.contracts import assert_trace_satisfies_contract
from pf_core.deciders import assert_action_semantics, event_safe, handoff_safe, trace_safe
from pf_core.errors import PFCoreError
from pf_core.event_kind import event_action
from pf_core.hash_chain import validate_hash_chain, validate_trace_hashes
from pf_core.schemas import load_registry, validate_object

SCHEMAS = ROOT / "schemas"
VALID = ROOT / "examples" / "valid"
INVALID = ROOT / "examples" / "invalid"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_valid(path: Path, registry) -> None:
    data = _load(path)
    kind = validate_object(data, registry)
    if kind == "event":
        validate_hash_chain([data])
        if not event_safe(data):
            raise PFCoreError("UnsafeEvent", f"valid fixture unsafe: {path.name}")
    elif kind == "trace":
        validate_trace_hashes(data)
        if not trace_safe(data):
            raise PFCoreError("UnsafeTrace", f"valid fixture unsafe: {path.name}")
    elif kind in {"handoff", "handoff_v1"}:
        if not handoff_safe(data):
            raise PFCoreError("UnsafeHandoff", f"valid fixture unsafe: {path.name}")
    elif kind == "contract":
        pass
    elif kind == "runtime_observation":
        event = compile_observation(data)
        validate_object(event, registry)


def _run_decider_check(data: dict, kind: str, path: Path) -> PFCoreError | None:
    if kind == "event":
        validate_hash_chain([data])
        if not event_safe(data):
            return PFCoreError("UnsafeEvent", f"unsafe event: {path.name}")
    elif kind == "trace":
        try:
            validate_trace_hashes(data)
        except PFCoreError as exc:
            return exc
        if not trace_safe(data):
            return PFCoreError("UnsafeTrace", f"unsafe trace: {path.name}")
    elif kind in {"handoff", "handoff_v1"}:
        if not handoff_safe(data):
            return PFCoreError("UnsafeHandoff", f"unsafe handoff: {path.name}")
    return None


def _validate_invalid(path: Path, registry) -> None:
    data = _load(path)
    expected = data.pop("expected_error", None)
    must_fail_at = data.pop("must_fail_at", None)
    if not expected:
        raise PFCoreError("FixtureError", f"invalid fixture missing expected_error: {path.name}")
    if not must_fail_at:
        raise PFCoreError("FixtureError", f"invalid fixture missing must_fail_at: {path.name}")

    try:
        if must_fail_at == "runtime_to_trace":
            compile_observation(data)
            raise PFCoreError("FixtureError", f"expected failure but passed: {path.name}")

        if must_fail_at == "action_semantics":
            assert_action_semantics(event_action(data))
            raise PFCoreError("FixtureError", f"expected failure but passed: {path.name}")

        if must_fail_at == "decision_check":
            event_safe(data)
            raise PFCoreError("FixtureError", f"expected failure but passed: {path.name}")

        kind = validate_object(data, registry)

        if must_fail_at == "schema_validation":
            raise PFCoreError("FixtureError", f"expected failure but passed: {path.name}")

        if must_fail_at == "decider_check":
            err = _run_decider_check(data, kind, path)
            if err is None:
                raise PFCoreError("FixtureError", f"expected failure but passed: {path.name}")
            if err.code != expected:
                raise PFCoreError(
                    "FixtureError",
                    f"{path.name}: expected {expected}, got {err.code}",
                )
            return

        raise PFCoreError("FixtureError", f"unknown must_fail_at: {must_fail_at}")
    except PFCoreError as exc:
        if exc.code != expected:
            raise PFCoreError(
                "FixtureError",
                f"{path.name}: expected {expected}, got {exc.code}",
            ) from exc


def test_compile_determinism() -> None:
    obs_path = VALID / "mcp_sidecar_observation.json"
    obs = _load(obs_path)
    first = compile_observation(obs)
    second = compile_observation(obs)
    if first != second:
        raise PFCoreError("DeterminismError", "compile(input) != compile(input)")


def main() -> int:
    registry = load_registry(SCHEMAS)
    for path in sorted(VALID.glob("*.json")):
        _validate_valid(path, registry)
    for path in sorted(INVALID.glob("*.json")):
        _validate_invalid(path, registry)
    test_compile_determinism()
    valid_n = len(list(VALID.glob("*.json")))
    invalid_n = len(list(INVALID.glob("*.json")))
    print(f"OK: {valid_n} valid, {invalid_n} invalid fixtures, determinism passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
