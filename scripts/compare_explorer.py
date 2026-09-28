#!/usr/bin/env python3
"""Content equivalence of the prerendered PHP pages: droplet (PHP per request) vs Workers.

    python3 scripts/compare_explorer.py --prod https://cheatsheets.davidveksler.com \\
        --candidate https://<alias>-cheatsheets-davidveksler-com.<acct>.workers.dev [--base origin/main]

cf_parity.py compares bodies byte for byte, which cannot pass for pages rendered at
request time on one side and at build time on the other. This script compares what
the pages say instead (spec §5):

  head       title, description, robots, canonical, every og:/twitter: meta
  JSON       JSON-LD (parsed), catalog-lite, daily-history, icons
  cards      every Explorer card in order: file, title, category, description,
             shape chips, dates, NEW badge, reviewed marker, hidden state
  rail       every facet link (facet, value, label, pressed, href), sort links
  links      every <a href> with its text, in order
  text       all visible text, line by line

Known, intended differences are normalized away before comparing, each listed in
KNOWN below; anything else is reported and fails the run (exit 1).

Pages: /, /index.php, every hub, /?view=paths, every /?view=paths&path=<id>, a set of
client-state URLs (the Worker adds noindex / sheet metadata), /popularity.php, and
/sitemap.php (URL set). Stdlib only.
"""
from __future__ import annotations

import argparse
import difflib
import gzip
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
GH = "https://github.com/DavidVeksler/CheatSheets/commits/main/"

KNOWN = [
    "history.php links point at GitHub (D-2): href 'history.php' -> " + GH,
    "relative time ('8 hours ago') is request time on the droplet, build time + JS on Workers",
    "'Last change' names the newest commit of the build (the branch), not of the droplet checkout",
    "catalog version (catalog.json 'generated') differs: the branch rebuilt the catalog",
    "sheets edited on the branch (--base..HEAD) have a newer 'updated' date",
    "popularity.php: 'Where readers come from' (referrer history) is dropped (D-2)",
    "Cloudflare zone script injections (challenge platform, beacon) exist only on the droplet side",
]
BLOCK = {"p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "section", "article", "header", "footer",
         "nav", "main", "ul", "ol", "table", "summary", "details", "dt", "dd", "br", "figcaption", "label", "small",
         "em", "b", "span", "a", "button", "title"}
AGO = re.compile(r"\b\d+ (?:second|minute|hour|day|week|month|year)s? ago\b|\bjust now\b")


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status, body, enc = r.status, r.read(), r.headers.get("Content-Encoding", "")
    except urllib.error.HTTPError as e:
        status, body, enc = e.code, e.read(), e.headers.get("Content-Encoding", "")
    if enc == "gzip":
        body = gzip.decompress(body)
    return status, body.decode("utf-8", "replace")


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.head, self.json, self.links, self.rail, self.sorts = {}, {}, [], [], []
        self.cards, self.lines = [], [""]
        self.stack = []  # open tags with attrs
        self.skip = 0  # inside script/style
        self.script_id = None
        self.script_buf = []
        self.card = None
        self.cur_a = None
        self.title_buf = None

    # -- helpers
    def _in(self, tag, cls=None):
        return any(t == tag and (cls is None or cls in (a.get("class") or "").split()) for t, a in self.stack)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag in ("script", "style"):
            self.skip += 1
            if tag == "script" and a.get("type") in ("application/ld+json", "application/json"):
                self.script_id = a.get("id") or "ld+json"
                self.script_buf = []
            else:
                self.script_id = None
            return
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key and (key in ("description", "robots", "keywords") or key.startswith(("og:", "twitter:"))):
                self.head[key] = a.get("content", "")
        elif tag == "link" and a.get("rel") in ("canonical", "sitemap", "alternate", "icon"):
            self.head["link:" + a["rel"] + ":" + a.get("type", "")] = a.get("href", "")
        elif tag == "title":
            self.title_buf = []
        if tag == "article" and "c" in (a.get("class") or "").split():
            cls = a["class"].split()
            self.card = {"cls": [c for c in cls if c != "off"], "off": "off" in cls, "file": "", "title": "",
                         "cat": "", "reviewed": "", "desc": "", "chips": "", "dates": "", "new": False}
        if self.card is not None:
            if tag == "span" and "n" in (a.get("class") or "").split():
                self.card["new"] = True
            if tag == "b":
                self.card["reviewed"] = a.get("title", "")
        if tag == "a":
            self.cur_a = {"href": a.get("href", ""), "text": ""}
            if a.get("data-facet"):
                self.rail.append((a["data-facet"], a.get("data-val", ""), a.get("aria-pressed", ""), a.get("href", "")))
            if a.get("data-sort"):
                self.sorts.append((a["data-sort"], a.get("aria-current", ""), a.get("href", "")))
            if self.card is not None and self._in("h3"):
                self.card["file"] = a.get("href", "")
        if tag not in ("br", "img", "input", "meta", "link", "hr", "source", "path", "circle", "rect", "polyline"):
            self.stack.append((tag, a))
        if tag in BLOCK:
            self.lines.append("")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
            if self.script_id:
                raw = "".join(self.script_buf).strip()
                try:
                    self.json[self.script_id] = json.loads(raw)
                except ValueError:
                    self.json[self.script_id] = raw
                self.script_id = None
            return
        if tag == "title" and self.title_buf is not None:
            self.head["title"] = "".join(self.title_buf).strip()
            self.title_buf = None
        if tag == "a" and self.cur_a is not None:
            self.links.append((self.cur_a["href"], " ".join(self.cur_a["text"].split())))
            self.cur_a = None
        if tag == "article" and self.card is not None:
            self.cards.append(self.card)
            self.card = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if tag in BLOCK:
            self.lines.append("")

    def handle_data(self, data):
        if self.skip:
            if self.script_id:
                self.script_buf.append(data)
            return
        if self.title_buf is not None:
            self.title_buf.append(data)
        if self.cur_a is not None:
            self.cur_a["text"] += data
        if self.card is not None:
            top = self.stack[-1][0] if self.stack else ""
            t = " ".join(data.split())
            if top == "b":
                self.card["cat"] += t
            elif top == "a" and self._in("h3"):
                self.card["title"] += t
            elif top == "p":
                self.card["desc"] += t
            elif top == "em":
                self.card["chips"] += t
            elif top == "small":
                self.card["dates"] += data
        self.lines[-1] += data

    def text(self):
        return [ln for ln in (" ".join(x.split()) for x in self.lines) if ln]


