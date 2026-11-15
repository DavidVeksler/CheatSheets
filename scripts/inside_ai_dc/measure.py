#!/usr/bin/env python3
"""Budget measurements for the inside-ai-data-center models (spec section 9), old (?models=procedural) vs new.

Profiles: desktop (no throttling) and mobile (375x812, 4x CPU throttle, Lighthouse "slow 4G": 150 ms RTT,
1.6 Mbit/s down). Headless Chromium renders with SwiftShader (software WebGL), so frame rates are CPU-bound and are
a relative comparison, not a device claim.

Per stop: draw calls and triangles from window.__dcMetrics (renderer.info, shadow pass included), cold time from
stop change to model on screen (fresh browser context, HTTP cache empty, model not prefetched), cached time
(stop revisited from stop n+1, parsed model in memory; n -> n+1 would add the 680 ms zoom transition), and orbit frame rate (arrow-key rotation every animation frame for 3 s).

Run: python scripts/inside_ai_dc/measure.py [out.json]
"""

from __future__ import annotations

import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
STOPS = (3, 4)
ORBIT_JS = """async () => {
  const c = document.querySelector('#canvas-wrap canvas'); let frames = 0; const t0 = performance.now();
  await new Promise(res => { function step() { c.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowLeft', bubbles: true}));
    frames++; if (performance.now() - t0 < 3000) requestAnimationFrame(step); else res(); } requestAnimationFrame(step); });
  return Math.round(frames / ((performance.now() - t0) / 1000) * 10) / 10; }"""
SWITCH_JS = """async (stop) => { const t0 = performance.now(); document.querySelector(`[data-go="${stop}"]`).click();
  await new Promise(res => { function poll() { const m = window.__dcMetrics;
    if (!m.loading && m.model && (m.model === 'procedural' || (m.modelPaintedAt || 0) > t0)) requestAnimationFrame(() => res()); else requestAnimationFrame(poll); } requestAnimationFrame(poll); });
  return Math.round(performance.now() - t0); }"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(p, base, query, mobile):
    browser = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    vp = {"width": 375, "height": 812} if mobile else {"width": 1280, "height": 800}
    out = {}
    for stop in STOPS:
        ctx = browser.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile)
        page = ctx.new_page()
        sizes = {}
        page.on("response", lambda r: r.url.endswith(".glb") and sizes.setdefault(r.url.rsplit("/", 1)[1], int(r.headers.get("content-length", 0))))
        cdp = ctx.new_cdp_session(page)
        page.goto(f"{base}{query}", wait_until="load")
        page.wait_for_function("document.documentElement.classList.contains('webgl')", timeout=30000)
        page.wait_for_timeout(500)
        if mobile:
            cdp.send("Network.enable")
            cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150,
                                                          "downloadThroughput": 1.6 * 1024 * 1024 / 8,
                                                          "uploadThroughput": 750 * 1024 / 8})
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        cold = page.evaluate(SWITCH_JS, stop)
        page.wait_for_timeout(800)
        metrics = page.evaluate("({...window.__dcMetrics})")
        fps = page.evaluate(ORBIT_JS)
        page.evaluate("document.querySelector('#reset').click()")
        other = stop + 1  # leave by the next stop and come back: n+1 -> n has no zoom transition
        page.evaluate(SWITCH_JS, other)
        page.wait_for_timeout(500)
        cached = page.evaluate(SWITCH_JS, stop)
        out[stop] = {"coldMs": cold, "cachedMs": cached, "orbitFps": fps, "drawCalls": metrics["drawCalls"],
                     "triangles": metrics["triangles"], "model": metrics.get("model"), "glbBytes": sizes}
        ctx.close()
    browser.close()
    return out


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}/inside-ai-data-center.html"
    result = {}
    try:
        with sync_playwright() as p:
            for label, query in (("old", "?models=procedural"), ("new", "?models=glb")):
                for profile, mobile in (("desktop", False), ("mobile", True)):
                    result[f"{label}-{profile}"] = run(p, base, query, mobile)
                    print(label, profile, json.dumps(result[f"{label}-{profile}"]))
    finally:
        server.shutdown()
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
