#!/usr/bin/env python3
"""Render images/artificial-gravity-calculator.png (1200x630) from the live spin chart.

The page draws the chart itself (inline SVG, `#spinChart`). This serves the repo root, moves that element into a
full-viewport report-paper overlay with a title strip, hides the live marker, enlarges the labels for a social
card, screenshots it in the light theme, and quantizes the result to a palette PNG like the other previews.

    python3 scripts/render_og_artificial_gravity.py

Re-run after changing the chart, the designs list or the palette.
"""
from __future__ import annotations

import functools
import http.server
import pathlib
import socketserver
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = "artificial-gravity-calculator.html"
OUT = ROOT / "images" / "artificial-gravity-calculator.png"
PORT = 8792

CSS = """
#spinChart .ch-live, #spinChart .ch-cross, #spinChart .ch-livelab { display: none; }
#spinChart .ch-lab { font-size: 15.5px; } #spinChart .ch-lab-cz { font-size: 19px; }
#spinChart .ch-tick { font-size: 13px; } #spinChart .ch-axt { font-size: 14px; }
#spinChart .ch-bandlab { font-size: 13px; } #spinChart .ch-isolab { font-size: 13.5px; } #spinChart .ch-isolab1 { font-size: 15px; }
#spinChart .ch-splab { font-size: 13px; }
#og .ogt { display: flex; justify-content: space-between; align-items: baseline; height: 50px; padding: 0 6px; }
#og .ogt b { font: 700 31px/1.1 Georgia, 'Times New Roman', serif; color: var(--ink); }
#og .ogt span { font: 600 15px ui-monospace, Consolas, monospace; color: var(--muted); letter-spacing: .04em; }
"""

JS = """() => {
  const ov = document.createElement('div');
  ov.id = 'og';
  ov.style.cssText = 'position:fixed;inset:0;z-index:99999;background:var(--paper);padding:6px 12px 0;box-sizing:border-box;overflow:hidden';
  ov.innerHTML = '<div class="ogt"><b>Artificial gravity: how fast to spin, and how big to build</b><span>cheatsheets.davidveksler.com</span></div>';
  const ch = document.getElementById('spinChart');
  ch.style.width = '1176px';
  ov.appendChild(ch);
  document.body.appendChild(ov);
}"""


def main() -> int:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    raw = OUT.with_suffix(".raw.png")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1, color_scheme="light")
        page.goto(f"http://127.0.0.1:{PORT}/{PAGE}", wait_until="networkidle")
        page.add_style_tag(content=CSS)
        page.evaluate(JS)
        page.wait_for_timeout(600)
        page.screenshot(path=str(raw), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        browser.close()
    httpd.shutdown()
    im = Image.open(raw).convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(OUT, optimize=True)
    raw.unlink()
    print("wrote", OUT, OUT.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
