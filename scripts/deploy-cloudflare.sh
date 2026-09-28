#!/usr/bin/env bash
#
# deploy.sh: guarded deploy of a static site to Cloudflare Workers static assets.
# Generated from ~/Projects/cf-static-kit/templates/site; runbook (governing):
# ~/Projects/cf-static-kit/docs/runbook.md
#
# Flow: preflight -> build + gates -> upload a preview version -> parity check
# against production -> confirm -> promote version + apply routes -> live verify.
#
# Before cutover (no "routes" in wrangler.jsonc) the run stops after the parity
# check: nothing public changes. Cutover = add routes, commit, run with
# --full-parity. Rollback after cutover: `npx wrangler rollback`, or remove the
# routes and run `npx wrangler triggers deploy` to hand traffic back to the
# old origin.
#
# Usage: scripts/deploy-cloudflare.sh [--yes] [--preview-only] [--full-parity] [--skip-parity]

set -euo pipefail
cd "$(dirname "$0")/.."

# ---- site settings (edit these) ---------------------------------------------
SITE="cheatsheets.davidveksler.com"                       # display name
PROD_URL="https://cheatsheets.davidveksler.com"               # canonical origin, no trailing slash
BUILD_CMD="python3 scripts/build_site.py"             # gates + prerender into dist/ (spec §2.1)
VERIFY_PATH="/"                       # page that must be live after deploy
VERIFY_GREP="Find the one page you"         # distinctive string on that page
PARITY_ARGS=(--allow deploy/parity-allow.txt --paths-file deploy/parity-paths.txt)
ORIGIN_SITE="cheatsheets.davidveksler.com"                        # droplet docroot name; full parity then also checks every file live there
ORIGIN_EXCLUDE=""                     # ERE of droplet paths to leave out of that list (e.g. '^/(forum|Wiki)/')
WRANGLER_CONFIG="wrangler.jsonc"      # a repo with several sites keeps one config per site
# -----------------------------------------------------------------------------

CF_ENV="$HOME/Projects/.cloudflare.env"
CF_KIT="${CF_KIT:-$HOME/Projects/cf-static-kit}"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

ASSUME_YES=0; PREVIEW_ONLY=0; FORCE_FULL=0; SKIP_PARITY=0
for arg in "$@"; do
  case "$arg" in
    --yes|-y) ASSUME_YES=1 ;;
    --preview-only) PREVIEW_ONLY=1 ;;
    --full-parity) FORCE_FULL=1 ;;
    --skip-parity) SKIP_PARITY=1 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

wr() { npx --no-install wrangler "$@" --config "$WRANGLER_CONFIG"; }
step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok() { printf '  \033[1;32mOK\033[0m   %s\n' "$*"; }
die() { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }
PY="$(command -v python3 || command -v python || true)"
PROMOTED=0
on_exit() {
  rc=$?
  if [ "$rc" -ne 0 ] && [ "$PROMOTED" -eq 1 ]; then
    printf '\n\033[1;31mDeploy FAILED after promotion. Roll back with: npx wrangler rollback\033[0m\n' >&2
  elif [ "$rc" -ne 0 ]; then
    printf '\n\033[1;31m%s deploy failed (exit %s). Production is unchanged.\033[0m\n' "$SITE" "$rc" >&2
  fi
}
trap on_exit EXIT

# Routes present in the config (comments stripped) = the site is cut over.
routed() {
  WRANGLER_CONFIG="$WRANGLER_CONFIG" "$PY" - <<'EOF'
import json, os, re, sys
s = open(os.environ["WRANGLER_CONFIG"], encoding="utf-8").read()
s = re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*|/\*.*?\*/', lambda m: m.group(1) or "", s, flags=re.S)
s = re.sub(r",(\s*[}\]])", r"\1", s)
c = json.loads(s)
sys.exit(0 if (c.get("routes") or c.get("route")) else 1)
EOF
}

