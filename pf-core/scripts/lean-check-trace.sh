#!/usr/bin/env bash
# Optional Lean replay check for golden traces (B3).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TRACE="${1:-$ROOT/pf-core/examples/valid/file_read_allowed_trace.json}"
cd "$ROOT/pf-core/lean"
lake build PFCore.Replay
python -m pf_core.cli core check-trace \
  --schemas "$ROOT/pf-core/schemas" \
  --file "$TRACE" \
  --lean-check
echo "OK: lean-check-trace passed for $TRACE"
