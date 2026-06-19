# Phase 7 parent-repo probe: Steps 2-5 from phase7-cross-repo-verification.md
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Docs = Join-Path $Root "docs\pf-core"
$env:PYTHONPATH = Join-Path $Root "pf-core\validator"

function Step([string]$Label) {
  Write-Host ""
  Write-Host ">>> $Label"
}

Step "Step 2: provability-fabric native path"
$sidecar = Join-Path $Root "adapters\provability-fabric\tests\fixtures\sidecar_audit_line.json"
if (Test-Path $sidecar) {
  python -c @"
import importlib.util, json, sys
from pathlib import Path
root = Path(r'$Root')
sys.path.insert(0, str(root / 'pf-core/validator'))
spec = importlib.util.spec_from_file_location('normalize', root / 'adapters/provability-fabric/mcp_sidecar/normalize.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
line = json.loads(Path(r'$sidecar').read_text())
obs = mod.normalize_sidecar_line(line)
from pf_core.schemas import load_registry, validate_object
from pf_core.compile import compile_observation
registry = load_registry(root / 'pf-core/schemas')
validate_object(obs, registry)
compile_observation(obs)
print('OK: sidecar golden compiles through PF-Core path')
"@
} else {
  Write-Host "SKIP: sidecar golden fixture missing"
}

Step "Step 3: pcs-core hash parity"
python -m pytest -q (Join-Path $Root "adapters\pcs\tests")

Step "Step 4: post-incident-proofs bundle verify"
if (Get-Command bash -ErrorAction SilentlyContinue) {
  bash (Join-Path $Root "adapters\post_incident_proofs\smoke_test.sh")
} else {
  Write-Host "SKIP: bash not available for smoke_test.sh"
}

Step "Step 5: real vision stack summary"
Write-Host "Reference path: Sidecar -> observation -> compile -> emit-artifacts -> verify_bundle"
Write-Host "Checklists under $Docs"
Write-Host "OK: parent probe complete"