# ---- 1. preflight -----------------------------------------------------------
step "Preflight: $SITE"
[ -n "$PY" ] || die "python not found"
[ -z "$(git status --porcelain)" ] || die "working tree is not clean; commit or stash first"
SHA="$(git rev-parse --short=7 HEAD)"
ok "clean tree at $SHA"
node -e 'process.exit(+process.versions.node.split(".")[0] >= 22 ? 0 : 1)' || die "Node 22+ required"
[ -d node_modules/wrangler ] || { step "Installing dependencies"; npm ci; }
# CI passes the token in the environment; locally it comes from the central env file.
if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  [ -f "$CF_ENV" ] || die "missing $CF_ENV and no CLOUDFLARE_API_TOKEN in the environment"
  CLOUDFLARE_API_TOKEN="$(grep -m1 -oE '^CLOUDFLARE_API_TOKEN=[^[:space:]]+' "$CF_ENV" | cut -d= -f2)"
fi
[ -n "$CLOUDFLARE_API_TOKEN" ] || die "no CLOUDFLARE_API_TOKEN"
export CLOUDFLARE_API_TOKEN
if [ "$SKIP_PARITY" -eq 0 ]; then
  [ -f "$CF_KIT/scripts/cf_parity.py" ] || die "parity checker not found at $CF_KIT (set CF_KIT or clone cf-static-kit)"
fi
if routed; then ROUTED=1; ok "routes configured: deploy goes live"; else ROUTED=0; ok "no routes: preview only, nothing public changes"; fi

# ---- 2. build + gates -------------------------------------------------------
if [ -n "$BUILD_CMD" ]; then
  step "Build and quality gates: $BUILD_CMD"
  bash -c "$BUILD_CMD"
  [ -z "$(git status --porcelain)" ] || die "build modified tracked files; commit the result or fix the build"
fi

# ---- 3. upload a preview version ---------------------------------------------
step "Upload preview version"
ALIAS="c$SHA"
upload() { wr versions upload --preview-alias "$ALIAS" --tag "$SHA" --message "deploy $SHA" 2>&1; }
if ! OUT="$(upload)"; then
  if echo "$OUT" | grep -q "does not yet exist"; then
    [ "$ROUTED" -eq 0 ] || die "Worker does not exist yet and $WRANGLER_CONFIG has routes. Bootstrap first without routes (runbook step 3)."
    step "Bootstrap: first deploy of the Worker (no routes, not public)"
    wr deploy
    OUT="$(upload)" || { echo "$OUT"; die "version upload failed"; }
  else
    echo "$OUT"; die "version upload failed"
  fi
fi
parse() {
  VERSION_ID="$(echo "$OUT" | sed -n 's/.*Worker Version ID: \([0-9a-f-]*\).*/\1/p' | head -1 || true)"
  PREVIEW_URL="$( (echo "$OUT" | grep -oE 'https://[a-z0-9-]+\.[a-z0-9-]+\.workers\.dev' | grep "^https://$ALIAS-" | head -1) || true)"
}
parse
# A Worker whose first `wrangler deploy` failed exists but has no deployment, and
# then gets versions without preview URLs. Bootstrap it (only when unrouted) and retry.
if [ -z "$PREVIEW_URL" ] && [ "$ROUTED" -eq 0 ]; then
  step "No preview URL issued; bootstrapping the Worker (no routes, not public) and retrying"
  wr deploy
  OUT="$(upload)" || { echo "$OUT"; die "version upload failed"; }
  parse
fi
echo "$OUT" | grep -E 'Version ID|Preview' || true
[ -n "$VERSION_ID" ] && [ -n "$PREVIEW_URL" ] || { echo "$OUT"; die "could not read version id / preview URL from wrangler output (is preview_urls true?)"; }
ok "version $VERSION_ID"
ok "preview $PREVIEW_URL"

