#!/usr/bin/env python3
"""Generate a 1200x630 dark-theme social preview for one or more pages.

Usage: python scripts/shot.py rockets-and-spaceflight.html [more.html ...]
Serves the repo root on a local port and screenshots each page to images/{stem}.png.
"""
import os, shutil, subprocess, sys, threading, functools, http.server, socketserver, pathlib

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
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        node = shutil.which("node")
        modules = None
        bundled = pathlib.Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node"
        if not node and (bundled / "bin" / "node.exe").is_file():
            node = str(bundled / "bin" / "node.exe")
        if (bundled / "node_modules" / "playwright").is_dir():
            modules = bundled / "node_modules"
        if not node or not modules:
            print("Playwright is unavailable in Python and no bundled Node runtime was found.")
            return 1
        env = os.environ.copy()
        env["NODE_PATH"] = str(modules)
        return subprocess.run([node, str(ROOT / "scripts" / "shot.cjs"), *files], cwd=ROOT, env=env).returncode
    serve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":1200,"height":630},
                                device_scale_factor=1,
                                color_scheme="dark")
        for f in files:
            stem = pathlib.Path(f).stem
            page.goto(f"http://127.0.0.1:{PORT}/{f}", wait_until="networkidle")
            # force dark, hide floating controls
            page.evaluate("""() => {
                document.documentElement.dataset.theme = 'dark';
                for (const sel of ['#themeToggle','.theme-button','.skip-link','#backTop','.utility','nav.sections']) {
                    document.querySelectorAll(sel).forEach(e => e.style.display='none');
                }
                window.scrollTo(0,0);
            }""")
            page.wait_for_timeout(400)
            out = ROOT / "images" / f"{stem}.png"
            capture = page.locator("[data-og-capture]")
            if capture.count():
                capture.evaluate("""target => {
                    [...document.body.children].forEach(el => { if (el !== target.parentElement) el.style.display = 'none'; });
                    [...target.parentElement.children].forEach(el => { if (el !== target) el.style.display = 'none'; });
                    Object.assign(target.parentElement.style, {padding:'0',width:'100%'});
                    Object.assign(target.style, {margin:'0',transform:'none',width:'100%'});
                    target.querySelectorAll(':scope > h2, :scope > .section-note, :scope > .matrix-key')
                        .forEach(el => el.style.display = 'none');
                    window.scrollTo(0, 0);
                }""")
                page.screenshot(path=str(out), clip={"x":0,"y":0,"width":1200,"height":630})
            else:
                page.screenshot(path=str(out), clip={"x":0,"y":0,"width":1200,"height":630})
            print("wrote", out)
        browser.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
