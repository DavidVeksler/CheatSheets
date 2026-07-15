#!/usr/bin/env python3
"""Validate the repository-wide SEO metadata acceptance gate."""

from html.parser import HTMLParser
import glob
import json
import re
import sys


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


def main() -> int:
    failures = []
    filenames = sys.argv[1:] or glob.glob("*.html")
    for filename in sorted(filenames):
        with open(filename, encoding="utf-8", errors="replace") as page:
            source = page.read()
        parsed = Head()
        parsed.feed(source)
        title = parsed.title or ""
        description = parsed.meta.get("description", "")

        if len(title) > 60:
            failures.append(f"{filename}: title {len(title)} chars > 60")
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

    print(f"{len(failures)} SEO acceptance failures")
    for failure in failures:
        print(f"  {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
