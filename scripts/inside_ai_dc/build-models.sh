#!/usr/bin/env bash
# Build the inside-ai-data-center GLB models: Blender (compose + validate + export), gltf-transform post-process, gates.
# Usage: scripts/inside_ai_dc/build-models.sh [3|4|5|6|7|all]      PowerShell twin: build-models.ps1
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
stop="${1:-all}"
blender="${BLENDER:-}"
if [ -z "$blender" ]; then
  for c in "/c/Program Files/Blender Foundation/Blender 4.5/blender.exe" "$(command -v blender || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && blender="$c" && break
  done
fi
[ -n "$blender" ] || { echo "Blender 4.5 not found; set BLENDER=/path/to/blender" >&2; exit 1; }
cd "$root"
[ -d node_modules/@gltf-transform/functions ] || { echo "run npm ci first" >&2; exit 1; }
mkdir -p build/inside_ai_dc && touch build/inside_ai_dc/.build-start
"$blender" -b --factory-startup -P scripts/inside_ai_dc/blender/build.py -- --stop "$stop" 2>&1 | grep -E "validate|VALIDATE|exported|Error|Traceback|File \"" || true
case "$stop" in
  all) ids="" ;;
  3) ids="s3-rack" ;;
  4) ids="s4-tray" ;;
  5) ids="s5-superchip" ;;
  6) ids="s6-gpu" ;;
  7) ids="s7-hbm" ;;
  *) echo "unknown stop $stop" >&2; exit 1 ;;
esac
for id in ${ids:-s3-rack s4-tray s5-superchip s6-gpu s7-hbm}; do
  [ "build/inside_ai_dc/raw/$id.meta.json" -nt build/inside_ai_dc/.build-start ] || { echo "Blender build or validation failed for $id" >&2; exit 1; }
done
node scripts/inside_ai_dc/post.mjs $ids
python scripts/check_inside_ai_dc.py
