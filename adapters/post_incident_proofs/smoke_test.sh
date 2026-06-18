#!/usr/bin/env bash
# PIP smoke: emit PF-Core artifacts and document expected verify_bundle invocation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${TMPDIR:-/tmp}/pf-core-pip-smoke-$$"
OBS="$ROOT/pf-core/examples/valid/mcp_sidecar_observation.json"

python -m pip install -q -e "$ROOT/pf-core/validator" jsonschema referencing

export PYTHONPATH="$ROOT/pf-core/validator"
python -m pf_core.cli core emit-artifacts \
  --schemas "$ROOT/pf-core/schemas" \
  --file "$OBS" \
  --out-dir "$OUT"

for f in runtime_observation.json event.json trace.json certificate.json audit.jsonl; do
  test -f "$OUT/$f" || { echo "missing $f"; exit 1; }
done

echo "OK: PF-Core artifact bundle at $OUT"
echo "Expected PIP invocation (when post-incident-proofs is cloned):"
echo "  verify_bundle --bundle-dir $OUT --pf-core-version \$(cat $ROOT/pf-core/VERSION)"

if [ -d /tmp/post-incident-proofs/src ]; then
  echo "PIP clone detected; skipping verify_bundle (not wired in pf-core repo)"
else
  echo "SKIP: post-incident-proofs not cloned (see docs/pf-core/extraction-log.md pin)"
fi

rm -rf "$OUT"
