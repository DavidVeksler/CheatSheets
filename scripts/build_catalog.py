#!/usr/bin/env python3
"""Build catalog.json: the data layer behind the index.php Explorer redesign.

Scans every catalogued *.html cheatsheet in the repo root and emits a single
compact catalog.json with per-sheet metadata (title, description, keywords,
headings with deep-link ids, outbound links, shape heuristics, git dates,
review status) plus collection-level stats and a precomputed force-directed
map layout. Supersedes generate-metadata.py (one script owns extraction, per
the automation-ladder rule in ~/.claude/CLAUDE.md).

Usage:
    python3 scripts/build_catalog.py                # build catalog.json
    python3 scripts/build_catalog.py --check         # freshness gate only, no write
    python3 scripts/build_catalog.py --output x.json # write elsewhere (tests)

Exit codes: 0 on success. Non-zero (with a message on stderr) when:
  - a paths.json step references a file not in the catalog
  - --check finds catalog.json's recorded inputs_hash no longer matches the
    content hash of the catalogued sources
Warnings (unmapped category, missing hue, thin category-hue coverage, count
crossing the "190+" rounding boundary, palette examples with no heading
match, shape heuristics degrading, layout drift) print to stderr but do not
fail the build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit

# BeautifulSoup is imported lazily (see _bs4()) so that --check, which never
# parses HTML, runs on a bare interpreter without the dependency installed.
BeautifulSoup = None  # type: ignore[assignment]
FeatureNotFound = None  # type: ignore[assignment]


def _bs4():
    """Import bs4 on first use and publish it at module scope.

    Only the parsing paths need it; --check works off content hashes.
    """
    global BeautifulSoup, FeatureNotFound
    if BeautifulSoup is None:
        try:
            from bs4 import BeautifulSoup as _Soup, FeatureNotFound as _NotFound
        except ImportError:  # pragma: no cover - environment guard
            raise SystemExit(
                "Error: BeautifulSoup is not installed. "
                "Run: python3 -m pip install beautifulsoup4"
            )
        BeautifulSoup, FeatureNotFound = _Soup, _NotFound
    return BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://cheatsheets.davidveksler.com/"
SITE_HOST = "cheatsheets.davidveksler.com"

CATALOG_PATH = ROOT / "catalog.json"
CATEGORY_MAP_PATH = ROOT / "category-map.php"
PATHS_PATH = ROOT / "paths.json"
OVERRIDES_PATH = ROOT / "catalog-overrides.json"
REFRESH_STATUS_PATH = ROOT / "refresh-status.json"

# Mirrors index.php's $excludedItems (the non-.html entries there can never
# match the *.html glob below, so only the .html exclusion matters here).
EXCLUDED_HTML = {
    "etz-chaim-tree-of-life.html",
}

# Copied from index.php's $categoryStyles light-mode "color" values, for
# continuity with the existing card badges. A dark-mode partner hue is
# generated for each (see generate_dark_hue) rather than hand-picked, so the
# 3:1-against-#0e1013 contrast requirement holds by construction; the
# resulting pairs are printed by --print-hues for the implementer to paste
# into index.php's CSS comment block in Phase 1.
CATEGORY_LIGHT_HUES = {
    "AI & Safety": "#0891b2",
    "Software & DevOps": "#4338ca",
    "Security & Privacy": "#dc2626",
    "Risk & Preparedness": "#0f766e",
    "Bitcoin & Finance": "#d97706",
    "Crypto Custody & Compliance": "#a21caf",
    "Martial Arts & Strategy": "#9f1239",
    "Firearms & Military": "#3f6212",
    "Radio": "#1e40af",
    "Health & Fitness": "#065f46",
    "Economics & Politics": "#7c2d12",
    "Philosophy & Religion": "#6b21a8",
    "Engineering & Science": "#0c4a6e",
    "Home & Lifestyle": "#0f766e",
    "Life Admin & Consumer Defense": "#4b5563",
    "Other": "#374151",
}
CATEGORY_ORDER = list(CATEGORY_LIGHT_HUES.keys())

DARK_PAGE_BG = "#0e1013"
MIN_CONTRAST = 3.0

# The spec's own anchor pattern (\d{2,5}) misses the corpus's own showcase
# example: "Baofeng UV-5R" has a single digit ("UV-5R"), as do most handheld
# radio and firearm model numbers ("GD-77" is the outlier with 2). Widened to
# \d{1,5} plus an optional trailing letter suffix (the "R" in "UV-5R", the
# "HP" in "BF-F8HP") so the heuristic actually catches its own worked example.
MODEL_NUMBER_RE = re.compile(r"\b[A-Z]{1,4}-?\d{1,5}[A-Z]{0,3}\b")
# \b word boundaries matter here: a plain substring match on "log" also fires
# on "terminology", "methodology", "catalog", "ideology", "psychology", etc.,
# which swamped the shape with false positives during corpus tuning.
TIMELINE_RE = re.compile(r"\b(timeline|history|log)\b", re.IGNORECASE)

PALETTE_EXAMPLES = ("torque", "ukemi", "ufw")


# --------------------------------------------------------------------------- #
# Parser selection (mirrors generate-metadata.py: prefer lxml, fall back to
# the stdlib html.parser when lxml is not installed).
# --------------------------------------------------------------------------- #
def get_html_parser() -> str:
    soup_cls = _bs4()
    try:
        soup_cls("<html></html>", "lxml")
        return "lxml"
    except FeatureNotFound:
        return "html.parser"


# --------------------------------------------------------------------------- #
# category-map.php parsing (regex, single source of truth stays the PHP file)
# --------------------------------------------------------------------------- #
def parse_category_map(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    pairs = re.findall(r"'([^']+\.html)'\s*=>\s*'([^']+)'", text)
    return dict(pairs)


# --------------------------------------------------------------------------- #
# catalog-overrides.json
# --------------------------------------------------------------------------- #
def load_overrides(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"WARNING: could not parse {path.name}: {exc}", file=sys.stderr)
        return {}
    return data if isinstance(data, dict) else {}


# --------------------------------------------------------------------------- #
# refresh-status.json
# --------------------------------------------------------------------------- #
def load_reviewed(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    files = data.get("files", {}) if isinstance(data, dict) else {}
    out = {}
    for filename, entry in files.items():
        if isinstance(entry, dict) and entry.get("last_reviewed"):
            out[filename] = entry["last_reviewed"]
    return out


# --------------------------------------------------------------------------- #
# git dates
# --------------------------------------------------------------------------- #
def git_created_updated(filename: str) -> tuple[int, int]:
    """(created, updated) epoch seconds in a single git call per file.

    ``git log --follow`` (no --diff-filter) lists every commit touching the
    file across renames, newest first: the first line is 'updated' (last
    commit) and the last line is 'created' (first commit): equivalent to
    running the spec's two separate commands but half the subprocess cost
    (git log --follow's rename detection dominates build time otherwise).
    """
    out = subprocess.run(
        ["git", "log", "--follow", "--format=%ct", "--", filename],
        cwd=ROOT, capture_output=True, text=True,
    )
    lines = [ln.strip() for ln in out.stdout.splitlines() if ln.strip().isdigit()]
    if not lines:
        return 0, 0
    return int(lines[-1]), int(lines[0])


# --------------------------------------------------------------------------- #
# Per-sheet extraction
# --------------------------------------------------------------------------- #
def meta_content(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None) -> str | None:
    tag = soup.find("meta", attrs={"name": name}) if name else soup.find("meta", attrs={"property": prop})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None


def humanize(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ").title()


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def heading_id(tag) -> str | None:
    """A heading's own id, else the id of the nearest enclosing <section>."""
    own = tag.get("id")
    if own:
        return own
    for parent in tag.parents:
        if getattr(parent, "name", None) == "section" and parent.get("id"):
            return parent.get("id")
    return None


def extract_headings(soup: BeautifulSoup) -> tuple[list[dict], str]:
    """h2 first; descend to h3/h4/h5 (first with 3+); else the richest level."""
    levels = ["h2", "h3", "h4", "h5"]
    by_level = {lvl: soup.find_all(lvl) for lvl in levels}

    chosen_level = None
    for lvl in levels:
        if len(by_level[lvl]) >= 3:
            chosen_level = lvl
            break
    if chosen_level is None:
        # Nothing reached the 3+ threshold at any level: fall back to
        # whichever level has the most headings (h2 wins ties, since it is
        # first in `levels` and Python's max() keeps the first max it sees).
        chosen_level = max(levels, key=lambda lvl: len(by_level[lvl]))

    headings = []
    for tag in by_level[chosen_level]:
        text = normalize_ws(tag.get_text(separator=" "))
        if not text:
            continue
        headings.append({"text": text, "id": heading_id(tag)})
    return headings, chosen_level


def extract_outlinks(soup: BeautifulSoup, own_filename: str, known_files: set[str]) -> list[str]:
    seen: list[str] = []
    seen_set: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        if href.startswith("http://") or href.startswith("https://"):
            parts = urlsplit(href)
            if parts.netloc and SITE_HOST not in parts.netloc:
                continue
            candidate = parts.path.rsplit("/", 1)[-1]
        else:
            candidate = href.split("#", 1)[0].split("?", 1)[0]
            candidate = candidate.rsplit("/", 1)[-1]
        if not candidate.lower().endswith(".html"):
            continue
        if candidate == own_filename:
            continue
        if candidate not in known_files:
            continue
        if candidate not in seen_set:
            seen_set.add(candidate)
            seen.append(candidate)
    return seen


def compute_shapes(counts: dict, title: str, keywords: list[str], headings: list[dict]) -> list[str]:
    shapes = []

    if counts["tables"] >= 3 or counts["max_table_rows"] >= 12:
        shapes.append("comparison")

    if counts["ordered_lists"] >= 3 or counts["checkboxes"] >= 10:
        shapes.append("procedure")

    if counts["number_range_output"] >= 3 and counts["has_script"]:
        shapes.append("calculator")

    if counts["has_local_storage"] and counts["checkboxes"] >= 10:
        shapes.append("tracker")

    if counts["pre_code_kbd"] >= 10:
        shapes.append("commands")

    title_and_keywords = " ".join([title, *keywords])
    lowered = title_and_keywords.lower()
    if MODEL_NUMBER_RE.search(title_and_keywords) or "programming" in lowered or "error codes" in lowered:
        shapes.append("device")

    if counts["words"] >= 4000 and counts["tables"] < 2:
        shapes.append("essay")

    heading_text = " ".join(h["text"] for h in headings)
    if TIMELINE_RE.search(title_and_keywords) or TIMELINE_RE.search(heading_text):
        shapes.append("timeline")

    if counts["svg"] >= 3 or counts["canvas"] >= 1:
        shapes.append("visual")

    return shapes or ["reference"]


def analyze_counts(soup: BeautifulSoup, raw_content: str, parser_name: str) -> dict:
    tables = soup.find_all("table")
    max_table_rows = max((len(t.find_all("tr")) for t in tables), default=0)

    # Strip script/style text before counting words so JS source and CSS
    # never inflate the word count (a plain get_text() would include it).
    words_soup = _bs4()(raw_content, parser_name)
    for tag in words_soup(["script", "style"]):
        tag.decompose()
    words = len(words_soup.get_text(separator=" ").split())

    return {
        "tables": len(tables),
        "max_table_rows": max_table_rows,
        "ordered_lists": len(soup.find_all("ol")),
        "checkboxes": len(soup.find_all("input", attrs={"type": "checkbox"})),
        "number_range_output": (
            len(soup.find_all("input", attrs={"type": "number"}))
            + len(soup.find_all("input", attrs={"type": "range"}))
            + len(soup.find_all("output"))
        ),
        "has_script": bool(soup.find("script")),
        "has_local_storage": "localStorage" in raw_content,
        "pre_code_kbd": len(soup.find_all(["pre", "code", "kbd"])),
        "svg": len(soup.find_all("svg")),
        "canvas": len(soup.find_all("canvas")),
        "sections": len(soup.find_all("section")),
        "form_inputs": len(soup.find_all(["input", "select", "textarea"])),
        "words": words,
    }


def extract_sheet(filename: str, parser_name: str, category_map: dict, overrides: dict,
                   reviewed: dict[str, str], unmapped_warnings: list[str]) -> dict:
    path = ROOT / filename
    content = path.read_text(encoding="utf-8", errors="replace")
    soup = _bs4()(content, parser_name)

    default_title = humanize(filename)
    title = default_title
    if soup.title and soup.title.string:
        title = soup.title.string.strip() or default_title

    description = meta_content(soup, name="description") or meta_content(soup, prop="og:description") or ""

    keywords_raw = meta_content(soup, name="keywords")
    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()] if keywords_raw else []

    own_url = urljoin(BASE_URL, filename)
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    url = canonical_tag["href"].strip() if canonical_tag and canonical_tag.get("href") else own_url

    image = None
    og_image = meta_content(soup, prop="og:image")
    if og_image:
        image = urljoin(own_url, og_image)

    category = category_map.get(filename)
    if category is None:
        category = "Other"
        unmapped_warnings.append(filename)

    headings, _level = extract_headings(soup)

    counts = analyze_counts(soup, content, parser_name)

    override = overrides.get(filename, {}) if isinstance(overrides.get(filename), dict) else {}
    shapes = override.get("shape") or compute_shapes(counts, title, keywords, headings)

    interactive = counts["has_local_storage"] or (counts["form_inputs"] >= 3 and counts["has_script"])

    created, updated = git_created_updated(filename)

    sheet = {
        "file": filename,
        "url": url,
        "title": title,
        "description": description,
        "keywords": keywords,
        "image": image,
        "category": category,
        "headings": headings,
        "outlinks": [],  # filled in a second pass once every filename is known
        "shape": shapes,
        "interactive": interactive,
        "words": counts["words"],
        "tables": counts["tables"],
        "sections": counts["sections"],
        "created": created,
        "updated": updated,
        "reviewed": reviewed.get(filename),
        "x": 0.0,
        "y": 0.0,
        "_soup": soup,  # dropped before serialization; kept for the outlink pass
    }
    if "featured" in override:
        sheet["featured"] = bool(override["featured"])
    return sheet


