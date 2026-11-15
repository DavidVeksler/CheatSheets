#!/usr/bin/env python3
"""Unlabelled part test captures for inside-ai-data-center.html (spec section 10).

Hides every overlay, pin, label and control, then screenshots the bare model at
the requested stops, desktop 1280x800 and phone 375x812.

Run: python scripts/inside_ai_dc/unlabelled.py OUT_DIR [--query ?models=procedural] [--stops 3,4]
"""

from __future__ import annotations

import argparse
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
HIDE = (".topbar,.crumbs,.overlay,.nameplate,.flow-tags,.drawing-title,.scale,.controls,"
        "#zoom-in,#inspector,#labels,#leaders{visibility:hidden!important}")


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--query", default="")
    ap.add_argument("--stops", default="3,4")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stops = [int(s) for s in args.stops.split(",")]
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/inside-ai-data-center.html{args.query}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
            for label, vp, mobile in [("desk", {"width": 1280, "height": 800}, False),
                                      ("phone", {"width": 375, "height": 812}, True)]:
                page = browser.new_page(viewport=vp, device_scale_factor=1, is_mobile=mobile, has_touch=mobile)
                page.goto(url, wait_until="domcontentloaded")
                page.locator("#stop-0").scroll_into_view_if_needed()
                page.wait_for_function("document.documentElement.classList.contains('webgl')", timeout=20000)
                page.add_style_tag(content=HIDE)
                for stop in stops:
                    page.evaluate(f"document.querySelector('[data-go=\"{stop}\"]').click()")
                    page.wait_for_function("window.__dcMetrics && !window.__dcMetrics.loading", timeout=30000)
                    page.wait_for_timeout(1500)
                    page.screenshot(path=str(out / f"bare-{label}-{stop}.png"))
                page.close()
            browser.close()
    finally:
        server.shutdown()
    print("unlabelled captures:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
