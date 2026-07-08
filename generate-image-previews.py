#!/usr/bin/env python3
"""generate-image-previews.py

Does exactly three things, and nothing else:

  1. Generates a 1200x630 social-preview screenshot per cheatsheet -> images/{stem}.png
  2. Runs ImageOptim.app on generated preview images to minify them
  3. Adds any MISSING Open Graph / Twitter / canonical meta tags to the <head>

It NEVER reformats or re-serializes your HTML. Tags are inserted surgically as a
text block immediately before </head>; existing tags are left untouched. This is
the deliberate fix for the old version, which round-tripped every file through
BeautifulSoup.prettify() and mangled <pre>/<code> whitespace and attribute order.

Usage:
  python3 generate-image-previews.py                 # dry run: report what's missing
  python3 generate-image-previews.py --apply         # add missing OG tags + make missing images
  python3 generate-image-previews.py --apply --force # also regenerate images that already exist
  python3 generate-image-previews.py --apply foo.html bar.html   # only these files
  python3 generate-image-previews.py --apply --no-images         # tags only
  python3 generate-image-previews.py --apply --no-og             # images only

Deps: beautifulsoup4 (tag reading), playwright (screenshots).
"""

import argparse
import html as html_lib
import socket
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Error: beautifulsoup4 is not installed. Run: python3 -m pip install beautifulsoup4")

DEFAULT_BASE_URL = "https://cheatsheets.davidveksler.com/"
VIEWPORT = {"width": 1200, "height": 630}
IMAGEOPTIM_BUNDLE_ID = "net.pornel.ImageOptim"
IMAGEOPTIM_SETTLE_SECONDS = 2
# Floating UI chrome that should not appear in the social preview.
HIDE_SELECTORS = ["#themeToggle", "#backTop", ".theme-toggle", ".back-top", ".back-to-top"]


class C:
    HEADER, BLUE, GREEN, YELLOW, RED, ENDC, BOLD = (
        "\033[95m", "\033[94m", "\033[92m", "\033[93m", "\033[91m", "\033[0m", "\033[1m",
    )


# --------------------------------------------------------------------------- #
# OG / meta tag analysis (read-only) + surgical insertion
# --------------------------------------------------------------------------- #

def attr(value: str) -> str:
    """Escape a string for safe use inside a double-quoted HTML attribute."""
    return html_lib.escape(value or "", quote=True)


def desired_tags(soup: BeautifulSoup, stem: str, page_url: str, image_url: str):
    """Return an ordered list of (label, html) for tags this page SHOULD have.

    Each tag's html is only used if the tag is currently missing (add-only).
    """
    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else stem

    desc_el = soup.find("meta", attrs={"name": "description"})
    desc = desc_el.get("content", "").strip() if desc_el else ""

    t, d = attr(title), attr(desc)
    img, url = attr(image_url), attr(page_url)

    tags = [
        ("og:title", f'<meta property="og:title" content="{t}">'),
        ("og:type", '<meta property="og:type" content="website">'),
        ("og:url", f'<meta property="og:url" content="{url}">'),
        ("og:image", f'<meta property="og:image" content="{img}">'),
        ("og:image:alt", f'<meta property="og:image:alt" content="{t}">'),
        ("twitter:card", '<meta name="twitter:card" content="summary_large_image">'),
        ("twitter:title", f'<meta name="twitter:title" content="{t}">'),
        ("twitter:image", f'<meta name="twitter:image" content="{img}">'),
        ("canonical", f'<link rel="canonical" href="{url}">'),
    ]
    # Description-derived tags only if the page actually has a description.
    if desc:
        tags.insert(1, ("og:description", f'<meta property="og:description" content="{d}">'))
        tags.append(("twitter:description", f'<meta name="twitter:description" content="{d}">'))
    return tags


def existing_labels(soup: BeautifulSoup) -> set:
    """Set of meta/link labels already present in the document."""
    present = set()
    for m in soup.find_all("meta"):
        key = m.get("property") or m.get("name")
        if key:
            present.add(key.lower())
    if soup.find("link", rel="canonical"):
        present.add("canonical")
    return present


def missing_tags(html_file: Path, base_url: str):
    """Return (list of html-strings to insert, error-or-None)."""
    try:
        content = html_file.read_text(encoding="utf-8")
    except Exception as e:
        return [], f"read failed: {e}"
    if not content.strip():
        return [], "empty file"

    soup = BeautifulSoup(content, "html.parser")
    if not soup.head:
        return [], "no <head>"

    stem = html_file.stem
    page_url = f"{base_url}{html_file.name}"
    image_url = f"images/{stem}.png"

    present = existing_labels(soup)
    return [html for label, html in desired_tags(soup, stem, page_url, image_url)
            if label not in present], None


