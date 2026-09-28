#!/usr/bin/env bash
#
# deploy-forms-cloudflare.sh: guarded deploy of the newsletter forms Worker
# (workers/forms/, cheatsheets-davidveksler-com-forms), which replaced subscribe.php
# and confirm.php and now answers /subscribe and /confirm (the .php spellings too). It has no route of its own: the site Worker reaches it through
# the FORMS service binding, so it is public exactly when the site Worker is routed.
# Spec: docs/specs/cloudflare-migration.md §2.4. Kit: ~/Projects/cf-static-kit/docs/runbook.md §4.
#
# Flow: preflight (clean tree, token) -> local contract suite (npm run test:forms;
#   no email leaves the machine) -> site not routed yet: deploy, upload a `preview`
#   version and probe its health. Site routed (cut over): confirm, deploy, probe
#   https://cheatsheets.davidveksler.com/subscribe.php?health=1 (the spelling every
#   site Worker version forwards, so the probe holds whichever deploys first).
# Never submits a signup: the end-to-end test is one real sign-up by David.
#
# Usage: scripts/deploy-forms-cloudflare.sh [--yes] [--skip-tests]
set -euo pipefail
cd "$(dirname "$0")/.."

PROD="https://cheatsheets.davidveksler.com"
PREVIEW="https://preview-cheatsheets-davidveksler-com-forms.david-veksler-s-websites.workers.dev"
CF_ENV="$HOME/Projects/.cloudflare.env"
HEALTHY='{"ok":true,"store":"writable","token_secret":true,"sending_key":true,"notify":true}'

YES=0; SKIP_TESTS=0
for arg in "$@"; do
  case "$arg" in
    --yes|-y) YES=1 ;;
    --skip-tests) SKIP_TESTS=1 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done
step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok() { printf '  \033[1;32mOK\033[0m   %s\n' "$*"; }
die() { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }
PY="$(command -v python3 || command -v python || true)"

step "Preflight"
[ -z "$(git status --porcelain)" ] || die "working tree is not clean; commit first"
[ -d node_modules/wrangler ] || npm ci
if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  [ -f "$CF_ENV" ] || die "missing $CF_ENV"
  CLOUDFLARE_API_TOKEN="$(grep -m1 -oE '^CLOUDFLARE_API_TOKEN=[^[:space:]]+' "$CF_ENV" | cut -d= -f2)"
fi
[ -n "$CLOUDFLARE_API_TOKEN" ] || die "no CLOUDFLARE_API_TOKEN"
export CLOUDFLARE_API_TOKEN
W="$PWD/node_modules/.bin/wrangler"
# Live exactly when the site Worker has routes (its FORMS binding is the only way in).
if "$PY" - <<'PYEOF'
import json, re, sys
s = open("wrangler.jsonc", encoding="utf-8").read()
s = re.sub(r'("(?:\.|[^"\])*")|//[^\n]*|/\*.*?\*/', lambda m: m.group(1) or "", s, flags=re.S)
c = json.loads(re.sub(r",(\s*[}\]])", r"\1", s))
sys.exit(0 if (c.get("routes") or c.get("route")) else 1)
PYEOF
then ROUTED=1; ok "site Worker is routed: this deploy is live"; else ROUTED=0; ok "site Worker not routed: preview only"; fi

if [ "$SKIP_TESTS" -eq 0 ]; then
  step "Contract suite (local wrangler dev, Resend stub)"
  npm run -s test:forms
fi

probe() { # label url expected
  local body
  body="$(curl -s --max-time 20 "$2" || true)"
  [ "$body" = "$3" ] || die "$1: expected $3, got ${body:-<no response>}"
  ok "$1: $body"
}

cd workers/forms
if [ "$ROUTED" -eq 0 ]; then
  step "Deploy unrouted and upload the preview version"
  "$W" deploy
  "$W" versions upload --preview-alias preview --message "deploy $(git rev-parse --short HEAD)"
  sleep 5
  probe "preview health" "$PREVIEW/subscribe?health=1" "$HEALTHY"
  step "Preview ready, production unchanged: $PREVIEW"
  exit 0
fi

if [ "$YES" -ne 1 ]; then
  read -r -p "Deploy the forms Worker behind $PROD/subscribe and /confirm? [y/N] " reply
  [[ "$reply" =~ ^[Yy]([Ee][Ss])?$ ]] || { echo "Cancelled."; exit 0; }
fi
step "Deploy"
"$W" deploy
sleep 5
probe "live health" "$PROD/subscribe.php?health=1" "$HEALTHY"
step "Forms Worker deployed and healthy"
