#!/usr/bin/env bash
# Phase 6 end-to-end replay gate: sidecar → normalize → compile → check-trace → certificate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCHEMAS="$ROOT/pf-core/schemas"
VALIDATOR="$ROOT/pf-core/validator"
WORK="${TMPDIR:-/tmp}/pf-core-e2e-$$"
GOLDEN_TRACES=(
  "$ROOT/pf-core/examples/valid/file_read_allowed_trace.json"
  "$ROOT/pf-core/examples/valid/handoff_trace.json"
  "$ROOT/pf-core/examples/valid/pcs_replay_trace.json"
)

export PYTHONPATH="$VALIDATOR"
PF="python -m pf_core.cli core"

mkdir -p "$WORK"

run_pass() {
  local name="$1"
  shift
  echo "== scenario PASS: $name"
  "$@"
}

run_fail() {
  local name="$1"
  shift
  echo "== scenario FAIL (expected): $name"
  if "$@"; then
    echo "ERROR: expected failure for $name"
    exit 1
  fi
}

pipeline_from_observation() {
  local obs="$1"
  local out="$2"
  local lean="${3:-false}"
  mkdir -p "$out"
  $PF compile-observation --schemas "$SCHEMAS" --file "$obs" --output "$out/event.json"
  $PF validate-event --schemas "$SCHEMAS" --file "$out/event.json" >/dev/null
  cp "$obs" "$out/runtime_observation.json"
  python - <<PY
import json
from pathlib import Path
from pf_core.hash_chain import compute_trace_hash
from pf_core.emitter import build_trace

out = Path("$out")
event = json.loads((out / "event.json").read_text())
trace = build_trace([event])
(out / "trace.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n")
PY
  local lean_flag=""
  if [ "$lean" = "true" ]; then
    lean_flag="--lean-check"
  fi
  $PF check-trace --schemas "$SCHEMAS" --file "$out/trace.json" $lean_flag >/dev/null
  $PF emit-certificate --schemas "$SCHEMAS" --trace "$out/trace.json" --output "$out/certificate.json" >/dev/null
  $PF schema-check --schemas "$SCHEMAS" >/dev/null
  python - <<PY
import json
from pathlib import Path
from pf_core.schemas import load_registry, validate_object
registry = load_registry(Path("$SCHEMAS"))
cert = json.loads(Path("$out/certificate.json").read_text())
validate_object(cert, registry)
assert cert.get("safe") is True
PY
}

# 1. File read allow (v1 observation via compile path)
run_pass "file-read-allow" pipeline_from_observation \
  "$ROOT/pf-core/examples/valid/file_read_observation.json" \
  "$WORK/file-read" false

# 2. MCP sidecar normalize → pipeline
run_pass "mcp-sidecar" bash -c "
  python - <<'PY'
import importlib.util, json, sys
from pathlib import Path
root = Path('$ROOT')
sys.path.insert(0, str(root / 'pf-core' / 'validator'))
spec = importlib.util.spec_from_file_location(
    'normalize', root / 'adapters/provability-fabric/mcp_sidecar/normalize.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
line = json.loads((root / 'adapters/provability-fabric/tests/fixtures/sidecar_audit_line.json').read_text())
obs = mod.normalize_sidecar_line(line)
out = Path('$WORK/mcp/observation.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(obs, indent=2, sort_keys=True) + '\n')
PY
  bash '$0' __internal_pipeline '$WORK/mcp/observation.json' '$WORK/mcp' false
" "$0"

if [ "${1:-}" = "__internal_pipeline" ]; then
  pipeline_from_observation "$2" "$3" "${4:-false}"
  exit 0
fi

# 3. File read deny stays in trace (compile downgrades unsafe allow)
run_pass "file-read-deny-compile" bash -c "
  python - <<'PY'
import json, sys
from pathlib import Path
root = Path('$ROOT')
sys.path.insert(0, str(root / 'pf-core' / 'validator'))
from pf_core.compile import compile_observation
obs = json.loads((root / 'pf-core/examples/valid/file_read_observation.json').read_text())
obs['decision'] = 'allowed'
obs['action']['reads'][0]['tenant_id'] = 'tenant-b'
out = Path('$WORK/deny/observation.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(obs, indent=2) + '\n')
event = compile_observation(json.loads(out.read_text()))
assert event['decision'] == 'denied', event['decision']
PY
"

# 4. Handoff subset deny
run_fail "handoff-subset-deny" $PF check-trace \
  --schemas "$SCHEMAS" \
  --file "$ROOT/pf-core/examples/invalid/handoff_trace_unsafe.json"

# 5. PCS replay trace
run_pass "pcs-replay" $PF check-trace \
  --schemas "$SCHEMAS" \
  --file "$ROOT/pf-core/examples/valid/pcs_replay_trace.json"

# 6. Tampered hash must fail
run_fail "tampered-hash" $PF check-trace \
  --schemas "$SCHEMAS" \
  --file "$ROOT/pf-core/examples/invalid/trace_tampered_chain.json"

# 7. Lean replay on 3 golden traces
for trace in "${GOLDEN_TRACES[@]}"; do
  run_pass "lean-check $(basename "$trace")" $PF check-trace \
    --schemas "$SCHEMAS" \
    --file "$trace" \
    --lean-check
done

# 8. Handoff validate-handoff CLI + audit.jsonl from handoff trace
run_pass "handoff-validate-cli" $PF validate-handoff \
  --schemas "$SCHEMAS" \
  --file "$ROOT/pf-core/examples/valid/handoff.json"

run_pass "handoff-artifact-audit" python - <<PY
import json
from pathlib import Path
import sys
sys.path.insert(0, "$VALIDATOR")
from pf_core.emitter import emit_audit_for_trace
from pf_core.audit_line import AUDIT_SCHEMA_VERSION

root = Path("$ROOT")
trace = json.loads((root / "pf-core/examples/valid/handoff_trace.json").read_text())
handoff = trace["events"][0]["event_kind"]["handoff"]
observation = {
    "policy_ref": "policy/default.v0",
    "evidence_ref": handoff["evidence_ref"],
}
out = Path("$WORK/handoff-audit")
out.mkdir(parents=True, exist_ok=True)
emit_audit_for_trace(
    trace,
    out_path=out / "audit.jsonl",
    trace_id="trace-handoff-1",
    observation=observation,
    runtime_id="pf-core-e2e",
)
line = json.loads((out / "audit.jsonl").read_text().strip())
assert line["schema_version"] == AUDIT_SCHEMA_VERSION
assert line["capability"] == "cap:handoff"
assert line["principal_id"] == "agent-1"
PY

# 9. Email send observation pipeline
run_pass "email-send" pipeline_from_observation \
  "$ROOT/pf-core/examples/valid/email_send_observation.json" \
  "$WORK/email-send" false

# 10. Network denied observation (compile preserves denied)
run_pass "network-denied-obs" pipeline_from_observation \
  "$ROOT/pf-core/examples/valid/network_denied_observation.json" \
  "$WORK/network-denied" false

# 11. Lab release observation + contract check
run_pass "lab-release-contract" bash -c "
  bash '$0' __internal_pipeline \
    '$ROOT/pf-core/examples/valid/lab_release_observation.json' \
    '$WORK/lab-release' false
  $PF check-trace \
    --schemas '$SCHEMAS' \
    --file '$WORK/lab-release/trace.json' \
    --contract '$ROOT/pf-core/examples/valid/lab_release_contract.json' >/dev/null
" "$0"

rm -rf "$WORK"
echo "OK: pf-core-e2e all scenarios passed"