# --------------------------------------------------------------------------- #
# Map layout: deterministic seeded Fruchterman-Reingold with category gravity
# --------------------------------------------------------------------------- #
def compute_layout(files: list[str], node_categories: list[str], edges: list[tuple[int, int]],
                    seed: int = 42, iterations: int = 200) -> list[tuple[float, float]]:
    """Deterministic for a given (files, node_categories, edges, seed): same
    inputs always produce the same positions (fixed seed, fixed iteration
    count, no wall-clock or hash-randomization dependence)."""
    n = len(files)
    if n == 0:
        return []
    rng = random.Random(seed)
    return _fr_layout(n, node_categories, edges, rng, iterations)


def _fr_layout(n: int, node_categories: list[str], edges: list[tuple[int, int]],
               rng: random.Random, iterations: int) -> list[tuple[float, float]]:
    cats = CATEGORY_ORDER
    angle_of = {cat: 2 * math.pi * i / len(cats) for i, cat in enumerate(cats)}
    cx, cy = 0.5, 0.5
    radius = 0.38

    centroid = []
    pos = []
    for i in range(n):
        cat = node_categories[i]
        angle = angle_of.get(cat, 0.0)
        centroid_x = cx + radius * math.cos(angle)
        centroid_y = cy + radius * math.sin(angle)
        centroid.append((centroid_x, centroid_y))
        jr = rng.uniform(0.0, 0.06)
        ja = rng.uniform(0.0, 2 * math.pi)
        pos.append([centroid_x + jr * math.cos(ja), centroid_y + jr * math.sin(ja)])

    area = 1.0
    k = math.sqrt(area / max(n, 1))
    temp = 0.1
    cooling = temp / max(iterations, 1)
    gravity_strength = 0.03

    for _ in range(iterations):
        disp = [[0.0, 0.0] for _ in range(n)]

        for i in range(n):
            xi, yi = pos[i]
            for j in range(i + 1, n):
                xj, yj = pos[j]
                dx, dy = xi - xj, yi - yj
                dist = math.hypot(dx, dy) or 1e-6
                force = (k * k) / dist
                fx, fy = dx / dist * force, dy / dist * force
                disp[i][0] += fx
                disp[i][1] += fy
                disp[j][0] -= fx
                disp[j][1] -= fy

        for (a, b) in edges:
            xa, ya = pos[a]
            xb, yb = pos[b]
            dx, dy = xa - xb, ya - yb
            dist = math.hypot(dx, dy) or 1e-6
            force = (dist * dist) / k
            fx, fy = dx / dist * force, dy / dist * force
            disp[a][0] -= fx
            disp[a][1] -= fy
            disp[b][0] += fx
            disp[b][1] += fy

        for i in range(n):
            gx, gy = centroid[i]
            disp[i][0] += (gx - pos[i][0]) * gravity_strength
            disp[i][1] += (gy - pos[i][1]) * gravity_strength

        for i in range(n):
            dx, dy = disp[i]
            dlen = math.hypot(dx, dy) or 1e-6
            capped = min(dlen, temp)
            pos[i][0] += dx / dlen * capped
            pos[i][1] += dy / dlen * capped

        temp = max(temp - cooling, 0.001)

    xs = [p[0] for p in pos]
    ys = [p[1] for p in pos]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    rangex = (maxx - minx) or 1.0
    rangey = (maxy - miny) or 1.0
    return [((x - minx) / rangex, (y - miny) / rangey) for x, y in pos]


