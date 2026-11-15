#!/usr/bin/env python3
"""Render space-combat.html from its embedded JSON data model.

The page's <script type="application/json" id="space-combat-data"> block is the only source of truth.
This script renders the header legend, the hero chart (desktop and mobile SVG), the four side scales,
the twenty cards and every text section into the region between <!--gen:body--> and <!--/gen:body-->.
The page therefore works without JavaScript, and crawlers see the full text.

    python scripts/build_space_combat.py           # rewrite the generated region in place
    python scripts/build_space_combat.py --check   # exit 1 if the committed region is stale

Edit the JSON, then rerun. render_chart(data, variant) is also used by
scripts/render_og_space_combat.py for the 1200x630 and 1200x1500 PNG exports, and
scripts/check_space_combat.py recomputes every figure and checks the rendered structure.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "space-combat.html"
DATA_RE = re.compile(r'<script type="application/json" id="space-combat-data">(.*?)</script>', re.S)
REGION_RE = re.compile(r"<!--gen:body-->.*?<!--/gen:body-->", re.S)

COLS = ["C1", "C2", "C3", "C4", "C5"]
ROWS = ["R1", "R2", "R3", "R4", "R5"]
COL_W = [1, 1, 1, 1, 0.62]
ROW_W = [1, 1, 1, 1, 1.45]
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")

# Geometry per rendering. "wide" and "mobile" are embedded in the page; "og" and "tall" are the exports.
VARIANTS = {
    "wide": dict(W=1200, H=544, top=12, title_h=0, left=206, right=14, plot_h=462, r=15, gap=37, maxcols=6,
                 fnum=14, fa=13.5, fs=11.5, fnote=13, short=False, foot=False,
                 wrap_note=34, wrap_threat=40, wrap_mastery=60, wrap_fringe=16, sw=1.8),
    "og": dict(W=1200, H=630, top=4, title_h=86, left=206, right=14, plot_h=462, r=15, gap=37, maxcols=6,
               fnum=14, fa=13.5, fs=11.5, fnote=13, short=False, foot=True,
               wrap_note=34, wrap_threat=40, wrap_mastery=60, wrap_fringe=16, sw=1.8),
    "mobile": dict(W=344, H=692, top=26, title_h=0, left=54, right=5, plot_h=600, r=12, gap=26, maxcols=2,
                   fnum=13.5, fa=12.5, fs=11.2, fnote=12, short=True, foot=False,
                   wrap_note=17, wrap_threat=10, wrap_mastery=21, wrap_fringe=0, sw=1.5),
    "tall": dict(W=1200, H=1500, top=0, title_h=300, left=290, right=24, plot_h=1062, r=26, gap=62, maxcols=3,
                 fnum=24, fa=22, fs=18, fnote=21, short=False, foot=True, fy=20, fd=16, xshort=True, ffr=14,
                 wrap_note=27, wrap_threat=16, wrap_mastery=30, wrap_fringe=14, sw=3),
}


# ---------------------------------------------------------------- data and text helpers

def load_data(text: str | None = None) -> dict:
    text = PAGE.read_text(encoding="utf-8") if text is None else text
    m = DATA_RE.search(text)
    if not m:
        raise SystemExit("space-combat.html: data block not found")
    return json.loads(m.group(1))


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def tier_html(data: dict, t: str) -> str:
    title = esc(f"Tier {t}: {data['tiers'][t]}")
    href = {"A": "#arithmetic", "B": "#sources"}.get(t)
    if href:
        return f'<a class="tier" data-tier="{t}" href="{href}" title="{title}">{t}</a>'
    return f'<span class="tier" data-tier="{t}" title="{title}">{t}</span>'


def rich(data: dict, s: str) -> str:
    """Mini-markup to HTML: 10^n superscripts, _emphasis_, {A}/{B}/{C} provenance tags."""
    out = html.escape(s, quote=False)
    out = re.sub(r"10\^(-?\d+)", r"10<sup>\1</sup>", out)
    out = re.sub(r"(?<![\w/])_([^_]+)_(?!\w)", r"<em>\1</em>", out)
    out = re.sub(r" ?\{([ABC])\}", lambda m: tier_html(data, m.group(1)), out)
    return out


def plain(s: str) -> str:
    s = re.sub(r" ?\{[ABC]\}", "", s)
    s = re.sub(r"10\^(-?\d+)", lambda m: "10" + m.group(1).translate(SUP), s)
    return s.replace("_", "")


def wrap(s: str, n: int) -> list[str]:
    if n <= 0:
        return [s]
    lines, cur = [], ""
    words = []
    for w in s.split():
        while len(w) > n and "-" in w[:n]:
            k = w[:n].rindex("-") + 1
            words.append(w[:k])
            w = w[k:]
        words.append(w)
    for w in words:
        if cur and len(cur) + (0 if cur.endswith("-") else 1) + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + w if cur.endswith("-") else f"{cur} {w}") if cur else w
    if cur:
        lines.append(cur)
    return lines


def stop_label(data: dict, scale: str, key: str) -> str:
    for sc in data["scales"]:
        if sc["key"] == scale:
            for st in sc["stops"]:
                if st["key"] == key:
                    return st["label"]
    raise KeyError((scale, key))


def by_id(data: dict) -> dict[int, dict]:
    return {e["id"]: e for e in data["entries"]}


def aria(data: dict, e: dict) -> str:
    return (f"{e['id']}. {e['name']}: {e['coord']}. {stop_label(data, 'substrate', e['substrate'])}, "
            f"{stop_label(data, 'tempo', e['tempo']).lower()}, {stop_label(data, 'visibility', e['visibility']).lower()}, "
            f"aim: {stop_label(data, 'aim', e['aim']).lower()}.")


def f1(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def T(x, y, s, size, cls="", anchor="start", extra="") -> str:
    c = f' class="{cls}"' if cls else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{f1(x)}" y="{f1(y)}" font-size="{f1(size)}"{a}{c}{extra}>{esc(s)}</text>'


# ---------------------------------------------------------------- glyphs

def pts(points) -> str:
    return " ".join(f"{f1(x)},{f1(y)}" for x, y in points)


def glyph_body(sub: str, cx: float, cy: float, r: float, num: int | str, fnum: float, ghost: bool = False) -> str:
    cls = "g-ghost" if ghost else "g-fill"
    out, ny, ncls, fs = [], cy, "g-num", fnum
    if sub == "human":
        out.append(f'<polygon class="{cls}" points="{pts([(cx, cy - 1.2 * r), (cx + 1.15 * r, cy + 0.82 * r), (cx - 1.15 * r, cy + 0.82 * r)])}"/>')
        ny, fs = cy + 0.24 * r, fnum * 0.95
    elif sub == "ai":
        k = 1.22 * r
        out.append(f'<polygon class="{cls}" points="{pts([(cx, cy - k), (cx + k, cy), (cx, cy + k), (cx - k, cy)])}"/>')
    elif sub == "swarm":
        import math
        for i in range(6):
            a = math.radians(30 + 60 * i)
            out.append(f'<circle class="{cls}" cx="{f1(cx + 1.06 * r * math.cos(a))}" cy="{f1(cy + 1.06 * r * math.sin(a))}" r="{f1(0.25 * r)}"/>')
        out.append(f'<circle class="{cls}" cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(0.8 * r)}"/>')
        fs = fnum * 0.92
    else:  # civilization
        if ghost:
            out.append(f'<circle class="{cls}" cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}"/>')
        else:
            out.append(f'<circle class="g-ring" cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(0.86 * r)}" stroke-width="{f1(0.3 * r)}"/>')
            ncls += " on-ring"
            fs = fnum * 0.92
    out.append(f'<text class="{ncls}" x="{f1(cx)}" y="{f1(ny)}" font-size="{f1(fs)}">{num}</text>')
    return "".join(out)


def mini_svg(sub: str, num, size: int = 30) -> str:
    """Self-contained tile with one glyph, for scales, cards and the legend."""
    c = size / 2
    r = size * 0.36
    return (f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" aria-hidden="true" focusable="false">'
            f'<rect width="{size}" height="{size}" rx="{size * 0.18:.0f}" fill="#0b1424"/>'
            f'{glyph_body(sub, c, c + (0.06 * size if sub == "human" else 0), r, num, size * 0.4)}</svg>')


# ---------------------------------------------------------------- hero chart

def layout(n: int, cx: float, cy: float, gap: float, maxcols: int) -> list[tuple[float, float]]:
    cols = min(n, maxcols)
    rows = -(-n // cols)
    out = []
    for i in range(n):
        r_, c_ = divmod(i, cols)
        in_row = min(cols, n - r_ * cols)
        out.append((cx + (c_ - (in_row - 1) / 2) * gap, cy + (r_ - (rows - 1) / 2) * gap))
    return out


def render_chart(data: dict, variant: str) -> str:
    v = VARIANTS[variant]
    W, H, r, gap, fa, fs, fnote = v["W"], v["H"], v["r"], v["gap"], v["fa"], v["fs"], v["fnote"]
    short = v["short"]
    uid = variant
    entries = data["entries"]
    cols = {c["id"]: c for c in data["columns"]}
    rows = {rw["id"]: rw for rw in data["rows"]}

    left, pw = v["left"], W - v["left"] - v["right"]
    unit = pw / sum(COL_W)
    cl, cr = {}, {}
    x = left
    for cid, w in zip(COLS, COL_W):
        cl[cid], cr[cid] = x, x + w * unit
        x += w * unit
    cc = {k: (cl[k] + cr[k]) / 2 for k in COLS}
    py0 = v["top"] + v["title_h"]
    ph = v["plot_h"]
    py1 = py0 + ph
    runit = ph / sum(ROW_W)
    rb, rt = {}, {}
    y = py1
    for rid, w in zip(ROWS, ROW_W):
        rb[rid], rt[rid] = y, y - w * runit
        y -= w * runit
    rh = {k: rb[k] - rt[k] for k in ROWS}
    r5h = rh["R5"]
    pad, band_h, bgap = 0.07 * r5h, 0.21 * r5h, 0.05 * r5h
    bands = sorted([e for e in entries if e["x"] == "band"], key=lambda e: e["id"])
    band_y = {e["id"]: rb["R5"] - pad - (len(bands) - i) * band_h - (len(bands) - 1 - i) * bgap for i, e in enumerate(bands)}
    zone5 = (rt["R5"] + min(band_y.values())) / 2 if bands else (rt["R5"] + rb["R5"]) / 2

    def cy_of(rid):
        return zone5 if rid == "R5" else (rt[rid] + rb[rid]) / 2

    out = [f'<svg class="chart chart-{variant}" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="group" '
           f'aria-labelledby="sc-t-{uid} sc-d-{uid}" xmlns="http://www.w3.org/2000/svg">',
           f'<title id="sc-t-{uid}">{esc(data["meta"]["title"])}: twenty systems by physics commanded and layer targeted</title>',
           f'<desc id="sc-d-{uid}">{esc(data["chart"]["shows"])} {esc(" ".join(data["chart"]["annotation"]))}</desc>']

    m_start = (cr["C4"] - 0.10 * unit, rt["R1"] + 0.22 * rh["R1"])
    m_end = (cl["C1"] + 0.14 * unit, rt["R5"] + 0.12 * r5h)
    out.append(
        f'<defs><pattern id="hatch-{uid}" patternUnits="userSpaceOnUse" width="9" height="9" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="9" class="hatch"/></pattern>'
        f'<linearGradient id="mastery-{uid}" gradientUnits="userSpaceOnUse" x1="{f1(m_start[0])}" y1="{f1(m_start[1])}" x2="{f1(m_end[0])}" y2="{f1(m_end[1])}">'
        f'<stop offset="0" style="stop-color:var(--sc-mastery);stop-opacity:.03"/><stop offset="1" style="stop-color:var(--sc-mastery);stop-opacity:.2"/></linearGradient>'
        f'<marker id="head-{uid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" class="threat-head"/></marker></defs>')
    out.append(f'<rect class="bg" x="0" y="0" width="{W}" height="{H}"/>')

    # title strip (exports only)
    if v["title_h"]:
        out.append(title_strip(data, v))

    # rows, fringe
    for i, rid in enumerate(ROWS):
        out.append(f'<rect class="row-{i + 1}" x="{f1(cl["C1"])}" y="{f1(rt[rid])}" width="{f1(cr["C4"] - cl["C1"])}" height="{f1(rh[rid])}"/>')
    out.append(f'<g class="fringe-group"><rect class="fringe" x="{f1(cl["C5"])}" y="{f1(py0)}" width="{f1(cr["C5"] - cl["C5"])}" height="{f1(ph)}"/>'
               f'<rect x="{f1(cl["C5"])}" y="{f1(py0)}" width="{f1(cr["C5"] - cl["C5"])}" height="{f1(ph)}" fill="url(#hatch-{uid})"/></g>')
    # grid
    g = [f'<rect class="grid" x="{f1(cl["C1"])}" y="{f1(py0)}" width="{f1(pw)}" height="{f1(ph)}"/>']
    for cid in COLS[1:4]:
        g.append(f'<line class="grid" x1="{f1(cl[cid])}" y1="{f1(py0)}" x2="{f1(cl[cid])}" y2="{f1(py1)}"/>')
    for rid in ROWS[1:]:
        g.append(f'<line class="grid" x1="{f1(cl["C1"])}" y1="{f1(rb[rid])}" x2="{f1(cr["C5"])}" y2="{f1(rb[rid])}"/>')
    tk = 0.3 * r
    for cid in COLS[1:]:
        for rid in ROWS[1:]:
            xx, yy = cl[cid], rb[rid]
            g.append(f'<path class="tick" d="M{f1(xx - tk)},{f1(yy)}H{f1(xx + tk)}M{f1(xx)},{f1(yy - tk)}V{f1(yy + tk)}"/>')
    out.append("".join(g))
    out.append(f'<line class="edge" x1="{f1(cl["C5"])}" y1="{f1(py0 - 4)}" x2="{f1(cl["C5"])}" y2="{f1(py1 + 4)}"/>')

    # mastery diagonal (under everything else)
    msw = 2.2 * r
    out.append(f'<path class="mastery" stroke="url(#mastery-{uid})" stroke-width="{f1(msw)}" d="M{f1(m_start[0])},{f1(m_start[1])}L{f1(m_end[0])},{f1(m_end[1])}"/>')
    import math
    ang = math.atan2(m_end[1] - m_start[1], m_end[0] - m_start[0])
    hl, hw = 0.55 * msw, 0.55 * msw
    tip = (m_end[0] + math.cos(ang) * hl * 0.6, m_end[1] + math.sin(ang) * hl * 0.6)
    b1 = (tip[0] - math.cos(ang) * hl + math.sin(ang) * hw, tip[1] - math.sin(ang) * hl - math.cos(ang) * hw)
    b2 = (tip[0] - math.cos(ang) * hl - math.sin(ang) * hw, tip[1] - math.sin(ang) * hl + math.cos(ang) * hw)
    out.append(f'<polygon class="mastery-head" points="{pts([tip, b1, b2])}"/>')
    mh, mrest = data["chart"]["mastery"]
    mx = cr["C4"] - 0.06 * unit
    mlines = wrap(mrest, v["wrap_mastery"])
    my = rb["R1"] - 0.16 * rh["R1"] - (len(mlines)) * fs * 1.25
    out.append(T(mx, my, f"{mh.upper()} ↖", fs, "t-mastery t-mastery-b", "end"))
    for i, ln in enumerate(mlines):
        out.append(T(mx, my + (i + 1) * fs * 1.25, ln, fs, "t-mastery", "end"))

    # axis labels
    for rid in ROWS:
        row = rows[rid]
        c = (rt[rid] + rb[rid]) / 2
        xr = left - (5 if short else 12)
        if short:
            out.append(T(xr, c - 0.35 * fa, rid, fa, "t-code", "end"))
            out.append(T(xr, c + 0.95 * fa, row["short"], fs, "", "end"))
        else:
            fy, fd = v.get("fy", fa), v.get("fd", fs)
            out.append(T(xr, c - 0.8 * fy, rid, fd, "t-code", "end"))
            out.append(T(xr, c + 0.5 * fy, row["label"], fy, "", "end", ' font-weight="600"'))
            out.append(T(xr, c + 0.5 * fy + 1.35 * fd, row["defeat"], fd, "t-muted", "end", ' font-style="italic"'))
    ylab = "LAYER TARGETED ↑" if short else "LAYER TARGETED →"
    if short:
        out.append(T(4, v["top"] - 10, ylab, fs, "t-axis"))
    else:
        out.append(f'<text class="t-axis" font-size="{f1(fs)}" text-anchor="middle" transform="translate({f1(fs + 4)},{f1((py0 + py1) / 2)}) rotate(-90)">{esc(ylab)}</text>')
    y1 = py1 + fa + 8
    y2 = y1 + fs + 6
    max_sub = 1
    for cid in COLS:
        col = cols[cid]
        cls_extra = ' opacity=".75"' if cid == "C5" else ""
        if short:
            out.append(T(cc[cid], y1, cid, fa, "t-code", "middle", cls_extra))
            out.append(T(cc[cid], y2, col["short"], fs, "", "middle", cls_extra))
        else:
            name = col["short"] if v.get("xshort") else col["chart"]
            out.append(f'<text x="{f1(cc[cid])}" y="{f1(y1)}" font-size="{f1(fa)}" text-anchor="middle" font-weight="600"{cls_extra}>'
                       f'<tspan class="t-code">{cid}</tspan> {esc(name)}</text>')
            sub_lines = wrap(plain(col["sub"]), int((cr[cid] - cl[cid]) / (fs * 0.56)))
            max_sub = max(max_sub, len(sub_lines))
            for j, ln in enumerate(sub_lines):
                out.append(T(cc[cid], y2 + j * fs * 1.2, ln, fs, "t-muted", "middle", cls_extra))
    y3 = y2 + fs + (12 if short else 16) + (max_sub - 1) * fs * 1.2
    out.append(T(cl["C1"], y3, "PHYSICS COMMANDED →", fs, "t-axis"))
    if v["foot"]:
        out.append(T(W - v["right"], y3, data["meta"]["url"], fs, "t-muted", "end"))

    # fringe column
    edge = data["chart"]["edge"]
    out.append(f'<text class="t-faint" font-size="{f1(fs)}" text-anchor="end" transform="translate({f1(cl["C5"] + fs + 2)},{f1(py0 + 8)}) rotate(-90)">{esc(edge)}</text>')
    if v["wrap_fringe"]:
        items = data["fringe"]["items"]
        slot = ph / len(items)
        ff = v.get("ffr", fs)
        fx = cl["C5"] + 2 * fs + 6
        nchar = min(v["wrap_fringe"], int((cr["C5"] - fx - 2) / (ff * 0.5)))
        for i, it in enumerate(items):
            lines = wrap(it["chart"], nchar)
            ty = py0 + slot * (i + 0.5) - (len(lines) - 1) * ff * 0.62 + ff * 0.35
            for j, ln in enumerate(lines):
                out.append(T(fx, ty + j * ff * 1.24, ln, ff, "t-faint"))

    # empty-block annotation
    head, body = data["chart"]["annotation"]
    nlines = wrap(body, v["wrap_note"])
    lh = fnote * 1.32
    ax = cl["C2"] + 0.07 * unit
    ay = (rt["R4"] + rb["R4"]) / 2 - (len(nlines)) * lh / 2 + fnote * 0.35 + (0.06 * rh["R4"] if short else 0)
    out.append(T(ax, ay, head, fnote, "t-note t-note-b"))
    for i, ln in enumerate(nlines):
        out.append(T(ax, ay + (i + 1) * lh, ln, fnote, "t-note"))

    # glyph positions
    pos: dict[int, tuple[float, float]] = {}
    cells: dict[tuple[str, str], list[dict]] = {}
    for e in sorted(entries, key=lambda e: e["id"]):
        if e["x"] != "band":
            cells.setdefault((e["x"], e["y"]), []).append(e)
    for (cx_, ry_), es in cells.items():
        for e, p in zip(es, layout(len(es), cc[cx_], cy_of(ry_), gap, v["maxcols"])):
            pos[e["id"]] = p
    ghosts: dict[int, tuple[float, float]] = {}
    gcells: dict[tuple[str, str], list[dict]] = {}
    for e in sorted(entries, key=lambda e: e["id"]):
        if e.get("y2"):
            gcells.setdefault((e["x"], e["y2"]), []).append(e)
    for (cx_, ry_), es in gcells.items():
        # A ghost sits straight above its primary unless two ghosts would collide; then use the cell grid.
        xs = [pos[e["id"]][0] for e in es]
        aligned = all(abs(a - b) >= gap for i, a in enumerate(xs) for b in xs[i + 1:])
        grid = layout(len(es), cc[cx_], cy_of(ry_), gap, v["maxcols"])
        for e, p in zip(es, grid):
            ghosts[e["id"]] = (pos[e["id"]][0], cy_of(ry_)) if aligned else p

    # connectors to secondary rows
    for eid, (gx, gy) in ghosts.items():
        px, py = pos[eid]
        e = by_id(data)[eid]
        bow = (-1.2 if gx <= cc[e["x"]] else 1.2) * gap
        out.append(f'<path class="conn" stroke-width="{f1(v["sw"] * 0.8)}" d="M{f1(px)},{f1(py)}Q{f1((px + gx) / 2 + bow)},{f1((py + gy) / 2)} {f1(gx)},{f1(gy)}"/>')

    # threat arrows
    ends = []
    for e in entries:
        if not e.get("arrowTo"):
            continue
        sx, sy = pos[e["id"]]
        sy -= 1.3 * r
        ex = cc[e["x"]] + 0.22 * unit
        ey = rb[e["arrowTo"]] - pad + 2
        bow = (0.4 if short else 0.34) * unit
        d = sy - ey
        out.append(f'<path class="threat" stroke-width="{f1(v["sw"])}" marker-end="url(#head-{uid})" '
                   f'd="M{f1(sx)},{f1(sy)}C{f1(sx + bow)},{f1(sy - 0.42 * d)} {f1(ex + 0.55 * bow)},{f1(ey + 0.38 * d)} {f1(ex)},{f1(ey + 2)}"/>')
        ends.append(ex)
    if ends:
        tl = wrap(data["chart"]["threat"], v["wrap_threat"])
        tx = sum(ends) / len(ends)
        ty = rt["R4"] + 0.2 * rh["R4"] + fs * 0.4
        for i, ln in enumerate(tl):
            out.append(T(tx, ty + i * fs * 1.22, ln, fs, "t-threat", "middle"))

    # bands
    for e in bands:
        bx, bw = cl["C1"] + 0.04 * unit, (cr["C4"] - 0.04 * unit) - (cl["C1"] + 0.04 * unit)
        by = band_y[e["id"]]
        rr = min(r, band_h * 0.38)
        gx, gy = bx + rr * 1.3 + 4, by + band_h / 2
        lab = aria(data, e)
        out.append(f'<a class="glyph primary band aim-{e["aim"]}" href="#c{e["id"]}" data-id="{e["id"]}" data-aim="{e["aim"]}" aria-label="{esc(lab)}">'
                   f'<title>{esc(lab)}</title>'
                   f'<rect class="band-rect" x="{f1(bx)}" y="{f1(by)}" width="{f1(bw)}" height="{f1(band_h)}" rx="{f1(band_h / 2)}"/>'
                   f'{glyph_body(e["substrate"], gx, gy, rr, e["id"], v["fnum"])}'
                   + T(gx + rr * 1.5 + 6, gy + fs * 0.36, e["name"], fs * (1 if short else 1.08), "band-text")
                   + ("" if short else T(gx + rr * 1.5 + 6 + len(e["name"]) * fs * 1.08 * 0.56 + 10, gy + fs * 0.36, e["coord"] + " · spans every physics column", fs, "t-muted"))
                   + "</a>")

    # ghosts, then primaries
    for eid, (gx, gy) in ghosts.items():
        e = by_id(data)[eid]
        lab = f"{eid}. {e['name']}: secondary target, {rows[e['y2']]['label'].lower()}."
        out.append(f'<a class="glyph ghost aim-{e["aim"]}" href="#c{eid}" data-id="{eid}" data-aim="{e["aim"]}" aria-label="{esc(lab)}">'
                   f'<title>{esc(lab)}</title>{glyph_body(e["substrate"], gx, gy, r, eid, v["fnum"], ghost=True)}</a>')
    for e in sorted(entries, key=lambda e: e["id"]):
        if e["id"] not in pos:
            continue
        gx, gy = pos[e["id"]]
        lab = aria(data, e)
        out.append(f'<a class="glyph primary aim-{e["aim"]}" href="#c{e["id"]}" data-id="{e["id"]}" data-aim="{e["aim"]}" aria-label="{esc(lab)}">'
                   f'<title>{esc(lab)}</title>{glyph_body(e["substrate"], gx, gy, r, e["id"], v["fnum"])}</a>')
    out.append("</svg>")
    return "\n".join(out)


def title_strip(data: dict, v: dict) -> str:
    W, tall = v["W"], v["title_h"] >= 200
    out = []
    if tall:
        out.append(T(40, 82, data["meta"]["title"], 58, "t-title"))
        out.append(T(40, 128, data["meta"]["subtitle"], 26, "t-sub"))
        for i, ln in enumerate(wrap(data["meta"]["thesis"], 92)):
            out.append(T(40, 174 + i * 30, ln, 21))
        rows_y, fsz, rl = [242, 278], 19, 11
        x_start = 40
    else:
        out.append(T(18, 40, data["meta"]["title"], 28, "t-title"))
        out.append(T(18, 66, data["meta"]["subtitle"], 15, "t-sub"))
        rows_y, fsz, rl = [30, 60], 12.5, 8
        x_start = None
    sub_items = [(st["label"], st["key"]) for st in data["scales"][0]["stops"]]
    aim_items = [(st["label"], st["key"]) for st in data["scales"][3]["stops"]]
    for row_i, items in enumerate([sub_items, aim_items]):
        widths = [2 * rl + 8 + len(lbl) * fsz * 0.52 + 16 for lbl, _ in items]
        x = x_start if x_start is not None else W - 16 - sum(widths) + 16
        yy = rows_y[row_i]
        prefix = "SHAPE = SUBSTRATE" if row_i == 0 else "COLOR = AIM"
        if tall:
            out.append(T(x, yy + fsz * 0.35, prefix, fsz * 0.8, "t-axis"))
            x += 240
        for (lbl, key), w in zip(items, widths):
            if row_i == 0:
                out.append(f'<g class="aim-legend" style="--c:#a3b2c4;--t:#07111d">{glyph_body(key, x + rl, yy, rl, "", 1)}</g>')
            else:
                out.append(f'<g class="aim-{key}"><circle class="g-fill" cx="{f1(x + rl)}" cy="{f1(yy)}" r="{f1(rl)}"/></g>')
            out.append(T(x + 2 * rl + 8, yy + fsz * 0.36, lbl, fsz))
            x += w
    return "".join(out)


# ---------------------------------------------------------------- page sections

def section(sid: str, kicker: str, title: str, inner: str) -> str:
    return (f'<section class="section" id="{sid}" aria-labelledby="{sid}-h">\n<p class="kicker">{esc(kicker)}</p>\n'
            f'<h2 id="{sid}-h">{esc(title)}</h2>\n{inner}\n</section>')


LAW_ICONS = {
    "heat": '<circle cx="22" cy="22" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M22 4v6M22 34v6M4 22h6M34 22h6M9.3 9.3l4.2 4.2M30.5 30.5l4.2 4.2M9.3 34.7l4.2-4.2M30.5 13.5l4.2-4.2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "lag": '<circle cx="8" cy="22" r="4" fill="currentColor"/><circle cx="36" cy="22" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M13 22h18" stroke="currentColor" stroke-width="2" stroke-dasharray="3 3"/><path d="M22 8v6l4 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "rocket": '<path d="M5 39C18 39 26 33 32 5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M5 5v34h34" fill="none" stroke="currentColor" stroke-width="1.4" opacity=".6"/>',
    "radiator": '<rect x="18" y="16" width="8" height="12" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 10l14 8M4 22h14M4 34l14-8M40 10l-14 8M40 22H26M40 34l-14-8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "drive": '<path d="M14 6h16v14l-8 6-8-6z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M18 28l-4 12M22 28v14M26 28l4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "offense": '<path d="M30 6v32" stroke="currentColor" stroke-width="3" opacity=".5"/><path d="M4 22h34M30 15l8 7-8 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>',
    "bits": '<rect x="5" y="5" width="9" height="9" fill="currentColor"/><rect x="18" y="5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="2"/><rect x="31" y="5" width="9" height="9" fill="currentColor"/><rect x="5" y="18" width="9" height="9" fill="none" stroke="currentColor" stroke-width="2"/><rect x="18" y="18" width="9" height="9" fill="currentColor"/><rect x="31" y="18" width="9" height="9" fill="none" stroke="currentColor" stroke-width="2"/><rect x="5" y="31" width="9" height="9" fill="currentColor"/><rect x="18" y="31" width="9" height="9" fill="currentColor"/><rect x="31" y="31" width="9" height="9" fill="none" stroke="currentColor" stroke-width="2"/>',
}


def render_body(data: dict) -> str:
    R = lambda s: rich(data, s)  # noqa: E731
    E = by_id(data)
    meta = data["meta"]
    out = []

    # header with legend
    sub_li = "".join(f'<li>{mini_svg(st["key"], "", 24)}<span>{esc(st["label"])}</span></li>' for st in data["scales"][0]["stops"])
    aim_li = "".join(f'<li class="aim-{st["key"]}"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="var(--c)"/></svg><span>{esc(st["label"])}</span></li>' for st in data["scales"][3]["stops"])
    tiers = " · ".join(f'{tier_html(data, t)} {esc(desc)}' for t, desc in data["tiers"].items())
    out.append(f'''<header class="mast">
<div>
<p class="eyebrow">{esc(meta["eyebrow"])}</p>
<h1>{esc(meta["title"])}</h1>
<p class="subtitle">{esc(meta["subtitle"])}</p>
<p class="thesis">{R(meta["thesis"])}</p>
</div>
<aside class="legend" aria-labelledby="legend-h">
<h2 id="legend-h">How to read a glyph</h2>
<ul aria-label="Glyph shape: combatant substrate">{sub_li}</ul>
<ul aria-label="Glyph color: political aim">{aim_li}</ul>
<p>Shape is the combatant, color is the political aim; the side scales repeat both as labels. A dashed outline marks a secondary target row, a band spans every physics column, and a red dashed arrow means the threat reaches incentives.</p>
<p>Provenance: {tiers}.</p>
</aside>
</header>''')
    out.append('<nav class="toc" aria-label="On this sheet"><a href="#chart">Chart</a><a href="#thesis">Thesis</a><a href="#read">How to read</a>'
               '<a href="#laws">Laws</a><a href="#nobody-aboard">Nobody aboard</a><a href="#systems">20 systems</a><a href="#myths">Myths</a>'
               '<a href="#unconfirmed">Unconfirmed physics</a><a href="#winners">Who wins</a><a href="#arithmetic">Arithmetic</a><a href="#sources">Sources</a></nav>')
    out.append('<main id="main">')

    # hero figure
    chips = "".join(f'<button type="button" data-aim="{st["key"]}" aria-pressed="false" class="aim-{st["key"]}" style="--c:var(--{st["key"]})"><i></i>{esc(st["label"])}</button>'
                    for st in data["scales"][3]["stops"])
    scales = []
    for sc in data["scales"]:
        stops = []
        for st in sc["stops"]:
            minis = "".join(f'<a class="mini aim-{e["aim"]}" href="#c{e["id"]}" data-id="{e["id"]}" aria-label="{esc(str(e["id"]) + ". " + e["name"])}">{mini_svg(e["substrate"], e["id"])}</a>'
                            for e in data["entries"] if e[sc["key"]] == st["key"])
            stops.append(f'<li class="stop"><span class="stop-label">{esc(st["label"])}</span><span class="stop-chips">{minis}</span></li>')
        scales.append(f'<section class="scale" aria-labelledby="scale-{sc["key"]}"><h3 id="scale-{sc["key"]}">{esc(sc["label"])}</h3>'
                      f'<ol class="stops" style="--n:{len(sc["stops"])}">{"".join(stops)}</ol></section>')
    out.append(f'''<figure class="hero" id="chart" aria-labelledby="chart-h">
<div class="hero-bar"><h2 id="chart-h">Physics commanded × layer targeted</h2>
<div class="chips" id="aim-filter" role="group" aria-label="Filter by political aim" hidden><span>Aim</span><button type="button" data-aim="all" aria-pressed="true">All</button>{chips}</div></div>
{render_chart(data, "wide")}
{render_chart(data, "mobile")}
<div class="scales">{"".join(scales)}</div>
<figcaption class="caption"><p><strong>What the chart shows.</strong> {R(data["chart"]["shows"])} {esc(data["chart"]["annotation"][1])}</p></figcaption>
</figure>''')

    # thesis
    th = data["thesis"]
    inner = "".join(f"<p class=\"lead\">{R(p)}</p>" for p in th["paragraphs"])
    inner += f"<p>{R(th['lead'])}</p><ol>" + "".join(f"<li>{R(p)}</li>" for p in th["points"]) + "</ol>"
    out.append(section("thesis", "01 · Thesis", "Victory is a changed decision", inner))

    # how to read
    rd = data["read"]
    xrows = "".join(f'<tr><td class="code">{c["id"]}</td><td>{esc(c["label"])}</td><td>{R(c["density"])}</td><td>{tier_html(data, c["tier"]) if c["tier"] else ""}</td></tr>' for c in data["columns"])
    yrows = "".join(f'<tr><td class="code">{rw["id"]}</td><td>{esc(rw["label"])}</td><td>{esc(rw["defeat"])}</td></tr>' for rw in data["rows"])
    sc_li = "".join(f'<li><strong>{esc(sc["label"])}:</strong> {esc(", ".join(st["label"] if i == 0 else st["label"][0].lower() + st["label"][1:] for i, st in enumerate(sc["stops"])))}</li>' for sc in data["scales"])
    inner = (f'<p>{R(rd["intro"])}</p><div class="twocol"><div><h3>X axis: physics commanded</h3>'
             f'<div class="scroll-table"><table><thead><tr><th>Column</th><th>Regime</th><th>Energy density</th><th>Tier</th></tr></thead><tbody>{xrows}</tbody></table></div>'
             f'<p>{R(rd["speed"])}</p></div><div><h3>Y axis: layer targeted</h3>'
             f'<div class="scroll-table"><table><thead><tr><th>Row</th><th>Target</th><th>What defeat looks like</th></tr></thead><tbody>{yrows}</tbody></table></div>'
             f'<h3>Side scales</h3><ul>{sc_li}</ul></div></div>')
    out.append(section("read", "02 · Legend", "How to read the chart", inner))

    # laws
    laws = "".join(f'<li><svg viewBox="0 0 44 44" aria-hidden="true">{LAW_ICONS[l["icon"]]}</svg><b><span>{i + 1:02d}</span>{R(l["title"])}</b><p>{R(l["text"])}</p></li>'
                   for i, l in enumerate(data["laws"]))
    out.append(section("laws", "03 · Constraints", "Laws of the arena", f'<ol class="laws">{laws}</ol>'))

    # post-human
    ph = data["posthuman"]
    prow = "".join(f"<tr><td><strong>{esc(a)}</strong></td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in ph["rows"])
    inner = (f'<p>{R(ph["intro"])}</p><div class="scroll-table"><table><thead><tr><th>Constraint</th><th>Human crew</th><th>Post-human combatant</th></tr></thead>'
             f'<tbody>{prow}</tbody></table></div><p>{R(ph["outro"])}</p>')
    out.append(section("nobody-aboard", "04 · Substrate", "What changes when nobody is aboard", inner))

    # cards
    inner = ""
    for gr in data["groups"]:
        es = [e for e in data["entries"] if e["group"] == gr["key"]]
        inner += f'<h3 class="group-h">{esc(gr["label"])} <small>{es[0]["id"]} to {es[-1]["id"]}</small></h3><div class="cards">'
        for e in es:
            tags = [stop_label(data, "substrate", e["substrate"]), stop_label(data, "tempo", e["tempo"]), stop_label(data, "visibility", e["visibility"])]
            tag_html = "".join(f"<li>{esc(t)}</li>" for t in tags) + f'<li class="aim">{esc(stop_label(data, "aim", e["aim"]))}</li>'
            where = ("C1 to C4" if e["x"] == "band" else e["x"]) + f' · {e["y"]}' + (f' + {e["y2"]}' if e.get("y2") else "") + (f' → {e["arrowTo"]}' if e.get("arrowTo") else "")
            dl = "".join(f"<div><dt>{esc(k)}</dt><dd>{R(t)}</dd></div>" for k, t in e["lines"])
            inner += (f'<article class="card aim-{e["aim"]}" id="c{e["id"]}" data-id="{e["id"]}" data-aim="{e["aim"]}" aria-labelledby="c{e["id"]}-h">'
                      f'<div class="card-head">{mini_svg(e["substrate"], e["id"], 40)}<div><h4 id="c{e["id"]}-h"><span class="n">{e["id"]}</span>{esc(e["name"])}</h4>'
                      f'<p class="coord">{esc(e["coord"])} <span title="Chart position">({esc(where)})</span></p></div></div>'
                      f'<ul class="tags" aria-label="Side-scale values">{tag_html}</ul><dl>{dl}</dl></article>')
        inner += "</div>"
    out.append(section("systems", "05 · Catalog", "The twenty systems", inner))

    # myths
    myths = "".join(f'<li><b>{R(m["title"])}</b><p>{R(m["text"])}</p></li>' for m in data["myths"])
    out.append(section("myths", "06 · Common mistakes", "Five myths", f'<ol class="myths">{myths}</ol>'))

    # fringe
    fr = data["fringe"]
    inner = f'<p>{R(fr["intro"])}</p><ul class="fringe-list">' + "".join(f"<li>{R(i['text'])}</li>" for i in fr["items"]) + "</ul>"
    out.append(section("unconfirmed", "07 · Out of bounds", "Beyond the line: unconfirmed physics", inner))

    # winners
    wn = data["winners"]
    wrows = ""
    for row in wn["rows"]:
        sys_html = ", ".join(f'<a href="#c{i}">{esc(name)}</a> ({i})' for i, name in row["systems"])
        wrows += f'<tr class="aim-{row["aim"]}"><td><i></i>{esc(stop_label(data, "aim", row["aim"]))}</td><td>{sys_html}</td><td>{R(row["why"])}</td></tr>'
    inner = (f'<div class="scroll-table winners"><table><thead><tr><th>Political aim</th><th>Cheapest sufficient system</th><th>Why</th></tr></thead><tbody>{wrows}</tbody></table></div>'
             f'<p class="closing">{R(wn["closing"])}</p>')
    out.append(section("winners", "08 · Verdict", "Who actually wins?", inner))

    # appendix
    ap = data["appendix"]
    tiers_li = "".join(f"<li>{tier_html(data, t)} {esc(desc[0].upper() + desc[1:])}.</li>" for t, desc in data["tiers"].items())
    arows = "".join(f"<tr><td>{esc(a)}</td><td>{R(b)}</td><td>{R(c)}</td></tr>" for a, b, c in ap["rows"])
    inner = (f'<p>Every figure carries a provenance tier:</p><ul>{tiers_li}</ul>'
             f'<p class="constants">Constants: {"; ".join(R(c) for c in ap["constants"])}.</p>'
             f'<div class="scroll-table arith"><table><thead><tr><th>Item</th><th>Formula and inputs</th><th>Result</th></tr></thead><tbody>{arows}</tbody></table></div>'
             f'<p>A build gate (<code>scripts/check_space_combat.py</code>) recomputes each row and fails if a figure on the page stops matching its rounding.</p>')
    out.append(section("arithmetic", "09 · Footnotes", "Assumptions and arithmetic", inner))

    # sources
    so = data["sources"]
    items = "".join(f'<li>{R(s["label"])}: ' + ", ".join(f'<a href="{esc(u)}">{esc(re.sub(r"^https?://(www\\.)?", "", u).split("/")[0])}</a>' for u in s["links"]) + "</li>" for s in so["items"])
    inner = f'<p>Checked {esc(so["checked"])}.</p><ol class="sources">{items}</ol><p>{R(so["unchecked"])}</p>'
    out.append(section("sources", "10 · Provenance", "Sources", inner))
    return "\n".join(out)


def build(text: str) -> str:
    data = load_data(text)
    body = "<!--gen:body-->\n" + render_body(data) + "\n<!--/gen:body-->"
    if not REGION_RE.search(text):
        raise SystemExit("space-combat.html: <!--gen:body--> region not found")
    return REGION_RE.sub(lambda _m: body, text, count=1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the generated region is stale")
    args = ap.parse_args()
    text = PAGE.read_text(encoding="utf-8")
    new = build(text)
    if args.check:
        if new != text:
            print("space-combat.html: generated region is stale; run python scripts/build_space_combat.py", file=sys.stderr)
            return 1
        print("space-combat.html: generated region is current")
        return 0
    if new != text:
        PAGE.write_text(new, encoding="utf-8", newline="\n")
        print("space-combat.html: regenerated")
    else:
        print("space-combat.html: already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
