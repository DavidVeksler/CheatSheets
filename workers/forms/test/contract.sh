#!/usr/bin/env bash
# Local contract suite for the newsletter forms Worker (workers/forms/), under
# `wrangler dev` with a local D1 and a local Resend stub (test/resend-stub.mjs):
# no email leaves this machine and nothing touches the remote D1.
# Proves the PHP contract (subscribe.php / confirm.php, docs/newsletter.md §2.3):
# status codes, JSON vs page, honeypot, intake + confirmed rows, the HMAC token,
# and that a token minted by the PHP code (lib/newsletter.php) verifies here.
# Usage: bash workers/forms/test/contract.sh   (from the repo root; needs node, php)
set -euo pipefail
cd "$(dirname "$0")/../../.."
REPO="$PWD"
W="$REPO/node_modules/.bin/wrangler"
T="$(mktemp -d)"
PORT=8797; STUB_PORT=8798
DEV= STUB=
cleanup() {
  kill "$DEV" "$STUB" 2>/dev/null || true
  if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'dev --port $PORT' -or \$_.CommandLine -match 'resend-stub.mjs' -or (\$_.Name -eq 'workerd.exe' -and \$_.CommandLine -match 'cs-forms-test') } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }" >/dev/null 2>&1 || true
    sleep 2
  fi
  rm -rf "${TROOT:-$T}" 2>/dev/null || true
}
trap cleanup EXIT

SECRET="test-secret-$(date +%s)"
TROOT="$T"
mkdir -p "$T/cs-forms-test"; T="$T/cs-forms-test"
cp -r workers/forms/src workers/forms/schema.sql "$T/"
cat > "$T/wrangler.jsonc" <<JSON
{ "name": "cs-forms-test", "main": "src/index.js", "compatibility_date": "2026-09-28",
  "d1_databases": [{ "binding": "DB", "database_name": "cs-forms-test", "database_id": "00000000-0000-0000-0000-000000000000" }] }
JSON
printf 'NEWSLETTER_TOKEN_SECRET=%s\nRESEND_SENDING_KEY=re_test_stub\nCHEATSHEET_NOTIFY_EMAIL=owner@example.com\nRESEND_API_BASE=http://127.0.0.1:%s/emails\n' "$SECRET" "$STUB_PORT" > "$T/.dev.vars"
(cd "$T" && "$W" d1 execute cs-forms-test --local --file schema.sql >/dev/null 2>&1)
STUB_PORT=$STUB_PORT STUB_OUT="$T/stub.json" node workers/forms/test/resend-stub.mjs & STUB=$!
(cd "$T" && "$W" dev --port $PORT --local >"$T/dev.log" 2>&1) & DEV=$!
B="http://127.0.0.1:$PORT"
for _ in $(seq 1 60); do curl -s -m 3 "$B/subscribe.php?health=1" >/dev/null 2>&1 && break; sleep 1; done

pass=0; fail=0
check() { if [ "$2" = "$3" ]; then pass=$((pass+1)); echo "  ok    $1"; else fail=$((fail+1)); echo "  FAIL  $1: expected [$2] got [$3]"; fi; }
code() { curl -s -m 20 -o /dev/null -w '%{http_code}' "$@"; }
body() { curl -s -m 20 "$@"; }
d1n() { (cd "$T" && "$W" d1 execute cs-forms-test --local --command "SELECT COUNT(*) AS n FROM $1" --json 2>/dev/null) | grep -oE '"n": *[0-9]+' | grep -oE '[0-9]+$'; }
J=(-H 'Accept: application/json')

