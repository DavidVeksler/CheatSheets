#!/usr/bin/env python3
"""Render the social preview from the live 3D scene.

Run: python scripts/render_inside_ai_dc_social.py
Requires playwright and Pillow, with Chromium installed for Playwright.
"""

from __future__ import annotations

import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=str(ROOT), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/inside-ai-data-center.html"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 800}, device_scale_factor=1)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function("document.documentElement.classList.contains('webgl')")
            page.set_viewport_size({"width": 1200, "height": 630})
            page.locator('[data-go="3"]').click()
            page.wait_for_function(
                "document.querySelector('#stop-title').textContent.startsWith('03 /')"
            )
            page.locator("#explode").click()
            page.evaluate("document.documentElement.classList.add('social')")
            page.wait_for_timeout(150)
            page.locator("#viewport").screenshot(path=str(ROOT / "images" / "inside-ai-data-center.png"))
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
