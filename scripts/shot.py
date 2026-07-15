#!/usr/bin/env python3
"""Generate a 1200x630 dark-theme social preview for one or more pages.

Usage: python scripts/shot.py rockets-and-spaceflight.html [more.html ...]
Serves the repo root on a local port and screenshots each page to images/{stem}.png.
"""
import sys, threading, functools, http.server, socketserver, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8791

def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

def main():
    files = sys.argv[1:]
    if not files:
        print("no files"); return 1
    serve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":1200,"height":630},
                                device_scale_factor=2,
                                color_scheme="dark")
        for f in files:
            stem = pathlib.Path(f).stem
            page.goto(f"http://127.0.0.1:{PORT}/{f}", wait_until="networkidle")
            # force dark, hide floating controls
            page.evaluate("""() => {
                document.documentElement.dataset.theme = 'dark';
                for (const sel of ['#themeToggle','.theme-button','.skip-link','#backTop']) {
                    document.querySelectorAll(sel).forEach(e => e.style.display='none');
                }
                window.scrollTo(0,0);
            }""")
            page.wait_for_timeout(400)
            out = ROOT / "images" / f"{stem}.png"
            page.screenshot(path=str(out), clip={"x":0,"y":0,"width":1200,"height":630})
            print("wrote", out)
        browser.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
