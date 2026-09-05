#!/usr/bin/env python3
"""Render the live Map lens to images/cheatsheets-og-portfolio.png.

Starts `php -S 127.0.0.1:8766` from the repo root, loads the index's
`?view=map&og=1` render mode (a minimal, always-noindex mode added to
index.php purely for this script: it forces the map lens and dark theme,
hides the topbar/rail/legend/hint text/lens switcher, and draws the canvas
at exactly 1200x630 with a caption naming the live counts), waits for the
map to finish its first draw, and screenshots the #mapfig element (canvas +
caption) to images/cheatsheets-og-portfolio.png.

This is the same headless-Chromium approach as scripts/shot.py: Playwright,
run from the repo's .venv (checked present at implementation time; shot.py's
node/shot.cjs fallback exists for environments without a Python Playwright
install, but is not duplicated here since a working .venv is this repo's
normal state — see docs/marketing.md if that ever needs to change).

Usage:
    .venv/bin/python scripts/render_og_map.py            # render + optimize
    .venv/bin/python scripts/render_og_map.py --check     # verify only, no render

Manual step, not part of any git hook or CI workflow (headless Chromium is
too slow for pre-commit) — see docs/marketing.md for when to re-run it.
"""

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _devserver import serve_php, stop_php  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "cheatsheets-og-portfolio.png"
PORT = 8766
WIDTH, HEIGHT = 1200, 630
MAX_BYTES = 300 * 1024


def png_dimensions(path: Path) -> tuple[int, int] | None:
    """Read width/height straight out of the PNG IHDR chunk; no Pillow needed."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def run_check() -> int:
    if not OUT.exists():
        print(f"{OUT} is missing. Run: .venv/bin/python scripts/render_og_map.py", file=sys.stderr)
        return 1
    dims = png_dimensions(OUT)
    if dims != (WIDTH, HEIGHT):
        print(f"{OUT} is {dims}, expected ({WIDTH}, {HEIGHT}). "
              f"Run: .venv/bin/python scripts/render_og_map.py", file=sys.stderr)
        return 1
    size = OUT.stat().st_size
    print(f"{OUT} is {WIDTH}x{HEIGHT}, {size:,} bytes.")
    if size > MAX_BYTES:
        print(f"WARNING: {size:,} bytes exceeds the {MAX_BYTES:,}-byte budget", file=sys.stderr)
    return 0


def render() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        print(
            "Playwright is not installed in this interpreter. Run this script with "
            ".venv/bin/python (the repo's venv has playwright + a Chromium build).",
            file=sys.stderr,
        )
        return 1

    php_proc = serve_php(ROOT, PORT)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": WIDTH, "height": HEIGHT},
                device_scale_factor=1,
                color_scheme="dark",
            )
            page.goto(f"http://127.0.0.1:{PORT}/?view=map&og=1", wait_until="networkidle")
            # The map block fetches catalog.json (lazy) then does one synchronous
            # draw(); window.csExplorer.mapDrawMs() is 0 until that draw has run
            # (see index.php's "Measurement hook" comment at the end of its
            # inline JS), so poll for a positive value instead of a fixed sleep.
            try:
                page.wait_for_function(
                    "window.csExplorer && window.csExplorer.mapDrawMs() > 0 "
                    "&& document.body.dataset.view === 'map'",
                    timeout=15000,
                )
            except Exception as exc:  # noqa: BLE001 - report and still try to shoot
                print(f"WARNING: map did not report a completed draw within 15s ({exc}); "
                      f"screenshotting anyway", file=sys.stderr)
            page.wait_for_timeout(150)  # let the final repaint settle on screen

            robots = page.locator('meta[name="robots"]').get_attribute("content")
            if not robots or "noindex" not in robots:
                print(f"ERROR: ?og=1 did not render noindex (robots={robots!r}); refusing to publish "
                      f"a page that could be mistaken for indexable.", file=sys.stderr)
                return 1

            fig = page.locator("#mapfig")
            box = fig.bounding_box()
            if not box or round(box["width"]) != WIDTH or round(box["height"]) != HEIGHT:
                print(f"WARNING: #mapfig measured {box}, expected {WIDTH}x{HEIGHT}", file=sys.stderr)
            OUT.parent.mkdir(parents=True, exist_ok=True)
            fig.screenshot(path=str(OUT))
            browser.close()
    finally:
        stop_php(php_proc)

    dims = png_dimensions(OUT)
    if dims != (WIDTH, HEIGHT):
        print(f"ERROR: wrote {OUT} at {dims}, expected ({WIDTH}, {HEIGHT})", file=sys.stderr)
        return 1

    optipng = shutil.which("optipng")
    if optipng:
        subprocess.run([optipng, "-quiet", "-o2", str(OUT)], check=False)
    else:
        print("optipng not found on PATH; wrote the PNG unoptimized.", file=sys.stderr)

    size = OUT.stat().st_size
    print(f"Wrote {OUT} — {WIDTH}x{HEIGHT}, {size:,} bytes.")
    if size > MAX_BYTES:
        print(f"WARNING: {size:,} bytes exceeds the {MAX_BYTES:,}-byte budget", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the existing PNG only; no render")
    args = parser.parse_args()
    if args.check:
        return run_check()
    return render()


if __name__ == "__main__":
    sys.exit(main())
