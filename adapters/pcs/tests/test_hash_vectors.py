"""PCS hash vector parity against PF-Core hash normalization (untrusted)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

import pytest

from pf_core.hash_chain import normalize_hash

SIGNATURE_FIELD = "signature_or_digest"


def _sort_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sort_keys(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [_sort_keys(item) for item in value]
    return value


def pcs_canonical_hash(data: Dict[str, Any]) -> str:
    """PCS v0.1.0 canonical hash (matches pcs_core.hash.canonical_hash)."""
    payload = dict(data)
    payload.pop(SIGNATURE_FIELD, None)
    canonical = _sort_keys(payload)
    digest = hashlib.sha256(
        json.dumps(canonical, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


FIXTURES = Path(__file__).parent / "fixtures" / "hash_vectors"


@pytest.mark.parametrize(
    "vector_dir",
    sorted(p for p in FIXTURES.iterdir() if p.is_dir()),
    ids=lambda p: p.name,
)
def test_pcs_hash_vector_parity(vector_dir: Path) -> None:
    input_path = vector_dir / "input.json"
    digest_path = vector_dir / "digest.txt"
    if not input_path.exists() or not digest_path.exists():
        pytest.skip("incomplete vector")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    expected = digest_path.read_text(encoding="utf-8").strip()
    computed = pcs_canonical_hash(data)
    assert computed == expected
    assert normalize_hash(computed) == normalize_hash(expected)
