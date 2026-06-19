#!/usr/bin/env bash
# Phase 7 cross-repo verification harness (provability-fabric-core).
# Runs in-repo gates and prints parent-repo checklist pointers.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DOCS="$ROOT/docs/pf-core"
export PYTHONPATH="$ROOT/pf-core/validator"

echo "=== Phase 7 cross-repo smoke (provability-fabric-core) ==="
echo "Checklists:"
echo "  - $DOCS/phase7-provability-fabric-checklist.md"
echo "  - $DOCS/phase7-pcs-checklist.md"
echo "  - $DOCS/phase7-pip-checklist.md"
echo "  - $DOCS/phase7-cross-repo-verification.md"
echo ""

step() { echo ""; echo ">>> $1"; }

step "Step 1a: pf-core-trusted"
if command -v make >/dev/null 2>&1 && [ -f Makefile ]; then
  make pf-core-trusted
else
  python -m pip install -q setuptools wheel jsonschema referencing
  python -m pip install -q -e pf-core/validator
  (cd pf-core/lean && lake build)
  python -m pf_core.cli core schema-check --schemas pf-core/schemas
  python pf-core/scripts/gen_fixtures.py
  python pf-core/scripts/validate_examples.py
  python -m pf_core.cli core audit-boundary --root .
fi

step "Step 1b: pf-core-e2e"
if command -v make >/dev/null 2>&1; then
  make pf-core-e2e
else
  bash "$ROOT/pf-core/scripts/e2e-replay-gate.sh"
fi

step "Step 1c: adapter + validator pytest"
python -m pip install -q setuptools wheel jsonschema referencing pytest
python -m pip install -q -e pf-core/validator
pytest adapters/provability-fabric/tests adapters/pcs/tests pf-core/validator/tests -v

step "Step 1d: PIP smoke (emit-artifacts + verify_bundle probe)"
bash adapters/post_incident_proofs/smoke_test.sh

echo ""
echo "=== In-repo gates: PASS ==="
echo ""
echo "=== Parent-repo work (blocked until PRs merge) ==="
echo "[ ] provability-fabric PR-1: native runtime_observation.v1 from sidecar-watcher"
echo "[ ] provability-fabric PR-2: pf-core schema dependency + CI schema-check"
echo "[ ] provability-fabric PR-3: pf core CLI wrapper"
echo "[ ] provability-fabric PR-4: admission-controller compile parity"
echo "[ ] pcs-core PR-1: docs/pf-core-trace-mapping.md"
echo "[ ] pcs-core PR-2: shared hash vector CI"
echo "[ ] post-incident-proofs PR-1: verify_bundle PF-Core five-file layout"
echo "[ ] post-incident-proofs PR-2: release forensic gate"
echo ""
echo "After parent PRs: re-run this script and complete Step 2-5 in phase7-cross-repo-verification.md"
