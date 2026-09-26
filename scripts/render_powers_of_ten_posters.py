#!/usr/bin/env python3
"""Render the eight text-free drawing plates and the social preview.

Run: python scripts/render_powers_of_ten_posters.py
Requires playwright and Pillow, with Chromium installed for Playwright.
"""

from __future__ import annotations

import io
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "inside-ai-data-center"


def save_image(image: Image.Image, path: Path, image_format: str, **options: object) -> None:
    data = io.BytesIO()
    image.save(data, format=image_format, **options)
    for attempt in range(8):
        try:
            path.write_bytes(data.getvalue())
            return
        except OSError:
            if attempt == 7:
                raise
            time.sleep(0.2 * (attempt + 1))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=str(ROOT), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/inside-ai-data-center.html"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 800}, device_scale_factor=1)
            # The live page lazy-loads these same fallback files while scrolling.
            # Skip those requests so Windows does not lock an image during overwrite.
            page.route("**/images/inside-ai-data-center/stop-*", lambda route: route.abort())
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function("document.documentElement.classList.contains('webgl')")
            for stop in range(8):
                page.locator(f'[data-go="{stop}"]').click()
                page.wait_for_function(
                    "stop => document.querySelector('#stop-title').textContent.startsWith(`0${stop} /`)",
                    arg=stop,
                )
                page.wait_for_timeout(80)  # let the completed scene paint before capture
                page.evaluate("document.documentElement.classList.add('poster')")
                raw = page.locator("#viewport").screenshot()
                image = Image.open(io.BytesIO(raw)).convert("RGB")
                save_image(image, OUT / f"stop-{stop}.png", "PNG", optimize=True)
                save_image(image, OUT / f"stop-{stop}.webp", "WEBP", quality=83, method=6)
                page.evaluate("document.documentElement.classList.remove('poster')")
                print(f"stop {stop}: {(OUT / f'stop-{stop}.webp').stat().st_size:,} WebP bytes")
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