def insert_tags(html_file: Path, tags: list) -> None:
    """Insert tag strings immediately before </head>, matching its indentation.

    Pure text edit — the rest of the document is byte-for-byte untouched.
    """
    content = html_file.read_text(encoding="utf-8")
    lower = content.lower()
    idx = lower.rfind("</head>")
    if idx == -1:
        raise ValueError("no </head> found")

    line_start = content.rfind("\n", 0, idx) + 1
    indent = content[line_start:idx]  # whitespace preceding </head>
    if indent.strip():
        indent = ""  # </head> not at line start; fall back to no indent

    block = "".join(f"{indent}{tag}\n" for tag in tags)
    new_content = content[:line_start] + block + content[line_start:]
    html_file.write_text(new_content, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Screenshots
# --------------------------------------------------------------------------- #

def start_server(directory: Path):
    handler = partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # silence per-request logging
        pass


def generate_screenshots(files: list, images_dir: Path, root: Path, dark: bool) -> list[Path]:
    try:
        from playwright.sync_api import sync_playwright, Error as PlaywrightError
    except ImportError:
        print(f"{C.RED}Playwright not installed. Skipping screenshots.{C.ENDC}")
        print(f"{C.YELLOW}Enable with: python3 -m pip install playwright && python3 -m playwright install chromium{C.ENDC}")
        return []

    images_dir.mkdir(exist_ok=True)
    server, port = start_server(root)
    generated = []
    print(f"\n{C.BLUE}Generating {len(files)} preview image(s)...{C.ENDC}")
    hide_css = ",".join(HIDE_SELECTORS) + "{display:none !important}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport=VIEWPORT,
                device_scale_factor=2,  # crisp 2400x1260 capture downscaled by viewers
                color_scheme="dark" if dark else "light",
            )
            page = context.new_page()
            for html_file in files:
                out = images_dir / f"{html_file.stem}.png"
                try:
                    page.goto(f"http://127.0.0.1:{port}/{html_file.name}", wait_until="load", timeout=30000)
                    page.add_style_tag(content=hide_css)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(400)  # let fonts/animations settle
                    page.screenshot(path=str(out), type="png", clip={"x": 0, "y": 0, **VIEWPORT})
                    generated.append(out)
                    print(f"  {C.GREEN}Generated:{C.ENDC} images/{out.name}")
                except PlaywrightError as e:
                    print(f"  {C.RED}Failed:{C.ENDC} {html_file.name}: {e}")
            browser.close()
    finally:
        server.shutdown()
    return generated


# --------------------------------------------------------------------------- #
# Image optimization
# --------------------------------------------------------------------------- #

