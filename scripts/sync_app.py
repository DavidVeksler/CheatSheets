#!/usr/bin/env python3
"""Rebuild a built multi-file app from its source repo and vendor it (docs/specs/apps.md).

    python scripts/sync_app.py black-hole-flight-simulator            # build, QA, copy, commit
    python scripts/sync_app.py black-hole-flight-simulator --skip-qa  # skip browser QA (needs a GPU browser)
    python scripts/sync_app.py black-hole-flight-simulator --no-commit

Reads apps/<slug>/app.json, then fails closed at the first problem:
  1. the source repo tree is clean (its HEAD is what gets recorded);
  2. this repo has no uncommitted changes to <slug>.html or apps/<slug>/;
  3. in the source repo, with APP_BASE=/apps/<slug>/: every npm script named in
     app.json "qa" (default: check, then qa:build);
  4. dist/index.html carries the canonical https://cheatsheets.davidveksler.com/<slug>.html;
  5. apps/<slug>/ is replaced with dist/ (minus index.html and "drop"), dist/index.html
     becomes <slug>.html, and app.json gets the source commit and build date;
  6. scripts/check_apps.py, then a commit "App sync: <slug> @ <sha>". The pre-commit hook
     regenerates catalog.json.

It never deploys; that stays scripts/deploy-cloudflare.sh with David's go-ahead.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://cheatsheets.davidveksler.com"


def die(msg: str) -> None:
    print(f"sync_app: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def git(cwd: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        die(f"git {' '.join(args)} failed in {cwd}: {r.stderr.strip()}")
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--skip-qa", action="store_true", help="run only `npm run check`, not the browser QA scripts")
    ap.add_argument("--no-commit", action="store_true")
    a = ap.parse_args()

    slug = a.slug
    app_dir = ROOT / "apps" / slug
    manifest_path = app_dir / "app.json"
    if not manifest_path.is_file():
        die(f"{manifest_path.relative_to(ROOT)} not found")
    meta = json.loads(manifest_path.read_text(encoding="utf-8"))
    src = Path(os.path.expanduser(meta["repo"])).resolve()
    if not (src / "package.json").is_file():
        die(f"source repo {src} has no package.json")

    if git(src, "status", "--porcelain"):
        die(f"source repo {src} has uncommitted changes; commit them first")
    sha = git(src, "rev-parse", "HEAD")
    if git(ROOT, "status", "--porcelain", "--", f"{slug}.html", f"apps/{slug}"):
        die(f"uncommitted changes to {slug}.html or apps/{slug}/ in this repo")

    npm = shutil.which("npm") or die("npm not on PATH")
    env = {**os.environ, "APP_BASE": f"/apps/{slug}/", "MSYS2_ENV_CONV_EXCL": "APP_BASE"}
    scripts = meta.get("qa") or ["check", "qa:build"]
    if a.skip_qa:
        scripts = [s for s in scripts if s == "check"] or ["check"]
    for script in scripts:
        print(f"sync_app: npm run {script} in {src.name} (APP_BASE={env['APP_BASE']})", flush=True)
        if subprocess.run([npm, "run", script], cwd=src, env=env).returncode != 0:
            die(f"npm run {script} failed in {src}")
    if git(src, "status", "--porcelain", "--untracked-files=no"):
        die(f"the build modified tracked files in {src}; commit or fix that first")

    dist = src / "dist"
    index = dist / "index.html"
    html = index.read_text(encoding="utf-8")
    canonical = f'rel="canonical" href="{SITE}/{slug}.html"'
    if canonical not in html:
        die(f"{index} lacks {canonical}")
    if f"/apps/{slug}/" not in html:
        die(f"{index} was not built with base /apps/{slug}/")

    drop = set(meta.get("drop") or [])
    for child in app_dir.iterdir():
        if child.name != "app.json":
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    copied = 0
    for f in sorted(dist.rglob("*")):
        rel = f.relative_to(dist).as_posix()
        if not f.is_file() or rel == "index.html" or rel in drop:
            continue
        out = app_dir / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
        copied += 1
    (ROOT / f"{slug}.html").write_text(html, encoding="utf-8", newline="\n")

    meta["commit"] = sha
    meta["built"] = dt.date.today().isoformat()
    manifest_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"sync_app: copied {copied} files from {src.name}@{sha[:7]}")

    if subprocess.run([sys.executable, str(ROOT / "scripts" / "check_apps.py")], cwd=ROOT).returncode != 0:
        die("check_apps.py failed; nothing committed")
    if a.no_commit:
        print("sync_app: --no-commit: changes left in the working tree")
        return 0
    git(ROOT, "add", "-A", "--", f"{slug}.html", f"apps/{slug}")
    msg = (f"App sync: {slug} @ {sha[:7]}\n\nBuilt from {meta.get('github') or src} {sha}.\n\n"
           "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    r = subprocess.run(["git", "commit", "-q", "-m", msg], cwd=ROOT)
    if r.returncode != 0:
        die("git commit failed (pre-commit hook?)")
    print("sync_app: committed. Deploy with scripts/deploy-cloudflare.sh (needs David's go-ahead).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
