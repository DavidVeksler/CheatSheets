<#
.SYNOPSIS
  Build the inside-ai-data-center GLB models: Blender (compose + validate + export), gltf-transform post-process, gates.
.EXAMPLE
  scripts/inside_ai_dc/build-models.ps1 -Stop 3
.NOTES
  Bash twin: build-models.sh. Needs Blender 4.5 LTS and `npm ci`.
#>
param([string]$Stop = 'all')
$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$blender = if ($env:BLENDER) { $env:BLENDER } else { 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' }
if (-not (Test-Path $blender)) { throw "Blender 4.5 not found at $blender; set `$env:BLENDER" }
if (-not (Test-Path (Join-Path $root 'node_modules\@gltf-transform\functions'))) { throw 'run npm ci first' }
$ids = switch ($Stop) { 'all' { @() } '3' { @('s3-rack') } '4' { @('s4-tray') } '5' { @('s5-superchip') } '6' { @('s6-gpu') } '7' { @('s7-hbm') } default { throw "unknown stop $Stop" } }
Push-Location $root
try {
  $start = Get-Date
  & $blender -b --factory-startup -P scripts/inside_ai_dc/blender/build.py -- --stop $Stop 2>&1 |
    Where-Object { $_ -match 'validate|VALIDATE|exported|Error|Traceback|File "' } | ForEach-Object { Write-Host $_ }
  foreach ($id in $(if ($ids.Count) { $ids } else { @('s3-rack', 's4-tray', 's5-superchip', 's6-gpu', 's7-hbm') })) {
    $meta = Join-Path $root "build\inside_ai_dc\raw\$id.meta.json"
    if (-not (Test-Path $meta) -or (Get-Item $meta).LastWriteTime -lt $start) { throw "Blender build or validation failed for $id" }
  }
  node scripts/inside_ai_dc/post.mjs @ids
  if ($LASTEXITCODE -ne 0) { throw "post.mjs failed ($LASTEXITCODE)" }
  python scripts/check_inside_ai_dc.py
  if ($LASTEXITCODE -ne 0) { throw "check_inside_ai_dc.py failed ($LASTEXITCODE)" }
} finally { Pop-Location }