check "health 200"                          200 "$(code "$B/subscribe.php?health=1")"
check "GET subscribe 405 (page)"            405 "$(code "$B/subscribe.php")"
check "GET subscribe 405 JSON body"         '{"ok":false,"error":"Method not allowed."}' "$(body "${J[@]}" "$B/subscribe.php")"
check "bad email 422 JSON body"             '{"ok":false,"error":"Please enter a valid email address."}' "$(body "${J[@]}" -d email=notanemail "$B/subscribe.php")"
check "bad email 422"                       422 "$(code "${J[@]}" -d email=a@b "$B/subscribe.php")"
check "honeypot silent success"             '{"ok":true,"message":"Thanks — check your inbox to confirm your subscription."}' "$(body "${J[@]}" -d email=bot@example.com -d website=x "$B/subscribe.php")"
check "honeypot stores nothing"             0 "$(d1n subscribers)"
check "valid signup 200 JSON"               '{"ok":true,"message":"Thanks — check your inbox to confirm your subscription."}' "$(body -H 'X-Requested-With: fetch' -H 'Referer: http://127.0.0.1/how-its-built.html' -F email=' Reader@Example.com ' "$B/subscribe.php")"
check "intake row stored"                   1 "$(d1n subscribers)"
sleep 1
LINK="$(node -e 'const s=require(process.argv[1]);process.stdout.write(s.link||"")' "$T/stub.json")"
SUBJ="$(node -e 'const s=require(process.argv[1]);process.stdout.write(s.subjects.join("|"))' "$T/stub.json")"
check "confirmation + owner notice sent"    "Confirm your subscription|New cheatsheet subscriber" "$SUBJ"
check "confirm link points at confirm.php"  1 "$(echo "$LINK" | grep -c "^$B/confirm.php?p=.*&s=")"
check "confirm link 200"                    200 "$(code "$LINK")"
check "confirm page says Subscribed"        1 "$(body "$LINK" | grep -c '<h1 class="h4 mb-2">Subscribed</h1>')"
check "confirmed row stored once"           1 "$(d1n confirmed)"
check "re-confirm is a silent no-op"        "200 1" "$(code "$LINK") $(d1n confirmed)"
check "confirm missing token 400"           400 "$(code "$B/confirm.php")"
check "confirm missing token page"          1 "$(body "$B/confirm.php" | grep -c 'This confirmation link is missing its token.')"
check "tampered signature 400"              400 "$(code "${LINK%?}A")"
# Tokens minted by the PHP code (the droplet's subscribe.php) must verify here.
MINT='require "lib/newsletter.php"; $t = newsletter_mint_token($argv[1], $argv[2]); echo "p=", rawurlencode($t["p"]), "&s=", rawurlencode($t["s"]);'
PHPQ="$(php -r "$MINT" phpuser@example.org "$SECRET" 2>/dev/null)"
check "PHP-minted token verifies (200)"     200 "$(code "$B/confirm.php?$PHPQ")"
check "PHP-minted address confirmed"        2 "$(d1n confirmed)"
OLD='require "lib/newsletter.php"; $p = newsletter_b64url_encode($argv[1]) . "." . (time() - 8*86400); echo "p=", rawurlencode($p), "&s=", rawurlencode(newsletter_b64url_encode(hash_hmac("sha256", $p, $argv[2], true)));'
check "8-day-old PHP token expired (400)"   400 "$(code "$B/confirm.php?$(php -r "$OLD" old@example.org "$SECRET" 2>/dev/null)")"
check "wrong-secret PHP token 400"          400 "$(code "$B/confirm.php?$(php -r "$MINT" x@example.org other-secret 2>/dev/null)")"
check "send failure 502"                    502 "$(code "${J[@]}" --data-urlencode email=reader+fail@example.com "$B/subscribe.php")"
check "no-JS signup page"                   1 "$(body -d email=nojs@example.com "$B/subscribe.php" | grep -c '<title>Check your inbox · Cheatsheets</title>')"
for _ in 1 2 3 4 5 6; do code "${J[@]}" -d email=x "$B/subscribe.php" >/dev/null; done
check "rate limit after 10 attempts (429)"  429 "$(code "${J[@]}" -d email=rl@example.com "$B/subscribe.php")"
check "unknown path 404"                    404 "$(code "$B/nope")"
echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
