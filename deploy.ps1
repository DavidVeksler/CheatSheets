<#
.SYNOPSIS
  Guarded deploy for cheatsheets.davidveksler.com (wraps scripts/deploy.py).
.EXAMPLE
  ./deploy.ps1            # full pipeline with confirm
  ./deploy.ps1 --yes      # no prompt
  ./deploy.ps1 --dry-run  # validate only, don't push
  All arguments are passed straight through to scripts/deploy.py.
#>
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
trap {
  Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$py =
  if     (Test-Path "$root/.venv/Scripts/python.exe") { "$root/.venv/Scripts/python.exe" }
  elseif (Test-Path "$root/.venv/bin/python")         { "$root/.venv/bin/python" }
  elseif (Get-Command python  -ErrorAction SilentlyContinue) { 'python' }
  elseif (Get-Command python3 -ErrorAction SilentlyContinue) { 'python3' }
  else { throw 'No python interpreter found on PATH.' }

& $py "$root/scripts/deploy.py" @args
if ($LASTEXITCODE -ne 0) { throw "scripts/deploy.py failed with exit code $LASTEXITCODE." }
