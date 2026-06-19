# PF-Core end-to-end replay gate (PowerShell)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Schemas = Join-Path $Root "pf-core\schemas"
$Validator = Join-Path $Root "pf-core\validator"
$Work = Join-Path $env:TEMP "pf-core-e2e-$PID"
$env:PYTHONPATH = $Validator

New-Item -ItemType Directory -Force -Path $Work | Out-Null

function Invoke-PfCore {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
  & python -m pf_core.cli core @Args
  if ($LASTEXITCODE -ne 0) { throw "pf core failed: $Args" }
}

function Pipeline-From-Observation {
  param([string]$ObsPath, [string]$OutDir, [switch]$LeanCheck)
  New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
  Invoke-PfCore compile-observation --schemas $Schemas --file $ObsPath --output (Join-Path $OutDir "event.json")
  Invoke-PfCore validate-event --schemas $Schemas --file (Join-Path $OutDir "event.json") | Out-Null
  Copy-Item $ObsPath (Join-Path $OutDir "runtime_observation.json")
  python -c @"
import json
from pathlib import Path
import sys
sys.path.insert(0, r'$Validator')
from pf_core.emitter import build_trace
out = Path(r'$OutDir')
event = json.loads((out / 'event.json').read_text())
trace = build_trace([event])
(out / 'trace.json').write_text(json.dumps(trace, indent=2, sort_keys=True) + '\n')
"@
  $leanFlag = @()
  if ($LeanCheck) { $leanFlag = @("--lean-check") }
  Invoke-PfCore check-trace --schemas $Schemas --file (Join-Path $OutDir "trace.json") @leanFlag | Out-Null
  Invoke-PfCore emit-certificate --schemas $Schemas --trace (Join-Path $OutDir "trace.json") --output (Join-Path $OutDir "certificate.json") | Out-Null
  Invoke-PfCore schema-check --schemas $Schemas | Out-Null
  python -c @"
import json
from pathlib import Path
import sys
sys.path.insert(0, r'$Validator')
from pf_core.schemas import load_registry, validate_object
registry = load_registry(Path(r'$Schemas'))
cert = json.loads(Path(r'$OutDir/certificate.json').read_text())
validate_object(cert, registry)
assert cert['safe'] is True
"@
}

Write-Host "== scenario PASS: file-read-allow"
Pipeline-From-Observation (Join-Path $Root "pf-core\examples\valid\file_read_observation.json") (Join-Path $Work "file-read")

Write-Host "== scenario PASS: mcp-sidecar"
$normalizeScript = Join-Path $Root "adapters\provability-fabric\mcp_sidecar\normalize.py"
$sidecarFixture = Join-Path $Root "adapters\provability-fabric\tests\fixtures\sidecar_audit_line.json"
python -c @"
import importlib.util, json, sys
from pathlib import Path
root = Path(r'$Root')
sys.path.insert(0, str(root / 'pf-core' / 'validator'))
spec = importlib.util.spec_from_file_location('normalize', Path(r'$normalizeScript'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
line = json.loads(Path(r'$sidecarFixture').read_text())
obs = mod.normalize_sidecar_line(line)
out = Path(r'$Work\mcp\observation.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(obs, indent=2, sort_keys=True) + '\n')
"@
Pipeline-From-Observation (Join-Path $Work "mcp\observation.json") (Join-Path $Work "mcp")

Write-Host "== scenario PASS: file-read-deny-compile"
python -c @"
import json, sys
from pathlib import Path
sys.path.insert(0, r'$Validator')
from pf_core.compile import compile_observation
obs = json.loads(Path(r'$Root/pf-core/examples/valid/file_read_observation.json').read_text())
obs['decision'] = 'allowed'
obs['action']['reads'][0]['tenant_id'] = 'tenant-b'
event = compile_observation(obs)
assert event['decision'] == 'denied', event['decision']
"@

Write-Host "== scenario FAIL (expected): handoff-subset-deny"
try {
  Invoke-PfCore check-trace --schemas $Schemas --file (Join-Path $Root "pf-core\examples\invalid\handoff_trace_unsafe.json")
  throw "expected handoff failure"
} catch {
  if ($_.Exception.Message -eq "expected handoff failure") { throw }
}

Write-Host "== scenario PASS: pcs-replay"
Invoke-PfCore check-trace --schemas $Schemas --file (Join-Path $Root "pf-core\examples\valid\pcs_replay_trace.json") | Out-Null

Write-Host "== scenario FAIL (expected): tampered-hash"
try {
  Invoke-PfCore check-trace --schemas $Schemas --file (Join-Path $Root "pf-core\examples\invalid\trace_tampered_chain.json")
  throw "expected tamper failure"
} catch {
  if ($_.Exception.Message -eq "expected tamper failure") { throw }
}

$goldens = @(
  "file_read_allowed_trace.json",
  "handoff_trace.json",
  "pcs_replay_trace.json"
)
foreach ($g in $goldens) {
  Write-Host "== scenario PASS: lean-check $g"
  Invoke-PfCore check-trace --schemas $Schemas --file (Join-Path $Root "pf-core\examples\valid\$g") --lean-check | Out-Null
}

Write-Host "== scenario PASS: handoff-validate-cli"
Invoke-PfCore validate-handoff --schemas $Schemas --file (Join-Path $Root "pf-core\examples\valid\handoff.json") | Out-Null

Write-Host "== scenario PASS: handoff-artifact-audit"
python -c @"
import json
from pathlib import Path
import sys
sys.path.insert(0, r'$Validator')
from pf_core.emitter import emit_audit_for_trace
from pf_core.schemas import load_registry, validate_object
from pf_core.audit_line import AUDIT_SCHEMA_VERSION

root = Path(r'$Root')
trace = json.loads((root / 'pf-core/examples/valid/handoff_trace.json').read_text())
handoff = trace['events'][0]['event_kind']['handoff']
observation = {
    'policy_ref': 'policy/default.v0',
    'evidence_ref': handoff['evidence_ref'],
}
out = Path(r'$Work\handoff-audit')
out.mkdir(parents=True, exist_ok=True)
emit_audit_for_trace(
    trace,
    out_path=out / 'audit.jsonl',
    trace_id='trace-handoff-1',
    observation=observation,
    runtime_id='pf-core-e2e',
)
line = json.loads((out / 'audit.jsonl').read_text().strip())
assert line['schema_version'] == AUDIT_SCHEMA_VERSION
assert line['capability'] == 'cap:handoff'
assert line['principal_id'] == 'agent-1'
"@

Write-Host "== scenario PASS: email-send"
Pipeline-From-Observation (Join-Path $Root "pf-core\examples\valid\email_send_observation.json") (Join-Path $Work "email-send")

Write-Host "== scenario PASS: network-denied-obs"
Pipeline-From-Observation (Join-Path $Root "pf-core\examples\valid\network_denied_observation.json") (Join-Path $Work "network-denied")

Write-Host "== scenario PASS: lab-release-contract"
Pipeline-From-Observation (Join-Path $Root "pf-core\examples\valid\lab_release_observation.json") (Join-Path $Work "lab-release")
Invoke-PfCore check-trace `
  --schemas $Schemas `
  --file (Join-Path $Work "lab-release\trace.json") `
  --contract (Join-Path $Root "pf-core\examples\valid\lab_release_contract.json") | Out-Null

Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue
Write-Host "OK: pf-core-e2e all scenarios passed"
