#!/usr/bin/env python3
"""Visual regression screenshots of index.php's three lenses.

Captures Grid, Map, and Paths at 375px and 1440px, in light and dark theme,
from a local `php -S` server, full page, into the directory given by --out.
12 PNGs total, named "<lens>-<width>-<theme>.png".

Not a pixel-diff tool — there is no baseline to diff against yet. This is the
"take the shots, then a human (or an agent) looks at every one" step the
spec's Phase 3 asks for; run it, then open each PNG and check for overflow,
clipped text, unreadable contrast, or a missing image.

Usage:
    .venv/bin/python scripts/shot_index.py --out /path/to/dir
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _devserver import serve_php, stop_php  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PORT = 8767

LENSES = {"grid": "/", "map": "/?view=map", "paths": "/?view=paths"}
WIDTHS = [375, 1440]
THEMES = ["light", "dark"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="directory to write the 12 PNGs into")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        print(
            "Playwright is not installed in this interpreter. Run this script with "
            ".venv/bin/python (the repo's venv has playwright + a Chromium build).",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    php_proc = serve_php(ROOT, PORT)
    written: list[Path] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for theme in THEMES:
                for width in WIDTHS:
                    height = 900 if width >= 1440 else 800
                    page = browser.new_page(
                        viewport={"width": width, "height": height},
                        device_scale_factor=1,
                        color_scheme=theme,
                    )
                    for lens, path in LENSES.items():
                        page.goto(f"http://127.0.0.1:{PORT}{path}", wait_until="networkidle")
                        # Belt-and-suspenders: force the data-theme attribute
                        # directly rather than relying only on prefers-color-scheme,
                        # so the shot is deterministic even if a previous run left
                        # something in this browser context's storage.
                        page.evaluate(
                            "t => { document.documentElement.dataset.theme = t; }", theme
                        )
                        if lens == "map":
                            # Give the lazy catalog.json fetch + first draw a
                            # moment; same readiness signal render_og_map.py uses.
                            try:
                                page.wait_for_function(
                                    "window.csExplorer && window.csExplorer.mapDrawMs() > 0",
                                    timeout=15000,
                                )
                            except Exception as exc:  # noqa: BLE001
                                print(f"WARNING: {lens}-{width}-{theme}: map draw did not "
                                      f"complete in time ({exc}); shooting anyway", file=sys.stderr)
                        page.wait_for_timeout(150)
                        out_path = out_dir / f"{lens}-{width}-{theme}.png"
                        page.screenshot(path=str(out_path), full_page=True)
                        written.append(out_path)
                        print(f"wrote {out_path}")
                    page.close()
            browser.close()
    finally:
        stop_php(php_proc)

    print(f"\n{len(written)} screenshots written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
