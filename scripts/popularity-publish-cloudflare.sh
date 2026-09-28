#!/usr/bin/env bash
#
# Daily popularity refresh for cheatsheets.davidveksler.com, published to the
# cheatsheets-davidveksler-com Worker. Pre-authorized auto-publish (David, 2026-09-27,
# server-mirror/docs/cloudflare-migration.md §7 #5). Replaces, at cutover, both the
# 02:30 GitHub Action commit (update-popularity.yml) and the droplet's 04:00
# `cheatsheets-pull.sh` that made that commit live. Spec: docs/specs/cloudflare-migration.md §2.5.
# Runs from .github/workflows/popularity-cloudflare.yml; also runs locally from Git Bash.
#
#   1. fetch-popularity.py + build_catalog.py (as update-popularity.yml did).
#   2. Commit and push popularity.json + catalog.json (only those may change).
#   3. Publish ONLY IF everything changed between the commit the live Worker was built
#      from (its "workers/tag" annotation, set by scripts/deploy-cloudflare.sh and by
#      this script) and HEAD is popularity.json, catalog.json, or a path that is neither
#      served nor read by the build (docs/, marketing/, TODO/, root *.md: INERT). An empty diff also
#      publishes: it rebuilds the date-dependent Explorer bits (deep cut of the day,
#      NEW badges). Anything else is DRIFT: nothing is published, and the change waits
#      for scripts/deploy-cloudflare.sh and David's approval.
#   4. Build (gates + prerender), upload a version tagged with the commit, promote it
#      to 100%, verify the live /popularity.json is the committed one.
#
# Not wired until cutover: while wrangler.jsonc has no routes, step 3 stops with
# "not cut over" (the droplet still publishes) unless CS_REHEARSE=1.
#
# Env:
#   CLOUDFLARE_ANALYTICS_TOKEN  Zone Analytics Read (fetch-popularity.py). Locally
#                               falls back to CLOUDFLARE_API_TOKEN in .cloudflare.env.
#   CLOUDFLARE_WORKERS_TOKEN    Workers Scripts Edit on the account (publish only).
#                               Locally falls back to ~/Projects/.cloudflare.env.
#   CS_DRY_RUN=1   refresh + gates + build, then discard: no commit, push or publish.
#   CS_REHEARSE=1  pre-cutover rehearsal: refresh discarded, guard + publish HEAD to the
#                  unrouted Worker and verify on the version's preview URL. No push.
#   CS_BRANCH      default main.

set -euo pipefail
cd "$(dirname "$0")/.."

BRANCH="${CS_BRANCH:-main}"
DRY_RUN="${CS_DRY_RUN:-}"
REHEARSE="${CS_REHEARSE:-}"
PUBLIC_URL="https://cheatsheets.davidveksler.com"
WRANGLER_CONFIG="wrangler.jsonc"
CF_ENV="$HOME/Projects/.cloudflare.env"
ALLOWED='^(popularity\.json|catalog\.json)$'
# Paths that are neither served nor read by the build (scripts/build_site.py): routine
# commits there (KPI log, Reddit drafts, specs) must not stall the daily publish.
INERT='^(docs|marketing|TODO|\.claude|\.agents|\.github)/|^[^/]+\.md$'
PY="$(command -v python3 || command -v python)"
UA="cheatsheets-popularity-publish/1.0 (+https://cheatsheets.davidveksler.com/)"

log() { echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $*"; }
die() { log "FAILED: $*"; echo "::error::popularity publish FAILED: $*"; exit 1; }
drift() { log "DRIFT: $*"; log "DRIFT: published nothing. Run scripts/deploy-cloudflare.sh to ship the real change."; echo "::warning::popularity publish DRIFT: $*"; exit 0; }
wr() { npx --no-install wrangler "$@" --config "$WRANGLER_CONFIG"; }
env_token() { [ -f "$CF_ENV" ] && grep -m1 -oE "^$1=[^[:space:]]+" "$CF_ENV" | cut -d= -f2 || true; }

[ "$(git rev-parse --abbrev-ref HEAD)" = "$BRANCH" ] || die "not on $BRANCH"
[ -z "$(git status --porcelain)" ] || die "working tree not clean"
head_before="$(git rev-parse --short=7 HEAD)"

# ---- 1. refresh -----------------------------------------------------------------
ANALYTICS="${CLOUDFLARE_ANALYTICS_TOKEN:-$(env_token CLOUDFLARE_API_TOKEN)}"
[ -n "$ANALYTICS" ] || die "no CLOUDFLARE_ANALYTICS_TOKEN"
CLOUDFLARE_API_TOKEN="$ANALYTICS" CLOUDFLARE_ZONE_ID="${CLOUDFLARE_ZONE_ID:-3d96473d69977c5c828b3079d9b9869c}" \
  "$PY" fetch-popularity.py || die "fetch-popularity.py"
"$PY" scripts/build_catalog.py || die "build_catalog.py"

# ---- 2. commit and push ---------------------------------------------------------
dirty="$(git status --porcelain | awk '{print $2}')"
if [ -n "$dirty" ]; then
  unexpected="$(echo "$dirty" | grep -Ev "$ALLOWED" || true)"
  [ -z "$unexpected" ] || die "refresh touched unexpected paths: $(echo "$unexpected" | tr '\n' ' ')"
  if [ -n "$DRY_RUN$REHEARSE" ]; then
    git --no-pager diff --stat
    git checkout -- popularity.json catalog.json
    if [ -n "$DRY_RUN" ]; then
      # The build ships committed bytes, so build HEAD to prove the toolchain works here.
      "$PY" scripts/build_site.py || die "build"
      log "CS_DRY_RUN: refreshed (discarded) and built HEAD; nothing committed or published"
      exit 0
    fi
    log "CS_REHEARSE: refresh discarded; rehearsing the publish of HEAD"
  else
    git -c user.name="github-actions[bot]" -c user.email="github-actions[bot]@users.noreply.github.com" \
      commit -q -m "chore: update popularity scores [skip ci]" -- popularity.json catalog.json || die "git commit"
    git push -q origin "$BRANCH" || die "git push (someone pushed meanwhile? next run retries)"
    log "committed and pushed $head_before -> $(git rev-parse --short=7 HEAD)"
  fi
else
  log "popularity already current at $head_before, nothing to commit"
  if [ -n "$DRY_RUN" ]; then "$PY" scripts/build_site.py || die "build"; log "CS_DRY_RUN: built; stopping"; exit 0; fi
fi
SHA="$(git rev-parse --short=7 HEAD)"

# ---- 3. publish guard -------------------------------------------------------------
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
if [ -n "$REHEARSE" ]; then
  log "CS_REHEARSE: publishing to the Worker whether or not it has routes"
elif ! routed; then
  log "not cut over ($WRANGLER_CONFIG has no routes): the droplet's 04:00 pull still publishes; nothing to do"
  exit 0
fi

WORKERS="${CLOUDFLARE_WORKERS_TOKEN:-$(env_token CLOUDFLARE_API_TOKEN)}"
[ -n "$WORKERS" ] || die "no CLOUDFLARE_WORKERS_TOKEN"
export CLOUDFLARE_API_TOKEN="$WORKERS"
[ -d node_modules/wrangler ] || npm ci --silent

json_field() { "$PY" -c "import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1], {'d': d}))" "$1"; }
live_version="$(wr deployments status --json 2>/dev/null \
  | json_field "[v['version_id'] for v in d['versions'] if v['percentage'] == 100][0]")" \
  || die "could not read the active deployment"
live_tag="$(wr versions view "$live_version" --json 2>/dev/null \
  | json_field "d.get('annotations', {}).get('workers/tag', '')")" \
  || die "could not read version $live_version"
[ -n "$live_tag" ] || drift "live version $live_version has no commit tag (not deployed by a repo script)"
git cat-file -e "$live_tag^{commit}" 2>/dev/null || drift "live version's commit $live_tag is not in this repo's history"
git merge-base --is-ancestor "$live_tag" HEAD || drift "live version's commit $live_tag is not an ancestor of $BRANCH"
others="$(git diff --name-only "$live_tag" HEAD | grep -Ev "$ALLOWED" | grep -Ev "$INERT" || true)"
[ -z "$others" ] || drift "changed since the live commit $live_tag besides popularity: $(echo "$others" | head -20 | tr '\n' ' ')"
log "guard: only popularity data changed since the live commit $live_tag"

# ---- 4. build, publish, verify ------------------------------------------------------
"$PY" scripts/build_site.py || die "build"
msg="daily popularity $SHA"; [ -z "$REHEARSE" ] || msg="rehearsal: $msg"
out="$(wr versions upload --tag "$SHA" --message "$msg" 2>&1)" || { echo "$out"; die "version upload"; }
version="$(echo "$out" | sed -n 's/.*Worker Version ID: \([0-9a-f-]*\).*/\1/p' | head -1)"
[ -n "$version" ] || { echo "$out"; die "no version id in wrangler output"; }
wr versions deploy "$version@100%" --yes --message "$msg" > /dev/null || die "versions deploy $version"
log "published $SHA as version $version (was $live_tag)"
if [ -n "$REHEARSE" ]; then
  PUBLIC_URL="$(echo "$out" | sed -n 's/.*Version Preview URL: \(https:[^ ]*\).*/\1/p' | head -1)"
  [ -n "$PUBLIC_URL" ] || { echo "$out"; die "no version preview URL in wrangler output"; }
fi
want="$(git show HEAD:popularity.json | sha256sum | cut -d' ' -f1)"
# The zone's Bot Fight Mode can challenge GitHub's runners (403 + cf-mitigated). A
# challenge is not a failed publish: fall back to the deployment record. Every curl here
# tolerates errors, because a non-200 inside $(...) under `set -e -o pipefail` would
# otherwise abort the script (exit 22) instead of retrying.
for _ in $(seq 1 24); do
  hdr="$(curl -sS -o /dev/null -D - -A "$UA" "$PUBLIC_URL/popularity.json?v=$SHA" 2>/dev/null || true)"
  if echo "$hdr" | grep -qi '^cf-mitigated: challenge'; then
    wr deployments status --json | grep -q "$version" || die "deployments status does not show $version"
    log "live URL challenged from this runner; deployments status shows $version at 100%"
    exit 0
  fi
  got="$( (curl -fsS -A "$UA" "$PUBLIC_URL/popularity.json?v=$SHA" 2>/dev/null || true) | sha256sum | cut -d' ' -f1)"
  if [ "$got" = "$want" ]; then
    wr deployments status --json | grep -q "$version" || die "deployments status does not show $version"
    log "verified $PUBLIC_URL/popularity.json is $SHA's; version $version at 100%"
    exit 0
  fi
  sleep 5
done
die "live popularity.json did not match $SHA within 2 minutes; roll back with: npx wrangler rollback"
