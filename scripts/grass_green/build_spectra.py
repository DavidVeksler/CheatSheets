#!/usr/bin/env python3
"""Render the measured spectra on why-is-grass-green.html into inline SVG.

Inputs (committed next to this script):
  chla.txt      PhotochemCAD 2.1a chlorophyll a in diethyl ether, molar extinction
                (M^-1 cm^-1) per nm, scaled to 111,700 at 427.8 nm. Source:
                https://omlc.org/spectra/PhotochemCAD/data/123-abs.txt
  chlb.txt      Same for chlorophyll b (159,100 at 453 nm).
                https://omlc.org/spectra/PhotochemCAD/data/125-abs.txt
  astmg173.csv  ASTM G173-03 reference spectra (NREL / SMARTS 2.9.2); the
                "global" column is AM1.5 global tilt irradiance, W m^-2 nm^-1.
                Copy from https://github.com/pvlib/pvlib-python (pvlib/data/ASTMG173.csv)

Outputs, written in place between the marker comments in the page:
  <!-- FIG:bench --> ... <!-- /FIG:bench -->     hero spectrum bench
  <!-- FIG:quiet --> ... <!-- /FIG:quiet -->     level-8 solar-vs-absorption figure
  <!-- DATA:spectra --> ... <!-- /DATA:spectra --> JSON used by the cursor readout

Every curve is normalised to its own maximum over 380-720 nm. The page states
this in the figure captions. Run: python scripts/grass_green/build_spectra.py
"""
from __future__ import annotations

import bisect
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PAGE = ROOT / "why-is-grass-green.html"

W0, W1, STEP = 380, 720, 2
WAVES = list(range(W0, W1 + 1, STEP))


def load_pcc(path: Path) -> dict[float, float]:
    out: dict[float, float] = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        a, b = line.split()[:2]
        out[float(a)] = float(b)
    return out


def load_g173(path: Path) -> dict[float, float]:
    lines = path.read_text().splitlines()[1:]  # first line is a title row
    return {float(r["wavelength"]): float(r["global"]) for r in csv.DictReader(lines)}


def interp(d: dict[float, float], x: float) -> float:
    ks = sorted(d)
    i = bisect.bisect_left(ks, x)
    if i == 0:
        return d[ks[0]]
    if i >= len(ks):
        return d[ks[-1]]
    x0, x1 = ks[i - 1], ks[i]
    y0, y1 = d[x0], d[x1]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def series(d: dict[float, float]) -> list[float]:
    return [interp(d, w) for w in WAVES]


def peak(d: dict[float, float], lo: float, hi: float) -> tuple[float, float]:
    k = max((w for w in d if lo <= w <= hi), key=lambda w: d[w])
    return k, d[k]


def path(xs: list[float], ys: list[float], close_y: float | None = None) -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    d = f"M{pts}"
    if close_y is not None:
        d += f" L{xs[-1]:.1f},{close_y:.1f} L{xs[0]:.1f},{close_y:.1f} Z"
    return d


SPECTRUM_STOPS = [
    (380, "#5b2a86"), (420, "#4c3fc7"), (450, "#2b6fe0"), (480, "#1fa7d6"),
    (500, "#22b878"), (530, "#5bc43a"), (560, "#b6d221"), (580, "#f2c928"),
    (600, "#f39a1e"), (630, "#e6512f"), (680, "#b81f1f"), (720, "#5e0d0d"),
]


def gradient(id_: str, x0: float, x1: float) -> str:
    stops = "".join(
        f'<stop offset="{(w - W0) / (W1 - W0):.4f}" stop-color="{c}"/>' for w, c in SPECTRUM_STOPS
    )
    return f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="{x0}" x2="{x1}" y1="0" y2="0">{stops}</linearGradient>'


