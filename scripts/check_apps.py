#!/usr/bin/env python3
"""Gate for built multi-file apps (docs/specs/apps.md).

Each app is apps/<slug>/app.json + a vendored build under apps/<slug>/ + its entry
page at the repo root as <slug>.html. Fails (exit 1) when:

  * <slug>.html is missing, not in category-map.php, or its canonical / og:image
    do not match the site contract;
  * the entry page points at a root-absolute path outside /apps/<slug>/, or at a
    file under it that does not exist;
  * app.json lacks the source commit (the copy must be traceable to a build);
  * a file under apps/<slug>/ is referenced by nothing: not the entry page, not a
    sibling CSS/JS file, and not a `runtime` glob in app.json (stale build output).

Run by scripts/build_site.py (Cloudflare deploy) and scripts/deploy.py --check.
"""

from __future__ import annotations

import fnmatch
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "apps"
SITE = "https://cheatsheets.davidveksler.com"
SHA = re.compile(r"^[0-9a-f]{40}$")


class Refs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []
        self.canonical: str | None = None
        self.og_image: str | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("src", "href"):
            if a.get(key):
                self.targets.append(a[key].strip())
        if tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")
        if tag == "meta" and a.get("property") == "og:image":
            self.og_image = a.get("content")


def check(manifest: Path) -> list[str]:
    errors: list[str] = []
    app_dir = manifest.parent
    slug = app_dir.name
    try:
        meta = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"{manifest.relative_to(ROOT)}: unreadable ({e})"]
    if meta.get("slug") != slug:
        errors.append(f"app.json slug {meta.get('slug')!r} != directory {slug!r}")
    if not SHA.match(meta.get("commit") or ""):
        errors.append(f"{slug}: app.json has no source commit; update it with scripts/sync_app.py {slug}")

    entry = ROOT / f"{slug}.html"
    if not entry.is_file():
        return errors + [f"{slug}: entry page {entry.name} missing at the repo root"]
    if f"'{slug}.html'" not in (ROOT / "category-map.php").read_text(encoding="utf-8"):
        errors.append(f"{slug}: {entry.name} is not in category-map.php")

    html = entry.read_text(encoding="utf-8")
    p = Refs()
    p.feed(html)
    if p.canonical != f"{SITE}/{slug}.html":
        errors.append(f"{slug}: canonical is {p.canonical!r}, expected {SITE}/{slug}.html")
    if p.og_image:
        img = p.og_image.removeprefix(SITE + "/").lstrip("/")
        if not img.startswith("http") and not (ROOT / img).is_file():
            errors.append(f"{slug}: og:image {p.og_image} has no file in the repo")
    else:
        errors.append(f"{slug}: og:image missing")

    base = f"/apps/{slug}/"
    referenced: set[str] = set()
    for t in p.targets:
        if t.startswith(("http://", "https://", "#", "mailto:", "data:")) or not t.startswith("/"):
            continue
        if t.startswith("//"):
            continue
        path = t.split("#", 1)[0].split("?", 1)[0]
        if not path.startswith(base):
            errors.append(f"{slug}: entry page references {path}, outside {base}")
            continue
        rel = path[len(base):]
        if not (app_dir / rel).is_file():
            errors.append(f"{slug}: entry page references {path}, which does not exist")
        referenced.add(rel)

    files = sorted(f.relative_to(app_dir).as_posix() for f in app_dir.rglob("*") if f.is_file())
    files = [f for f in files if f != "app.json"]
    bundle_text = "\n".join((app_dir / f).read_text(encoding="utf-8", errors="replace")
                            for f in files if f.endswith((".js", ".css", ".mjs")))
    runtime = meta.get("runtime") or []
    for f in files:
        if f in referenced or any(fnmatch.fnmatch(f, g) for g in runtime):
            continue
        if Path(f).name in bundle_text:  # chunk imports, CSS url(), worker scripts
            continue
        errors.append(f"{slug}: apps/{slug}/{f} is referenced by nothing (stale build output?)")
    if not files:
        errors.append(f"{slug}: apps/{slug}/ holds no build output")
    return errors


def main() -> int:
    manifests = sorted(APPS.glob("*/app.json")) if APPS.is_dir() else []
    errors = [e for m in manifests for e in check(m)]
    if errors:
        print(f"check_apps: {len(errors)} problem(s)")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"check_apps: {len(manifests)} app(s) OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
