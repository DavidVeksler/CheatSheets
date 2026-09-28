# deploy-cloudflare.ps1: Windows entry point for scripts/deploy-cloudflare.sh (the logic lives there).
# Generated from ~/Projects/cf-static-kit/templates/site.
[CmdletBinding()]
param(
  [switch]$Yes,
  [switch]$PreviewOnly,
  [switch]$FullParity,
  [switch]$SkipParity
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Prefer Git Bash: `bash.exe` on PATH can resolve to WSL, whose Node may be too old.
$candidates = @(
  "C:\Program Files\Git\bin\bash.exe",
  "C:\Program Files\Git\usr\bin\bash.exe",
  "C:\Program Files (x86)\Git\bin\bash.exe"
)
$git = Get-Command git.exe -ErrorAction SilentlyContinue
if ($git) { $candidates += (Join-Path (Split-Path (Split-Path $git.Source -Parent) -Parent) "bin\bash.exe") }
$bash = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $bash) { throw "Git Bash not found. Install Git for Windows or run scripts/deploy-cloudflare.sh from Bash." }

$deployArgs = @("scripts/deploy-cloudflare.sh")
if ($Yes) { $deployArgs += "--yes" }
if ($PreviewOnly) { $deployArgs += "--preview-only" }
if ($FullParity) { $deployArgs += "--full-parity" }
if ($SkipParity) { $deployArgs += "--skip-parity" }

Push-Location (Split-Path $PSScriptRoot -Parent)
try {
  & $bash @deployArgs
  if ($LASTEXITCODE -ne 0) { throw "deploy.sh failed with exit code $LASTEXITCODE" }
} finally {
  Pop-Location
}
