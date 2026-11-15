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

# reference_build.json is the single numeric source; the inline block is its page subset.
REF_JSON = ROOT / "scripts" / "inside_ai_dc" / "reference_build.json"
build_ref = json.loads(REF_JSON.read_text(encoding="utf-8"))
check(build_ref.get("page") == ref, "inline REFERENCE_BUILD differs from reference_build.json 'page'")
order = build_ref["rackOrder"]["fromTop"]
for kind, key in (("compute", "computeTrays"), ("switch", "switchTrays"), ("power", "powerShelves"), ("tor", "torSwitches")):
    check(order.count(kind) == build_ref["counts"][key]["value"], f"rackOrder {kind} count != counts.{key}")
check(build_ref["counts"]["computeTrays"]["value"] == ref.get("rack", {}).get("computeTrays"), "computeTrays count drift")


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

# Blender models (docs/specs/inside-ai-data-center-blender-models.md section 10)
MODELS = ROOT / "models" / "inside-ai-data-center"
MODEL_IDS = {
    3: {"rack", "domain", "return", "nvlink-spine", "person", "rack-gpus"},
    4: {"tray", "tray-supply", "tray-return", "power-contact"},
    5: {"superchip", "power-delivery", "c2c-link-two", "superchip-cool", "id-card"},
    6: {"substrate", "die-link", "gpu-power", "stiffener", "cold-plate-lifted", "section", "fingertip"},
    7: {"base-die", "mold", "die-edge", "hair", "card-edge"},
}
# Scale wording on the GLB path (spec D4): every exaggeration constant is exported and printed on the stage label.
EXAG_STOPS = {6: {"packageSliceHeight"}, 7: {"hbmHeight", "hbmVia"}}
model_manifest = MODELS / "manifest.json"
if model_manifest.is_file():
    import ast
    import hashlib
    import struct

    mf = json.loads(model_manifest.read_text(encoding="utf-8"))
    budget = mf.get("budget", {})
    total = 0
    for name, entry in mf.get("files", {}).items():
        glb = MODELS / name
        check(glb.is_file(), f"{name} listed in manifest.json but missing")
        if not glb.is_file():
            continue
        data = glb.read_bytes()
        total += len(data)
        check(hashlib.sha256(data).hexdigest() == entry["sha256"], f"{name}: sha256 differs from manifest.json")
        check(len(data) == entry["bytes"], f"{name}: byte count differs from manifest.json")
        jlen = struct.unpack_from("<I", data, 12)[0]
        gltf = json.loads(data[20:20 + jlen])
        check(not gltf.get("images") and not gltf.get("textures"), f"{name}: contains images or textures")
        check("KHR_draco_mesh_compression" not in gltf.get("extensionsUsed", []), f"{name}: Draco is not allowed")
        stop = entry["stop"]
        section = soup.select_one(f"#stop-{stop}")
        anchors = {c["data-anchor"] for c in section.select(".pin-wrap[data-anchor]")} if section else set()
        anchors |= {c["data-anchor"] for c in soup.select(f'#common-mistakes .correction[data-stop="{stop}"]')}
        for pid in sorted(part_ids[stop] | anchors | MODEL_IDS.get(stop, set())):
            check(pid in entry["parts"], f"{name}: part id {pid} missing")
        for pid in sorted(anchors):
            check(pid in entry["anchors"], f"{name}: no anchor empty for callout {pid}")
        for key, limit in (("uniqueTriangles", "uniqueTriangles"), ("renderedTriangles", "renderedTriangles"),
                           ("drawCallEstimate", "drawCalls"), ("bytes", "bytes")):
            if limit in budget:
                check(entry[key] <= budget[limit], f"{name}: {key} {entry[key]} > budget {budget[limit]}")
        check(all(t in ("vendor", "derived", "illustrative") for t in entry["tiers"].values()), f"{name}: bad tier")
        for key in EXAG_STOPS.get(stop, ()):
            check(entry.get("exaggeration", {}).get(key) == build_ref["exaggeration"][key]["value"],
                  f"{name}: exaggeration {key} differs from reference_build.json")
            check(f"e.{key}" in html, f"page stage label does not print {key}")
    if "totalBytes" in budget:
        check(total <= budget["totalBytes"], f"all GLBs {total} B > {budget['totalBytes']} B")
    check(f"MODEL_FILES={{" in html, "page has no model loader")
    for name in mf.get("files", {}):
        check(f"'{name}'" in html, f"page does not load {name}")
    # runtime palette equals the Blender palette (spec 5.2)
    lib_src = (ROOT / "scripts" / "inside_ai_dc" / "blender" / "lib.py").read_text(encoding="utf-8")
    i = lib_src.index("PALETTE = {")
    j = lib_src.index("}\n", i) + 1
    lib_palette = {k: list(v) for k, v in ast.literal_eval(lib_src[i + len("PALETTE = "):j]).items()}
    pm = re.search(r"const PALETTE=(\{.*?\});", html)
    check(pm is not None and json.loads(pm.group(1)) == lib_palette, "page PALETTE differs from blender/lib.py PALETTE")

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
