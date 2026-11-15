#!/usr/bin/env python3
"""Render the space-combat.html share images from the generated chart SVG.

    python scripts/render_og_space_combat.py

Writes images/space-combat.png (1200x630, Open Graph / X card) and images/space-combat-portrait.png
(1200x1500). Both come from build_space_combat.render_chart() ("og" and "tall" variants, which add
the title strip and legend to the same geometry) injected into the live page so the page CSS styles
them, then screenshotted at 1x and quantized to a palette PNG. Re-run after changing the data.
"""
from __future__ import annotations

import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_space_combat as B  # noqa: E402

ROOT = B.ROOT
PORT = 8793
OUTS = {"og": ROOT / "images" / "space-combat.png", "tall": ROOT / "images" / "space-combat-portrait.png"}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):  # noqa: D401
        pass


def main() -> int:
    data = B.load_data()
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for variant, out in OUTS.items():
                v = B.VARIANTS[variant]
                page = browser.new_page(viewport={"width": v["W"], "height": v["H"]}, device_scale_factor=1, color_scheme="dark")
                page.goto(f"http://127.0.0.1:{PORT}/space-combat.html", wait_until="networkidle")
                page.evaluate("""svg => {
                  const fig = document.createElement('figure');
                  fig.className = 'hero'; fig.id = 'export';
                  fig.style.cssText = 'position:fixed;inset:0;margin:0;border:0;border-radius:0;z-index:99999';
                  fig.innerHTML = svg;
                  document.body.appendChild(fig);
                }""", B.render_chart(data, variant))
                raw = out.with_suffix(".raw.png")
                page.locator("#export svg").screenshot(path=str(raw))
                page.close()
                img = Image.open(raw).convert("RGB")
                assert img.size == (v["W"], v["H"]), img.size
                img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(out, optimize=True)
                raw.unlink()
                print(f"{out.relative_to(ROOT)}: {img.size[0]}x{img.size[1]}, {out.stat().st_size // 1024} KB")
            browser.close()
    finally:
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