def parse(html: str) -> Doc:
    d = Doc()
    d.feed(html)
    d.close()
    return d


def normalize(d: Doc, side: str, changed: set[str], changed_dates: set[str] = frozenset()) -> dict:
    """Structured view of a page with the KNOWN differences normalized away."""
    def fix_href(h):
        return GH if h in ("history.php",) or h.startswith("history.php?") else h

    text = [AGO.sub("<ago>", ln) for ln in d.text()]
    # 'Last change: <subject> <ago>' is the build's newest commit (the subject is its own line).
    for i, ln in enumerate(text):
        if ln.startswith("Last change:"):
            text[i] = "Last change: <commit>"
            if i + 1 < len(text) and ln == "Last change:":
                text[i + 1] = "<commit>"
    # Date lines of cards whose sheet was edited on the branch (both sides' strings).
    text = ["<changed dates>" if " ".join(ln.split()) in changed_dates else ln for ln in text]
    text = [ln for ln in text if not re.fullmatch(r"<ago>", ln)]
    links = [(fix_href(h), AGO.sub("<ago>", t)) for h, t in d.links]
    # The "Last change" link text is the newest commit subject.
    links = [(h, "<commit>") if h == GH and t and t not in ("Change history", "change history", "change-history page",
                                                             "Change History", "Public change history") else (h, t)
             for h, t in links]
    cards = []
    for c in d.cards:
        c = dict(c)
        if c["file"] in changed:
            c["dates"] = re.sub(r" · upd .*$", " · upd <changed>", c["dates"].strip())
        c["dates"] = " ".join(c["dates"].split())
        cards.append(c)
    js = dict(d.json)
    lite = js.get("catalog-lite")
    if isinstance(lite, dict) and changed:
        lite = dict(lite)
        lite["up"] = [None if f in changed else u for f, u in zip(lite.get("f", []), lite.get("up", []))]
        js["catalog-lite"] = lite
    return {"head": d.head, "json": js, "cards": cards, "rail": d.rail, "sorts": d.sorts,
            "links": links, "text": text}


# popularity.php renders "Where readers come from" only when the server-side referrer
# store exists (droplet). It runs from its section label to the panels grid.
REFERRER_SECTION = re.compile(
    r'<p class="lbl sectlbl">(?:(?!</p>).)*Where readers come from</p>.*?(?=<div class="panels">)', re.S)


def strip_referrers(html: str) -> str:
    return REFERRER_SECTION.sub("", html, count=1)