# --------------------------------------------------------------------------- #
# Dark-hue generation (contrast >= 3:1 against #0e1013)
# --------------------------------------------------------------------------- #
def _hex_to_rgb(hexcode: str) -> tuple[int, int, int]:
    hexcode = hexcode.lstrip("#")
    return tuple(int(hexcode[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in rgb)


def _rgb_to_hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (c / 255 for c in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    h *= 60
    return h, s, l


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[float, float, float]:
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return ((r + m) * 255, (g + m) * 255, (b + m) * 255)


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    def chan(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_ratio(rgb_a: tuple[int, int, int], rgb_b: tuple[int, int, int]) -> float:
    la, lb = _relative_luminance(rgb_a), _relative_luminance(rgb_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def generate_dark_hue(light_hex: str, bg_hex: str = DARK_PAGE_BG, min_contrast: float = MIN_CONTRAST) -> str:
    """Lighten `light_hex` (same hue) until it hits `min_contrast` against `bg_hex`.

    Keeps the category's hue identity across themes while guaranteeing the
    3:1 non-text contrast the spec requires for map nodes and badge borders.
    """
    h, s, l = _rgb_to_hsl(_hex_to_rgb(light_hex))
    bg_rgb = _hex_to_rgb(bg_hex)
    for step in range(0, 101):
        candidate_l = min(l + step * 0.01, 0.92)
        rgb = _hsl_to_rgb(h, s, candidate_l)
        if _contrast_ratio(rgb, bg_rgb) >= min_contrast:
            return _rgb_to_hex(rgb)
    return _rgb_to_hex(_hsl_to_rgb(h, s, 0.92))


# --------------------------------------------------------------------------- #
# paths.json validation
# --------------------------------------------------------------------------- #
def validate_paths(paths_data: dict, known_files: set[str]) -> list[str]:
    """Return a list of 'path_id: file' errors; empty means every step file exists."""
    errors = []
    for path in paths_data.get("paths", []):
        pid = path.get("id", "<unknown>")
        for step in path.get("steps", []):
            f = step.get("file")
            if f not in known_files:
                errors.append(f"{pid}: {f}")
    return errors


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def discover_files(overrides: dict) -> list[str]:
    hidden = {f for f, o in overrides.items() if isinstance(o, dict) and o.get("hide")}
    files = sorted(
        f.name for f in ROOT.glob("*.html")
        if f.name not in EXCLUDED_HTML and f.name not in hidden
    )
    return files


# --------------------------------------------------------------------------- #
# Inputs hash: a content fingerprint of everything the catalog is derived from.
#
# mtimes cannot answer "is catalog.json stale?" — `git pull --rebase`, a fresh
# clone, and rsync all rewrite mtimes on files whose bytes never changed, which
# made the old mtime comparison fire on unchanged trees. Hashing the content
# answers the real question and costs about 30 ms over the whole corpus.
# --------------------------------------------------------------------------- #
def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_inputs_hash(overrides: dict | None = None) -> str:
    """sha256 over the sorted (path, content-sha256) pairs of every input."""
    if overrides is None:
        overrides = load_overrides(OVERRIDES_PATH)

    entries: list[tuple[str, str]] = []
    for filename in discover_files(overrides):
        path = ROOT / filename
        if path.exists():
            entries.append((filename, _file_sha256(path)))
    for tracked in (CATEGORY_MAP_PATH, PATHS_PATH, OVERRIDES_PATH, REFRESH_STATUS_PATH):
        if tracked.exists():
            entries.append((tracked.name, _file_sha256(tracked)))

    rollup = hashlib.sha256()
    for name, digest in sorted(entries):
        rollup.update(name.encode("utf-8"))
        rollup.update(b"\0")
        rollup.update(digest.encode("ascii"))
        rollup.update(b"\n")
    return rollup.hexdigest()


def build(warn_only: bool = False) -> dict:
    parser_name = get_html_parser()
    category_map = parse_category_map(CATEGORY_MAP_PATH)
    overrides = load_overrides(OVERRIDES_PATH)
    reviewed = load_reviewed(REFRESH_STATUS_PATH)

    files = discover_files(overrides)
    filenames_set = set(files)

    unmapped_warnings: list[str] = []
    sheets: list[dict] = []
    for filename in files:
        sheet = extract_sheet(filename, parser_name, category_map, overrides, reviewed, unmapped_warnings)
        sheets.append(sheet)

    # Second pass: outlinks need the full filename set.
    for sheet in sheets:
        soup = sheet.pop("_soup")
        sheet["outlinks"] = extract_outlinks(soup, sheet["file"], filenames_set)

    index_of = {s["file"]: i for i, s in enumerate(sheets)}
    edges: list[tuple[int, int]] = []
    for i, sheet in enumerate(sheets):
        for target in sheet["outlinks"]:
            edges.append((i, index_of[target]))

    node_categories = [s["category"] for s in sheets]
    positions = compute_layout(files, node_categories, edges)
    for sheet, (x, y) in zip(sheets, positions):
        sheet["x"] = round(x, 5)
        sheet["y"] = round(y, 5)

    # Category rollup, in the canonical badge order, counts only for present categories.
    from collections import Counter
    counts = Counter(s["category"] for s in sheets)
    categories = []
    unknown_hue_categories = []
    seen_cats = set()
    for cat in CATEGORY_ORDER:
        if counts.get(cat):
            light = CATEGORY_LIGHT_HUES[cat]
            categories.append({
                "name": cat,
                "count": counts[cat],
                "hue": {"light": light, "dark": generate_dark_hue(light)},
            })
            seen_cats.add(cat)
    for cat in counts:
        if cat not in seen_cats:
            unknown_hue_categories.append(cat)
            categories.append({"name": cat, "count": counts[cat], "hue": None})

    total_sections_indexed = sum(len(s["headings"]) for s in sheets)

    catalog = {
        "generated": _iso_now(),
        "inputs_hash": compute_inputs_hash(overrides),
        "count": len(sheets),
        "categories": categories,
        "edges": [[a, b] for a, b in edges],
        "stats": {"sections": total_sections_indexed, "edges": len(edges)},
        "sheets": sheets,
    }

    # --- warnings (never fail the build) ---
    for filename in unmapped_warnings:
        print(f"WARNING: {filename} has no entry in category-map.php; filed under Other", file=sys.stderr)
    for cat in unknown_hue_categories:
        print(f"WARNING: category '{cat}' has no hue defined in build_catalog.py's CATEGORY_LIGHT_HUES", file=sys.stderr)
    if len(sheets) >= 200:
        print(f"WARNING: catalog count is {len(sheets)}; the spec's '190+' title round-down is now wrong", file=sys.stderr)

    shape_counts = Counter(sh for s in sheets for sh in s["shape"])
    reference_only = sum(1 for s in sheets if s["shape"] == ["reference"])
    if len(sheets) and reference_only / len(sheets) > 0.10:
        print(f"WARNING: {reference_only}/{len(sheets)} sheets ({reference_only / len(sheets):.0%}) "
              f"fall to plain 'reference'; consider re-tuning the shape heuristics", file=sys.stderr)

    all_heading_text = " ".join(h["text"] for s in sheets for h in s["headings"]).lower()
    for example in PALETTE_EXAMPLES:
        if example.lower() not in all_heading_text:
            print(f"WARNING: palette placeholder example '{example}' matches no heading text in the catalog", file=sys.stderr)

    _check_layout_drift(catalog)

    catalog["_shape_counts"] = dict(shape_counts)  # informational only; stripped before write
    return catalog


def _iso_now() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_layout_drift(catalog: dict) -> None:
    if not CATALOG_PATH.exists():
        return
    try:
        old = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    old_by_file = {s["file"]: s for s in old.get("sheets", [])}
    old_edges = {(e[0], e[1]) for e in old.get("edges", [])}
    old_index_to_file = {i: s["file"] for i, s in enumerate(old.get("sheets", []))}
    old_edge_files = {(old_index_to_file.get(a), old_index_to_file.get(b)) for a, b in old_edges}

    new_by_file = {s["file"]: s for s in catalog["sheets"]}
    new_index_of = {s["file"]: i for i, s in enumerate(catalog["sheets"])}
    new_edge_files = {(catalog["sheets"][a]["file"], catalog["sheets"][b]["file"]) for a, b in catalog["edges"]}

    if old_edge_files != new_edge_files:
        return  # edges changed; drift is expected, nothing to warn about

    moves = []
    for filename, old_sheet in old_by_file.items():
        new_sheet = new_by_file.get(filename)
        if not new_sheet:
            continue
        dx = new_sheet["x"] - old_sheet.get("x", new_sheet["x"])
        dy = new_sheet["y"] - old_sheet.get("y", new_sheet["y"])
        moves.append(math.hypot(dx, dy))

    if not moves:
        return
    moves.sort()
    median = moves[len(moves) // 2]
    if median > 0.05:
        print(f"WARNING: layout drift: median node move {median:.3f} (>5% of canvas) "
              f"with unchanged edges; check the layout seed/cooling schedule", file=sys.stderr)


# --------------------------------------------------------------------------- #
# --check gate
# --------------------------------------------------------------------------- #
def run_check() -> int:
    if not CATALOG_PATH.exists():
        print("catalog.json is missing. Run: python3 scripts/build_catalog.py", file=sys.stderr)
        return 1

    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"catalog.json does not parse: {exc}", file=sys.stderr)
        return 1

    # Content fingerprint, not mtimes: a rebase or fresh clone rewrites mtimes
    # on identical bytes, which used to fail this gate for no reason.
    recorded = catalog.get("inputs_hash")
    actual = compute_inputs_hash()
    if not recorded:
        print("catalog.json has no inputs_hash (built by an older build_catalog.py).",
              file=sys.stderr)
        print("Run: python3 scripts/build_catalog.py", file=sys.stderr)
        return 1
    if recorded != actual:
        print("catalog.json is stale: the catalogued sources have changed since it was built.",
              file=sys.stderr)
        print(f"  recorded inputs_hash {recorded[:12]}, actual {actual[:12]}", file=sys.stderr)
        print("Run: python3 scripts/build_catalog.py", file=sys.stderr)
        return 1

    if PATHS_PATH.exists():
        try:
            paths_data = json.loads(PATHS_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"paths.json does not parse: {exc}", file=sys.stderr)
            return 1
        known_files = {s["file"] for s in catalog.get("sheets", [])}
        errors = validate_paths(paths_data, known_files)
        if errors:
            print("paths.json references files not in the catalog:", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
            return 1

    print("catalog.json is up to date and paths.json validates.")
    return 0


# --------------------------------------------------------------------------- #
# Write
# --------------------------------------------------------------------------- #
def write_catalog(catalog: dict, output: Path) -> None:
    catalog = dict(catalog)
    catalog.pop("_shape_counts", None)
    text = json.dumps(catalog, indent=None, separators=(",", ":"), ensure_ascii=False, sort_keys=False)
    output.write_text(text + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build catalog.json for the cheatsheets index.")
    parser.add_argument("--check", action="store_true",
                        help="inputs-hash freshness + paths.json gate only; no write, no bs4 needed")
    parser.add_argument("--output", default=str(CATALOG_PATH), help="output path (default catalog.json)")
    parser.add_argument("--print-hues", action="store_true", help="print the light/dark category hue table and exit")
    args = parser.parse_args()

    if args.print_hues:
        for cat, light in CATEGORY_LIGHT_HUES.items():
            print(f"{cat:35s} light={light}  dark={generate_dark_hue(light)}")
        return 0

    if args.check:
        return run_check()

    catalog = build()
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output

    known_files = {s["file"] for s in catalog["sheets"]}
    if PATHS_PATH.exists():
        try:
            paths_data = json.loads(PATHS_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"ERROR: paths.json does not parse: {exc}", file=sys.stderr)
            return 1
        errors = validate_paths(paths_data, known_files)
        if errors:
            print("ERROR: paths.json references files not in the catalog:", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
            return 1

    write_catalog(catalog, output)

    print(f"Wrote {catalog['count']} sheets, {catalog['stats']['sections']} sections, "
          f"{catalog['stats']['edges']} edges to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
