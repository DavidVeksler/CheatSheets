#!/usr/bin/env python3
"""Validate the repository-wide SEO metadata acceptance gate.

Two passes:

1. Static ``*.html`` sheets (title <= 65, description 150-200, canonical,
   valid JSON-LD).
2. The rendered front door: ``index.php`` and each ``?cat=`` landing page,
   rendered through the ``php`` CLI with a stubbed ``$_SERVER``. These carry a
   tighter title budget (<= 60) because the Explorer spec sets one, and any PHP
   warning or notice in the output is itself a failure. Skipped with a printed
   note when ``php`` is not on PATH, and with ``--skip-rendered``.
   ``--only-rendered`` runs pass 2 alone (used by deploy.py when no sheet
   changed but the front door still has to be gated).
"""

from html.parser import HTMLParser
from pathlib import Path
import glob
import html as html_module
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
RENDER_TITLE_MAX = 60
PHP_DIAGNOSTIC = re.compile(r"\b(Warning|Notice|Deprecated|Fatal error|Parse error)\b:")


class Head(HTMLParser):
    """Parse only document metadata inside ``head``.

    Scoping matters because inline SVG ``title`` elements otherwise pollute the
    page-title result.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inhead = self.done = self._intitle = False
        self.title = None
        self._title_parts = []
        self.meta = {}
        self.prop = {}
        self.canonical = None

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        attributes = dict(attrs)
        if tag == "head":
            self.inhead = True
        elif tag == "body":
            self.inhead = False
            self.done = True
        elif not self.inhead:
            return
        elif tag == "title" and self.title is None:
            self._intitle = True
            self._title_parts = []
        elif tag == "meta":
            if attributes.get("name"):
                self.meta.setdefault(
                    attributes["name"].lower(), attributes.get("content", "")
                )
            if attributes.get("property"):
                self.prop.setdefault(
                    attributes["property"].lower(), attributes.get("content", "")
                )
        elif tag == "link":
            rel = attributes.get("rel")
            rel = " ".join(rel) if isinstance(rel, list) else (rel or "")
            if rel.lower() == "canonical" and not self.canonical:
                self.canonical = attributes.get("href", "")

    def handle_endtag(self, tag):
        if tag == "title" and self._intitle:
            self._intitle = False
            self.title = " ".join("".join(self._title_parts).split())
        if tag == "head":
            self.inhead = False
            self.done = True

    def handle_data(self, data):
        if self._intitle:
            self._title_parts.append(data)


def render_index(query: str) -> tuple[str, str]:
    """Render index.php through the php CLI with a stubbed request.

    Returns (stdout, stderr). The query string arrives via the environment so
    that category names containing '&' survive intact.
    """
    code = (
        '$_SERVER["HTTP_HOST"]="cheatsheets.davidveksler.com";'
        '$_SERVER["SCRIPT_NAME"]="/index.php";'
        '$_SERVER["HTTPS"]="on";'
        'parse_str((string)getenv("SEO_QS"),$_GET);'
        'include "index.php";'
    )
    env = dict(os.environ, SEO_QS=query)
    result = subprocess.run(
        ["php", "-d", "display_errors=1", "-d", "error_reporting=E_ALL", "-r", code],
        cwd=ROOT, capture_output=True, text=True, env=env,
    )
    return result.stdout, result.stderr


def check_rendered(label: str, source: str, stderr: str, failures: list) -> None:
    parsed = Head()
    parsed.feed(source)
    title = html_module.unescape(parsed.title or "")
    description = html_module.unescape(parsed.meta.get("description", ""))

    if not title:
        failures.append(f"{label}: no title")
    elif len(title) > RENDER_TITLE_MAX:
        failures.append(f"{label}: title {len(title)} chars > {RENDER_TITLE_MAX}")
    if not description:
        failures.append(f"{label}: no meta description")
    elif not 150 <= len(description) <= 200:
        failures.append(f"{label}: description {len(description)} chars, want 150-200")
    if not parsed.canonical:
        failures.append(f"{label}: no canonical")

    blocks = re.findall(
        r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>",
        source, re.DOTALL | re.IGNORECASE,
    )
    if not blocks:
        failures.append(f"{label}: no JSON-LD")
    for index, block in enumerate(blocks):
        try:
            json.loads(block)
        except Exception as error:  # noqa: BLE001 - print the parser's exact error
            failures.append(f"{label}: ld+json block {index} invalid: {error}")

    for stream, name in ((source, "output"), (stderr, "stderr")):
        hit = PHP_DIAGNOSTIC.search(stream)
        if hit:
            line = stream[max(0, hit.start() - 40):hit.start() + 160].replace("\n", " ")
            failures.append(f"{label}: PHP diagnostic in {name}: {line.strip()}")


def check_front_door(failures: list) -> None:
    """Gate index.php and every ?cat= landing page it renders."""
    if not shutil.which("php"):
        print("note: php not on PATH, skipping the rendered index and category gate")
        return

    source, stderr = render_index("")
    if not source.strip():
        failures.append(f"index.php: rendered nothing (php stderr: {stderr.strip()[:200]})")
        return
    check_rendered("index.php", source, stderr, failures)

    catalog_path = ROOT / "catalog.json"
    if not catalog_path.is_file():
        failures.append("index.php: catalog.json missing, category pages cannot be checked")
        return
    try:
        categories = json.loads(catalog_path.read_text(encoding="utf-8")).get("categories", [])
    except Exception as error:  # noqa: BLE001
        failures.append(f"catalog.json: does not parse: {error}")
        return

    from urllib.parse import quote
    for category in categories:
        name = category.get("name")
        if not name:
            continue
        page, page_err = render_index("cat=" + quote(name, safe=""))
        check_rendered(f"index.php?cat={name}", page, page_err, failures)


def main() -> int:
    failures = []
    args = sys.argv[1:]
    skip_rendered = "--skip-rendered" in args
    only_rendered = "--only-rendered" in args
    named = [a for a in args if not a.startswith("--")]
    filenames = [] if only_rendered else (named or glob.glob("*.html"))
    for filename in sorted(filenames):
        # Templates are validated by their rendered output in pass 2, never as source.
        if not filename.lower().endswith(".html"):
            continue
        with open(filename, encoding="utf-8", errors="replace") as page:
            source = page.read()
        parsed = Head()
        parsed.feed(source)
        title = parsed.title or ""
        description = parsed.meta.get("description", "")

        if len(title) > 65:
            failures.append(f"{filename}: title {len(title)} chars > 65")
        if not description:
            failures.append(f"{filename}: no meta description")
        elif not 150 <= len(description) <= 200:
            failures.append(
                f"{filename}: description {len(description)} chars, want 150-200"
            )
        if not parsed.canonical:
            failures.append(f"{filename}: no canonical")
        if "application/ld+json" not in source:
            failures.append(f"{filename}: no JSON-LD")

        # Pages legitimately contain multiple blocks; validate each independently.
        blocks = re.findall(
            r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>",
            source,
            re.DOTALL | re.IGNORECASE,
        )
        for index, block in enumerate(blocks):
            try:
                json.loads(block)
            except Exception as error:  # noqa: BLE001 - print the parser's exact error
                failures.append(
                    f"{filename}: ld+json block {index} invalid: {error}"
                )

    if not skip_rendered:
        check_front_door(failures)

    print(f"{len(failures)} SEO acceptance failures")
    for failure in failures:
        print(f"  {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
