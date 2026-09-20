#!/usr/bin/env python3
"""Render images/why-is-grass-green.png (1200x630): title beside the live spectrum bench.

scripts/shot.py captures the top of the page, which for this sheet is only the
title and deck. This script restyles the hero for one frame so the measured
spectra sit next to the headline, as the og:image:alt promises.
"""
import functools, http.server, pathlib, socketserver, threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PORT = 8797
OUT = ROOT / "images" / "why-is-grass-green.png"
CSS = """
.masthead,.deck,.callout,.bench-controls,.bench-readout,figcaption,.depth-nav,main,footer,.eyebrow{display:none!important}
.hero{display:grid;grid-template-columns:400px 1fr;align-items:center;height:630px;min-height:0;column-gap:0}
.hero .intro{padding:0 0 0 44px;max-width:none}
.hero h1{font-size:4.9rem;line-height:.95}
.bench-wrap{width:auto;margin:0 34px 0 0;padding:0}
.bench{padding:10px 8px 4px;border-color:rgba(255,255,255,.2)}
.bench .plot{overflow:visible}
"""

def main():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1, color_scheme="dark")
        pg.goto(f"http://127.0.0.1:{PORT}/why-is-grass-green.html", wait_until="networkidle")
        pg.add_style_tag(content=CSS)
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        b.close()
    print("wrote", OUT)

if __name__ == "__main__":
    main()
