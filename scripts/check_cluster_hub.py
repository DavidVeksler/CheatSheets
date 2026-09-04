#!/usr/bin/env python3
"""Fail closed when the Crypto Custody hub drifts from its nine spokes."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent.parent
HUB = "crypto-custody-index.html"
CATEGORY = "Crypto Custody & Compliance"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("href"):
            self.hrefs.append(values["href"] or "")
        if values.get("id"):
            self.ids.add(values["id"] or "")

    handle_startendtag = handle_starttag


def parse_links(source: str) -> LinkParser:
    parser = LinkParser()
    parser.feed(source)
    parser.close()
    return parser


def category_members() -> set[str]:
    source = (ROOT / "category-map.php").read_text(encoding="utf-8")
    members = set(re.findall(
        rf"'([^']+\.html)'\s*=>\s*'{re.escape(CATEGORY)}'", source
    ))
    members.discard(HUB)
    return members


def llms_members(filename: str) -> set[str]:
    source = (ROOT / filename).read_text(encoding="utf-8")
    match = re.search(
        rf"^## {re.escape(CATEGORY)}\s*$\n(.*?)(?=^## |\Z)",
        source,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return set()
    members = {
        Path(urlparse(url).path).name
        for url in re.findall(r"\((https://cheatsheets\.davidveksler\.com/[^)]+\.html)\)", match.group(1))
    }
    members.discard(HUB)
    return members


def linked_members(source: str, pattern: str, failures: list[str], label: str) -> set[str]:
    block = re.search(pattern, source, re.IGNORECASE | re.DOTALL)
    if not block:
        failures.append(f"{label} not found")
        return set()
    return {
        Path(unquote(target)).name
        for target in re.findall(r'href="([^"#]+\.html)(?:#[^"]+)?"', block.group(0), re.IGNORECASE)
    }


def check_reciprocal_links(members: set[str], failures: list[str]) -> None:
    for member in sorted(members):
        source = (ROOT / member).read_text(encoding="utf-8", errors="replace")
        related = re.search(
            r'<(?:aside|section)[^>]*class="[^"]*related[^"]*".*?</(?:aside|section)>',
            source,
            re.IGNORECASE | re.DOTALL,
        )
        first = re.search(r'<a\s+href="([^"]+)"', related.group(0), re.IGNORECASE) if related else None
        if not first or first.group(1) != HUB:
            failures.append(f"{member} does not link to {HUB} first in its related block")

    generator = (ROOT / "scripts" / "generate_custody_batch.py").read_text(encoding="utf-8")
    shared = re.search(r"SHARED_RELATED\s*=\s*\[(.*?)\]", generator, re.DOTALL)
    if not shared or not re.search(
        rf'^\s*\("Custody cluster index",\s*"{re.escape(HUB)}"\)',
        shared.group(1),
        re.MULTILINE,
    ):
        failures.append("SHARED_RELATED does not list the custody hub first")


def item_list_members(source: str, failures: list[str]) -> set[str]:
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source,
        re.IGNORECASE | re.DOTALL,
    )
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if data.get("@type") == "CollectionPage" and data.get("mainEntity", {}).get("@type") == "ItemList":
            item_list = data["mainEntity"]
            items = item_list.get("itemListElement", [])
            if item_list.get("numberOfItems") != len(items):
                failures.append("ItemList numberOfItems does not match its entries")
            return {Path(urlparse(item.get("url", "")).path).name for item in items}
    failures.append("CollectionPage ItemList JSON-LD not found")
    return set()


def matrix_details(source: str, failures: list[str]) -> tuple[set[str], Counter[str]]:
    section = re.search(
        r'<section[^>]+id="responsibility-matrix".*?</section>',
        source,
        re.IGNORECASE | re.DOTALL,
    )
    if not section:
        failures.append("responsibility matrix section not found")
        return set(), Counter()
    markup = section.group(0)
    rows = re.findall(r'<tr\b[^>]*data-matrix-row\b[^>]*>', markup, re.IGNORECASE)
    bands = re.findall(r'<tr\b[^>]*data-matrix-band\b[^>]*>', markup, re.IGNORECASE)
    if len(rows) != 34:
        failures.append(f"matrix has {len(rows)} decision rows; expected 34")
    if len(bands) != 8:
        failures.append(f"matrix has {len(bands)} bands; expected 8")

    target_counts: Counter[str] = Counter()
    for target in re.findall(r'href="([^"#]+\.html)#[^"]+"', markup, re.IGNORECASE):
        target_counts[Path(unquote(target)).name] += 1

    always = 0
    for owners in re.findall(r'data-owners="([^"]+)"', markup, re.IGNORECASE):
        tokens = owners.upper().split()
        if len(tokens) != 5 or any(token not in {"YOU", "SHARED", "VENDOR", "NA"} for token in tokens):
            failures.append(f"invalid matrix ownership vector: {owners}")
        elif all(token in {"YOU", "SHARED"} for token in tokens):
            always += 1
    metric = re.search(r'id="metric-always"[^>]*>(\d+)<', source)
    if not metric or int(metric.group(1)) != always:
        failures.append(f"quick-reference always-owned count does not equal computed value {always}")
    caption = re.search(r'id="matrix-always-count"[^>]*>(\d+)<', source)
    if not caption or int(caption.group(1)) != always:
        failures.append(f"matrix caption count does not equal computed value {always}")
    return set(target_counts), target_counts


def check_table_count(source: str, table_id: str, marker: str, expected: int, failures: list[str]) -> None:
    table = re.search(
        rf'<table[^>]+id="{re.escape(table_id)}".*?</table>',
        source,
        re.IGNORECASE | re.DOTALL,
    )
    actual = len(re.findall(rf'<tr\b[^>]*{re.escape(marker)}\b', table.group(0), re.IGNORECASE)) if table else 0
    if actual != expected:
        failures.append(f"{table_id} has {actual} rows; expected {expected}")


def check_anchor_targets(source: str, failures: list[str]) -> None:
    links = parse_links(source)
    cache: dict[str, set[str]] = {}
    for href in links.hrefs:
        match = re.fullmatch(r"([^?#]+\.html)#([^#?]+)", href)
        if not match:
            continue
        filename, fragment = unquote(match.group(1)), unquote(match.group(2))
        target = ROOT / filename
        if not target.is_file():
            failures.append(f"missing target file for {href}")
            continue
        if filename not in cache:
            cache[filename] = parse_links(target.read_text(encoding="utf-8", errors="replace")).ids
        if fragment not in cache[filename]:
            failures.append(f"missing target anchor for {href}")


def main() -> int:
    failures: list[str] = []
    hub_path = ROOT / HUB
    if not hub_path.is_file():
        print(f"cluster hub check failed: {HUB} not found")
        return 1
    source = hub_path.read_text(encoding="utf-8", errors="replace")

    category = category_members()
    llms = llms_members("llms.txt")
    llms_full = llms_members("llms-full.txt")
    item_list = item_list_members(source, failures)
    matrix, target_counts = matrix_details(source, failures)
    roster = linked_members(
        source,
        r'<table[^>]+id="roster-table".*?</table>',
        failures,
        "nine-sheet roster",
    )
    related = linked_members(
        source,
        r'<aside[^>]*class="[^"]*related[^"]*".*?</aside>',
        failures,
        "hub related block",
    )
    sets = {
        "category-map.php": category,
        "llms.txt": llms,
        "llms-full.txt": llms_full,
        "ItemList": item_list,
        "matrix": matrix,
        "roster": roster,
        "hub related block": related,
    }
    baseline = category
    for label, members in sets.items():
        if members != baseline:
            failures.append(
                f"{label} roster differs: missing={sorted(baseline - members)}, extra={sorted(members - baseline)}"
            )
    for member in sorted(baseline):
        if target_counts[member] < 2:
            failures.append(f"matrix routes to {member} only {target_counts[member]} time(s); expected at least 2")

    check_reciprocal_links(baseline, failures)
    check_anchor_targets(source, failures)
    check_table_count(source, "model-chooser-table", "data-model-row", 5, failures)
    check_table_count(source, "symptom-table", "data-symptom-row", 16, failures)
    check_table_count(source, "lifecycle-table", "data-lifecycle-row", 8, failures)
    check_table_count(source, "refusals-table", "data-refusal-row", 6, failures)
    check_table_count(source, "roster-table", "data-roster-row", 9, failures)

    if failures:
        print(f"{len(failures)} crypto custody hub failure(s)")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("Crypto custody hub parity passed: 9 spokes, 34 decisions, all deep links resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
