#!/usr/bin/env python3
"""Gate: recompute every figure on space-combat.html and check the rendered structure. Exit 1 on failure.

Numbers: each check names where a figure lives in the page's JSON data model, the exact text shown,
and the value recomputed here from the constants below. The displayed number must equal the
recomputed value rounded to the precision shown (significant figures, trailing zeros of integers
not significant). Structure: 20 entries with contiguous ids, valid enums, every id exactly once on
each chart rendering and each side scale, one card per id, and a generated region that matches the
data (scripts/build_space_combat.py --check).

    python scripts/check_space_combat.py

Run by scripts/build_site.py as a deploy gate.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_space_combat as B  # noqa: E402

C = 2.998e8
TON = 4.184e9
MT = 4.184e15
LSUN = 3.828e26
LY = 9.461e15
AU = 1.496e11
MPC = 3.086e22
SIGMA = 5.670e-8
G = 6.674e-11
MOON = 3.844e8
NEPTUNE_AU = 30.07

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def text_at(data: dict, path: tuple) -> str:
    """('entry', 2, 'Scale') | ('law', 1) | ('myth', 1) | ('read',) | ('column', 'C3') | ('appendix', 'Missile')."""
    kind = path[0]
    if kind == "entry":
        e = B.by_id(data)[path[1]]
        return dict(e["lines"])[path[2]]
    if kind == "law":
        return data["laws"][path[1] - 1]["text"]
    if kind == "myth":
        return data["myths"][path[1] - 1]["text"]
    if kind == "read":
        return data["read"]["speed"]
    if kind == "column":
        c = next(c for c in data["columns"] if c["id"] == path[1])
        return c["density"] + " | " + c["sub"]
    if kind == "appendix":
        row = next(r for r in data["appendix"]["rows"] if r[0] == path[1])
        return row[1] + " | " + row[2]
    raise KeyError(path)


NUM = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:×10\^(-?\d+))?")


def shown_matches(snippet: str, value: float) -> tuple[bool, str]:
    m = NUM.search(snippet)
    if not m:
        return False, "no number in snippet"
    mant_s, exp_s = m.group(1), m.group(2)
    digits = mant_s.replace(",", "")
    shown = float(digits) * (10 ** int(exp_s) if exp_s else 1)
    if "." in digits:
        sig = len(digits.replace(".", "").lstrip("0"))
    else:
        sig = len(digits.rstrip("0")) or 1
    if value == 0:
        return shown == 0, "zero"
    rounded = float(f"{value:.{sig}g}")
    ok = math.isclose(rounded, shown, rel_tol=1e-9)
    return ok, f"shown {shown:g} ({sig} sig), recomputed {value:.6g} -> {rounded:g}"


CHECKED = 0


def check(data: dict, path: tuple, snippet: str, value: float) -> None:
    global CHECKED
    CHECKED += 1
    t = text_at(data, path)
    if snippet not in t:
        fail(f"{path}: expected text {snippet!r} not found in {t!r}")
        return
    ok, why = shown_matches(snippet, value)
    if not ok:
        fail(f"{path}: {snippet!r}: {why}")


def numbers(data: dict) -> None:
    gamma = 1 / math.sqrt(1 - 0.9 ** 2)
    torch = 0.5 * (1e6 * 9.81) * 1e6
    missile = 0.5 * 100 * 1e5 ** 2
    spot = lambda rng: 2.44 * 1e-6 * rng / 10  # noqa: E731
    debris = 0.5 * 1 * 1e4 ** 2
    rock_m = 4 / 3 * math.pi * 500 ** 3 * 2600
    rock = 0.5 * rock_m * 2e4 ** 2
    rkv = (gamma - 1) * 1000 * C ** 2
    lag = 10 / 0.9 - 10
    ked = (gamma - 1) * C ** 2
    anti = 2 * C ** 2
    sun = LSUN / MT
    dyson = 2.44e-6 * 10 * LY / AU
    rs = lambda m: 2 * G * m / C ** 2  # noqa: E731
    flash = 1e6 * C ** 2
    gw = 1e-21 * (410 * MPC / AU) * 2
    glow = SIGMA * 300 ** 4
    radiator = 1e9 / (SIGMA * 1000 ** 4)
    ratio = math.exp(30 / 4.5)
    beam = 1e6 * 10e-3

    # cards
    check(data, ("entry", 1, "Scale"), "5 terawatts", torch / 1e12)
    check(data, ("entry", 2, "Scale"), "120 tons", missile / TON)
    check(data, ("entry", 3, "Scale"), "2.4 m spot", spot(1e7))
    check(data, ("entry", 3, "Scale"), "73 m spot", spot(C))
    check(data, ("entry", 5, "Scale"), "10 kilowatts", beam / 1e3)
    check(data, ("entry", 6, "Scale"), "12 kg of TNT", debris / (TON / 1000))
    check(data, ("entry", 9, "Scale"), "2.7×10^20 joules", rock)
    check(data, ("entry", 9, "Scale"), "65,000 megatons", rock / MT)
    check(data, ("entry", 10, "Scale"), "28,000 megatons", rkv / MT)
    check(data, ("entry", 10, "Scale"), "1.1 years", lag)
    check(data, ("entry", 10, "Note on antimatter"), "43 megatons", anti / MT)
    check(data, ("entry", 11, "Scale"), "0.9 attometers", rs(6.06e8) / 1e-18)
    check(data, ("entry", 11, "Scale"), "21 million megatons", flash / MT / 1e6)
    check(data, ("entry", 12, "Scale"), "91 billion megatons", sun / 1e9)
    if "meter-scale" not in text_at(data, ("entry", 12, "Scale")) or not 1 <= dyson < 10:
        fail(f"entry 12: 'meter-scale' spot claim vs recomputed {dyson:.3g} m")
    if "in principle" not in text_at(data, ("entry", 12, "Scale")):
        fail("entry 12: the Dyson spot must keep the 'in principle' qualifier")
    # laws, axis, myths
    check(data, ("law", 1), "460 W", glow)
    check(data, ("law", 2), "1.3 seconds", MOON / C)
    check(data, ("law", 2), "8.3 minutes", AU / C / 60)
    check(data, ("law", 2), "4.2 hours", NEPTUNE_AU * AU / C / 3600)
    check(data, ("law", 3), "790", ratio)
    check(data, ("law", 4), "18,000 square meters", radiator)
    check(data, ("law", 5), "5 terawatts", torch / 1e12)
    check(data, ("read",), "1.16×10^17 J/kg", ked)
    if not ked > C ** 2:
        fail("read: 0.9c kinetic energy density should exceed antimatter fuel (c² per kg of reactants)")
    check(data, ("column", "C3"), "9×10^16 J/kg", C ** 2)
    if "~10^17" not in text_at(data, ("column", "C3")) or round(math.log10(C ** 2)) != 17:
        fail("column C3: chart label order of magnitude")
    check(data, ("myth", 1), "0.17 microns", gw / 1e-6)
    if not 1e-15 <= rs(1e12) <= 2e-15:
        fail(f"myth 2: mountain-mass hole radius {rs(1e12):.3g} m is not proton-sized")
    # appendix rows
    A = lambda item, snip, val: check(data, ("appendix", item), snip, val)  # noqa: E731
    A("Torch drive power", "4.9×10^12 W", torch)
    A("Missile", "5×10^11 J", missile)
    A("Missile", "120 tons TNT", missile / TON)
    A("Laser spot", "2.44 m at", spot(1e7))
    A("Laser spot", "73 m at", spot(3e8))
    A("Debris", "5×10^7 J", debris)
    A("Debris", "12 kg TNT", debris / (TON / 1000))
    A("Asteroid", "1.36×10^12 kg", rock_m)
    A("Asteroid", "2.7×10^20 J", rock)
    A("Asteroid", "65,000 Mt", rock / MT)
    A("Relativistic kill vehicle", "2.294", gamma)
    A("Relativistic kill vehicle", "1.16×10^20 J", rkv)
    A("Relativistic kill vehicle", "27,800 Mt", rkv / MT)
    A("Its warning time", "1.1 years", lag)
    A("Kinetic energy density at 0.9c", "1.16×10^17 J/kg", ked)
    A("Antimatter", "1.8×10^17 J", anti)
    A("Antimatter", "43 Mt", anti / MT)
    A("Sun, one second", "9.1×10^10 Mt", sun)
    A("Dyson beam spot", "1.5 m", dyson)
    A("Black hole radius", "9×10^-19 m", rs(6.06e8))
    A("Black hole radius", "1.5×10^-15 m", rs(1e12))
    A("Black hole final flash", "9×10^22 J", flash)
    A("Black hole final flash", "2.1×10^7 Mt", flash / MT)
    A("Gravity-wave stretch", "1.7×10^-7 m", gw)
    A("Hull glow", "459 W/m²", glow)
    A("Radiator area", "17,600 m²", radiator)
    A("Chemical mass ratio", "786", ratio)
    A("Particle beam test power", "10 kW", beam / 1e3)
    A("Light lag", "Moon 1.28 s", MOON / C)
    A("Light lag", "Sun 8.3 min", AU / C / 60)
    A("Light lag", "Neptune 4.2 h", NEPTUNE_AU * AU / C / 3600)


def structure(data: dict, page: str) -> None:
    es = data["entries"]
    ids = [e["id"] for e in es]
    if len(es) != 20:
        fail(f"expected 20 entries, found {len(es)}")
    if ids != list(range(1, len(es) + 1)):
        fail(f"ids must be unique and contiguous from 1: {ids}")
    enums = {sc["key"]: {st["key"] for st in sc["stops"]} for sc in data["scales"]}
    for e in es:
        for k, allowed in enums.items():
            if e[k] not in allowed:
                fail(f"entry {e['id']}: {k}={e[k]!r} not in {sorted(allowed)}")
        if e["x"] not in B.COLS[:4] + ["band"]:
            fail(f"entry {e['id']}: x={e['x']!r}")
        for k in ("y", "y2", "arrowTo"):
            if k in e and e[k] not in B.ROWS:
                fail(f"entry {e['id']}: {k}={e[k]!r}")
        if e["group"] not in {g["key"] for g in data["groups"]}:
            fail(f"entry {e['id']}: group {e['group']!r}")
        labels = [k for k, _ in e["lines"]]
        for need in ("Scale", "Counter", "Political use", "Fiction"):
            if need not in labels:
                fail(f"entry {e['id']}: missing card line {need!r}")
    for row in data["winners"]["rows"]:
        for i, _name in row["systems"]:
            # A system may serve an aim other than its own primary one (16 captures a fleet: subvert, used to disarm).
            if i not in ids:
                fail(f"winners: unknown id {i}")

    for variant in B.VARIANTS:
        svg = B.render_chart(data, variant)
        prim = re.findall(r'class="glyph primary[^"]*"[^>]*data-id="(\d+)"', svg)
        for i in ids:
            n = prim.count(str(i))
            if n != 1:
                fail(f"chart {variant}: id {i} appears {n} times as a primary glyph")
        ghosts = sorted(int(x) for x in re.findall(r'class="glyph ghost[^"]*"[^>]*data-id="(\d+)"', svg))
        if ghosts != sorted(e["id"] for e in es if e.get("y2")):
            fail(f"chart {variant}: secondary glyphs {ghosts}")
        if svg.count('class="threat"') != sum(1 for e in es if e.get("arrowTo")):
            fail(f"chart {variant}: threat arrow count")
        for must in (data["chart"]["annotation"][0], data["chart"]["edge"]):
            if B.esc(must) not in svg:
                fail(f"chart {variant}: missing {must!r}")
    for sc in data["scales"]:
        m = re.search(rf'<section class="scale" aria-labelledby="scale-{sc["key"]}">(.*?)</section>', page, re.S)
        if not m:
            fail(f"scale {sc['key']}: not rendered")
            continue
        got = re.findall(r'class="mini[^"]*"[^>]*data-id="(\d+)"', m.group(1))
        for i in ids:
            if got.count(str(i)) != 1:
                fail(f"scale {sc['key']}: id {i} appears {got.count(str(i))} times")
    for i in ids:
        if page.count(f'id="c{i}"') != 1:
            fail(f"card #c{i}: found {page.count(f'id=\"c{i}\"')} times")
    if B.build(page) != page:
        fail("generated region is stale: run python scripts/build_space_combat.py")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    page = B.PAGE.read_text(encoding="utf-8")
    data = B.load_data(page)
    numbers(data)
    structure(data, page)
    if failures:
        for f in failures:
            print("FAIL", f, file=sys.stderr)
        print(f"space-combat: {len(failures)} failure(s)", file=sys.stderr)
        return 1
    print(f"space-combat: {CHECKED} figures recomputed; structure and generated region OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
