# Phase 7 cross-repo verification harness (provability-fabric-core).
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

$Docs = Join-Path $Root "docs\pf-core"
$env:PYTHONPATH = Join-Path $Root "pf-core\validator"

Write-Host "=== Phase 7 cross-repo smoke (provability-fabric-core) ==="
Write-Host "Checklists:"
Write-Host "  - $Docs\phase7-provability-fabric-checklist.md"
Write-Host "  - $Docs\phase7-pcs-checklist.md"
Write-Host "  - $Docs\phase7-pip-checklist.md"
Write-Host "  - $Docs\phase7-cross-repo-verification.md"
Write-Host ""

function Step([string]$Label) {
  Write-Host ""
  Write-Host ">>> $Label"
}

Step "Step 1a: pf-core-trusted"
& (Join-Path $Root "pf-core\scripts\pf-core-trusted.ps1")

Step "Step 1b: pf-core-e2e"
& (Join-Path $Root "pf-core\scripts\e2e-replay-gate.ps1")

Step "Step 1c: adapter + validator pytest"
python -m pip install -q setuptools wheel jsonschema referencing pytest
python -m pip install -q -e pf-core/validator
python -m pytest adapters/provability-fabric/tests adapters/pcs/tests pf-core/validator/tests -v

Step "Step 1d: PIP smoke (emit-artifacts + verify_bundle probe)"
if (Get-Command bash -ErrorAction SilentlyContinue) {
  bash adapters/post_incident_proofs/smoke_test.sh
} else {
  Write-Host "SKIP: bash not available; run smoke_test.sh in Git Bash or WSL"
}

Step "Step 2: parent-repo probe (Steps 2-5)"
& (Join-Path $Root "scripts\phase7-parent-probe.ps1")

Write-Host ""
Write-Host "=== In-repo gates: PASS ==="
Write-Host ""
Write-Host "=== Parent-repo work (blocked until PRs merge) ==="
Write-Host "[ ] provability-fabric PR-1: native runtime_observation.v1 from sidecar-watcher"
Write-Host "[ ] provability-fabric PR-2: pf-core schema dependency + CI schema-check"
Write-Host "[ ] provability-fabric PR-3: pf core CLI wrapper"
Write-Host "[ ] provability-fabric PR-4: admission-controller compile parity"
Write-Host "[ ] pcs-core PR-1: docs/pf-core-trace-mapping.md"
Write-Host "[ ] pcs-core PR-2: shared hash vector CI"
Write-Host "[ ] post-incident-proofs PR-1: verify_bundle PF-Core five-file layout"
Write-Host "[ ] post-incident-proofs PR-2: release forensic gate"
Write-Host ""
Write-Host "After parent PRs: re-run this script and complete Step 2-5 in phase7-cross-repo-verification.md"
