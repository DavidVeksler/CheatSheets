#!/usr/bin/env python3
"""Layout QA for inside-ai-data-center.html.

Screenshots every stop and state at 1280x800 and 375x812 (mobile emulation),
then reports overlapping overlay UI, elements pushed off-screen, page errors,
and render metrics (draw calls, triangles, callout layout time).

Run: python scripts/qa_inside_ai_dc.py [out_dir]   (default: a temp dir)
Exits 1 if any desktop state has an overlap or the page logs an error.
Phone overlaps are reported but not fatal: at 375 px labels share the drawing.
"""

from __future__ import annotations

import json
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="dc-qa-"))
OUT.mkdir(parents=True, exist_ok=True)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


OVERLAP_JS = """() => {
  const sel = '.nameplate,.drawing-title,.controls button:not([hidden]),.flow-tags span:not([hidden]),.worked.active,.css2d .callout:not([data-pin-only=true]),.css2d .pin,#zoom-in:not([hidden]),.overlay,.topbar,.crumbs,.lineup-tag,.dimension-label,.css2d .correction button,.scale';
  const els = [...document.querySelectorAll(sel)].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden' && r.bottom > 0 && r.top < innerHeight; });
  const name = e => (e.className || e.id || e.tagName).toString().slice(0, 18) + ':' + (e.textContent || '').trim().slice(0, 22);
  const out = [];
  for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) {
    const a = els[i], b = els[j]; if (a.contains(b) || b.contains(a)) continue;
    const r = a.getBoundingClientRect(), s = b.getBoundingClientRect();
    const w = Math.min(r.right, s.right) - Math.max(r.left, s.left), h = Math.min(r.bottom, s.bottom) - Math.max(r.top, s.top);
    if (w > 3 && h > 3) out.push(name(a) + '  X  ' + name(b));
  }
  const off = els.filter(e => { const r = e.getBoundingClientRect(); return r.left < -2 || r.right > innerWidth + 2; }).map(name);
  return {overlaps: out, offscreen: off, scrollWidth: document.documentElement.scrollWidth, metrics: window.__dcMetrics};
}"""

STATES = [(s, None) for s in range(8)] + [(3, "explode"), (3, "lineup"), (3, "fail"), (4, "fail")]


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/inside-ai-data-center.html"
    report: dict = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
            for label, vp, mobile in [("desk", {"width": 1280, "height": 800}, False), ("phone", {"width": 375, "height": 812}, True)]:
                page = browser.new_page(viewport=vp, device_scale_factor=1, is_mobile=mobile, has_touch=mobile)
                errors: list[str] = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("console", lambda m: m.type == "error" and errors.append(m.text))
                page.goto(url, wait_until="domcontentloaded")
                page.locator("#stop-0").scroll_into_view_if_needed()
                page.wait_for_function("document.documentElement.classList.contains('webgl')", timeout=20000)
                for stop, action in STATES:
                    page.evaluate(f"document.querySelector('[data-go=\"{stop}\"]').click()")
                    page.wait_for_timeout(1100)
                    if action:
                        page.evaluate(f"document.querySelector('#{action}').click()")
                        page.wait_for_timeout(500)
                    key = f"{label}-{stop}{'-' + action if action else ''}"
                    page.screenshot(path=str(OUT / f"{key}.png"))
                    report[key] = page.evaluate(OVERLAP_JS)
                    if report[key]["scrollWidth"] > vp["width"]:
                        errors.append(f"{key}: page scrollWidth {report[key]['scrollWidth']} > viewport")
                    if action:
                        page.evaluate(f"document.querySelector('#{action}').click()")
                        page.wait_for_timeout(300)
                report[label + "-errors"] = errors
                page.close()
            browser.close()
    finally:
        server.shutdown()
    (OUT / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    for key, value in report.items():
        if key.endswith("errors"):
            print(key, value)
            continue
        print(f"== {key}: {len(value['overlaps'])} overlaps, offscreen={value['offscreen']} metrics={value['metrics']}")
        for overlap in value["overlaps"]:
            print("   ", overlap)
    print("screenshots:", OUT)
    bad = [k for k, v in report.items() if k.startswith("desk") and not k.endswith("errors") and v["overlaps"]]
    return 1 if bad or report.get("desk-errors") or report.get("phone-errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
