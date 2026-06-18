"""SHA-256 hash chain utilities (PCS-style canonical JSON)."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Mapping

from pf_core.errors import InvalidHash
from pf_core.schemas import GENESIS_HASH

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SHA256_URI = re.compile(r"^sha256:([0-9a-f]{64})$")


def normalize_hash(value: str) -> str:
    """Accept hex64 or `sha256:` URI prefix; return lowercase hex64."""
    if HEX64.match(value):
        return value
    match = SHA256_URI.match(value)
    if match:
        return match.group(1)
    raise InvalidHash(f"expected hex64 or sha256:hex64, got {value!r}", "hash")


def canonical_json(obj: Mapping[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payload_for_event_hash(event: Mapping[str, Any]) -> Dict[str, Any]:
    payload = dict(event)
    payload.pop("event_hash", None)
    return payload


def payload_for_trace_hash(trace: Mapping[str, Any]) -> Dict[str, Any]:
    payload = dict(trace)
    payload.pop("trace_hash", None)
    return payload


def compute_event_hash(event: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(
        canonical_json(payload_for_event_hash(event)).encode("utf-8")
    ).hexdigest()
    return digest


def compute_trace_hash(trace: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(
        canonical_json(payload_for_trace_hash(trace)).encode("utf-8")
    ).hexdigest()
    return digest


def compute_trace_hash_from_events(events: List[Mapping[str, Any]]) -> str:
    trace = {"schema_version": "pf-core.trace.v0", "events": events}
    return compute_trace_hash(trace)


def assert_hex64(value: str, path: str) -> None:
    try:
        normalize_hash(value)
    except InvalidHash as exc:
        raise InvalidHash(exc.message, path) from exc


def validate_hash_chain(events: List[Mapping[str, Any]]) -> None:
    prev = GENESIS_HASH
    for idx, event in enumerate(events):
        base = f"events[{idx}]"
        event_hash = normalize_hash(str(event.get("event_hash", "")))
        prev_field = normalize_hash(str(event.get("previous_event_hash", "")))
        if prev_field != prev:
            raise InvalidHash(
                "previous_event_hash mismatch: "
                f"expected {prev}, got {prev_field}",
                f"{base}.previous_event_hash",
            )
        expected = compute_event_hash(event)
        if event_hash != expected:
            raise InvalidHash(
                f"event_hash mismatch: expected {expected}, got {event_hash}",
                f"{base}.event_hash",
            )
        prev = event_hash


def validate_trace_hashes(trace: Mapping[str, Any]) -> None:
    events = list(trace["events"])
    validate_hash_chain(events)
    expected = compute_trace_hash(trace)
    actual = trace.get("trace_hash")
    if actual is None:
        raise InvalidHash("missing trace_hash", "trace_hash")
    actual_hex = normalize_hash(str(actual))
    if actual_hex != expected:
        raise InvalidHash(
            f"trace_hash mismatch: expected {expected}, got {actual_hex}",
            "trace_hash",
        )
