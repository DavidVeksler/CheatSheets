#!/usr/bin/env python3
"""Deterministic source, arithmetic, and copy gates for inside-ai-data-center.html."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "inside-ai-data-center.html"
html = PAGE.read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")
errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


match = re.search(r"const REFERENCE_BUILD=(\{.*?\});", html, re.S)
check(match is not None, "REFERENCE_BUILD missing")
ref = json.loads(match.group(1)) if match else {}


def lookup(key: str) -> float:
    value = ref
    for part in key.split("."):
        value = value[part]
    return float(value)


for data in soup.select("data[data-key]"):
    key = data["data-key"]
    try:
        actual = float(data["value"])
        expected = lookup(key)
        check(abs(actual - expected) < 1e-9, f"{key}: HTML {actual} != reference {expected}")
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f"{key}: invalid data key or value: {exc}")

if ref:
    rack, tray, superchip, campus, cooling = (
        ref[k] for k in ("rack", "tray", "superchip", "campus", "cooling")
    )
    check(tray["superchips"] * superchip["gpus"] == tray["gpus"], "tray GPU multiplication")
    check(rack["computeTrays"] * tray["gpus"] == rack["gpus"], "rack GPU multiplication")
    check(campus["racks"] * rack["gpus"] == campus["gpus"], "campus GPU multiplication")
    scenario_racks = campus["MW"] * 1000 / campus["pue"] / campus["rackEffectiveKW"]
    check(abs(scenario_racks - campus["racks"]) < 1, "campus rack scenario")
    flow = rack["kW"] * rack["liquidShare"] * 60 / (cooling["cpKJkgK"] * cooling["deltaK"])
    check(abs(flow - rack["flowLmin"]) < 0.25, "rack coolant calculation")
    check("~146 L/min" in html, "computed flow tag missing")

part_ids = {
    0: {"substation", "cooling-plant", "campus-hall", "backup-generation"},
    1: {"hall-busway", "hall-rows", "hall-cdu", "hall-ups"},
    2: {"row-racks", "row-fabric", "row-pdu", "row-cdu"},
    3: {"compute-tray", "switch-tray", "manifold", "busbar", "domain"},
    4: {"superchip-a", "superchip-b", "cold-plate", "nic"},
    5: {"grace-cpu", "gpu-left", "gpu-right", "c2c-link"},
    6: {"compute-die-a", "compute-die-b", "hbm-array", "interposer"},
    7: {"dram-layers", "tsv", "base-die", "die-edge"},
}


def words(value: str) -> int:
    return len(re.findall(r"\S+", value.strip()))


for stop in range(8):
    section = soup.select_one(f"#stop-{stop}")
    check(section is not None, f"stop {stop} missing")
    if section is None:
        continue
    callouts = section.select(".pin-wrap[data-anchor]")
    check(len(callouts) == 4, f"stop {stop} needs four callouts")
    for callout in callouts:
        anchor = callout["data-anchor"]
        check(anchor in part_ids[stop], f"stop {stop}: unknown anchor {anchor}")
        collapsed = callout.select_one(".callout b")
        expanded = callout.select_one(".callout .more")
        check(collapsed is not None and words(collapsed.get_text(" ", strip=True)) <= 8,
              f"stop {stop}: collapsed callout exceeds eight words")
        check(expanded is not None and words(expanded.get_text(" ", strip=True)) <= 45,
              f"stop {stop}: expanded callout exceeds 45 words")
    check(section.select_one(".fallback-plate") is None,
          f"stop {stop}: static drawing fallback remains")

corrections = soup.select("#common-mistakes .correction")
check(len(corrections) == 8, "eight correction tags required")
for correction in corrections:
    stop = int(correction["data-stop"])
    check(correction["data-anchor"] in part_ids[stop], f"correction anchor at stop {stop}")
    check(words(correction.get_text(" ", strip=True)) <= 35, "correction exceeds 35 words")

for paragraph in soup.select("p"):
    check(words(paragraph.get_text(" ", strip=True)) <= 60, "paragraph exceeds 60 words")

preview = ROOT / "images" / "inside-ai-data-center.png"
check(preview.is_file(), "social preview missing")
if preview.is_file():
    from PIL import Image

    with Image.open(preview) as image:
        check(image.size == (1200, 630), "social preview must be 1200x630")

if errors:
    for error in errors:
        print("FAIL:", error)
    raise SystemExit(1)
print("inside-ai-data-center: source, arithmetic, word budgets, and assets pass")
