"""Unit tests for hash chain utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pf_core.errors import InvalidHash
from pf_core.hash_chain import (
    canonical_json,
    compute_event_hash,
    compute_trace_hash,
    normalize_hash,
    validate_hash_chain,
    validate_trace_hashes,
)
from pf_core.schemas import GENESIS_HASH

ROOT = Path(__file__).resolve().parents[3]


def test_normalize_hash_hex64():
    h = "a" * 64
    assert normalize_hash(h) == h


def test_normalize_hash_sha256_uri():
    h = "a" * 64
    assert normalize_hash(f"sha256:{h}") == h


def test_normalize_hash_invalid_raises():
    with pytest.raises(InvalidHash):
        normalize_hash("not-a-hash")


def test_genesis_hash_is_zeros():
    assert GENESIS_HASH == "0" * 64


def test_compute_event_hash_deterministic():
    event = json.loads((ROOT / "pf-core/examples/valid/file_read_allowed.json").read_text())
    assert compute_event_hash(event) == event["event_hash"]


def test_validate_trace_hashes_passes_golden():
    trace = json.loads((ROOT / "pf-core/examples/valid/file_read_allowed_trace.json").read_text())
    validate_trace_hashes(trace)


def test_validate_hash_chain_rejects_tamper():
    event = json.loads((ROOT / "pf-core/examples/valid/file_read_allowed.json").read_text())
    event = dict(event)
    event["event_hash"] = "f" * 64
    with pytest.raises(InvalidHash):
        validate_hash_chain([event])


def test_canonical_json_sorted():
    obj = {"b": 1, "a": 2}
    assert canonical_json(obj) == '{"a":2,"b":1}'