def bench_svg(chla, chlb, sol, amax, bmax, smax, apk, aq, bpk, bq, spk) -> tuple[str, dict]:
    X0, X1, Y0, Y1 = 60.0, 960.0, 40.0, 330.0
    pxnm = (X1 - X0) / (W1 - W0)
    xs = [X0 + (w - W0) * pxnm for w in WAVES]
    ya = [Y1 - (v / amax) * (Y1 - Y0) for v in chla]
    yb = [Y1 - (v / bmax) * (Y1 - Y0) for v in chlb]
    ys = [Y1 - (v / smax) * (Y1 - Y0) for v in sol]
    ticks = "".join(
        f'<line class="grid" x1="{X0 + (w - W0) * pxnm:.1f}" x2="{X0 + (w - W0) * pxnm:.1f}" y1="{Y0}" y2="{Y1}"/>'
        f'<text class="lab" x="{X0 + (w - W0) * pxnm:.1f}" y="{Y1 + 40}" text-anchor="middle">{w}</text>'
        for w in range(400, 701, 50)
    )
    hgrid = "".join(
        f'<line class="grid" x1="{X0}" x2="{X1}" y1="{Y1 - f * (Y1 - Y0):.1f}" y2="{Y1 - f * (Y1 - Y0):.1f}"/>'
        f'<text class="lab" x="{X0 - 8}" y="{Y1 - f * (Y1 - Y0) + 5:.1f}" text-anchor="end">{int(f * 100)}%</text>'
        for f in (0.25, 0.5, 0.75, 1.0)
    )
    cx = X0 + (550 - W0) * pxnm

    def lab(w, y, text, cls="lab b", anchor="middle", dy=-8):
        return f'<text class="{cls}" x="{X0 + (w - W0) * pxnm:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{text}</text>'

    svg = f"""<svg viewBox="0 0 1000 432" role="img" aria-labelledby="bench-cap" preserveAspectRatio="xMidYMid meet">
<defs>{gradient("bench-spectrum", X0, X1)}<linearGradient id="sun-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#f0c15a" stop-opacity=".9"/><stop offset="1" stop-color="#f0c15a" stop-opacity=".15"/></linearGradient></defs>
<g>{hgrid}{ticks}</g>
<rect x="{X0}" y="{Y1 + 8}" width="{X1 - X0}" height="14" rx="3" fill="url(#bench-spectrum)"/>
<path class="sol" d="{path(xs, ys, Y1)}"/><path class="sol-line" d="{path(xs, ys)}"/>
<path class="chlb" d="{path(xs, yb)}"/>
<path class="chla" d="{path(xs, ya)}"/>
<line class="axis" x1="{X0}" x2="{X1}" y1="{Y1}" y2="{Y1}"/><line class="axis" x1="{X0}" x2="{X0}" y1="{Y0}" y2="{Y1}"/>
{lab(apk, Y0, f"Soret {apk:.0f} nm", dy=-10)}{lab(aq, Y1 - (chla[WAVES.index(660)] / amax) * (Y1 - Y0), f"Q<tspan font-size='10' dy='4'>y</tspan><tspan dy='-4'> {aq:.0f} nm</tspan>", dy=-10)}
{lab(bpk, Y0, f"chl b {bpk:.0f}", cls="lab", dy=14, anchor="start")}{lab(bq, Y1 - (chlb[WAVES.index(644)] / bmax) * (Y1 - Y0), f"chl b {bq:.0f}", cls="lab", dy=-8, anchor="start")}
{lab(spk, Y0, f"sunlight peak {spk:.0f} nm", cls="lab", dy=-10)}
<text class="lab" x="{X0 + (545 - W0) * pxnm:.1f}" y="{Y1 - 0.5 * (Y1 - Y0):.1f}" text-anchor="middle" font-size="15" font-weight="700" fill="#9be08f">the green gap</text>
<line id="bench-cursor" class="cursor" x1="{cx:.1f}" x2="{cx:.1f}" y1="{Y0 - 6}" y2="{Y1 + 22}"/>
<text id="bench-cursor-label" class="lab b" x="{cx:.1f}" y="{Y1 + 62}" text-anchor="middle">550 nm · green</text>
<text class="lab" x="{X1}" y="{Y1 + 62}" text-anchor="end">wavelength, nm</text>
<g transform="translate({X0} {Y1 + 92})" font-size="13"><line x1="0" x2="26" y1="0" y2="0" stroke="#8ff08a" stroke-width="3"/><text class="lab" x="32" y="4">chlorophyll a, diethyl ether (PhotochemCAD)</text><line x1="330" x2="356" y1="0" y2="0" stroke="#63c4ff" stroke-width="2.2" stroke-dasharray="7 5"/><text class="lab" x="362" y="4">chlorophyll b, diethyl ether</text><rect x="600" y="-6" width="26" height="12" fill="#f0c15a" opacity=".6"/><text class="lab" x="632" y="4">sunlight at ground level, ASTM G173 AM1.5G</text></g>
</svg>"""
    meta = {"x0": X0, "pxnm": round(pxnm, 6)}
    return svg, meta