def diff_models(a: dict, b: dict) -> list[str]:
    out = []
    for key in ("head", "json", "cards", "rail", "sorts", "links", "text"):
        if a[key] == b[key]:
            continue
        if key in ("head", "json"):
            for k in sorted(set(a[key]) | set(b[key])):
                if a[key].get(k) != b[key].get(k):
                    out.append(f"{key}[{k}]: {str(a[key].get(k))[:160]!r} -> {str(b[key].get(k))[:160]!r}")
        else:
            sa = [json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x for x in a[key]]
            sb = [json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x for x in b[key]]
            lines = list(difflib.unified_diff(sa, sb, lineterm="", n=0))[2:]
            out.append(f"{key}: {len(sa)} vs {len(sb)} items; diff:\n    " + "\n    ".join(l[:220] for l in lines[:30]))
    return out


def changed_files(base: str) -> set[str]:
    r = subprocess.run(["git", "diff", "--name-only", f"{base}..HEAD", "--", "*.html"], cwd=ROOT,
                       capture_output=True, text=True)
    return {p for p in r.stdout.split() if "/" not in p}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--prod", default="https://cheatsheets.davidveksler.com")
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--base", default="origin/main", help="commit the droplet serves (sheets changed since then may show a newer date)")
    a = ap.parse_args()
    prod, cand = a.prod.rstrip("/"), a.candidate.rstrip("/")
    changed = changed_files(a.base)

    hubs = json.loads((ROOT / "category-hubs.json").read_text(encoding="utf-8"))["hubs"]
    paths = [p["id"] for p in json.loads((ROOT / "paths.json").read_text(encoding="utf-8"))["paths"] if p.get("steps")]
    pages = ["/", "/index.php", "/?view=paths"] + [f"/{v['slug']}" for v in hubs.values()]
    pages += [f"/?view=paths&path={p}" for p in paths]
    # Client-state URLs: the Worker serves the prerendered grid (+ noindex, sheet head);
    # PHP rendered the filtered state. Compare head + JSON-LD-free parts only where the
    # server-side filtering changed nothing structural: head and rail pressed state are
    # client-side on Workers, so these are checked for head only.
    state_pages = ["/?q=torque", "/?shape=reference", "/?sort=popular", "/?fresh=new30", "/?interactive=1",
                   "/?view=map", "/?sheet=judo.html", "/?sheet=how-its-built.html", "/radio?sort=title",
                   "/?cat=No%20Such%20Category"]

    failures, checked = 0, 0
    print(f"compare_explorer: {prod} vs {cand}; sheets changed since {a.base}: {sorted(changed) or 'none'}")
    for path in pages + state_pages + ["/popularity.php"]:
        (ps, ph), (cs, ch) = fetch(prod + path), fetch(cand + path)
        checked += 1
        if ps != 200 or cs != 200:
            print(f"FAIL {path}: status {ps} vs {cs}")
            failures += 1
            continue
        if path == "/popularity.php":
            ph = strip_referrers(ph)
        dp, dc = parse(ph), parse(ch)
        changed_dates = {" ".join(c["dates"].split()) for c in dp.cards + dc.cards if c["file"] in changed}
        mp, mc = normalize(dp, "prod", changed, changed_dates), normalize(dc, "cand", changed, changed_dates)
        if path in state_pages:
            # Head only: the Worker must reproduce index.php's title/robots/canonical/og.
            mp = {k: (v if k == "head" else []) for k, v in mp.items()}
            mc = {k: (v if k == "head" else []) for k, v in mc.items()}
        diffs = diff_models(mp, mc)
        if diffs:
            failures += 1
            print(f"FAIL {path}")
            for d in diffs:
                print("  " + d)
        else:
            n = len(mp["cards"])
            print(f"ok   {path}" + (f"  ({n} cards, {len(mp['links'])} links, {len(mp['text'])} text lines)" if n else ""))

    # Sitemap: same URL set (lastmod now comes from git, spec §2.1).
    locs = {}
    for side, base in (("prod", prod), ("cand", cand)):
        _, body = fetch(base + "/sitemap.php")
        locs[side] = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", body))
    checked += 1
    if set(locs["prod"]) != set(locs["cand"]):
        failures += 1
        print(f"FAIL /sitemap.php URL set: only prod {sorted(set(locs['prod']) - set(locs['cand']))[:5]}, "
              f"only candidate {sorted(set(locs['cand']) - set(locs['prod']))[:5]}")
    else:
        moved = sum(1 for u in locs["prod"] if locs["prod"][u] != locs["cand"][u])
        print(f"ok   /sitemap.php  ({len(locs['prod'])} URLs identical; {moved} lastmod values differ: git dates vs mtimes)")

    print("\nknown differences normalized:\n  - " + "\n  - ".join(KNOWN))
    print(f"\nRESULT: {'PASS' if failures == 0 else 'FAIL'}  {failures} of {checked} pages differ")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
