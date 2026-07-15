#!/usr/bin/env bash
# Guarded deploy for cheatsheets.davidveksler.com (wraps scripts/deploy.py).
#   ./deploy.sh            # full pipeline with confirm
#   ./deploy.sh --yes      # no prompt
#   ./deploy.sh --dry-run  # validate only, don't push
# All arguments pass through to scripts/deploy.py.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if   [ -x "$root/.venv/bin/python" ];          then py="$root/.venv/bin/python"
elif [ -x "$root/.venv/Scripts/python.exe" ];  then py="$root/.venv/Scripts/python.exe"
elif command -v python  >/dev/null 2>&1;       then py=python
elif command -v python3 >/dev/null 2>&1;       then py=python3
else echo "deploy: no python interpreter found on PATH." >&2; exit 1
fi

exec "$py" "$root/scripts/deploy.py" "$@"