def quiet_svg(chla, chlb, sol, amax, bmax, smax, spk) -> str:
    X0, X1, Y0, Y1 = 50.0, 500.0, 72.0, 260.0
    pxnm = (X1 - X0) / (W1 - W0)
    xs = [X0 + (w - W0) * pxnm for w in WAVES]
    ya = [Y1 - (v / amax) * (Y1 - Y0) for v in chla]
    yb = [Y1 - (v / bmax) * (Y1 - Y0) for v in chlb]
    ys = [Y1 - (v / smax) * (Y1 - Y0) for v in sol]
    ticks = "".join(
        f'<line class="gl" x1="{X0 + (w - W0) * pxnm:.1f}" x2="{X0 + (w - W0) * pxnm:.1f}" y1="{Y0}" y2="{Y1}"/>'
        f'<text class="lab" x="{X0 + (w - W0) * pxnm:.1f}" y="{Y1 + 18}" text-anchor="middle" font-size="12">{w}</text>'
        for w in range(400, 701, 50)
    )
    px = X0 + (spk - W0) * pxnm
    # bands: where chl a > 25% of its max
    def bands(vals, vmax, thr=0.25):
        out, start = [], None
        for w, v in zip(WAVES, vals):
            on = v / vmax >= thr
            if on and start is None:
                start = w
            if not on and start is not None:
                out.append((start, w)); start = None
        if start is not None:
            out.append((start, WAVES[-1]))
        return out
    band_rects = "".join(
        f'<rect class="band" x="{X0 + (a - W0) * pxnm:.1f}" y="{Y0}" width="{(b - a) * pxnm:.1f}" height="{Y1 - Y0}" fill="var(--leaf)"/>'
        for a, b in bands(chla, amax)
    )
    return f"""<svg viewBox="0 0 520 350" role="img" aria-labelledby="quiet-cap">
<defs>{gradient("quiet-spectrum", X0, X1)}</defs>
<text x="20" y="26" class="lab b">Sunlight at the ground vs. where chlorophyll absorbs</text>
{ticks}{band_rects}
<path class="sun" d="{path(xs, ys, Y1)}"/><path class="sunline" d="{path(xs, ys)}"/>
<path class="chlb2" d="{path(xs, yb)}"/><path class="chla2" d="{path(xs, ya)}"/>
<line class="ax" x1="{X0}" x2="{X1}" y1="{Y1}" y2="{Y1}"/>
<rect x="{X0}" y="{Y1 + 4}" width="{X1 - X0}" height="6" fill="url(#quiet-spectrum)"/>
<line x1="{px:.1f}" x2="{px:.1f}" y1="{Y0 - 4}" y2="{Y1}" stroke="var(--gold)" stroke-width="1.5" stroke-dasharray="4 3"/>
<text class="lab b" x="{px + 6:.1f}" y="{Y0 + 14}" font-size="12" fill="var(--gold)">solar peak {spk:.0f} nm</text>
<text class="lab b" x="{X0 + (428 - W0) * pxnm:.1f}" y="{Y0 - 14}" font-size="12" text-anchor="middle" fill="var(--leaf)">absorb here ↓</text>
<text class="lab b" x="{X0 + (660 - W0) * pxnm:.1f}" y="{Y0 - 14}" font-size="12" text-anchor="middle" fill="var(--leaf)">and here ↓</text>
<text class="lab" x="{X0 + (545 - W0) * pxnm:.1f}" y="{Y0 - 14}" font-size="12" text-anchor="middle">not at the solar peak</text>
<g transform="translate({X0} {Y1 + 36})" font-size="12"><line x1="0" x2="22" y1="0" y2="0" stroke="var(--leaf)" stroke-width="2.5"/><text class="lab" x="28" y="4">chlorophyll a</text><line x1="120" x2="142" y1="0" y2="0" stroke="var(--soret)" stroke-width="2" stroke-dasharray="6 4"/><text class="lab" x="148" y="4">chlorophyll b</text><rect x="240" y="-6" width="22" height="12" fill="var(--gold)" opacity=".5"/><text class="lab" x="268" y="4">AM1.5G irradiance</text></g>
<text class="lab" x="{X0}" y="{Y1 + 62}" font-size="12">Shaded: where chlorophyll a exceeds 25% of its peak.</text><text class="lab" x="{X0}" y="{Y1 + 78}" font-size="12">Each curve is normalised to its own maximum.</text>
</svg>"""


def splice(html: str, tag: str, body: str, kind: str = "FIG") -> str:
    pat = re.compile(rf"(<!-- {kind}:{tag} -->)[\s\S]*?(<!-- /{kind}:{tag} -->)")
    if not pat.search(html):
        raise SystemExit(f"marker {kind}:{tag} not found in page")
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", html, count=1)


def main() -> int:
    a = load_pcc(HERE / "chla.txt")
    b = load_pcc(HERE / "chlb.txt")
    s = load_g173(HERE / "astmg173.csv")
    chla, chlb, sol = series(a), series(b), series(s)
    apk, amax = peak(a, W0, W1)
    aq, aqv = peak(a, 600, W1)
    bpk, bmax = peak(b, W0, W1)
    bq, _ = peak(b, 600, W1)
    spk, smax = peak(s, W0, W1)
    bench, meta = bench_svg(chla, chlb, sol, amax, bmax, smax, apk, aq, bpk, bq, spk)
    quiet = quiet_svg(chla, chlb, sol, amax, bmax, smax, spk)
    data = {
        "w0": W0, "step": STEP,
        "chla": [round(v) for v in chla], "chlb": [round(v) for v in chlb], "sol": [round(v, 4) for v in sol],
        "amax": round(amax), "aq": round(aqv), "bmax": round(bmax), "smax": round(smax, 4),
        "apk": apk, "aqnm": aq, "bpk": bpk, "spk": spk, **meta,
    }
    html = PAGE.read_text(encoding="utf-8")
    html = splice(html, "bench", bench)
    html = splice(html, "quiet", quiet)
    html = splice(html, "spectra", json.dumps(data, separators=(",", ":")), kind="DATA")
    PAGE.write_text(html, encoding="utf-8", newline="\n")
    print(f"chl a: Soret {apk} nm eps {amax:.0f}; Qy {aq} nm eps {aqv:.0f}; 550 nm {interp(a, 550):.0f}")
    print(f"chl b: {bpk} nm eps {bmax:.0f}; {bq} nm")
    print(f"AM1.5G peak {spk} nm {smax:.4f} W m^-2 nm^-1; wrote {PAGE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