# ---- 4. parity ----------------------------------------------------------------
PARITY="skipped"
if [ "$SKIP_PARITY" -eq 0 ]; then
  MODE=smoke; { [ "$ROUTED" -eq 0 ] || [ "$FORCE_FULL" -eq 1 ]; } && MODE=full
  step "Parity check ($MODE) against $PROD_URL"
  mkdir -p .wrangler
  # A brand-new preview can 404 for a few seconds; wait until it serves before comparing.
  for _ in $(seq 1 24); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' -A "$UA" "$PREVIEW_URL$VERIFY_PATH")" = 200 ] && break
    sleep 5
  done
  if [ "$MODE" = full ] && [ -n "$ORIGIN_SITE" ]; then
    bash "$CF_KIT/scripts/origin_paths.sh" "$ORIGIN_SITE" \
      | { if [ -n "$ORIGIN_EXCLUDE" ]; then grep -Ev -- "$ORIGIN_EXCLUDE"; else cat; fi; } > .wrangler/origin-paths.txt \
      || die "could not list droplet docroot for $ORIGIN_SITE"
    ok "$(wc -l < .wrangler/origin-paths.txt | tr -d ' ') files live on the droplet added to the check"
    PARITY_ARGS+=(--paths-file .wrangler/origin-paths.txt)
  fi
  "$PY" "$CF_KIT/scripts/cf_parity.py" --mode "$MODE" --prod "$PROD_URL" --candidate "$PREVIEW_URL" \
    --report ".wrangler/parity-$SHA.json" ${PARITY_ARGS[@]+"${PARITY_ARGS[@]}"} \
    || die "parity check failed; see .wrangler/parity-$SHA.json. Fix, or explain each diff in the allow file."
  PARITY="pass ($MODE)"
  # The prerendered Explorer, hubs, lenses and popularity page differ byte for byte
  # from PHP's per-request render (parity-allow.txt lets those bodies through);
  # this compares what they say instead (spec §5). Only meaningful against the droplet.
  if [ "$MODE" = full ] && [ "$ROUTED" -eq 0 ]; then
    step "Strict re-check of allowed differences"
    "$PY" scripts/parity_body_recheck.py ".wrangler/parity-$SHA.json"       || die "an allowed parity difference is not explained; see above"
    step "Explorer content equivalence against $PROD_URL"
    "$PY" scripts/compare_explorer.py --prod "$PROD_URL" --candidate "$PREVIEW_URL"       || die "Explorer content differs from the droplet; see above"
    PARITY="pass ($MODE + explorer)"
  fi
else
  printf '\033[1;33m  WARNING: parity check skipped\033[0m\n'
fi

if [ "$PREVIEW_ONLY" -eq 1 ] || [ "$ROUTED" -eq 0 ]; then
  step "Preview ready, production unchanged: $PREVIEW_URL"
  exit 0
fi

# ---- 5. confirm -------------------------------------------------------------
if [ "$ASSUME_YES" -ne 1 ]; then
  step "Deployment plan"
  printf '  Site:    %s\n  Target:  %s\n  Commit:  %s\n  Version: %s\n  Preview: %s\n  Parity:  %s\n' \
    "$SITE" "$PROD_URL" "$SHA" "$VERSION_ID" "$PREVIEW_URL" "$PARITY"
  read -r -p "Deploy to production? [y/N] " reply
  [[ "$reply" =~ ^[Yy]([Ee][Ss])?$ ]] || { echo "Cancelled. Production is unchanged."; exit 0; }
fi

# ---- 6. promote + routes ------------------------------------------------------
step "Promote version and apply routes"
PROMOTED=1
wr versions deploy "$VERSION_ID@100%" --yes --message "deploy $SHA"
wr triggers deploy

# ---- 7. live verification -----------------------------------------------------
step "Verify live: $PROD_URL$VERIFY_PATH"
# A new route or version can take minutes to reach every edge (seen up to ~4 min).
same_as_preview() {
  [ -f "$CF_KIT/scripts/cf_parity.py" ] || return 0   # without the kit, the grep + deployments check below still gate
  "$PY" "$CF_KIT/scripts/cf_parity.py" --mode full --no-sitemap --variant-sample 0 --headers "" \
    --prod "$PROD_URL" --candidate "$PREVIEW_URL" --path "$VERIFY_PATH" >/dev/null 2>&1
}
for i in $(seq 1 72); do
  BODY="$(curl -fsS -A "$UA" "$PROD_URL$VERIFY_PATH" 2>/dev/null || true)"
  if echo "$BODY" | grep -qF -- "$VERIFY_GREP" && same_as_preview; then
    ok "live page contains \"$VERIFY_GREP\" and matches version $VERSION_ID"
    wr deployments status 2>/dev/null | grep -q "$VERSION_ID" || die "deployments status does not show $VERSION_ID at 100%"
    ok "version $VERSION_ID is the active deployment"
    step "Deployed and verified: $SITE $SHA"
    exit 0
  fi
  sleep 5
done
die "live page did not match the new version within 6 minutes"
