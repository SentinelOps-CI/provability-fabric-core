# PF-Core trusted gate (PowerShell)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $Root

$env:PYTHONPATH = Join-Path $Root "pf-core\validator"

# Optional deps; gate uses PYTHONPATH (editable install often fails on Windows).
try {
  python -m pip install -q setuptools wheel jsonschema referencing *> $null
  python -m pip install -q -e pf-core/validator *> $null
} catch {
  Write-Host "Note: pip install skipped; using PYTHONPATH"
}

Push-Location pf-core/lean
lake build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Pop-Location

python -m pf_core.cli core schema-check --schemas pf-core/schemas
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python pf-core/scripts/gen_fixtures.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python pf-core/scripts/validate_examples.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pf_core.cli core audit-boundary --root .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "pf-core-trusted: all checks passed"
