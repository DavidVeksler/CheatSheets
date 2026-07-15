#!/usr/bin/env python3
"""
Robust deploy for cheatsheets.davidveksler.com.

Replaces a bare ``git push production`` with a guarded pipeline:

    preflight  -> validate (local) -> confirm -> push -> verify (live)

The ``production`` remote points straight at the live docroot
(``johngalt@direct.vellum.capital:/var/www/cheatsheets.davidveksler.com/htdocs``),
so a push *is* the deploy. This script refuses to ship a dirty tree, a wrong or
divergent branch, or pages that link to files that aren't committed, then curls
the live URLs afterward to prove the deploy landed. Cloudflare cache purging
still happens server-side in the repo's post-receive hook (see purge-cache.py).

Stdlib only - no venv or pip install required.

Usage:
  python scripts/deploy.py                 # full pipeline, interactive confirm
  python scripts/deploy.py --yes           # skip the confirm prompt
  python scripts/deploy.py --dry-run       # preflight + validate, stop before push
  python scripts/deploy.py --check         # preflight + validate only (used by pre-push hook)
  python scripts/deploy.py --all           # validate every page, not just changed ones

Escape hatches (use sparingly):
  --force        allow a non-main branch, skip the origin-sync check, and
                 force-push HEAD to production/main (overrides non-fast-forward)
  --skip-seo     skip scripts/seo_check.py
  --skip-links   skip internal link/asset integrity check
  --skip-verify  skip the post-deploy live curl checks
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ORIGIN = "https://cheatsheets.davidveksler.com"
DEPLOY_BRANCH = "main"
PRODUCTION_REMOTE = "production"
ORIGIN_REMOTE = "origin"
HTML_CACHE_MAXAGE = "max-age=1800"

# href/src targets we never treat as local files.
SKIP_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "data:",
                 "javascript:", "#", "{", "%7b")
ATTR_RE = re.compile(r"""\b(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if os.name == "nt" and not os.environ.get("WT_SESSION"):
    # Enable ANSI on legacy Windows consoles; harmless if it fails.
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        GREEN = RED = YELLOW = DIM = RESET = ""


def c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


def step(msg: str) -> None:
    print(c("\033[1m", f"\n== {msg}"))


def ok(msg: str) -> None:
    print(f"  {c(GREEN, 'OK')}   {msg}")


def warn(msg: str) -> None:
    print(f"  {c(YELLOW, 'WARN')} {msg}")


def fail(msg: str) -> None:
    print(f"{c(RED, 'deploy: ' + msg)}", file=sys.stderr)
    sys.exit(1)


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and result.returncode != 0:
        fail((result.stderr or result.stdout).strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


# --------------------------------------------------------------------------- #
# Preflight
# --------------------------------------------------------------------------- #
def preflight(args) -> str:
    """Return the diff base (production/main, or empty-tree hash) after checks."""
    step("Preflight")

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != DEPLOY_BRANCH and not args.force:
        fail(f"on branch '{branch}', not '{DEPLOY_BRANCH}'. "
             f"Switch to {DEPLOY_BRANCH} or pass --force.")
    ok(f"branch is '{branch}'")

    if git("status", "--porcelain"):
        fail("working tree is not clean. Commit or stash before deploying "
             "(you deploy commits, not uncommitted files).")
    ok("working tree is clean")

    # Live must never get a commit GitHub doesn't have.
    git("fetch", "--quiet", ORIGIN_REMOTE, DEPLOY_BRANCH, check=False)
    local = git("rev-parse", "HEAD")
    try:
        origin = git("rev-parse", f"{ORIGIN_REMOTE}/{DEPLOY_BRANCH}")
    except SystemExit:
        origin = ""
    if origin and local != origin and not args.force:
        ahead = git("rev-list", "--count", f"{ORIGIN_REMOTE}/{DEPLOY_BRANCH}..HEAD", check=False)
        behind = git("rev-list", "--count", f"HEAD..{ORIGIN_REMOTE}/{DEPLOY_BRANCH}", check=False)
        fail(f"local {DEPLOY_BRANCH} is not in sync with {ORIGIN_REMOTE}/{DEPLOY_BRANCH} "
             f"(ahead {ahead}, behind {behind}). Push/pull GitHub first, or pass --force.")
    ok(f"in sync with {ORIGIN_REMOTE}/{DEPLOY_BRANCH}" if origin else
       f"no {ORIGIN_REMOTE}/{DEPLOY_BRANCH} to compare (skipped)")

    # Refresh the production tracking ref so the changeset diff is accurate.
    git("fetch", "--quiet", PRODUCTION_REMOTE, check=False)
    base = git("rev-parse", f"{PRODUCTION_REMOTE}/{DEPLOY_BRANCH}", check=False)
    if not base:
        base = git("hash-object", "-t", "tree", "/dev/null", check=False) or \
            "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # git empty-tree
        warn("no production/main ref; treating every tracked file as changed")
    else:
        ok(f"production is at {base[:9]}")
    return base


def changed_files(base: str, exts: tuple[str, ...]) -> list[str]:
    out = git("diff", "--name-only", "--diff-filter=ACMR", base, "HEAD", check=False)
    files = [f for f in out.splitlines() if f]
    return [f for f in files if f.lower().endswith(exts)]


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def validate(args, base: str) -> None:
    step("Validate")

    if args.all:
        html = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
        json_files = sorted(f for f in os.listdir(ROOT) if f.endswith(".json"))
        php_files = sorted(f for f in os.listdir(ROOT) if f.endswith(".php"))
        scope = "all files"
    else:
        html = changed_files(base, (".html",))
        json_files = changed_files(base, (".json",))
        php_files = changed_files(base, (".php",))
        scope = "changed files"
    print(f"  {c(DIM, f'scope: {scope} - {len(html)} html, {len(json_files)} json, {len(php_files)} php')}")

    if not (html or json_files or php_files):
        warn("no publishable files changed vs production. Nothing new to validate.")
        return

    failures: list[str] = []

    # 1. SEO acceptance gate (scripts/seo_check.py) on the pages being shipped.
    if html and not args.skip_seo:
        seo = os.path.join(ROOT, "scripts", "seo_check.py")
        res = subprocess.run([sys.executable, seo, *html], cwd=ROOT,
                             capture_output=True, text=True)
        if res.returncode != 0:
            # seo_check.py prints a summary line, then indents each failure by 2 spaces.
            detail = [ln.strip() for ln in res.stdout.splitlines() if ln.startswith("  ")]
            if detail:
                failures.extend(f"seo: {ln}" for ln in detail)
            else:
                failures.append(f"seo: seo_check.py failed:\n{res.stdout}{res.stderr}".rstrip())
        else:
            ok(f"SEO metadata gate passed ({len(html)} page(s))")
    elif args.skip_seo:
        warn("SEO gate skipped (--skip-seo)")

    # 2. Internal link/asset integrity - every local href/src must resolve.
    if html and not args.skip_links:
        missing = check_links(html)
        if missing:
            failures.extend(f"link: {m}" for m in missing)
        else:
            ok(f"internal links/assets resolve ({len(html)} page(s))")
    elif args.skip_links:
        warn("link integrity skipped (--skip-links)")

    # 3. JSON data files must parse.
    for jf in json_files:
        path = os.path.join(ROOT, jf)
        try:
            with open(path, encoding="utf-8") as fh:
                json.load(fh)
        except (OSError, ValueError) as e:
            failures.append(f"json: {jf}: {e}")
    if json_files and not any(f.startswith("json:") for f in failures):
        ok(f"JSON parses ({len(json_files)} file(s))")

    # 4. php -l on changed PHP, only if a local php is available.
    if php_files:
        php = which("php")
        if not php:
            warn(f"php not on PATH - skipped lint of {len(php_files)} .php file(s)")
        else:
            for pf in php_files:
                res = subprocess.run([php, "-l", os.path.join(ROOT, pf)],
                                     capture_output=True, text=True)
                if res.returncode != 0:
                    failures.append(f"php: {pf}: {res.stdout.strip() or res.stderr.strip()}")
            if not any(f.startswith("php:") for f in failures):
                ok(f"PHP lints clean ({len(php_files)} file(s))")

    if failures:
        print()
        for f in failures:
            print(f"  {c(RED, 'FAIL')} {f}")
        fail(f"{len(failures)} validation issue(s) - fix or use the matching --skip-* flag.")


def check_links(html_files: list[str]) -> list[str]:
    missing: list[str] = []
    for rel in html_files:
        path = os.path.join(ROOT, rel)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                source = fh.read()
        except OSError as e:
            missing.append(f"{rel}: cannot read ({e})")
            continue
        page_dir = os.path.dirname(path)
        seen: set[str] = set()
        for match in ATTR_RE.finditer(source):
            target = (match.group(1) or match.group(2) or "").strip()
            low = target.lower()
            if not target or low.startswith(SKIP_PREFIXES):
                continue
            clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not clean or clean in seen:
                continue
            seen.add(clean)
            if clean.startswith("/"):
                resolved = os.path.join(ROOT, clean.lstrip("/"))
            else:
                resolved = os.path.normpath(os.path.join(page_dir, clean))
            # Keep resolution inside the repo.
            if os.path.commonpath([os.path.abspath(resolved), ROOT]) != ROOT:
                continue
            if os.path.isdir(resolved) or clean.endswith("/"):
                if not (os.path.exists(os.path.join(resolved, "index.html"))
                        or os.path.exists(os.path.join(resolved, "index.php"))):
                    missing.append(f"{rel} -> {target} (no index in directory)")
            elif not os.path.exists(resolved):
                missing.append(f"{rel} -> {target} (file not committed)")
    return missing


def which(cmd: str) -> str | None:
    from shutil import which as _which
    return _which(cmd)


# --------------------------------------------------------------------------- #
# Confirm + push + verify
# --------------------------------------------------------------------------- #
def show_changeset(base: str) -> list[str]:
    step("Changeset going live")
    stat = git("diff", "--stat", base, "HEAD", check=False)
    print(stat if stat else c(DIM, "  (no diff vs production/main)"))
    return changed_files(base, (".html",))


def confirm(args) -> None:
    if args.yes:
        return
    try:
        answer = input(f"\nPush {DEPLOY_BRANCH} to '{PRODUCTION_REMOTE}' and update the "
                       f"live site? [y/N] ").strip()
    except EOFError:
        answer = ""
    if not re.match(r"^y(es)?$", answer, re.IGNORECASE):
        print("Aborted.")
        sys.exit(1)


def push(args) -> None:
    step("Deploy")
    env = dict(os.environ, CHEATSHEETS_DEPLOY="1")  # let the pre-push hook no-op
    # Push HEAD (not the local main ref) so a --force deploy from a non-main
    # branch ships the commits you actually validated.
    cmd = ["git", "push", PRODUCTION_REMOTE, f"HEAD:{DEPLOY_BRANCH}"]
    if args.force:
        # --force-with-lease is checked against production/main, which preflight
        # just fetched, so it still refuses to clobber an unexpected remote state.
        cmd.insert(2, "--force-with-lease")
        warn(f"force-pushing HEAD to {PRODUCTION_REMOTE}/{DEPLOY_BRANCH} (--force)")
    result = subprocess.run(cmd, cwd=ROOT, env=env)
    if result.returncode != 0:
        fail("git push to production failed (see output above).")
    ok("pushed. Server post-receive hook builds nothing (static) and purges Cloudflare.")


def verify(changed_html: list[str]) -> None:
    step("Verify live")
    curl = which("curl")
    if not curl:
        warn("curl not found - skipping live verification.")
        return

    checks: list[tuple[str, str, str | None]] = [("/", "200", None)]
    for rel in changed_html:
        checks.append((f"/{rel}", "200", HTML_CACHE_MAXAGE))
    checks.append(("/no-such-page-cheatsheets-xyz", "404", None))

    problems = 0
    for path, want_status, want_cache in checks:
        url = SITE_ORIGIN + path
        status, cache = curl_head(curl, url)
        detail = f"{status}"
        if want_cache:
            detail += f", cache-control: {cache or '(none)'}"
        good = status == want_status and (not want_cache or (cache and want_cache in cache))
        line = f"{path}  ->  {detail}"
        if good:
            ok(line)
        else:
            problems += 1
            print(f"  {c(RED, 'FAIL')} {line}  (wanted {want_status}"
                  + (f" + {want_cache}" if want_cache else "") + ")")

    if problems:
        print(c(YELLOW, f"\n{problems} live check(s) failed. The push already landed - "
                        "investigate the server/nginx/Cloudflare before assuming success."))
        sys.exit(1)
    print(c(GREEN, "\nAll live checks passed."))


def curl_head(curl: str, url: str) -> tuple[str, str | None]:
    res = subprocess.run(
        [curl, "-sS", "--max-time", "20", "-A", "cheatsheets-deploy/1.0",
         "-o", os.devnull, "-D", "-", "-w", "\nHTTPSTATUS:%{http_code}", url],
        capture_output=True, text=True)
    status, cache = "ERR", None
    for line in res.stdout.splitlines():
        if line.startswith("HTTPSTATUS:"):
            status = line.split(":", 1)[1].strip()
        elif line.lower().startswith("cache-control:"):
            cache = line.split(":", 1)[1].strip().lower()
    if res.returncode != 0 and status == "ERR":
        status = f"ERR({res.returncode})"
    return status, cache


# --------------------------------------------------------------------------- #
def main() -> None:
    p = argparse.ArgumentParser(description="Guarded deploy for cheatsheets.davidveksler.com")
    p.add_argument("--yes", "-y", action="store_true", help="skip the confirmation prompt")
    p.add_argument("--dry-run", action="store_true", help="preflight + validate, then stop")
    p.add_argument("--check", action="store_true",
                   help="preflight + validate only (used by the pre-push hook)")
    p.add_argument("--all", action="store_true", help="validate every file, not just changed")
    p.add_argument("--force", action="store_true",
                   help="allow non-main branch, skip origin sync, and force-push HEAD to production")
    p.add_argument("--skip-seo", action="store_true")
    p.add_argument("--skip-links", action="store_true")
    p.add_argument("--skip-verify", action="store_true")
    args = p.parse_args()

    base = preflight(args)
    validate(args, base)

    if args.check:
        print(c(GREEN, "\nPre-push checks passed."))
        return

    changed_html = show_changeset(base)

    if args.dry_run:
        print(c(GREEN, "\nDry run complete - not pushing."))
        return

    confirm(args)
    push(args)

    if args.skip_verify:
        warn("live verification skipped (--skip-verify)")
        return
    verify(changed_html)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
