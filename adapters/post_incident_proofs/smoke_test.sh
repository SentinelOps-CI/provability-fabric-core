#!/usr/bin/env bash
# PIP smoke: emit PF-Core artifacts; call verify_bundle when PIP clone supports PF layout.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${TMPDIR:-/tmp}/pf-core-pip-smoke-$$"
OBS="$ROOT/pf-core/examples/valid/mcp_sidecar_observation.json"
PIP_SHA="d5f3051b927f2f68cabac1a37c85d5113b9d77ad"
VERSION="$(cat "$ROOT/pf-core/VERSION")"

export PYTHONPATH="$ROOT/pf-core/validator"

if [ -z "${PYTHON:-}" ]; then
  for candidate in python python3 "py -3"; do
    if command -v ${candidate%% *} >/dev/null 2>&1; then
      if $candidate -c "import pf_core" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
      fi
    fi
  done
  PYTHON="${PYTHON:-python3}"
  command -v ${PYTHON%% *} >/dev/null 2>&1 || PYTHON=python
fi

if ! $PYTHON -c "import pf_core, referencing, jsonschema" >/dev/null 2>&1; then
  if [ -n "${PYTHONPATH:-}" ]; then
    echo "ERROR: pf_core not importable (PYTHON=$PYTHON, PYTHONPATH=$PYTHONPATH)"
    echo "Install pf-core-validator or set PYTHON to an interpreter with dependencies."
    exit 1
  fi
  $PYTHON -m pip install -q setuptools wheel jsonschema referencing
  $PYTHON -m pip install -q -e "$ROOT/pf-core/validator" jsonschema referencing 2>/dev/null || true
fi

$PYTHON -m pf_core.cli core emit-artifacts \
  --schemas "$ROOT/pf-core/schemas" \
  --file "$OBS" \
  --out-dir "$OUT"

for f in runtime_observation.json event.json trace.json certificate.json audit.jsonl; do
  test -f "$OUT/$f" || { echo "missing $f"; exit 1; }
done

echo "OK: PF-Core artifact bundle at $OUT"

echo "Running local pf core verify-bundle (reference verifier)"
$PYTHON -m pf_core.cli core verify-bundle \
  --schemas "$ROOT/pf-core/schemas" \
  --bundle-dir "$OUT" \
  --pf-core-version "$VERSION"
echo "OK: local verify-bundle passed"

_find_pip_root() {
  local candidate
  for candidate in \
    "/tmp/post-incident-proofs" \
    "$ROOT/../post-incident-proofs" \
    "$ROOT/../../post-incident-proofs"; do
    if [ -d "$candidate/src" ] && [ -f "$candidate/lakefile.lean" ]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

_pip_supports_pf_core_bundle() {
  local pip_root="$1"
  local verify="$pip_root/src/VerifyBundle.lean"
  if [ ! -f "$verify" ]; then
    return 1
  fi
  if grep -qE 'pf-core|pf_core|--bundle-dir|--pf-core-version|PFCoreArtifacts' "$verify"; then
    return 0
  fi
  return 1
}

_run_verify_bundle() {
  local pip_root="$1"
  echo "PIP clone at $pip_root (pin $PIP_SHA); invoking verify_bundle"
  (
    cd "$pip_root"
    if lake exe verify_bundle --help 2>/dev/null | grep -q 'bundle-dir'; then
      lake exe verify_bundle --bundle-dir "$OUT" --pf-core-version "$VERSION"
    elif lake exe verify_bundle --help 2>/dev/null | grep -q 'pf-core'; then
      lake exe verify_bundle "$OUT" --pf-core-version "$VERSION"
    else
      lake exe verify_bundle --bundle-dir "$OUT" --pf-core-version "$VERSION"
    fi
  )
}

if PIP_ROOT="$(_find_pip_root)"; then
  if _pip_supports_pf_core_bundle "$PIP_ROOT"; then
    _run_verify_bundle "$PIP_ROOT"
    echo "OK: verify_bundle accepted PF-Core artifact layout"
  else
    echo "SKIP: verify_bundle at pin $PIP_SHA does not yet accept PF-Core layout (PIP PR-1 pending)"
    echo "Documented invocation for post-incident-proofs PR-1:"
    echo "  verify_bundle --bundle-dir $OUT --pf-core-version $VERSION"
    echo "  # or: cd $PIP_ROOT && lake exe verify_bundle -- $OUT --pf-core-version $VERSION"
  fi
else
  echo "SKIP: post-incident-proofs not cloned (see docs/pf-core/extraction-log.md pin $PIP_SHA)"
  echo "Expected PIP invocation when clone present:"
  echo "  verify_bundle --bundle-dir $OUT --pf-core-version $VERSION"
fi

rm -rf "$OUT"
