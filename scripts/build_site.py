#!/usr/bin/env python3
"""Build dist/ for the Cloudflare Workers deploy of cheatsheets.davidveksler.com.

Spec: docs/specs/cloudflare-migration.md §2.1. Deploy: scripts/deploy-cloudflare.sh.

    python3 scripts/build_site.py                      # gates + build
    python3 scripts/build_site.py --skip-gates         # build only
    python3 scripts/build_site.py --write-worker-first # regenerate wrangler.jsonc's run_worker_first block

Steps:
  1. Gates: the always-run checks of scripts/deploy.py --check (catalog fresh, hubs,
     hub breadcrumbs, crypto custody hub).
  2. Copy every git-tracked file the droplet served publicly into dist/, through one
     rule set mirroring nginx (internal-paths.conf + WordOps denies). Everything else
     404s on Workers. No .php source is ever copied.
  3. Prerender the PHP pages with PHP CLI (scripts/prerender.php) into dist/_x/:
     Explorer, paths lens, each curated path, each category hub, popularity, sitemap.
     The site Worker (workers/site/index.js) maps the public URLs onto them.
  4. Write dist/_redirects (extensionless sheet URLs, retired URLs), dist/_headers and
     dist/404.html (from deploy/cloudflare/), and build/site-routes.json for the Worker.
  5. Check that wrangler.jsonc's run_worker_first lists every hub slug.

Stdlib only. Needs git and php (8.1+) on PATH.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SRC = ROOT / "deploy" / "cloudflare"
WRANGLER = ROOT / "wrangler.jsonc"
HOST = "cheatsheets.davidveksler.com"

# nginx internal-paths.conf: served on purpose (linked from sheets as provenance),
# as text/plain. The site Worker sets the content type.
PROVENANCE = ["docs/how-do-rainbows-work-production.md", "scripts/grass_green/build_spectra.py"]

# Files nginx never served, by name or rule. Anything here 404s on Workers.
INTERNAL_DIRS = {"docs", "marketing", "TODO", "scripts", "deploy", "conf", "lib", "workers", "state"}
INTERNAL_ROOT_NAMES = {"AGENTS.md", "SEO_PROMPT.txt", "requirements.txt", "check-category-map.php",
                       # repo tooling added for the Workers build, never public
                       "package.json", "package-lock.json", "wrangler.jsonc"}
# internal-paths.conf `\.(md|py|ps1)$`, every .php (source, not pages), and WordOps
# locations-wo.conf denies (403 on the droplet, 404 here).
INTERNAL_EXT = re.compile(
    r"\.(md|py|ps1|php|jsonc|old|orig|original|php#|php~|php_bak|save|swo|aspx?|tpl|sh|bash|bak?|cfg|cgi|"
    r"dll|exe|git|hg|ini|jsp|log|mdb|out|sql|svn|swp|tar|rdf|gz|zip|bz2|7z|pem|asc|conf|dump)$", re.I)
WORDOPS_DENY_NAME = re.compile(r"(^|/)(readme|license|example|legalnotice|installation|changelog)\.(txt|html|md)$", re.I)
NEWSLETTER_PUBLIC = re.compile(r"^newsletter/\d{4}-\d{2}\.html$")

TIMEOUT = 120


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", **kw)


def die(msg: str) -> None:
    print(f"build_site: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def git_files() -> list[str]:
    out = run(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD"], capture_output=True, check=True).stdout
    return [p for p in out.split("\0") if p]


def export_head(paths: list[str], dest: Path) -> None:
    """Write the committed bytes of `paths` (HEAD, LF per .gitattributes) under dest.
    The working tree can hold other bytes (a CRLF-writing tool on Windows, local
    edits); the deploy ships exactly what is committed."""
    r = subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=ROOT, capture_output=True, check=True)
    want = set(paths)
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tar:
        for m in tar.getmembers():
            if m.isfile() and m.name in want:
                out = dest / m.name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(tar.extractfile(m).read())
                want.discard(m.name)
    if want:
        die(f"not in HEAD: {sorted(want)[:5]}")


def is_public(path: str) -> bool:
    """Would nginx have served this repo path with a 200? (spec §1.2)"""
    if path in PROVENANCE:
        return True
    parts = path.split("/")
    if any(p.startswith(".") for p in parts):  # root dotfiles, .github/, .claude/ ...
        return False
    if NEWSLETTER_PUBLIC.match(path):
        return True
    if len(parts) > 1 and parts[0] in INTERNAL_DIRS | {"newsletter"}:
        return False
    if len(parts) == 1 and path in INTERNAL_ROOT_NAMES:
        return False
    if INTERNAL_EXT.search(path) or WORDOPS_DENY_NAME.search(path):
        return False
    return True


# --------------------------------------------------------------------- gates --
GATES = [
    ["scripts/build_catalog.py", "--check"],
    ["scripts/check_hubs.py"],
    ["scripts/add_hub_breadcrumbs.py", "--check"],
    ["scripts/check_cluster_hub.py"],
]


def gates() -> None:
    for g in GATES:
        print(f"  gate: {' '.join(g)}", flush=True)
        r = run([sys.executable, *g], capture_output=True, timeout=600)
        if r.returncode != 0:
            print(r.stdout[-3000:], r.stderr[-3000:], sep="\n", file=sys.stderr)
            die(f"gate failed: {' '.join(g)}")


# ----------------------------------------------------------------- prerender --
def prerender(page: str, uri: str, query: str, out: Path) -> None:
    env = dict(os.environ, TZ="UTC", MSYS_NO_PATHCONV="1")
    r = subprocess.run(["php", "-d", "display_errors=stderr", "scripts/prerender.php", page, uri, query],
                       cwd=ROOT, env=env, capture_output=True, timeout=TIMEOUT)
    errs = [ln for ln in r.stderr.decode("utf-8", "replace").splitlines()
            if ln.strip() and "already loaded" not in ln]  # a local php.ini duplicate-module notice
    if r.returncode != 0 or not r.stdout:
        die(f"prerender {page} {uri}?{query} failed (exit {r.returncode}): {' | '.join(errs[-5:])}")
    if errs:
        die(f"prerender {page} {uri}?{query} printed warnings: {' | '.join(errs[-5:])}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(r.stdout)


def clamp_text(s: str, n: int) -> str:
    """index.php clamp_text(): cut on a word boundary, append an ellipsis."""
    if len(s) <= n:
        return s
    cut = s[: n - 1]
    sp = cut.rfind(" ")
    if sp != -1 and sp > n * 0.6:
        cut = cut[:sp]
    return cut.rstrip(" ,;:.") + "…"


# ----------------------------------------------------------- worker globs --
def worker_first(hub_slugs: list[str]) -> list[str]:
    globs = ["/", "/*.php", "/_x/*", "/404.html", "/favicon.ico", *(("/" + p) for p in PROVENANCE)]
    for s in sorted(hub_slugs):
        globs += [f"/{s}", f"/{s}/"]
    if len(globs) > 100:
        die(f"run_worker_first would have {len(globs)} entries (limit 100)")
    return globs


BLOCK = re.compile(r"(// BEGIN run_worker_first\n)(.*?)(\s*// END run_worker_first)", re.S)


def render_block(globs: list[str], indent: str) -> str:
    body = ",\n".join(f'{indent}  "{g}"' for g in globs)
    return f'{indent}"run_worker_first": [\n{body}\n{indent}]'


def check_worker_first(globs: list[str], write: bool) -> None:
    text = WRANGLER.read_text(encoding="utf-8")
    m = BLOCK.search(text)
    if not m:
        die("wrangler.jsonc has no // BEGIN run_worker_first ... // END run_worker_first block")
    indent = re.match(r"\s*", m.group(2)).group(0) or "    "
    want = render_block(globs, indent)
    if m.group(2).rstrip() == want.rstrip():
        return
    if write:
        WRANGLER.write_text(text[: m.start(2)] + want + text[m.end(2):], encoding="utf-8", newline="\n")
        print("  wrangler.jsonc run_worker_first rewritten; commit it")
        return
    have = set(re.findall(r'"([^"]+)"', m.group(2)))
    missing = [g for g in globs if g not in have]
    extra = sorted(have - set(globs) - {"run_worker_first"})
    die("wrangler.jsonc run_worker_first is stale (missing %s, extra %s); run "
        "python3 scripts/build_site.py --write-worker-first and commit" % (missing, extra))


# --------------------------------------------------------------------- main --
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip-gates", action="store_true")
    ap.add_argument("--write-worker-first", action="store_true",
                    help="rewrite wrangler.jsonc's run_worker_first block from category-hubs.json and exit")
    a = ap.parse_args()

    hubs = json.loads((ROOT / "category-hubs.json").read_text(encoding="utf-8"))["hubs"]
    slug_to_cat = {v["slug"]: k for k, v in hubs.items() if isinstance(v, dict) and v.get("slug")}
    globs = worker_first(list(slug_to_cat))
    if a.write_worker_first:
        check_worker_first(globs, write=True)
        return 0

    for tool in ("git", "php"):
        if not shutil.which(tool):
            die(f"{tool} not found on PATH")

    if not a.skip_gates:
        print("==> gates", flush=True)
        gates()

    print("==> copy public files", flush=True)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    files = git_files()
    public = [p for p in files if is_public(p)]
    export_head(public, DIST)
    missing_prov = [p for p in PROVENANCE if p not in files]
    if missing_prov:
        die(f"provenance files linked from sheets are missing: {missing_prov}")
    print(f"  {len(public)} of {len(files)} tracked files are public")

    print("==> prerender PHP pages", flush=True)
    X = DIST / "_x"
    paths = json.loads((ROOT / "paths.json").read_text(encoding="utf-8")).get("paths", [])
    path_ids = [p["id"] for p in paths if isinstance(p, dict) and p.get("id") and p.get("steps")]
    jobs = [("index.php", "/", "", X / "index.html"),
            ("index.php", "/", "view=paths", X / "paths.html"),
            ("popularity.php", "/popularity.php", "", X / "popularity.html"),
            ("sitemap.php", "/sitemap.php", "", X / "sitemap.xml")]
    jobs += [("index.php", "/", f"view=paths&path={pid}", X / "path" / f"{pid}.html") for pid in path_ids]
    jobs += [("index.php", f"/{slug}", f"hub={slug}", X / "hub" / f"{slug}.html") for slug in sorted(slug_to_cat)]
    for page, uri, query, out in jobs:
        prerender(page, uri, query, out)
    print(f"  {len(jobs)} pages")

    # Sanity: the Explorer lists every catalogued sheet exactly once.
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    sheets = [s for s in catalog["sheets"] if s.get("file")]
    index_html = (X / "index.html").read_text(encoding="utf-8")
    cards = re.findall(r'<article class="c k\d+[^"]*"><.*?<h3><a href="([^"]+)"', index_html)
    if sorted(cards) != sorted(s["file"] for s in sheets):
        die(f"prerendered Explorer lists {len(cards)} cards, catalog has {len(sheets)} sheets")

    print("==> _redirects, _headers, 404, Worker routes", flush=True)
    root_html = sorted(p[:-5] for p in files if "/" not in p and p.endswith(".html"))
    lines = ["# Generated by scripts/build_site.py; do not edit dist/_redirects.",
             "# deploy/cloudflare/redirects.txt (was nginx redirects.conf): retired URLs."]
    lines += [ln.strip() for ln in (SRC / "redirects.txt").read_text(encoding="utf-8").splitlines()
              if ln.strip() and not ln.lstrip().startswith("#")]
    lines += ["# nginx category-hubs.conf + index.php: an extensionless sheet URL 301s to the file,",
             "# and its trailing-slash form 301s to the extensionless one (two hops, as before).",
             "# Hub slugs are served by the site Worker, never here."]
    for name in root_html:
        if name in slug_to_cat or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            continue
        lines += [f"/{name} /{name}.html 301", f"/{name}/ /{name} 301"]
    static = [ln for ln in lines if not ln.startswith("#")]
    if len(static) > 2000:
        die(f"{len(static)} static redirects exceed the 2,000 limit")
    (DIST / "_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    shutil.copyfile(SRC / "_headers", DIST / "_headers")
    shutil.copyfile(SRC / "404.html", DIST / "404.html")
    (DIST / ".well-known").mkdir(exist_ok=True)
    shutil.copyfile(SRC / ".well-known" / "traffic-advice", DIST / ".well-known" / "traffic-advice")

    by_file = {s["file"]: s for s in sheets}
    routes = {
        "hubs": slug_to_cat,
        "categories": {cat: slug for slug, cat in slug_to_cat.items()},
        "sheetFiles": root_html,
        # index.php's <title> for ?sheet=: clamp_text(title, 58), unescaped.
        "sheetTitles": {f: clamp_text(str(s.get("title") or f), 58) for f, s in by_file.items()},
        "paths": path_ids,
        "provenance": PROVENANCE,
    }
    BUILD.mkdir(exist_ok=True)
    (BUILD / "site-routes.json").write_text(json.dumps(routes, ensure_ascii=False, indent=1) + "\n",
                                            encoding="utf-8", newline="\n")
    check_worker_first(globs, write=False)

    n = sum(1 for _ in DIST.rglob("*") if _.is_file())
    size = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"==> dist/: {n} files, {size / 1e6:.1f} MB; {len(static)} redirects; {len(globs)} worker-first globs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