def imageoptim_installed() -> bool:
    """Return whether ImageOptim.app is installed on this macOS machine."""
    if sys.platform != "darwin":
        return False

    app_paths = [
        Path("/Applications/ImageOptim.app"),
        Path.home() / "Applications" / "ImageOptim.app",
    ]
    if any(path.exists() for path in app_paths):
        return True

    try:
        result = subprocess.run(
            ["mdfind", 'kMDItemCFBundleIdentifier == "net.pornel.ImageOptim"'],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return bool(result.stdout.strip())


def imageoptim_queue_count() -> int | None:
    """Read ImageOptim's active queue length via its AppleScript dictionary."""
    try:
        result = subprocess.run(
            ["osascript", "-e", f'tell application id "{IMAGEOPTIM_BUNDLE_ID}" to do queuecount command'],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def optimize_images(images: list[Path], timeout: int) -> None:
    """Send generated images to ImageOptim.app and wait for lossless minification."""
    existing_images = [image for image in images if image.exists()]
    if not existing_images:
        return

    if not imageoptim_installed():
        print(f"\n{C.YELLOW}ImageOptim.app not found. Skipping image minification.{C.ENDC}")
        return

    before_sizes = {image: image.stat().st_size for image in existing_images}
    print(f"\n{C.BLUE}Optimizing {len(existing_images)} preview image(s) with ImageOptim.app...{C.ENDC}")

    try:
        subprocess.run(
            ["open", "-b", IMAGEOPTIM_BUNDLE_ID, *[str(image) for image in existing_images]],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"  {C.YELLOW}ImageOptim launch failed. Skipping minification: {e}{C.ENDC}")
        return

    start = time.monotonic()
    deadline = start + timeout
    saw_work = False
    zero_since = None

    while time.monotonic() < deadline:
        count = imageoptim_queue_count()
        if count is None:
            print(f"  {C.YELLOW}Could not read ImageOptim queue. It was launched; verify completion in the app.{C.ENDC}")
            return

        if count > 0:
            saw_work = True
            zero_since = None
        elif saw_work:
            if zero_since is None:
                zero_since = time.monotonic()
            elif time.monotonic() - zero_since >= IMAGEOPTIM_SETTLE_SECONDS:
                break
        elif time.monotonic() - start >= IMAGEOPTIM_SETTLE_SECONDS:
            break

        time.sleep(1)
    else:
        print(f"  {C.YELLOW}ImageOptim still appears busy after {timeout}s; continuing without waiting longer.{C.ENDC}")
        return

    for image in existing_images:
        before = before_sizes[image]
        after = image.stat().st_size
        saved = before - after
        if saved > 0:
            pct = (saved / before) * 100
            print(f"  {C.GREEN}Optimized:{C.ENDC} images/{image.name} (-{saved:,} bytes, {pct:.1f}%)")
        else:
            print(f"  {C.GREEN}Optimized:{C.ENDC} images/{image.name} (already optimal)")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="Specific .html files (default: all in --dir).")
    ap.add_argument("--dir", default=".", help="Directory to scan (default: current).")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for canonical/og:url.")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default: dry run).")
    ap.add_argument("--force", action="store_true", help="Regenerate images that already exist.")
    ap.add_argument("--no-images", action="store_true", help="Skip screenshot generation.")
    ap.add_argument("--no-imageoptim", action="store_true", help="Skip ImageOptim.app minification after screenshots.")
    ap.add_argument("--no-og", action="store_true", help="Skip OG/meta tag insertion.")
    ap.add_argument("--dark", action="store_true", help="Render previews in dark color scheme.")
    ap.add_argument("--imageoptim-timeout", type=int, default=300, help="Seconds to wait for ImageOptim.app (default: 300).")
    args = ap.parse_args()

    root = Path(args.dir).resolve()
    if not root.is_dir():
        sys.exit(f"{C.RED}Directory not found: {root}{C.ENDC}")

    if args.files:
        files = [Path(f) if Path(f).is_absolute() else root / Path(f).name for f in args.files]
        files = [f for f in files if f.suffix == ".html" and f.exists()]
    else:
        files = sorted(root.glob("*.html"))
    if not files:
        sys.exit(f"{C.YELLOW}No HTML files found.{C.ENDC}")

    images_dir = root / "images"

    # --- Plan OG tag insertions ---
    tag_plan = {}  # file -> list[str]
    if not args.no_og:
        for f in files:
            tags, err = missing_tags(f, args.base_url)
            if err:
                print(f"  {C.YELLOW}Skip OG:{C.ENDC} {f.name} ({err})")
            elif tags:
                tag_plan[f] = tags

    # --- Plan screenshots ---
    shot_plan = []
    if not args.no_images:
        for f in files:
            if args.force or not (images_dir / f"{f.stem}.png").exists():
                shot_plan.append(f)

    # --- Report ---
    print(f"\n{C.BOLD}{C.HEADER}Plan ({len(files)} file(s) scanned){C.ENDC}")
    if tag_plan:
        print(f"\n{C.BOLD}OG/meta tags to add:{C.ENDC}")
        for f, tags in sorted(tag_plan.items()):
            print(f"  {C.BOLD}{f.name}{C.ENDC}")
            for t in tags:
                print(f"    {C.GREEN}+{C.ENDC} {t}")
    else:
        print(f"  {C.GREEN}No missing OG tags.{C.ENDC}")

    if shot_plan:
        print(f"\n{C.BOLD}Preview images to generate:{C.ENDC}")
        for f in shot_plan:
            print(f"    {C.GREEN}+{C.ENDC} images/{f.stem}.png")
    else:
        print(f"  {C.GREEN}No images to generate.{C.ENDC}")

    if not tag_plan and not shot_plan:
        return

    if not args.apply:
        print(f"\n{C.YELLOW}Dry run. Re-run with {C.BOLD}--apply{C.ENDC}{C.YELLOW} to make changes.{C.ENDC}")
        return

    # --- Apply ---
    if tag_plan:
        print(f"\n{C.BLUE}Inserting OG tags...{C.ENDC}")
        for f, tags in sorted(tag_plan.items()):
            try:
                insert_tags(f, tags)
                print(f"  {C.GREEN}Updated:{C.ENDC} {f.name} (+{len(tags)})")
            except Exception as e:
                print(f"  {C.RED}Failed:{C.ENDC} {f.name}: {e}")

    if shot_plan:
        generated_images = generate_screenshots(shot_plan, images_dir, root, args.dark)
        if not args.no_imageoptim:
            optimize_images(generated_images, args.imageoptim_timeout)

    print(f"\n{C.GREEN}Done.{C.ENDC}")


if __name__ == "__main__":
    main()
