#!/usr/bin/env bash
# Phase 7 parent-repo probe: Steps 2-5 from phase7-cross-repo-verification.md
# Run after in-repo Step 1 passes. Probes sibling clones when present; SKIP otherwise.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$ROOT/docs/pf-core"
PF_SHA="a567c8dca015fac3890fddbb77dfd254caa720d8"
PCS_SHA="280bbea4bf3bf3e45004b6254bc72b603030f179"
PIP_SHA="d5f3051b927f2f68cabac1a37c85d5113b9d77ad"
VERSION="$(cat "$ROOT/pf-core/VERSION")"

export PYTHONPATH="$ROOT/pf-core/validator"
PF="python -m pf_core.cli core"

step() { echo ""; echo ">>> $1"; }

_find_repo() {
  local name="$1"
  shift
  local candidate
  for candidate in "$@"; do
    if [ -d "$candidate/.git" ] || [ -f "$candidate/lakefile.lean" ] || [ -d "$candidate/runtime" ]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

step "Step 2: provability-fabric native path (pin $PF_SHA)"
if PF_ROOT="$(_find_repo provability-fabric /tmp/provability-fabric "$ROOT/../provability-fabric")"; then
  echo "Found provability-fabric at $PF_ROOT"
  if [ -f "$ROOT/adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json" ]; then
    python - <<PY
import importlib.util, json, sys
from pathlib import Path
root = Path("$ROOT")
sys.path.insert(0, str(root / "pf-core/validator"))
spec = importlib.util.spec_from_file_location(
    "normalize", root / "adapters/provability-fabric/mcp_sidecar/normalize.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
line = json.loads((root / "adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json").read_text())
obs = mod.normalize_sidecar_line(line)
from pf_core.schemas import load_registry, validate_object
from pf_core.compile import compile_observation
registry = load_registry(root / "pf-core/schemas")
validate_object(obs, registry)
compile_observation(obs)
print("OK: sidecar golden compiles through PF-Core path")
PY
  fi
  if [ -f "$PF_ROOT/runtime/sidecar-watcher" ] || [ -d "$PF_ROOT/runtime" ]; then
    echo "NOTE: verify native v1 emission in provability-fabric CI after PR-1 merge"
  fi
else
  echo "SKIP: provability-fabric not cloned (pin $PF_SHA)"
fi

step "Step 3: pcs-core hash parity (pin $PCS_SHA)"
python -m pytest -q "$ROOT/adapters/pcs/tests/"
if PCS_ROOT="$(_find_repo pcs-core /tmp/pcs-core "$ROOT/../pcs-core")"; then
  echo "Found pcs-core at $PCS_ROOT"
  if [ -f "$PCS_ROOT/docs/pf-core-trace-mapping.md" ]; then
    echo "OK: pcs-core has docs/pf-core-trace-mapping.md"
  else
    echo "PENDING: pcs-core missing docs/pf-core-trace-mapping.md (PR-1)"
  fi
else
  echo "SKIP: pcs-core not cloned (pin $PCS_SHA)"
fi

step "Step 4: post-incident-proofs bundle verify (pin $PIP_SHA)"
bash "$ROOT/adapters/post_incident_proofs/smoke_test.sh"

step "Step 5: real vision stack summary"
echo "Reference path documented in $DOCS/phase7-cross-repo-verification.md"
echo "  Sidecar -> runtime_observation.v1 -> compile -> check-trace -> emit-artifacts -> verify_bundle"
echo ""
echo "Parent PR checklists:"
echo "  $DOCS/phase7-provability-fabric-checklist.md"
echo "  $DOCS/phase7-pcs-checklist.md"
echo "  $DOCS/phase7-pip-checklist.md"
echo ""
echo "OK: parent probe complete (see SKIP/PENDING lines for blocked parent work)"
