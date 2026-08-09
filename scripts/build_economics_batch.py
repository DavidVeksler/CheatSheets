#!/usr/bin/env python3
"""Build the economics-comparison batch from primary-source data.

The historical/ideological tables below are deliberately explicit source-backed
content.  The two statistical sheets refresh their volatile rows from BEA,
Census, BLS, World Bank, and Tax Foundation source tables before rendering the
standalone HTML files.  Run from the repository root:

    python scripts/build_economics_batch.py

The generated pages remain fully static: no reader-side API calls or build step.
"""
from __future__ import annotations

import csv
import html
import io
import json
import math
import re
import tempfile
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
VERIFIED = "2026-08-09"
DATA_YEAR = "2024"

BEA_GDP_ZIP = "https://apps.bea.gov/regional/zip/SAGDP.zip"
BEA_RPP_ZIP = "https://apps.bea.gov/regional/zip/SARPP.zip"
CENSUS_MEDIAN_INCOME = (
    "https://www2.census.gov/programs-surveys/acs/data/2024/"
    "1_year_ranking/R1901.xlsx"
)
CENSUS_POVERTY = (
    "https://www2.census.gov/programs-surveys/acs/data/2024/"
    "1_year_ranking/R1701.xlsx"
)
CENSUS_MIGRATION = (
    "https://www2.census.gov/programs-surveys/popest/tables/2020-2024/"
    "state/totals/NST-EST2024-COMP.xlsx"
)
CENSUS_POPULATION = (
    "https://www2.census.gov/programs-surveys/popest/tables/2020-2024/"
    "state/totals/NST-EST2024-POP.xlsx"
)
CENSUS_STATE_KML = (
    "https://www2.census.gov/geo/tiger/GENZ2024/kml/"
    "cb_2024_us_state_20m.zip"
)
WORLD_BANK_GDP = (
    "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?"
    "date=2024&format=json&per_page=400"
)
WORLD_BANK_POP = (
    "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?"
    "date=2024&format=json&per_page=400"
)
WORLD_BANK_COUNTRIES = "https://api.worldbank.org/v2/country?format=json&per_page=400"
WORLD_BANK_PPP_PC = (
    "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.CD?"
    "date=2024&format=json&per_page=400"
)
WORLD_BANK_FX = (
    "https://api.worldbank.org/v2/country/GBR/indicator/PA.NUS.FCRF?"
    "date=2024&format=json"
)
TAX_BURDEN = "https://taxfoundation.org/data/all/state/tax-burden-by-state-2022/"
BLS_API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"


STATE_FIPS = {
    "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
    "California": "06", "Colorado": "08", "Connecticut": "09", "Delaware": "10",
    "District of Columbia": "11", "Florida": "12", "Georgia": "13", "Hawaii": "15",
    "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19", "Kansas": "20",
    "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24",
    "Massachusetts": "25", "Michigan": "26", "Minnesota": "27", "Mississippi": "28",
    "Missouri": "29", "Montana": "30", "Nebraska": "31", "Nevada": "32",
    "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35", "New York": "36",
    "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40",
    "Oregon": "41", "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45",
    "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49",
    "Vermont": "50", "Virginia": "51", "Washington": "53", "West Virginia": "54",
    "Wisconsin": "55", "Wyoming": "56",
}

RED_STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "Florida", "Georgia", "Idaho",
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Michigan", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Pennsylvania", "South Carolina", "South Dakota", "Tennessee",
    "Texas", "Utah", "West Virginia", "Wisconsin", "Wyoming",
}

# Rockefeller Institute 2025 report, Table 6: federal fiscal year 2023 balance
# of payments in dollars per capita. DC is not included in the report.
BOP_2023 = {
    "Virginia":16650,"New Mexico":16178,"Alaska":14760,"Maryland":13037,
    "West Virginia":12130,"Mississippi":11714,"Kentucky":10813,"Hawaii":10291,
    "Alabama":10268,"Maine":9144,"Louisiana":8784,"Oklahoma":8097,
    "South Carolina":7926,"Arkansas":7340,"Arizona":7195,"Missouri":7150,
    "Vermont":5558,"Delaware":5360,"Ohio":5075,"Montana":4929,
    "Pennsylvania":4826,"North Carolina":4808,"Rhode Island":4767,
    "Tennessee":4589,"Michigan":4584,"Indiana":4415,"Oregon":4389,
    "Idaho":4191,"Georgia":3951,"Kansas":3900,"South Dakota":3626,
    "Iowa":3481,"Wyoming":3218,"Connecticut":2937,"Wisconsin":2887,
    "North Dakota":2787,"Texas":2603,"Florida":2574,"Nebraska":2351,
    "Nevada":2120,"Utah":1067,"Colorado":1051,"Illinois":818,
    "Minnesota":807,"New York":674,"California":342,"New Hampshire":23,
    "Washington":-7,"Massachusetts":-967,"New Jersey":-2011,
}

BLS_UNEMPLOYMENT_2024 = {
    "Alabama":3.1,"Alaska":4.6,"Arizona":3.6,"Arkansas":3.5,"California":5.3,
    "Colorado":4.3,"Connecticut":3.2,"Delaware":3.7,"District of Columbia":5.2,
    "Florida":3.4,"Georgia":3.5,"Hawaii":3.0,"Idaho":3.7,"Illinois":5.0,
    "Indiana":4.2,"Iowa":3.0,"Kansas":3.6,"Kentucky":5.1,"Louisiana":4.4,
    "Maine":3.1,"Maryland":3.0,"Massachusetts":4.0,"Michigan":4.7,
    "Minnesota":3.0,"Mississippi":3.2,"Missouri":3.7,"Montana":3.0,
    "Nebraska":2.8,"Nevada":5.6,"New Hampshire":2.6,"New Jersey":4.5,
    "New Mexico":4.1,"New York":4.3,"North Carolina":3.6,"North Dakota":2.4,
    "Ohio":4.3,"Oklahoma":3.3,"Oregon":4.2,"Pennsylvania":3.6,
    "Rhode Island":4.3,"South Carolina":4.1,"South Dakota":1.8,"Tennessee":3.4,
    "Texas":4.1,"Utah":3.2,"Vermont":2.3,"Virginia":2.9,"Washington":4.5,
    "West Virginia":4.1,"Wisconsin":3.0,"Wyoming":3.2,
}


@dataclass
class StateRow:
    name: str
    side: str
    population: int
    gdp_m: float
    real_gdp_2019_m: float
    real_gdp_2024_m: float
    rpp: float
    median_income: int
    poverty: float
    migration: int
    unemployment: float | None
    tax_burden: float | None

    @property
    def gdp_pc(self) -> float:
        return self.gdp_m * 1_000_000 / self.population

    @property
    def rpp_income(self) -> float:
        return self.median_income / (self.rpp / 100)

    @property
    def growth_5y(self) -> float:
        return (self.real_gdp_2024_m / self.real_gdp_2019_m - 1) * 100


def fetch(url: str, *, data: bytes | None = None, headers: dict | None = None) -> bytes:
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": "CheatSheets data refresh (github.com/DavidVeksler/CheatSheets)",
                 **(headers or {})},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def read_zip_csv(payload: bytes, pattern: str) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        name = next(n for n in archive.namelist() if re.search(pattern, n))
        text = archive.read(name).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def load_state_geometry() -> dict[str, list[list[list[tuple[float, float]]]]]:
    """Load official 2024 Census state boundaries from the 1:20m KML."""
    payload = fetch(CENSUS_STATE_KML)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        name = next(item for item in archive.namelist() if item.endswith(".kml"))
        root = ET.fromstring(archive.read(name))

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    geometry: dict[str, list[list[list[tuple[float, float]]]]] = {}
    for placemark in root.findall(".//kml:Placemark", ns):
        fields = {
            item.attrib.get("name"): (item.text or "").strip()
            for item in placemark.findall(".//kml:SimpleData", ns)
        }
        state_name = fields.get("NAME")
        if state_name not in STATE_FIPS or state_name == "District of Columbia":
            continue
        polygons: list[list[list[tuple[float, float]]]] = []
        for polygon in placemark.findall(".//kml:Polygon", ns):
            rings: list[list[tuple[float, float]]] = []
            for boundary_name in ("outerBoundaryIs", "innerBoundaryIs"):
                for coordinates in polygon.findall(
                    f"kml:{boundary_name}/kml:LinearRing/kml:coordinates", ns
                ):
                    ring = []
                    for point in (coordinates.text or "").split():
                        lon, lat, *_ = point.split(",")
                        longitude = float(lon)
                        if state_name == "Alaska" and longitude > 0:
                            longitude -= 360
                        ring.append((longitude, float(lat)))
                    if ring:
                        rings.append(ring)
            if rings:
                polygons.append(rings)
        if polygons:
            geometry[state_name] = polygons

    missing = sorted((set(STATE_FIPS) - {"District of Columbia"}) - set(geometry))
    if missing:
        raise RuntimeError(f"Census state geometry missing: {', '.join(missing)}")
    return geometry


def state_map_svg(states: list[StateRow]) -> str:
    """Project Census state geometry into a responsive SVG with AK/HI insets."""
    geometry = load_state_geometry()

    phi1, phi2, phi0 = map(math.radians, (29.5, 45.5, 23.0))
    lambda0 = math.radians(-96)
    n = (math.sin(phi1) + math.sin(phi2)) / 2
    c = math.cos(phi1) ** 2 + 2 * n * math.sin(phi1)
    rho0 = math.sqrt(c - 2 * n * math.sin(phi0)) / n

    def albers(point: tuple[float, float]) -> tuple[float, float]:
        lon, lat = map(math.radians, point)
        rho = math.sqrt(c - 2 * n * math.sin(lat)) / n
        theta = n * (lon - lambda0)
        return rho * math.sin(theta), -(rho0 - rho * math.cos(theta))

    def inset(point: tuple[float, float]) -> tuple[float, float]:
        return point[0], -point[1]

    def points_for(names: set[str], projector) -> list[tuple[float, float]]:
        return [
            projector(point)
            for name in names
            for polygon in geometry[name]
            for ring in polygon
            for point in ring
        ]

    def fit(points: list[tuple[float, float]], box: tuple[float, float, float, float]):
        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)
        left, top, width, height = box
        scale = min(width / (max_x - min_x), height / (max_y - min_y))
        dx = left + (width - (max_x - min_x) * scale) / 2 - min_x * scale
        dy = top + (height - (max_y - min_y) * scale) / 2 - min_y * scale
        return lambda point: (point[0] * scale + dx, point[1] * scale + dy)

    lower_names = set(geometry) - {"Alaska", "Hawaii"}
    lower_fit = fit(points_for(lower_names, albers), (20, 14, 935, 472))
    alaska_fit = fit(points_for({"Alaska"}, inset), (20, 458, 250, 136))
    hawaii_fit = fit(points_for({"Hawaii"}, inset), (294, 510, 184, 84))

    def project(name: str, point: tuple[float, float]) -> tuple[float, float]:
        if name == "Alaska":
            return alaska_fit(inset(point))
        if name == "Hawaii":
            return hawaii_fit(inset(point))
        return lower_fit(albers(point))

    side = {row.name: ("trump" if row.side == "Red" else "harris") for row in states}
    paths = []
    for name in sorted(geometry):
        commands = []
        for polygon in geometry[name]:
            for ring in polygon:
                projected = [project(name, point) for point in ring]
                commands.append(
                    "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in projected) + "Z"
                )
        label = html.escape(name, quote=True)
        paths.append(
            f'<path class="state-shape side-{side[name]}" data-state="{label}" '
            f'role="button" tabindex="0" aria-label="{label}" d="{"".join(commands)}">'
            f'<title>{label}</title></path>'
        )
    return "".join(paths)


def number(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    cleaned = str(value).replace(",", "").replace("%", "").strip()
    if cleaned in {"", "(NA)", "N/A", "nan", "—"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def load_unemployment() -> dict[str, float]:
    # BLS blocks some automated retrieval even when its public API is used.
    # These values are the agency's final 2024 annual averages (release
    # 2025-03-05), kept here so a refresh fails deterministically rather than
    # silently replacing annual values with monthly rates.
    return dict(BLS_UNEMPLOYMENT_2024)


def load_tax_burden() -> dict[str, float]:
    try:
        source = fetch(TAX_BURDEN).decode("utf-8", errors="replace")
        match = re.search(
            r"<caption>Table 2\. State-Local Tax Burdens.*?</table>",
            source, flags=re.DOTALL | re.IGNORECASE,
        )
        if not match:
            raise ValueError("Table 2 not found")
        result = {}
        for raw_row in re.findall(r"<tr>(.*?)</tr>", match.group(0), flags=re.DOTALL | re.IGNORECASE):
            cells = [
                html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
                for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", raw_row, flags=re.DOTALL | re.IGNORECASE)
            ]
            if len(cells) >= 2 and cells[0] in STATE_FIPS:
                result[cells[0]] = float(cells[1].replace("%", ""))
        return result
    except Exception as error:  # fail visibly in the generated source note
        print(f"warning: Tax Foundation table unavailable: {error}")
        return {}


def load_states() -> list[StateRow]:
    gdp_rows = read_zip_csv(fetch(BEA_GDP_ZIP), r"SAGDP1__ALL_AREAS_1997_2025\.csv$")
    rpp_rows = read_zip_csv(fetch(BEA_RPP_ZIP), r"SARPP_STATE_2008_2024\.csv$")
    gdp: dict[str, dict[str, float]] = {}
    for row in gdp_rows:
        state = (row.get("GeoName") or "").strip()
        if state not in STATE_FIPS:
            continue
        line = row.get("LineCode")
        gdp.setdefault(state, {})
        if line == "1":
            gdp[state]["real2019"] = float(row["2019"])
            gdp[state]["real2024"] = float(row["2024"])
        elif line == "3":
            gdp[state]["current2024"] = float(row["2024"])

    rpp = {
        (row.get("GeoName") or "").strip(): float(row["2024"])
        for row in rpp_rows
        if (row.get("GeoName") or "").strip() in STATE_FIPS
    }

    def ranking_values(url: str) -> dict[str, float]:
        frame = pd.read_excel(io.BytesIO(fetch(url)), header=None)
        return {
            str(row.iloc[1]).strip(): float(row.iloc[2])
            for _, row in frame.iloc[9:].iterrows()
            if str(row.iloc[1]).strip() in STATE_FIPS
        }

    median_income = ranking_values(CENSUS_MEDIAN_INCOME)
    poverty = ranking_values(CENSUS_POVERTY)

    population_df = pd.read_excel(io.BytesIO(fetch(CENSUS_POPULATION)), header=3)
    population = {}
    for _, row in population_df.iterrows():
        state = str(row.iloc[0]).strip().lstrip(".")
        if state in STATE_FIPS:
            population[state] = int(row.iloc[-1])

    migration_df = pd.read_excel(io.BytesIO(fetch(CENSUS_MIGRATION)), header=4)
    migration = {}
    for _, row in migration_df.iterrows():
        state = str(row.iloc[0]).strip().lstrip(".")
        if state in STATE_FIPS:
            migration[state] = int(row.iloc[7])

    unemployment = load_unemployment()
    taxes = load_tax_burden()
    rows = []
    for state in STATE_FIPS:
        rows.append(StateRow(
            name=state,
            side="Red" if state in RED_STATES else "Blue",
            population=population[state],
            gdp_m=gdp[state]["current2024"],
            real_gdp_2019_m=gdp[state]["real2019"],
            real_gdp_2024_m=gdp[state]["real2024"],
            rpp=rpp[state],
            median_income=int(median_income[state]),
            poverty=poverty[state],
            migration=migration.get(state, 0),
            unemployment=unemployment.get(state),
            tax_burden=taxes.get(state),
        ))
    return rows


def load_countries() -> list[dict]:
    gdp_raw = json.loads(fetch(WORLD_BANK_GDP))[1]
    pop_raw = json.loads(fetch(WORLD_BANK_POP))[1]
    ppp_raw = json.loads(fetch(WORLD_BANK_PPP_PC))[1]
    metadata = json.loads(fetch(WORLD_BANK_COUNTRIES))[1]
    nonsovereign_codes = {
        "ABW", "ASM", "BMU", "CYM", "CHI", "CUW", "FRO", "GIB", "GRL",
        "GUM", "HKG", "IMN", "MAC", "MAF", "MNP", "NCL", "PRI", "PYF",
        "SXM", "TCA", "VGB", "VIR",
    }
    sovereign_codes = {
        row["id"] for row in metadata
        if row.get("region", {}).get("id") not in {"", "NA"}
        and row["id"] not in nonsovereign_codes
    }
    populations = {row["countryiso3code"]: row["value"] for row in pop_raw if row.get("value")}
    ppp = {row["countryiso3code"]: row["value"] for row in ppp_raw if row.get("value")}
    countries = []
    for row in gdp_raw:
        iso3 = row.get("countryiso3code")
        if not row.get("value") or not populations.get(iso3) or not row.get("country", {}).get("id"):
            continue
        # World Bank aggregates have an empty region in the country metadata endpoint,
        # but the indicator feed does not expose that flag. Keep plausible sovereign
        # economies and explicitly exclude the common aggregate codes.
        if iso3 not in sovereign_codes:
            continue
        countries.append({
            "name": row["country"]["value"],
            "iso3": iso3,
            "gdp": float(row["value"]),
            "population": int(populations[iso3]),
            "ppp_pc": float(ppp[iso3]) if ppp.get(iso3) else None,
        })
    return countries


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def money(value: float, *, compact: bool = False) -> str:
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    if compact:
        if magnitude >= 1_000_000_000_000:
            return f"{sign}${magnitude / 1_000_000_000_000:.2f}T"
        if magnitude >= 1_000_000_000:
            return f"{sign}${magnitude / 1_000_000_000:.1f}B"
        if magnitude >= 1_000_000:
            return f"{sign}${magnitude / 1_000_000:.1f}M"
    return f"{sign}${magnitude:,.0f}"


def table(headers: list[str], rows: list[list[object]], *, cls: str = "") -> str:
    head = "".join(f"<th scope=\"col\">{h}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(
            f"<{('th scope=\"row\"' if i == 0 else 'td')}>{cell}</{('th' if i == 0 else 'td')}>"
            for i, cell in enumerate(row)
        ) + "</tr>"
        for row in rows
    )
    return f'<div class="table-wrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


COMMON_CSS = r"""
@layer reset, base, components;
@layer reset{*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0}button,a,summary{font:inherit}}
@layer base{
:root{color-scheme:light dark;--paper:light-dark(#f4efe4,#111821);--panel:light-dark(#fffaf0,#18222e);--ink:light-dark(#1d2730,#e9eef2);--muted:light-dark(#59636b,#aeb9c2);--line:light-dark(#b9ad96,#3a4857);--accent:light-dark(#812f35,#e6a15c);--accent2:light-dark(#244e6a,#79b6d2);--shadow:0 12px 30px #0002;--radius:12px}
html[data-theme="light"]{color-scheme:light}html[data-theme="dark"]{color-scheme:dark}
body{background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;text-wrap:pretty}
a{color:var(--accent2);text-underline-offset:.18em}a:hover{text-decoration-thickness:2px}a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:4px;border-radius:3px}
.shell{width:min(1480px,calc(100% - 28px));margin:auto}.hero{padding:52px 0 28px;border-bottom:1px solid var(--line)}.hero .shell{position:relative}
.theme-toggle{display:none}.js .theme-toggle{display:inline-flex;align-items:center;gap:7px;position:absolute;right:0;top:0;border:1px solid var(--line);border-radius:999px;background:var(--panel);color:var(--ink);padding:7px 11px;cursor:pointer}.theme-toggle:hover{border-color:var(--accent)}
.eyebrow{font:700 .78rem/1.2 ui-monospace,Consolas,monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
h1,h2,h3{font-family:Georgia,"Times New Roman",serif;line-height:1.08;text-wrap:balance}h1{font-size:clamp(2.2rem,7vw,5.4rem);margin:.18em 0}.lede{font-size:clamp(1rem,2vw,1.25rem);max-width:78ch;color:var(--muted)}
.hero-meta,.legend{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}.pill{border:1px solid var(--line);border-radius:999px;padding:6px 10px;background:var(--panel);font-size:.86rem}.pill strong{color:var(--accent)}
main{padding:26px 0 60px}section{margin:42px 0}h2{font-size:clamp(1.75rem,4vw,3rem);margin:0 0 10px}.section-note{color:var(--muted);max-width:92ch;margin:0 0 18px}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:14px}.card,details{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}.card{padding:18px}.card h3{margin:.1em 0 .5em}.card p:last-child{margin-bottom:0}
details{margin:10px 0;overflow:hidden}summary{cursor:pointer;padding:16px 18px;font-weight:750;list-style-position:inside}details[open] summary{border-bottom:1px solid var(--line);color:var(--accent)}.detail-body{padding:4px 18px 18px}.detail-body li{margin:.55em 0}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--panel);box-shadow:var(--shadow)}table{border-collapse:separate;border-spacing:0;width:100%;min-width:760px;font-size:.9rem}th,td{padding:11px 12px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);vertical-align:top}thead th{position:sticky;top:0;z-index:2;background:var(--ink);color:var(--paper);text-align:left}tbody th{background:color-mix(in srgb,var(--panel) 80%,var(--accent) 20%);min-width:160px;text-align:left}tr:last-child>*{border-bottom:0}tr>*:last-child{border-right:0}tbody tr:hover>*{background:color-mix(in srgb,var(--panel) 85%,var(--accent2) 15%)}
.callout{border-left:5px solid var(--accent);background:var(--panel);padding:16px 18px;margin:18px 0;border-radius:0 var(--radius) var(--radius) 0}.callout strong{color:var(--accent)}
.sources{font-size:.92rem}.sources li{margin:.6em 0}.related{display:flex;gap:10px;flex-wrap:wrap}.related a{border:1px solid var(--line);background:var(--panel);padding:8px 11px;border-radius:8px;text-decoration:none}
footer{border-top:1px solid var(--line);padding:24px 0 44px;color:var(--muted);font-size:.9rem}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
}
@media(max-width:600px){.shell{width:min(100% - 18px,1480px)}.hero{padding-top:72px}.hero-meta{gap:6px}.pill{font-size:.76rem}section{margin:32px 0}th,td{padding:9px;font-size:.82rem}.card{padding:14px}}
@media(prefers-reduced-motion:no-preference){@layer base{a,.card,tbody tr>*{transition:color .16s,background .16s,transform .16s}.card:hover{transform:translateY(-2px)}}}
@media print{*{box-shadow:none!important}body{background:#fff;color:#111;font-size:9pt}.shell{width:100%}.hero{padding:0 0 12pt}h1{font-size:28pt}section{break-inside:auto;margin:16pt 0}.table-wrap{overflow:visible;border:1px solid #555}table{min-width:0;font-size:6.5pt}th,td{padding:4pt}.no-print{display:none!important}a{color:#111;text-decoration:none}a[href^="http"]::after{content:" (" attr(href) ")";font-size:6pt}.page-break{break-before:page}}
"""


def document(*, title: str, description: str, keywords: str, filename: str,
             h1: str, eyebrow: str, lede: str, theme_css: str, content: str,
             image_alt: str, sources: str, related: list[tuple[str, str]]) -> str:
    canonical = f"https://cheatsheets.davidveksler.com/{filename}"
    image = f"images/{filename.removesuffix('.html')}.png"
    related_html = "".join(f'<a href="{esc(url)}">{esc(label)}</a>' for label, url in related)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="keywords" content="{esc(keywords)}"><link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{image}"><meta property="og:image:alt" content="{esc(image_alt)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{image}"><meta name="twitter:creator" content="@heroiclife">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"TechArticle","headline":title,"description":description,"author":{"@type":"Person","name":"David Veksler (AI Generated)"},"publisher":{"@type":"Organization","name":"David Veksler Cheatsheets"},"datePublished":VERIFIED,"dateModified":VERIFIED,"keywords":keywords})}</script>
<style>{COMMON_CSS}\n{theme_css}</style></head>
<body><header class="hero"><div class="shell"><button class="theme-toggle no-print" type="button" aria-pressed="false"><span aria-hidden="true">◐</span><span>Dark theme</span></button><div class="eyebrow">{esc(eyebrow)}</div><h1>{esc(h1)}</h1><p class="lede">{lede}</p><div class="hero-meta"><span class="pill"><strong>Last verified</strong> {VERIFIED}</span><span class="pill">Standalone · print-ready · works without JavaScript</span></div></div></header>
<main class="shell">{content}
<section aria-labelledby="sources"><h2 id="sources">Sources &amp; method</h2><div class="sources">{sources}</div></section>
<section aria-labelledby="related"><h2 id="related">Related sheets</h2><div class="related" data-seo-related-links aria-label="Related Economics and Politics cheatsheets">{related_html}</div></section></main>
<footer><div class="shell"><p><strong>Last verified: {VERIFIED}.</strong> Volatile figures are labeled with their data year. Definitions classify institutions and policies, not entire populations.</p><p>One person + AI agents build and maintain this collection through public specs, QA gates, and git history. <a href="how-its-built.html">How this site is built</a> · <a href="https://github.com/DavidVeksler/CheatSheets">Source on GitHub</a></p></div></footer>
<script>(()=>{{const root=document.documentElement;root.classList.add("js");const button=document.querySelector(".theme-toggle");const media=matchMedia("(prefers-color-scheme: dark)");let saved=null;try{{saved=localStorage.getItem("cheatsheets-theme")}}catch{{}}if(saved==="light"||saved==="dark")root.dataset.theme=saved;const render=()=>{{const dark=(root.dataset.theme|| (media.matches?"dark":"light"))==="dark";button.setAttribute("aria-pressed",String(dark));button.lastElementChild.textContent=dark?"Light theme":"Dark theme"}};button.addEventListener("click",()=>{{root.dataset.theme=(root.dataset.theme|| (media.matches?"dark":"light"))==="dark"?"light":"dark";try{{localStorage.setItem("cheatsheets-theme",root.dataset.theme)}}catch{{}}render()}});render()}})();</script></body></html>'''


def build_economic_systems() -> str:
    systems = [
        "Mercantilism", "Free-market capitalism", "Social democracy",
        "State socialism", "State capitalism", "Corporatist economics",
    ]
    matrix = [
        ["Purpose", "Increase state power through a trade surplus and strategic reserves", "Coordinate voluntary exchange through private property and profit/loss", "Combine private markets with social insurance and bargaining institutions", "Execute a political production plan and replace capital markets", "Use markets while the state controls strategic capital and national objectives", "Organize private owners and labor into state-supervised sectors"],
        ["Capital ownership", "Crown-chartered or politically privileged merchants; farms and shops remain private", "Private individuals, partnerships, cooperatives, and firms", "Mostly private firms; public ownership concentrated in selected services", "State owns or directs major productive assets; private capital is marginal or prohibited", "Mixed, but state firms and state-guided finance dominate strategic sectors", "Nominally private, conditional on political direction and cartel membership"],
        ["Price formation", "Markets inside licenses, tariffs, quotas, and monopolies", "Competitive bids and offers; bankruptcy reallocates failed capital", "Market prices plus taxes, benefits, wage bargaining, and regulated services", "Administrative prices and physical quotas allocated through ministries", "Market prices for much consumer activity; administrative credit and industrial targets steer investment", "Market exchange inside state-approved cartels, wage rules, and procurement plans"],
        ["Trade posture", "Exports praised; imports restricted unless they supply strategic inputs", "Unilateral or negotiated openness; imports are gains to consumers and inputs to producers", "Generally open trade with adjustment assistance and product regulation", "State foreign-trade monopoly; imports allocated by plan", "Export-led strategy, managed technology access, and selective protection", "Bilateral clearing, autarky goals, exchange controls, and strategic imports"],
        ["State role", "Grant monopolies, police shipping routes, accumulate fiscal and military capacity", "Define property and contract rules, adjudicate disputes, and supply limited public goods", "Regulate markets, tax broadly, insure income and health risks, provide services", "Own firms, set output targets, allocate labor/capital, and ration shortages", "Own commanding firms, direct banks, set plans, and permit bounded private enterprise", "Choose sector bodies, suppress independent unions, set production priorities"],
        ["Meaning of wealth", "Bullion, a favorable trade balance, taxable commerce, and naval capacity", "Value people place on goods and services; productive capital raises future output", "Market output plus security, health, and broadly shared consumption", "Physical output targets and collectively controlled productive capacity", "National productive capability, technological autonomy, and state balance-sheet strength", "Mobilization capacity, employment discipline, and national self-sufficiency"],
        ["Money and credit", "Specie reserves and chartered banks support state trade and war", "Competitive capital markets; monetary regime varies by school", "Central bank stabilization plus regulated private finance", "State bank creates and allocates credit to plan targets", "State-influenced banks channel credit to priority sectors", "Centralized credit allocation and capital controls support the political plan"],
        ["Labor position", "Workers are subjects; guild, settlement, and poor-law rules limit movement", "Labor contracts in markets; unions may bargain but receive no production quota", "Independent unions and sector bargaining share productivity gains", "State is the dominant employer; independent bargaining is absent", "Private labor markets coexist with state-sector employment and political union control", "Independent unions abolished or absorbed into state corporations"],
        ["Canonical case", "England, Navigation Acts 1651/1660 through the 18th century", "Hong Kong after 1961 or post-1948 West German market reforms", "Sweden's postwar model, especially 1950s–1980s", "USSR from the first Five-Year Plan in 1928 to dissolution in 1991", "China after the 1978 reforms, especially the 2000s–2020s", "Fascist Italy after the 1927 Labour Charter; Nazi Germany after the 1936 Four Year Plan"],
        ["Thinker / text", "Thomas Mun, <cite>England's Treasure by Forraign Trade</cite> (published 1664)", "Adam Smith, <cite>Wealth of Nations</cite> (1776), Book IV", "T. H. Marshall, <cite>Citizenship and Social Class</cite> (1950); Nordic labor institutions", "Karl Marx, <cite>Capital</cite> vol. I (1867); Lenin's state implementation", "No single canon: reform directives, five-year plans, and state-ownership law", "Giuseppe Bottai's 1927 Labour Charter; state corporatist doctrine"],
        ["Measured record", "Expanded protected shipping and customs revenue, but raised consumer/input prices and invited retaliation", "West Germany coupled June 1948 currency reform with price liberalization; output and exchange recovered rapidly", "High living standards with private production, high taxes, and universal social insurance", "Rapid heavy-industrial buildup alongside chronic shortage, coercive collectivization, and the 1932–33 famine", "Large post-1978 output gains alongside preferential finance for state firms and investment-heavy growth", "Rearmament reduced measured unemployment while controls, repression, and war made the system fiscally and humanly catastrophic"],
        ["Characteristic failure", "Rent-seeking coalitions turn national power into producer privilege", "Externalities, market power, fraud, and underprovided public goods when institutions fail", "High marginal wedges, benefit lock-in, and political difficulty reforming universal promises", "Calculation failure: quotas cannot reproduce the information carried by changing prices", "Soft budget constraints, politically directed overinvestment, and unequal access to credit", "Political loyalty replaces competition; nominal private ownership offers no protection from command"],
    ]
    master = table(["Criterion", *systems], matrix, cls="master-matrix")

    cards = [
        ("Mercantilism", "State-power trade strategy", [
            "Definition: a policy system that treats trade as an instrument of state power, using monopoly grants, navigation rules, tariffs, and export promotion.",
            "Canonical implementation: England's Navigation Acts of 1651 and 1660 reserved much imperial carriage to English ships and merchants.",
            "Policy examples: chartered trading companies, colonial raw-material rules, customs walls, and bounties for selected exports.",
            "Text: Thomas Mun's <cite>England's Treasure by Forraign Trade</cite>, published posthumously in 1664.",
            "Critique: Adam Smith's 1776 Book IV argued that consumption, not producer privilege or bullion, is the end of production.",
            "Often confused with protectionism. Protection is one tool; mercantilism is the larger state-power and trade-surplus logic.",
        ]),
        ("Free-market capitalism", "Private capital under general rules", [
            "Definition: productive assets are privately controlled and decentralized prices coordinate investment and exchange.",
            "Canonical reform: West Germany's June 1948 currency reform was paired with relaxation of price controls; the 1957 competition law constrained cartels.",
            "Mechanism: profit rewards serving willing buyers; loss and bankruptcy withdraw capital from failed uses.",
            "Texts: Smith's <cite>Wealth of Nations</cite> (1776), Mises's <cite>Human Action</cite> (1949), and Hayek's price-system essays.",
            "Measured record: market reform coincided with a fast postwar recovery, but Marshall aid, reconstruction, and catch-up growth are real co-causes.",
            "Often confused with corporatism. Subsidies, licensing monopolies, and bailouts socialize risk while leaving titles private.",
        ]),
        ("Social democracy", "Private markets plus universal insurance", [
            "Definition: a democratic program that retains market production while using taxes, transfers, labor bargaining, and public services to distribute risk and income.",
            "Canonical case: postwar Sweden combined private exporters, centralized bargaining, universal benefits, and high broad-based taxation.",
            "Policies: public health and education, earnings-related pensions, unemployment insurance, and coordinated wage bargaining.",
            "Intellectual roots: reformist socialism and social citizenship, including T. H. Marshall's 1950 formulation.",
            "Measured record: Nordic countries achieved high income and broad insurance, then repeatedly adjusted taxes, pensions, and regulation as costs changed.",
            "Often confused with state socialism. Redistribution changes disposable income; it does not by itself nationalize production.",
        ]),
        ("State socialism", "Production by administrative plan", [
            "Definition: the state owns or commands major productive assets and substitutes administrative allocation for capital markets.",
            "Canonical case: the USSR launched its first Five-Year Plan in 1928 and forced agricultural collectivization from 1929.",
            "Policies: Gosplan physical targets, state foreign-trade monopoly, administered prices, and soft budget constraints for state enterprises.",
            "Texts: Marx's <cite>Capital</cite> (1867) did not supply a detailed planning manual; Lenin and later Soviet institutions supplied the governing form.",
            "Measured record: heavy industry expanded, but consumer shortage, coercion, famine, and unreliable official valuations complicate headline growth.",
            "Often confused with any welfare state. A public pension does not determine who owns steel mills or allocates investment.",
        ]),
        ("State capitalism", "Markets inside state strategic control", [
            "Definition: profit-seeking firms and markets operate, while the state owns strategic firms or channels finance toward national plans.",
            "Canonical case: China after the 1978 reform opening, with private enterprise expanding beside state firms and state-directed banks.",
            "Policies: state shareholding, industrial plans, preferential credit, local-government investment, and bounded foreign participation.",
            "Institutional fact: the IMF's 2024 Article IV counted 97 central SOEs under SASAC plus central financial and ministry-controlled firms as of 2023.",
            "Measured record: immense output and poverty reduction, paired with investment imbalance, property risk, and an SOE productivity gap noted by the IMF.",
            "Often confused with command planning. Most consumer prices can be market prices even while the investment system is politically steered.",
        ]),
        ("Corporatist economics", "Private title, political command", [
            "Definition: the state organizes employers and labor into compulsory sector bodies and subordinates property rights to political goals.",
            "Canonical cases: Fascist Italy's 1927 Labour Charter and Nazi Germany's Four Year Plan beginning in 1936.",
            "Policies: cartelization, wage controls, procurement direction, exchange controls, union suppression, and autarky drives.",
            "Doctrine: class conflict is declared resolved through state-supervised corporations representing occupations and industries.",
            "Measured record: mobilization and rearmament can raise output statistics while destroying consumer choice, fiscal durability, liberty, and life.",
            "Often confused with laissez-faire because legal titles remain private. The operational question is who decides, not whose name is on the deed.",
        ]),
    ]
    details = "".join(
        f'<details><summary>{name} · <span>{tag}</span></summary><div class="detail-body"><ul>{"".join(f"<li>{item}</li>" for item in items)}</ul></div></details>'
        for name, tag, items in cards
    )

    head_to_head = table(
        ["Question", "Mercantilism", "Capitalism"],
        [
            ["What creates gain?", "Capturing scarce trade, bullion, and strategic advantage from rival states", "Specialization and voluntary exchange can make both sides better off"],
            ["What is protected?", "Domestic producers, shipping, and the fiscal-military state", "General property/contract rules and the consumer's freedom to switch"],
            ["How are imports treated?", "A leakage unless needed for export production or security", "Goods received: the reason exports are worthwhile"],
            ["Where does capital go?", "Toward chartered, subsidized, or politically selected activity", "Toward expected risk-adjusted returns, corrected by profit and loss"],
            ["Core metric", "Trade balance, reserves, shipping share, strategic capacity", "Productivity, real consumption, return on capital, and consumer surplus"],
        ],
    )
    today = table(
        ["Modern policy (as of Aug 2026)", "Mercantilist ancestor", "Named example", "Precise classification"],
        [
            ["Strategic manufacturing subsidy", "Bounties for favored exports", "U.S. CHIPS and Science Act (2022) semiconductor incentives", "Mercantilist instrument inside a market economy"],
            ["Local-content production credit", "Navigation/local-carriage rules", "U.S. Inflation Reduction Act (2022) domestic-content conditions", "Industrial policy with mercantilist design"],
            ["Retaliatory tariff", "Customs wall", "U.S. Section 301 tariffs on Chinese goods, begun 2018 and modified thereafter", "Direct protection; motive determines whether it is strategic mercantilism"],
            ["Technology export control", "Ban strategic machinery to rivals", "U.S. advanced-computing and semiconductor controls begun October 2022", "Security control with mercantilist effect"],
            ["Production self-sufficiency target", "Autarky for war-critical goods", "EU Net-Zero Industry Act entered into force June 2024", "Rules-based industrial policy, not a whole mercantilist system"],
            ["National manufacturing plan", "State-selected strategic trades", "China's Made in China 2025 program announced in 2015", "State-capitalist and mercantilist elements overlap"],
            ["Managed currency / reserves", "Accumulate specie and improve export position", "Central banks hold reserves for stability; deliberate undervaluation is the mercantilist case", "Do not label every reserve policy mercantilist"],
            ["Government procurement preference", "Crown buys domestic ships and arms", "Buy American rules across federal procurement", "A durable mercantilist-style preference"],
        ],
    )
    classify = table(
        ["Economy", "Ownership", "Prices / trade", "State direction", "Verdict"],
        [
            ["England, 1670s", "Private farms and merchants; charter monopolies", "Market exchange behind Navigation Acts and customs barriers", "Crown privileges strategic traders and shipping", "Mercantilist commercial economy"],
            ["United States, 1920s", "Predominantly private", "Market prices; high 1922 and 1930 tariff walls", "Limited planning, strong protection", "Capitalism with protectionist policy"],
            ["USSR, 1955", "State ownership dominates", "Administered prices and state foreign trade", "Gosplan sets physical targets", "State-socialist command economy"],
            ["West Germany, 1955", "Private firms", "Market prices and growing trade openness", "Social insurance plus competition rules", "Social-market capitalism"],
            ["Sweden, 1985", "Production mostly private", "Open market prices", "High taxes, universal benefits, centralized bargaining", "Social democracy / welfare capitalism"],
            ["Chile, 1985", "Privatization expanding", "Market pricing and trade liberalization", "Authoritarian state with market program", "Market capitalism under dictatorship, not political liberalism"],
            ["China, 2025", "Private firms plus large state sector", "Most consumer prices market; trade and capital tightly managed", "Plans, SOEs, and banks steer strategic investment", "State capitalism with mercantilist tools"],
            ["United States, 2025", "Predominantly private", "Market prices; selective tariffs, subsidies, and export controls", "Regulation and fiscal policy shape sectors", "Mixed-market capitalism with industrial policy"],
            ["Norway, 2025", "Private economy plus state oil and sovereign wealth ownership", "Open trade and market pricing", "Public balance sheet funds universal welfare", "Social democracy with strategic state ownership"],
            ["North Korea, 2025", "State ownership dominates; tolerated informal markets", "Administrative allocation plus black/gray markets", "Party-state plan and rationing", "Command economy with survival markets"],
        ],
    )
    mistakes = "".join(f'<div class="card"><h3>{title}</h3><p>{text}</p></div>' for title, text in [
        ("Capitalism is not corporatism", "Private title is insufficient. If political allocation decides entry, credit, wages, and output, the operating system is corporatist or state-capitalist."),
        ("Socialism is not a welfare check", "Ask who owns and allocates productive capital. Tax-financed benefits in a private economy redistribute market income; they do not abolish the capital market."),
        ("Mercantilism is not merely old", "Tariffs, local-content rules, strategic subsidies, and export controls reproduce its tools. Classify the policy, not the century."),
        ("Command economies can report growth", "Forced saving can move labor and materials into heavy industry quickly. Official prices, missing quality, shortage, coercion, and foregone consumption make the headline incomplete."),
        ("Mixed economy is a coordinate", "It says institutions are combined, not which ones. Name the ownership, pricing, trade, welfare, and credit rules separately."),
        ("Trade deficits are not a score", "A deficit can accompany capital inflow and rising consumption; a surplus can reflect weak domestic demand. The balance alone does not measure living standards."),
    ])

    content = f'''
<section class="matrix-section" aria-labelledby="quick"><div class="stamp">QUICK REFERENCE · 6 SYSTEMS × 12 TESTS</div><h2 id="quick">The master matrix</h2><p class="section-note">Read down a column for a system; read across a row to settle a comparison. Hover a row to hold your place. No real economy occupies a pure column.</p>{master}</section>
<section aria-labelledby="difference"><h2 id="difference">What's the difference between mercantilism and capitalism?</h2><div class="callout"><strong>Short answer:</strong> Mercantilism asks how commerce can strengthen the state against rival states; capitalism asks how private owners and customers can coordinate production through prices and profit/loss. Mercantilism treats imports as a potential national loss and producer privilege as strategy. Capitalism treats imports as goods received and competition, including foreign competition, as a discipline on producers.</div>{head_to_head}</section>
<section aria-labelledby="deep"><h2 id="deep">Six systems at working depth</h2><p class="section-note">Each card gives a usable definition, an implementation, named policies, a text, an outcome, and the confusion to avoid.</p>{details}</section>
<section class="page-break" aria-labelledby="today"><h2 id="today">Is mercantilism still practiced today?</h2><p class="section-note">Yes, as a policy logic. Calling one tariff mercantilist does not make the entire economy mercantilist; the label fits when trade and industrial policy are used to accumulate national capacity or advantage.</p>{today}</section>
<section aria-labelledby="classify"><h2 id="classify">Classify a real economy</h2><p class="section-note">Use ownership, price formation, trade, and credit direction. The final column gives a defensible classification instead of “it's complicated.”</p>{classify}</section>
<section aria-labelledby="mistakes"><h2 id="mistakes">Common mistakes and anti-patterns</h2><div class="card-grid">{mistakes}</div></section>'''
    theme = r'''
@layer base{:root{--accent:light-dark(#7b2630,#e2a55f);--accent2:light-dark(#1e4d6b,#79b7d4)}body{background-image:linear-gradient(90deg,transparent 97%,color-mix(in srgb,var(--line) 30%,transparent) 97%),linear-gradient(color-mix(in srgb,var(--line) 12%,transparent) 1px,transparent 1px);background-size:100% 100%,100% 28px}.hero{background:linear-gradient(135deg,color-mix(in srgb,var(--paper) 87%,var(--accent) 13%),var(--paper))}.stamp{display:inline-block;border:2px solid var(--accent);color:var(--accent);padding:5px 8px;transform:rotate(-.5deg);font:800 .75rem ui-monospace,Consolas,monospace;letter-spacing:.08em;margin-bottom:12px}.master-matrix thead th:not(:first-child){min-width:190px;border-top:7px solid var(--accent)}.master-matrix tbody th{font-family:Georgia,serif}.matrix-section .table-wrap{border-width:2px}}
'''
    sources = '''<ol>
<li><a href="https://oll.libertyfund.org/titles/smith-an-inquiry-into-the-nature-and-causes-of-the-wealth-of-nations-cannan-ed-vol-2">Adam Smith, <cite>Wealth of Nations</cite>, vol. II, Book IV (1776)</a> for the mercantile-system critique.</li>
<li><a href="https://www.britannica.com/topic/Navigation-Acts">UK Navigation Acts record</a> and the act dates; <a href="https://history.state.gov/milestones/1945-1952/marshall-plan">U.S. Office of the Historian</a> for the 1948 European recovery context.</li>
<li><a href="https://www.imf.org/en/Publications/CR/Issues/2024/08/02/Peoples-Republic-of-China-2024-Article-IV-Consultation-Press-Release-Staff-Report-and-552174">IMF China 2024 Article IV</a> for state ownership, industrial policy, and the central-SOE count.</li>
<li><a href="https://www.riksdagen.se/en/how-the-riksdag-works/democracy/the-history-of-the-riksdag/">Swedish institutional history</a>; <a href="https://www.riksbank.se/en-gb/about-the-riksbank/history/">Riksbank history</a> for the social-democratic case context.</li>
<li><a href="https://www.congress.gov/bill/117th-congress/house-bill/4346">CHIPS and Science Act</a>, <a href="https://www.congress.gov/bill/117th-congress/house-bill/5376">Inflation Reduction Act</a>, and <a href="https://eur-lex.europa.eu/eli/reg/2024/1735/oj">EU Regulation 2024/1735</a> for current industrial-policy examples.</li>
</ol><p><strong>Method:</strong> systems are ideal types. The classification exercise applies four observable tests: productive ownership, price formation, trade posture, and allocation of credit. Historical outcome language avoids false single-cause claims.</p>'''
    return document(
        title="Mercantilism vs Capitalism vs Socialism: Economic Systems",
        description="Mercantilism, capitalism, socialism, and modern hybrids side by side: ownership, prices, trade, thinkers, policies, historical cases, outcomes, and failure modes.",
        keywords="mercantilism vs capitalism, capitalism vs socialism, economic systems comparison, state capitalism, command economy, corporatism",
        filename="economic-systems-compared.html", h1="Economic Systems, Compared",
        eyebrow="Ledger 01 · ownership, prices, trade, power",
        lede="A system is not its slogan. Test who owns productive capital, who sets prices, how trade is treated, and who allocates credit. The matrix turns six rival systems into observable criteria.",
        theme_css=theme, content=content,
        image_alt="Ledger-style comparison matrix for mercantilism, capitalism, socialism, state capitalism, and corporatism",
        sources=sources,
        related=[("Political Ideologies Compared", "political-ideologies-compared.html"), ("Capitalism", "capitalism.html"), ("Objectivism", "objectivism.html"), ("Currency Timeline", "currency-timeline.html")],
    )


def build_political_ideologies() -> str:
    translation = table(
        ["Label", "United States", "United Kingdom", "Continental Europe", "Latin America", "Academic / historical"],
        [
            ["Liberal", "Center-left: civil rights, regulated markets, social insurance; U.S. Democratic mainstream", "Often centrist or center-left; Liberal Democrats combine social liberalism and regulated markets", "Usually constitutional, pro-European, and market-friendly; may sit center-left or center-right", "Often means pro-market constitutional liberal, contrasted with socialist or conservative traditions", "A family centered on justified authority, individual liberty, rights, and legal equality"],
            ["Classical liberal", "Limited government, private property, free exchange; e.g. many Cato-style positions", "Nineteenth-century liberal lineage; some modern free-market liberals", "Ordoliberal, liberal-conservative, or economic-liberal currents depending on country", "Market-liberal reformers; the label can distinguish them from U.S.-style social liberals", "Locke, Smith, Constant, Tocqueville, and Mill, with major internal differences"],
            ["Libertarian", "Strong presumption against coercion; Libertarian Party is the named party example", "Smaller current spanning economic and civil-liberty radicalism", "Often a small classical-liberal or anarchist current; translation varies", "Can mean market anarchist, minarchist, or civil-libertarian depending on movement", "A family grounding politics in self-ownership, rights, nonaggression, or strong liberty presumptions"],
            ["Neoliberal", "Usually an external label for market-oriented technocracy, deregulation, trade, and fiscal discipline", "Often linked to Thatcher-era reform, though supporters rarely use the label consistently", "Historically includes 1930s efforts to renew liberalism; modern use often means EU-compatible market reform", "Strongly associated with 1980s–1990s stabilization, privatization, and Washington Consensus reforms", "Three usages: 1938 renewal project, a policy program, and a broad critical epithet"],
            ["Conservative", "Tradition, order, markets, national defense; the coalition includes libertarian and populist wings", "Tory tradition mixes institutions, nation, property, and pragmatic welfare-state stewardship", "Christian democracy, liberal conservatism, or national conservatism are distinct families", "May mean market reform plus social order, or older oligarchic/clerical traditions", "A disposition toward inherited institutions, not one universal economic program"],
            ["Social democrat", "Left-liberal reformer favoring unions, universal benefits, and regulated private markets", "Labour's reformist tradition, distinct from revolutionary socialism", "Major center-left family: capitalist production plus welfare state and bargaining institutions", "Democratic left combining elections, labor rights, and redistribution", "Historically revised socialism toward parliamentary reform; today usually retains mixed-market production"],
        ],
    )

    lineage_svg = r'''
<figure class="lineage" aria-labelledby="lineage-caption"><svg viewBox="0 0 1160 650" role="img" aria-labelledby="lineage-title lineage-desc">
<title id="lineage-title">Lineage of liberal political ideologies from 1689 to the present</title><desc id="lineage-desc">Classical liberal texts branch toward modern American liberalism, libertarianism, neoliberalism, social democracy, fusionist conservatism, and national conservatism.</desc>
<g class="links" fill="none"><path d="M130 95 C250 95 240 170 350 170"/><path d="M130 235 C250 235 240 170 350 170"/><path d="M130 365 C255 365 245 170 350 170"/><path d="M510 170 C600 170 590 82 690 82"/><path d="M510 170 C600 170 590 205 690 205"/><path d="M510 170 C600 170 590 328 690 328"/><path d="M510 170 C600 170 590 451 690 451"/><path d="M850 82 C930 82 920 112 1010 112"/><path d="M850 205 C930 205 920 250 1010 250"/><path d="M850 328 C930 328 920 388 1010 388"/><path d="M850 451 C930 451 920 526 1010 526"/></g>
<g class="node root"><rect x="30" y="45" width="200" height="100"/><text x="50" y="75">LOCKE · 1689</text><text x="50" y="102">Two Treatises</text><text x="50" y="126">rights + consent</text></g>
<g class="node root"><rect x="30" y="185" width="200" height="100"/><text x="50" y="215">SMITH · 1776</text><text x="50" y="242">Wealth of Nations</text><text x="50" y="266">exchange + institutions</text></g>
<g class="node root"><rect x="30" y="315" width="200" height="100"/><text x="50" y="345">MILL · 1859</text><text x="50" y="372">On Liberty</text><text x="50" y="396">harm principle</text></g>
<g class="node trunk"><rect x="330" y="120" width="200" height="100"/><text x="350" y="150">CLASSICAL LIBERAL</text><text x="350" y="177">18th–19th centuries</text><text x="350" y="201">liberty + property</text></g>
<g class="node social"><rect x="670" y="32" width="200" height="100"/><text x="690" y="62">NEW LIBERALISM</text><text x="690" y="89">Green · 1881</text><text x="690" y="113">enabling freedom</text></g>
<g class="node liberty"><rect x="670" y="155" width="200" height="100"/><text x="690" y="185">LIBERTARIAN</text><text x="690" y="212">Russell · 1955</text><text x="690" y="236">label reclaimed</text></g>
<g class="node market"><rect x="670" y="278" width="200" height="100"/><text x="690" y="308">NEOLIBERAL</text><text x="690" y="335">Paris · 1938</text><text x="690" y="359">liberal renewal</text></g>
<g class="node order"><rect x="670" y="401" width="200" height="100"/><text x="690" y="431">FUSIONISM</text><text x="690" y="458">Meyer · 1962</text><text x="690" y="482">virtue + liberty</text></g>
<g class="node social"><rect x="990" y="62" width="150" height="100"/><text x="1010" y="92">US LIBERAL</text><text x="1010" y="119">New Deal · 1933+</text><text x="1010" y="143">rights + welfare</text></g>
<g class="node liberty"><rect x="990" y="200" width="150" height="100"/><text x="1010" y="230">MINARCHIST</text><text x="1010" y="257">Nozick · 1974</text><text x="1010" y="281">rights state</text></g>
<g class="node market"><rect x="990" y="338" width="150" height="100"/><text x="1010" y="368">POLICY PROGRAM</text><text x="1010" y="395">Williamson · 1989</text><text x="1010" y="419">10 reform areas</text></g>
<g class="node order"><rect x="990" y="476" width="150" height="100"/><text x="1010" y="506">NATCON</text><text x="1010" y="533">2010s+</text><text x="1010" y="557">nation + industry</text></g>
</svg><figcaption id="lineage-caption">A family tree, not a purity test. Arrows show intellectual descent, not agreement; each branch contains rival theories.</figcaption></figure>
<ol class="lineage-list"><li><strong>1689 · Locke:</strong> <cite>Two Treatises</cite>, rights and consent.</li><li><strong>1776 · Smith:</strong> <cite>Wealth of Nations</cite>, commerce and institutions.</li><li><strong>1859 · Mill:</strong> <cite>On Liberty</cite>, the harm principle.</li><li><strong>1881 · T. H. Green:</strong> positive capacity and New Liberalism.</li><li><strong>1933+ · New Deal:</strong> “liberal” becomes the U.S. center-left governing label.</li><li><strong>1938 · Colloque Walter Lippmann:</strong> competing programs to renew liberalism.</li><li><strong>1955 · Dean Russell:</strong> proposes “libertarian” for the displaced classical-liberal label.</li><li><strong>1958 · Isaiah Berlin:</strong> negative and positive liberty lecture.</li><li><strong>1962 · Frank Meyer:</strong> fusionist conservative case in <cite>In Defense of Freedom</cite>.</li><li><strong>1971 · Rawls:</strong> egalitarian liberalism in <cite>A Theory of Justice</cite>.</li><li><strong>1974 · Nozick:</strong> rights-based minimal state in <cite>Anarchy, State, and Utopia</cite>.</li><li><strong>1989 · Williamson:</strong> names the Washington Consensus reform list.</li></ol>'''

    master = table(
        ["Criterion", "Classical liberal", "Modern US liberal", "Libertarian", "Neoliberal program", "Conservative", "Social democrat", "Democratic socialist", "National conservative"],
        [
            ["Economic state", "Protect property, competition, and public goods; strong presumption against privilege", "Regulate markets, manage demand, insure risks, and correct exclusion/externalities", "Rights-protection state or stateless legal order; broad privatization", "Stable macro rules, competition, privatization, and openness", "Markets plus order, family policy, defense, and selective protection", "Private markets with unions, universal services, and broad taxes", "Democratize ownership through public, cooperative, or worker control", "Direct trade, finance, and industry toward national resilience"],
            ["Tax / redistribution", "Limited and rule-bound; views range from proportional tax to social minimum", "Progressive taxes and targeted/universal benefits", "Minimal taxes; some accept land or consumption taxes, others reject compulsory tax", "Broader tax base, fiscal discipline, targeted safety nets", "Lower taxes in market wing; family/industrial subsidies in communitarian wing", "High broad-based taxes funding universal insurance", "Redistribution plus ownership change and workplace democracy", "Benefits prioritized for citizens/families; protection and industrial subsidies"],
            ["Civil liberties", "Strong speech, conscience, due process, and association", "Strong rights plus antidiscrimination enforcement", "Very strong presumption for speech, privacy, bodily autonomy, and due process", "Usually liberal constitutionalism; program itself is economic", "Free institutions constrained by order, tradition, or security concerns", "Liberal-democratic rights plus social rights", "Democratic rights; views on speech and party power vary", "Civil liberty may yield to national cohesion and executive capacity"],
            ["Trade", "Open trade as exchange and peace; exceptions for genuine security", "Rules-based trade with labor/environment conditions", "Unilateral free trade; migration and capital generally open", "Tariff reduction, competitive exchange rate, and FDI openness", "Free trade in market wing; strategic protection in nationalist wing", "Open trade with bargaining standards and adjustment policy", "Managed trade protecting labor and democratic planning", "Tariffs, local content, and strategic supply chains"],
            ["Immigration", "Generally freer movement, subject to legal-order and fiscal debates", "Legal immigration plus humanitarian protection and integration", "Free movement or radically expanded legal migration", "Labor mobility favored, but not a defining plank", "Ranges from skills-based limits to restriction for cultural continuity", "Managed openness with labor standards and welfare eligibility rules", "Varies: solidarity and refuge versus labor-market planning", "Restriction and assimilation are core program elements"],
            ["Authority", "Consent, general law, individual rights, and separated powers", "Democratic legitimacy plus equal citizenship and expert administration", "Pre-political individual rights; state powers must be strictly justified", "Constitutional government plus technocratic, credibility-enhancing institutions", "Inherited institutions, nation, constitution, religion, and prudence", "Parliamentary democracy, unions, and social citizenship", "Democratic control of economy and state", "Sovereign nation, historic community, and elected executive"],
            ["Canonical text", "Locke, <cite>Two Treatises</cite> (1689); Mill, <cite>On Liberty</cite> (1859)", "Rawls, <cite>A Theory of Justice</cite> (1971); New Deal legislation", "Nozick (1974); Rothbard, <cite>For a New Liberty</cite> (1973)", "Williamson's Washington Consensus list (1989/1990)", "Burke, <cite>Reflections</cite> (1790); Oakeshott (1956)", "Marshall, <cite>Citizenship and Social Class</cite> (1950)", "Mill, <cite>Chapters on Socialism</cite> (1879); modern workplace-democracy programs", "Recent national-conservative statements; no single canonical text"],
            ["Flagship policy", "Equal legal status, free entry, religious toleration", "Social Security, civil-rights enforcement, Medicare, environmental rules", "Occupational-licensing repeal, drug decriminalization, surveillance limits", "Fiscal discipline, trade liberalization, privatization, property security", "School choice, defense spending, family tax policy", "Universal health coverage, sector bargaining, paid leave", "Worker cooperatives, codetermination, public utilities or funds", "Industrial strategy, border restriction, procurement preference"],
            ["Party example (Aug 2026)", "Germany's FDP and classical-liberal factions elsewhere, imperfectly", "U.S. Democratic Party mainstream, imperfectly", "U.S. Libertarian Party; Europe's smaller liberal-libertarian currents", "No stable mass party self-label; technocratic reform factions", "U.S. Republican and UK Conservative traditions, both internally divided", "Nordic and European center-left parties", "Some democratic-socialist parties and factions; programs differ on ownership", "National-conservative and populist-right factions in the U.S. and Europe"],
            ["Most confused with", "Libertarianism or conservatism", "Leftism or socialism", "Conservatism", "Classical liberalism or any disliked market policy", "Libertarianism or nationalism", "Democratic socialism", "Social democracy or state socialism", "Traditional conservatism or fascism"],
        ],
    )

    liberal_vs = table(
        ["Split question", "Modern U.S. liberal", "Libertarian"],
        [
            ["What may government do beyond protecting rights?", "Supply education, health insurance, income security, infrastructure, environmental protection, and antidiscrimination enforcement", "Only functions tightly justified by rights protection; some libertarians accept a minimal safety net, others do not"],
            ["May taxes change distribution?", "Yes: progressive taxation can secure fair opportunity and insure social risk", "Generally no: holdings and voluntary transfer constrain redistribution; views differ on rectification and land"],
            ["What is liberty?", "Both noninterference and effective capacity to participate as an equal citizen", "Primarily freedom from coercion; positive goals do not automatically create claims on others"],
        ],
    )
    consensus = table(
        ["Williamson's 1989/1990 reform area", "What it meant", "Not the caricature"],
        [
            ["1. Fiscal discipline", "Avoid large, sustained deficits that drive inflation or payments crises", "Not zero public spending"],
            ["2. Public-expenditure priorities", "Shift from generalized subsidies toward basic health, education, and infrastructure", "Not abolish the state"],
            ["3. Tax reform", "Broaden the base and use moderate marginal rates", "Not simply cut every tax"],
            ["4. Interest rates", "Market-determined rates, with positive real rates", "Not permanently high rates"],
            ["5. Competitive exchange rate", "A rate consistent with export growth and external balance", "Not a single mandated exchange regime"],
            ["6. Trade liberalization", "Replace quantitative barriers and reduce protection on a schedule", "Not instant exposure without transition"],
            ["7. Inward foreign investment", "Remove barriers to foreign direct investment", "Williamson did not list full capital-account liberalization"],
            ["8. Privatization", "Sell state enterprises where private operation can work", "Not privatize natural monopolies without rules"],
            ["9. Deregulation", "Remove entry/exit barriers while retaining safety, environmental, and prudential rules", "Not no regulation"],
            ["10. Property rights", "Make secure rights available, including to informal firms", "Not privilege incumbents"],
        ],
    )
    mistakes = "".join(f'<div class="card"><h3>{t}</h3><p>{x}</p></div>' for t, x in [
        ("Liberal is not a universal left label", "In U.S. speech it usually means center-left. In Europe and Latin America it often signals constitutional and market liberalism. Translate before arguing."),
        ("Libertarian is not conservative", "They overlap on some markets. Drug law, surveillance, immigration, war, speech, and sexual autonomy expose the split."),
        ("Neoliberal does not mean new liberal", "The 1938 renewal project, Williamson's ten reform areas, and today's catch-all epithet are three different usages."),
        ("Classical liberal is not conservative", "Classical liberalism judges inherited institutions by liberty and general law; conservatism grants inheritance and social continuity independent weight."),
        ("Social democracy is not democratic socialism", "The practical dividing question is ownership: redistribute income from mostly private production, or democratize productive ownership itself?"),
        ("Fascist economics was not laissez-faire", "Private titles survived, but independent unions, entry, investment, trade, and production were subordinated to the state. See the corporatism column in the systems sheet."),
        ("One left-right axis loses information", "Economic control, civil liberty, national identity, institutional trust, and foreign policy do not move as one bundle. Two-axis charts help, but every chosen axis also hides dimensions."),
    ])

    content = f'''
<section aria-labelledby="translate"><div class="plate">PLATE I · TRANSLATE BEFORE YOU ARGUE</div><h2 id="translate">What does “liberal” mean here?</h2><p class="section-note">A label is a local dialect. Each cell states the normal center of gravity, not a membership test; named parties are examples, not exact embodiments.</p>{translation}</section>
<section class="page-break" aria-labelledby="lineage"><h2 id="lineage">How one word split into rival traditions</h2><p class="section-note">The dated nodes are the signature map. On small screens the same lineage appears as a linear list immediately below it.</p>{lineage_svg}</section>
<section aria-labelledby="matrix"><h2 id="matrix">The master matrix: eight ideologies, ten tests</h2><p class="section-note">Systems answer who owns capital. Ideologies answer what political authority should do. That is why a liberal, conservative, or socialist movement can operate inside more than one economic arrangement.</p>{master}</section>
<section aria-labelledby="liberal-libertarian"><h2 id="liberal-libertarian">What's the difference between a liberal and a libertarian?</h2><div class="callout"><strong>Short answer:</strong> Both descend from a tradition of individual rights, constitutional government, toleration, and legal equality. Modern U.S. liberals permit a broader state to secure fair opportunity, social insurance, and effective citizenship. Libertarians put a stronger presumption against coercion and redistribution, usually limiting government to rights protection or arguing for voluntary alternatives.</div>{liberal_vs}</section>
<section aria-labelledby="neoliberal"><h2 id="neoliberal">“Neoliberal”: the word, the program, and the epithet</h2><div class="card-grid"><div class="card"><h3>1938: renewal project</h3><p>The Colloque Walter Lippmann in Paris debated how liberalism should answer monopoly, mass democracy, depression, and totalitarian planning. Its participants did not share one modern program.</p></div><div class="card"><h3>1989: policy list</h3><p>John Williamson used “Washington Consensus” for ten reform areas he thought Washington institutions broadly supported for crisis-hit Latin America. The list below is narrower than later uses.</p></div><div class="card"><h3>1990s+: critical epithet</h3><p>Writers expanded “neoliberal” to cover globalization, austerity, privatization, technocracy, financialization, or market reasoning itself. Ask for the policy, institution, time, and author.</p></div></div>{consensus}</section>
<section aria-labelledby="mistakes"><h2 id="mistakes">Common mistakes</h2><div class="card-grid">{mistakes}</div></section>'''
    theme = r'''
@layer base{:root{--accent:light-dark(#6b3b15,#dfaa67);--accent2:light-dark(#265b63,#6fc4c7)}body{background-image:radial-gradient(circle at 18% 8%,color-mix(in srgb,var(--accent) 8%,transparent),transparent 26%),linear-gradient(90deg,transparent 49.8%,color-mix(in srgb,var(--line) 18%,transparent) 50%,transparent 50.2%);background-size:auto,42px 42px}.plate{font:800 .74rem ui-monospace,Consolas,monospace;letter-spacing:.15em;border-block:1px solid var(--line);padding:8px 0;color:var(--accent);margin-bottom:14px}.lineage{margin:0;padding:14px;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}.lineage svg{width:100%;height:auto}.lineage .links path{stroke:var(--line);stroke-width:3}.lineage .node rect{fill:var(--panel);stroke:var(--line);stroke-width:2;rx:8}.lineage .node text{fill:var(--ink);font:700 13px ui-monospace,Consolas,monospace}.lineage .node text:nth-of-type(n+2){font-weight:500;fill:var(--muted)}.lineage .root rect{stroke:#96734e}.lineage .social rect{stroke:#9a5062}.lineage .liberty rect{stroke:#477f72}.lineage .market rect{stroke:#4d708e}.lineage .order rect{stroke:#8b7049}.lineage figcaption{color:var(--muted);font-size:.85rem}.lineage-list{display:none}.master-matrix thead th:not(:first-child){min-width:185px}@media(max-width:600px){.lineage svg{display:none}.lineage-list{display:block;padding-left:24px}.lineage-list li{margin:.55em 0}}}
'''
    sources = '''<ol>
<li><a href="https://plato.stanford.edu/entries/liberalism/">Stanford Encyclopedia of Philosophy, “Liberalism” (revised 2026)</a> and <a href="https://plato.stanford.edu/entries/libertarianism/">“Libertarianism”</a> for doctrine families and their internal disputes.</li>
<li><a href="https://fee.org/articles/who-is-a-libertarian/">Dean Russell, “Who Is a Libertarian?” (May 1, 1955)</a> for the American label-reclamation node.</li>
<li><a href="https://catalogue.bnf.fr/ark:/12148/cb455760525">Bibliothèque nationale de France record for the Colloque Walter Lippmann</a>, held in Paris August 26–30, 1938.</li>
<li><a href="https://www.piie.com/blogs/realtime-economics/2021/what-washington-consensus">Peterson Institute, “What is the Washington Consensus?”</a> and Williamson's original ten reform areas.</li>
<li>Primary texts: Locke's <cite>Two Treatises</cite> (1689), Smith's <cite>Wealth of Nations</cite> (1776), Mill's <cite>On Liberty</cite> (1859), Berlin's “Two Concepts of Liberty” (1958), Rawls (1971), and Nozick (1974).</li>
</ol><p><strong>Scope:</strong> transatlantic and Latin American liberal-family labels. Party examples are orientation points verified as of August 2026, not claims that every member or platform plank fits the column.</p>'''
    return document(
        title="Liberal, Libertarian, Neoliberal: Political Labels Decoded",
        description="Classical liberal, liberal, libertarian, neoliberal, conservative, and socialist compared in one matrix, with a dated lineage map and cross-Atlantic translation guide.",
        keywords="liberal vs libertarian, classical liberalism vs libertarianism, neoliberalism vs liberalism, political ideologies chart",
        filename="political-ideologies-compared.html", h1="Political Ideologies, Compared",
        eyebrow="Atlas of ideas · translate the label first",
        lede="“Liberal” can identify the American center-left, a European market party, a Latin American reformer, or a centuries-old philosophy. This atlas translates the dialect, traces the family tree, and compares eight programs on concrete questions.",
        theme_css=theme, content=content,
        image_alt="Annotated intellectual-history lineage map from classical liberalism to modern liberal, libertarian, neoliberal, and conservative branches",
        sources=sources,
        related=[("Economic Systems Compared", "economic-systems-compared.html"), ("Capitalism", "capitalism.html"), ("Objectivism", "objectivism.html")],
    )


def build_states_vs_countries(states: list[StateRow], countries: list[dict]) -> str:
    ms = next(row for row in states if row.name == "Mississippi")
    uk = next(row for row in countries if row["iso3"] == "GBR")
    fx = float(json.loads(fetch(WORLD_BANK_FX))[1][0]["value"])
    uk_nominal_pc = uk["gdp"] / uk["population"]
    ms_rpp_pc = ms.gdp_pc / (ms.rpp / 100)
    uk_final_income_usd = 41_900 / fx
    uk_consumption_usd = 24_154 / fx
    verdict_rows = [
        ["Nominal GDP per person (2024)", money(ms.gdp_pc), money(uk_nominal_pc), "Mississippi" if ms.gdp_pc > uk_nominal_pc else "United Kingdom", "Output converted at market exchange rates"],
        ["PPP / price-adjusted GDP per person (2024)", money(ms_rpp_pc), money(uk["ppp_pc"]), "Mississippi" if ms_rpp_pc > uk["ppp_pc"] else "United Kingdom", "Output after price-level adjustment; state side uses BEA RPP"],
        ["Regional price level (US = 100, 2024)", f"{ms.rpp:.1f}", "International PPP, not the BEA index", "Not a score", "Why one nominal dollar buys different baskets"],
        ["Household consumption/person (2023)", "$42,131 (BEA PCE)", f"£24,154 / {money(uk_consumption_usd)} (ONS)", "Mississippi", "Current-price household consumption; PCE and HFCE boundaries are close, not identical"],
        ["Median household resources", f"{money(ms.median_income)} gross household (ACS 2024)", f"£41,900 / {money(uk_final_income_usd)} final equivalised household (ONS FYE 2024)", "No honest winner", "Gross vs after-tax-and-in-kind, and unequal household definitions"],
    ]
    verdict = table(["Measure", "Mississippi", "United Kingdom", "Verdict", "What it measures"], verdict_rows, cls="verdict-table")

    steps = [
        ("01", "Start with the numerator", f"Mississippi current-dollar GDP = {money(ms.gdp_m * 1_000_000, compact=True)}. UK current-dollar GDP = {money(uk['gdp'], compact=True)}. Total GDP answers economic scale, not how well the typical resident lives."),
        ("02", "Divide by people", f"Mississippi: {money(ms.gdp_m * 1_000_000, compact=True)} ÷ {ms.population:,} = <strong>{money(ms.gdp_pc)} per person</strong>. UK: {money(uk['gdp'], compact=True)} ÷ {uk['population']:,} = <strong>{money(uk_nominal_pc)}</strong>. Nominal output favors {'Mississippi' if ms.gdp_pc > uk_nominal_pc else 'the UK'}."),
        ("03", "Correct prices inside the United States", f"Mississippi's BEA regional price parity is {ms.rpp:.1f} where US = 100. {money(ms.gdp_pc)} ÷ {ms.rpp / 100:.3f} = <strong>{money(ms_rpp_pc)}</strong> in national-price purchasing power. This transparent adjustment is analytical, not a BEA-published “state PPP GDP” series."),
        ("04", "Use the international PPP benchmark", f"World Bank 2024 PPP GDP per capita for the UK is <strong>{money(uk['ppp_pc'])}</strong>. Compare it with Mississippi's RPP-adjusted {money(ms_rpp_pc)} only as an approximation: international PPP and regional RPP baskets are built separately."),
        ("05", "Change the question from production to households", f"BEA reports Mississippi personal consumption expenditures of <strong>$42,131 per person in 2023</strong>. ONS reports UK median equivalised final household income of <strong>£41,900 in FYE 2024</strong> after taxes and benefits in cash and kind. They cannot be ranked as the same statistic."),
        ("06", "State the real verdict", "Mississippi can exceed the UK on one output-per-person measure without proving that its median household consumes more, has more disposable income, or receives better services. The correct sentence names the measure every time."),
    ]
    step_html = "".join(f'<article class="flip-row"><div class="flip-no">{n}</div><div><h3>{title}</h3><p>{text}</p></div></article>' for n, title, text in steps)

    matches = []
    for state in sorted(states, key=lambda row: row.gdp_m, reverse=True):
        state_gdp = state.gdp_m * 1_000_000
        nearest = min(countries, key=lambda country: abs(country["gdp"] - state_gdp))
        gap = (state_gdp / nearest["gdp"] - 1) * 100
        matches.append([
            state.name,
            money(state_gdp, compact=True),
            nearest["name"],
            money(nearest["gdp"], compact=True),
            f"{gap:+.1f}%",
        ])
    match_table = table(["US state / district", "2024 GDP", "Nearest national economy", "2024 GDP", "State gap"], matches, cls="match-table")

    featured_states = {"California", "Texas", "New York", "Florida", "Illinois", "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Washington", "New Jersey", "Virginia", "Massachusetts", "Colorado", "Mississippi"}
    g20_codes = {"ARG", "AUS", "BRA", "CAN", "CHN", "FRA", "DEU", "IND", "IDN", "ITA", "JPN", "KOR", "MEX", "RUS", "SAU", "ZAF", "TUR", "GBR"}
    ranking = []
    for state in states:
        if state.name in featured_states:
            ranking.append({"name": state.name, "kind": "US state", "nominal": state.gdp_pc, "adjusted": state.gdp_pc / (state.rpp / 100), "method": f"BEA RPP {state.rpp:.1f}"})
    for country in countries:
        if country["iso3"] in g20_codes and country["ppp_pc"]:
            ranking.append({"name": country["name"], "kind": "G20 country", "nominal": country["gdp"] / country["population"], "adjusted": country["ppp_pc"], "method": "World Bank PPP"})
    ranking.sort(key=lambda row: row["nominal"], reverse=True)
    ranking_table = table(
        ["Economy", "Type", "Nominal GDP/person, 2024", "Price-adjusted GDP/person, 2024", "Adjustment"],
        [[r["name"], r["kind"], money(r["nominal"]), money(r["adjusted"]), r["method"]] for r in ranking],
    )

    explanations = "".join(f'<div class="card"><h3>{title}</h3><p>{text}</p></div>' for title, text in [
        ("Market exchange rates", "Nominal dollars answer questions about global purchasing power, debt service, imported goods, and economic scale. A strong or weak currency can move the ranking without changing local production overnight."),
        ("PPP and RPP", "International purchasing-power parities compare national price baskets; BEA regional price parities compare prices among U.S. states. Both are index constructions, not exchange rates offered at a bank."),
        ("GDP is production", "GDP includes corporate profits, government output, rent, and healthcare production. It is neither take-home pay nor a measure of who receives the output."),
        ("Ireland warning", "Ireland's multinational balance sheets inflate GDP. Ireland's CSO reports 2024 modified GNI* of €321 billion, 57.1% of GDP, specifically to remove disproportionate globalization effects."),
        ("Services are priced differently", "A U.S. healthcare procedure can add more measured GDP because its price is higher. Government health and education are often valued by input cost, not a market sale or measured outcome."),
        ("Hours and distribution", "Two economies with equal GDP per capita can differ in hours worked, median income, inequality, leisure, household size, and unpaid work. Use a household measure for a household claim."),
    ])
    mistakes = "".join(f'<div class="card"><h3>{t}</h3><p>{x}</p></div>' for t, x in [
        ("Mixing nominal and PPP", "Never compare a state's current-dollar GDP with a country's PPP GDP. Keep both sides in the same accounting basis and year."),
        ("Calling GDP income", "GDP per capita is mean production. It is not the median worker's wage, household disposable income, or consumption."),
        ("Treating state RPP as country PPP", "They solve related problems with different baskets and universes. Crosswalking them is an estimate that must be labeled."),
        ("Dropping the denominator", "“California is the world's fourth-largest economy” is a total-output claim. It says nothing about per-person income or living standards."),
        ("Mismatching vintages", "BEA revises state GDP quarterly; World Bank and IMF revise country histories. Save the year and retrieval date with every match table."),
        ("Picking the measure after seeing the winner", "Decide whether the claim is about scale, production per person, purchasing power, median resources, or consumption before opening the data."),
    ])
    content = f'''
<section aria-labelledby="verdict"><div class="board-label">MSY ↔ GBR · FIVE MEASURES · 2024 VINTAGE</div><h2 id="verdict">Is Mississippi really richer than the UK?</h2><p class="section-note">Sometimes on output per person; not as a general statement about residents. The measure changes the claim, and the last row refuses a fake apples-to-oranges ranking.</p>{verdict}</section>
<section aria-labelledby="worked"><h2 id="worked">Worked example: watch the answer flip</h2><div class="departures">{step_html}</div></section>
<section class="page-break" aria-labelledby="matches"><h2 id="matches">Which country matches each U.S. state's economy?</h2><p class="section-note">Nearest whole national economy by absolute difference in 2024 current-dollar GDP. This is the classic headline comparison, with both numbers and the gap exposed.</p>{match_table}</section>
<section aria-labelledby="percapita"><h2 id="percapita">Large states and G20 economies per person</h2><p class="section-note">The order is nominal. The next column shows how price adjustment reorders the same economies. State adjusted figures divide by BEA RPP; country figures use World Bank PPP.</p>{ranking_table}</section>
<section aria-labelledby="why"><h2 id="why">Why the measures disagree</h2><div class="card-grid">{explanations}</div></section>
<section aria-labelledby="mistakes"><h2 id="mistakes">Common mistakes</h2><div class="card-grid">{mistakes}</div></section>'''
    theme = r'''
@layer base{:root{--accent:light-dark(#a64f14,#ffb44c);--accent2:light-dark(#165d78,#70d0ee);--paper:light-dark(#f2f5f4,#07131f);--panel:light-dark(#ffffff,#0d2232);--ink:light-dark(#14212a,#edf6f8);--line:light-dark(#93a2a7,#29475a)}body{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;background-image:linear-gradient(color-mix(in srgb,var(--line) 13%,transparent) 1px,transparent 1px);background-size:100% 26px}h1,h2,h3{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}.board-label{display:inline-block;background:var(--ink);color:var(--paper);padding:8px 12px;letter-spacing:.11em;font-weight:800}.verdict-table td:nth-child(2),.verdict-table td:nth-child(3),.verdict-table td:nth-child(4){font-variant-numeric:tabular-nums;font-weight:800}.departures{border:2px solid var(--line);background:var(--panel);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow)}.flip-row{display:grid;grid-template-columns:70px 1fr;gap:16px;padding:16px;border-bottom:1px dashed var(--line)}.flip-row:last-child{border-bottom:0}.flip-no{font-size:2rem;color:var(--accent);font-variant-numeric:tabular-nums}.flip-row h3{margin:0 0 5px}.flip-row p{margin:0}.match-table td:nth-child(2),.match-table td:nth-child(4),.match-table td:nth-child(5){font-variant-numeric:tabular-nums;white-space:nowrap}@media(max-width:600px){.flip-row{grid-template-columns:42px 1fr;gap:9px}.flip-no{font-size:1.4rem}}}
@media(prefers-reduced-motion:no-preference){@layer base{.flip-row{animation:arrival .35s both;animation-timeline:view();animation-range:entry 0 entry 25%}@keyframes arrival{from{opacity:.35;transform:translateY(8px)}to{opacity:1;transform:none}}}}
'''
    sources = f'''<ol>
<li><a href="https://apps.bea.gov/iTable/?ReqID=70&amp;step=1">U.S. Bureau of Economic Analysis, SAGDP1</a>: 2024 current-dollar and real GDP by state; <a href="https://apps.bea.gov/itable/?ReqID=70&amp;step=1">BEA regional price parities</a> for 2024.</li>
<li><a href="https://api.worldbank.org/v2/indicator/NY.GDP.MKTP.CD">World Bank WDI</a>: 2024 country GDP, population, nominal GDP per capita, and PPP GDP per capita. Values retrieved {VERIFIED}.</li>
<li><a href="https://www.bea.gov/sites/default/files/2024-10/pce1024.pdf">BEA state personal consumption expenditures release</a>: Mississippi $42,131 per person in 2023.</li>
<li><a href="https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome/bulletins/regionalhouseholdfinalconsumptionexpenditureuk/2009to2023">UK Office for National Statistics</a>: £24,154 household final consumption per person in 2023; <a href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/theeffectsoftaxesandbenefitsonhouseholdincome/2024">ONS household income</a>: £41,900 median equivalised final income, FYE 2024.</li>
<li><a href="https://www.cso.ie/en/releasesandpublications/ep/p-ana/annualnationalaccounts2024/gniandde-globalisedresults/">Ireland Central Statistics Office</a>: 2024 modified GNI* €321 billion, 57.1% of GDP.</li>
</ol><p><strong>Reproducibility:</strong> <code>python scripts/build_economics_batch.py</code> downloads the dated BEA, Census, BLS, and World Bank tables and rebuilds all 51 state rows. Country matches exclude World Bank regional and income aggregates.</p>'''
    return document(
        title="Is Mississippi Richer Than the UK? US States vs Countries",
        description="US state GDP compared with whole countries using nominal, PPP, regional prices, consumption, and household measures, including a worked Mississippi-versus-UK verdict.",
        keywords="Mississippi GDP per capita vs UK, US states compared to countries GDP, California GDP vs countries, state GDP comparison",
        filename="us-states-vs-countries-gdp.html", h1="US States vs National Economies",
        eyebrow="International arrivals · scale is not living standards",
        lede="The viral comparison is built to flip: one measure says Mississippi is richer than Britain, another changes the gap, and household measures ask a different question entirely. Here is the arithmetic, the denominator, and the honest sentence.",
        theme_css=theme, content=content,
        image_alt="Split-flap style verdict board comparing Mississippi and the United Kingdom across five economic measures",
        sources=sources,
        related=[("Red vs Blue State Economies", "red-vs-blue-state-economies.html"), ("Economic Systems Compared", "economic-systems-compared.html"), ("The Household Numbers", "the-household-numbers.html"), ("Housing Comparison", "housing-comparison.html")],
    )


def build_red_blue(states: list[StateRow]) -> str:
    state_only = [row for row in states if row.name != "District of Columbia"]

    def group(side: str, pool: list[StateRow] | None = None) -> dict[str, float]:
        rows = [row for row in (pool or state_only) if row.side == side]
        pop = sum(row.population for row in rows)
        def weighted(attr: str) -> float:
            usable = [row for row in rows if getattr(row, attr) is not None]
            return sum(getattr(row, attr) * row.population for row in usable) / sum(row.population for row in usable)
        return {
            "count": len(rows), "population": pop,
            "gdp": sum(row.gdp_m for row in rows) * 1_000_000,
            "gdp_pc": sum(row.gdp_m for row in rows) * 1_000_000 / pop,
            "income": weighted("median_income"), "rpp_income": weighted("rpp_income"),
            "growth": (sum(row.real_gdp_2024_m for row in rows) / sum(row.real_gdp_2019_m for row in rows) - 1) * 100,
            "unemployment": weighted("unemployment"), "migration": sum(row.migration for row in rows),
            "tax": weighted("tax_burden") if any(row.tax_burden is not None for row in rows) else math.nan,
            "poverty": weighted("poverty"),
            "bop": sum(BOP_2023[row.name] * row.population for row in rows if row.name in BOP_2023) / sum(row.population for row in rows if row.name in BOP_2023),
        }

    red, blue = group("Red"), group("Blue")
    map_svg = state_map_svg(state_only)
    map_data = {
        row.name: {
            "winner": "Trump" if row.side == "Red" else "Harris",
            "gdp_pc": round(row.gdp_pc),
            "rpp_income": round(row.rpp_income),
            "growth": round(row.growth_5y, 1),
            "migration": row.migration,
            "unemployment": row.unemployment,
            "tax": row.tax_burden,
            "poverty": row.poverty,
            "bop": BOP_2023.get(row.name),
        }
        for row in state_only
    }
    state_options = "".join(
        f'<option value="{html.escape(row.name, quote=True)}">{html.escape(row.name)}</option>'
        for row in sorted(state_only, key=lambda item: item.name)
    )
    score_rows = [
        ["Total GDP", money(red["gdp"], compact=True), money(blue["gdp"], compact=True), "Scale of production, not individual welfare", "2024 BEA"],
        ["GDP per resident", money(red["gdp_pc"]), money(blue["gdp_pc"]), "Output divided by population", "2024 BEA + ACS"],
        ["Avg. state median household income", money(red["income"]), money(blue["income"]), "Population-weighted state medians; not a national microdata median", "2024 ACS"],
        ["RPP-adjusted median income", money(red["rpp_income"]), money(blue["rpp_income"]), "Approximate purchasing power after state price levels", "2024 ACS + BEA"],
        ["Aggregate real GDP growth, 2019–24", f"{red['growth']:.1f}%", f"{blue['growth']:.1f}%", "Five-year output change; pandemic endpoints matter", "2019–24 BEA"],
        ["Annual unemployment", f"{red['unemployment']:.1f}%", f"{blue['unemployment']:.1f}%", "Population-weighted state annual rates", "2024 BLS"],
        ["Net domestic migration", f"{red['migration']:+,}", f"{blue['migration']:+,}", "People moving between states, not international migration", "Jul 2023–Jul 2024 Census"],
        ["State-local tax burden", f"{red['tax']:.1f}%" if not math.isnan(red['tax']) else "n/a", f"{blue['tax']:.1f}%" if not math.isnan(blue['tax']) else "n/a", "Residents' estimated state-local taxes as share of income", "2022 Tax Foundation model"],
        ["Federal balance per resident", money(red["bop"]), money(blue["bop"]), "Federal spending located in states minus receipts allocated to states", "FFY 2023 Rockefeller"],
        ["Official poverty rate", f"{red['poverty']:.1f}%", f"{blue['poverty']:.1f}%", "ACS official measure; does not adjust state costs", "2024 ACS"],
    ]
    scoreboard = table(["Measure", f"Slate side · {int(red['count'])} Trump states", f"Bronze side · {int(blue['count'])} Harris states", "What it tells you", "Vintage"], score_rows, cls="scoreboard")

    ledger_rows = []
    for row in sorted(states, key=lambda item: item.gdp_m, reverse=True):
        ledger_rows.append([
            row.name,
            "Trump" if row.side == "Red" else "Harris",
            money(row.gdp_m * 1_000_000, compact=True),
            money(row.gdp_pc), money(row.rpp_income), f"{row.growth_5y:+.1f}%",
            f"{row.migration:+,}", f"{row.unemployment:.1f}%" if row.unemployment is not None else "—",
            f"{row.tax_burden:.1f}%" if row.tax_burden is not None else "—",
            f"{row.poverty:.1f}%", money(BOP_2023[row.name]) if row.name in BOP_2023 else "not reported",
        ])
    ledger = table(
        ["State / district", "2024 winner", "GDP", "GDP/person", "RPP-adjusted median HH income", "Real GDP 5y", "Domestic migration", "Unemployment", "Tax burden", "Poverty", "Federal BOP/person"],
        ledger_rows, cls="ledger-table",
    )

    flips = table(
        ["Claim / measure", "Higher side in this vintage", "Complicating measure", "Defensible sentence"],
        [
            ["Which side produces more in total?", "Slate" if red["gdp"] > blue["gdp"] else "Bronze", "Population and number of states", f"The {'Trump' if red['gdp'] > blue['gdp'] else 'Harris'} states produced more combined 2024 GDP under this fixed election grouping."],
            ["Which side produces more per resident?", "Slate" if red["gdp_pc"] > blue["gdp_pc"] else "Bronze", "Industry mix and urban concentration", f"The {'Trump' if red['gdp_pc'] > blue['gdp_pc'] else 'Harris'} group had higher 2024 GDP per resident."],
            ["Where is nominal median income higher?", "Slate" if red["income"] > blue["income"] else "Bronze", "Regional prices", f"Population-weighted state medians favor the {'Trump' if red['income'] > blue['income'] else 'Harris'} group before price adjustment."],
            ["Where does median income buy more?", "Slate" if red["rpp_income"] > blue["rpp_income"] else "Bronze", "Housing quality and household composition", f"BEA price adjustment {'reverses' if (red['income'] > blue['income']) != (red['rpp_income'] > blue['rpp_income']) else 'narrows but does not reverse'} the nominal result."],
            ["Where are people moving?", "Slate" if red["migration"] > blue["migration"] else "Bronze", "Weather, housing supply, age, and job mix", f"Net domestic migration favored the {'Trump' if red['migration'] > blue['migration'] else 'Harris'} states from July 2023 to July 2024."],
            ["Who gets more from Washington?", "Slate" if red["bop"] > blue["bop"] else "Bronze", "Bases, federal payroll, age, poverty, disasters, and progressive taxes", f"The {'Trump' if red['bop'] > blue['bop'] else 'Harris'} group had the larger population-weighted FFY 2023 federal balance per resident."],
        ],
    )

    excluded = {"Wisconsin", "Michigan", "Pennsylvania", "Georgia", "North Carolina", "Nevada"}
    reduced_pool = [row for row in state_only if row.name not in excluded]
    red_x, blue_x = group("Red", reduced_pool), group("Blue", reduced_pool)
    sensitivity = table(
        ["Measure", "All states winner", "Excluding WI, MI, PA, GA, NC, NV", "Interpretation"],
        [
            ["Total GDP", "Trump" if red["gdp"] > blue["gdp"] else "Harris", "Trump" if red_x["gdp"] > blue_x["gdp"] else "Harris", "Large close states can move the pooled total"],
            ["GDP per resident", "Trump" if red["gdp_pc"] > blue["gdp_pc"] else "Harris", "Trump" if red_x["gdp_pc"] > blue_x["gdp_pc"] else "Harris", "Tests whether the result rests on swing-state assignment"],
            ["RPP-adjusted median income", "Trump" if red["rpp_income"] > blue["rpp_income"] else "Harris", "Trump" if red_x["rpp_income"] > blue_x["rpp_income"] else "Harris", "Price-adjusted household-resource proxy"],
            ["Real GDP growth, 2019–24", "Trump" if red["growth"] > blue["growth"] else "Harris", "Trump" if red_x["growth"] > blue_x["growth"] else "Harris", "Five-year aggregate growth"],
            ["Domestic migration", "Trump" if red["migration"] > blue["migration"] else "Harris", "Trump" if red_x["migration"] > blue_x["migration"] else "Harris", "Absolute net movers, not a rate"],
            ["Federal BOP/person", "Trump" if red["bop"] > blue["bop"] else "Harris", "Trump" if red_x["bop"] > blue_x["bop"] else "Harris", "Federal geography can dominate ideology"],
        ],
    )

    gainers = sorted(state_only, key=lambda row: row.migration, reverse=True)[:10]
    losers = sorted(state_only, key=lambda row: row.migration)[:10]
    migration_table = table(
        ["Rank", "Top gainer", "Net domestic movers", "2024 result", "Top loser", "Net domestic movers", "2024 result"],
        [[str(i + 1), gainers[i].name, f"{gainers[i].migration:+,}", "Trump" if gainers[i].side == "Red" else "Harris", losers[i].name, f"{losers[i].migration:+,}", "Trump" if losers[i].side == "Red" else "Harris"] for i in range(10)],
    )

    bop_sorted = sorted(BOP_2023.items(), key=lambda item: item[1], reverse=True)
    bop_table = table(
        ["Rank", "Highest federal balance", "$/resident", "2024 result", "Lowest federal balance", "$/resident", "2024 result"],
        [[str(i + 1), bop_sorted[i][0], money(bop_sorted[i][1]), "Trump" if bop_sorted[i][0] in RED_STATES else "Harris", bop_sorted[-(i + 1)][0], money(bop_sorted[-(i + 1)][1]), "Trump" if bop_sorted[-(i + 1)][0] in RED_STATES else "Harris"] for i in range(10)],
    )

    mistakes = "".join(f'<div class="card"><h3>{t}</h3><p>{x}</p></div>' for t, x in [
        ("Totals vs per-capita", "California and Texas move totals. A resident-level claim needs a denominator; an aggregate market-size claim does not."),
        ("Ignoring prices", "Nominal income buys different housing and services. RPP adjustment helps, but it does not measure quality, taxes, climate, or household size."),
        ("Credit to today's governor", "Oil geology, ports, universities, finance clusters, age structure, and housing stock predate any current officeholder."),
        ("Migration as a policy referendum", "Jobs and taxes matter, but so do weather, family, retirement, remote work, housing supply, disaster, and international immigration."),
        ("Cherry-picked endpoints", "A five-year window starting in 2019 crosses a pandemic shock. Use several windows before claiming a durable growth regime."),
        ("DC as an ordinary state", "DC is shown in the ledger but excluded from red/blue pooled results and federal BOP ranking. Its federal payroll and city-state structure break the comparison."),
        ("One party caused one economy", "Presidential vote is a classification key, not a causal design. These are descriptive groups with enormous within-group variance."),
    ])
    red_names = ", ".join(sorted(RED_STATES))
    blue_names = ", ".join(sorted(set(STATE_FIPS) - RED_STATES - {"District of Columbia"}))
    map_script = r'''<script>(()=>{
const data=__MAP_DATA__;
const money=value=>`${value<0?"-":""}$${Math.abs(Math.round(value)).toLocaleString("en-US")}`;
const signed=(value,digits)=>`${value>0?"+":""}${value.toLocaleString("en-US",{minimumFractionDigits:digits,maximumFractionDigits:digits})}`;
const metrics={
side:{label:"2024 presidential winner",format:value=>value},
gdp_pc:{label:"2024 GDP per resident",format:value=>money(value)},
rpp_income:{label:"2024 RPP-adjusted median household income",format:value=>money(value)},
growth:{label:"Real GDP growth, 2019–24",format:value=>`${signed(value,1)}%`},
migration:{label:"Net domestic migration, Jul 2023–Jul 2024",format:value=>signed(value,0)},
unemployment:{label:"2024 annual unemployment",format:value=>`${value.toFixed(1)}%`},
tax:{label:"2022 state-local tax burden",format:value=>`${value.toFixed(1)}%`},
poverty:{label:"2024 official poverty rate",format:value=>`${value.toFixed(1)}%`},
bop:{label:"FFY 2023 federal balance per resident",format:value=>money(value)}
};
const metricSelect=document.getElementById("economy-metric");
const stateSelect=document.getElementById("economy-state");
const paths=[...document.querySelectorAll(".state-shape")];
const detailName=document.getElementById("map-detail-name");
const detailWinner=document.getElementById("map-detail-winner");
const detailValue=document.getElementById("map-detail-value");
const detailRank=document.getElementById("map-detail-rank");
const legend=document.getElementById("map-legend");
const tooltip=document.getElementById("map-tooltip");
const mapWrap=document.querySelector(".map-figure");
let selected="California";
let ranking=[];
const valueFor=(name,metric)=>metric==="side"?data[name].winner:data[name][metric];
function updateDetail(){
  const metric=metricSelect.value;const row=data[selected];const value=valueFor(selected,metric);
  detailName.textContent=selected;detailWinner.textContent=`${row.winner} won in 2024`;
  detailValue.textContent=value==null?"Not reported":metrics[metric].format(value);
  if(metric==="side") detailRank.textContent="Election result is a grouping key, not a causal claim.";
  else if(value==null) detailRank.textContent="This source does not report a value for the state.";
  else detailRank.textContent=`${metrics[metric].label} · rank ${ranking.findIndex(item=>item[0]===selected)+1} of ${ranking.length} by value`;
}
function setSelected(name){selected=name;stateSelect.value=name;paths.forEach(path=>path.classList.toggle("is-selected",path.dataset.state===name));updateDetail()}
function buildLegend(metric){
  legend.replaceChildren();
  if(metric==="side"){
    [["side-trump","Trump · 31 states"],["side-harris","Harris · 19 states"]].forEach(([className,label])=>{
      const item=document.createElement("span");item.className="map-legend-item";
      const swatch=document.createElement("i");swatch.className=`map-swatch ${className}`;swatch.setAttribute("aria-hidden","true");
      item.append(swatch,document.createTextNode(label));legend.append(item);
    });return;
  }
  legend.append(document.createTextNode("Lowest"));
  for(let index=1;index<=5;index++){const swatch=document.createElement("i");swatch.className=`map-swatch q${index}`;swatch.setAttribute("aria-hidden","true");legend.append(swatch)}
  legend.append(document.createTextNode("Highest"));
}
function render(){
  const metric=metricSelect.value;
  ranking=Object.entries(data).filter(([,row])=>metric!=="side"&&Number.isFinite(row[metric])).sort((a,b)=>b[1][metric]-a[1][metric]);
  const ascending=[...ranking].reverse();
  paths.forEach(path=>{
    const name=path.dataset.state;const row=data[name];const value=valueFor(name,metric);
    path.classList.remove("side-trump","side-harris","q1","q2","q3","q4","q5","no-data");
    if(metric==="side") path.classList.add(row.winner==="Trump"?"side-trump":"side-harris");
    else if(!Number.isFinite(value)) path.classList.add("no-data");
    else path.classList.add(`q${Math.min(5,Math.floor(ascending.findIndex(item=>item[0]===name)/ascending.length*5)+1)}`);
    const label=`${name}: ${value==null?"not reported":metrics[metric].format(value)}`;
    path.setAttribute("aria-label",label);path.querySelector("title").textContent=label;
  });
  buildLegend(metric);updateDetail();
}
function showTooltip(event,path){
  const metric=metricSelect.value;const name=path.dataset.state;const value=valueFor(name,metric);
  tooltip.textContent=`${name} · ${value==null?"not reported":metrics[metric].format(value)}`;tooltip.hidden=false;
  const bounds=mapWrap.getBoundingClientRect();const x=event.clientX-bounds.left+12;const y=event.clientY-bounds.top+12;
  tooltip.style.left=`${Math.max(8,Math.min(x,bounds.width-tooltip.offsetWidth-8))}px`;tooltip.style.top=`${Math.max(8,y)}px`;
}
paths.forEach(path=>{
  path.addEventListener("click",()=>setSelected(path.dataset.state));
  path.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();setSelected(path.dataset.state)}});
  path.addEventListener("focus",()=>setSelected(path.dataset.state));
  path.addEventListener("pointerenter",event=>showTooltip(event,path));path.addEventListener("pointermove",event=>showTooltip(event,path));
  path.addEventListener("pointerleave",()=>{tooltip.hidden=true});
});
metricSelect.addEventListener("change",render);stateSelect.addEventListener("change",()=>setSelected(stateSelect.value));
document.documentElement.classList.add("js");render();setSelected(selected);
})();</script>'''.replace("__MAP_DATA__", json.dumps(map_data, separators=(",", ":")))

    content = f'''
<section class="map-stage" aria-labelledby="economy-map-title"><div class="data-years"><strong>Data years:</strong> GDP, RPP, ACS, migration, unemployment 2024 · tax burden 2022 · federal balance FFY 2023 · grouping fixed by 2024 presidential winner until the 2028 election.</div><div class="score-label">INTERACTIVE STATE MAP · 50 STATES</div><h2 id="economy-map-title">See the comparison state by state</h2><p class="section-note">Choose a measure, then hover, focus, or select a state for its exact value. Color shows rank, not whether a policy or party caused the result.</p><div class="map-toolbar no-print"><label for="economy-metric">Map measure<select id="economy-metric"><option value="side">2024 presidential winner</option><option value="gdp_pc">GDP per resident</option><option value="rpp_income">RPP-adjusted median income</option><option value="growth">Real GDP growth, 2019–24</option><option value="migration">Domestic migration</option><option value="unemployment">Unemployment</option><option value="tax">State-local tax burden</option><option value="poverty">Official poverty rate</option><option value="bop">Federal balance per resident</option></select></label><label for="economy-state">Selected state<select id="economy-state">{state_options}</select></label></div><div class="map-grid"><figure class="map-figure"><svg class="economy-map" viewBox="0 0 975 610" role="img" aria-labelledby="economy-map-svg-title economy-map-svg-desc"><title id="economy-map-svg-title">United States economic comparison map</title><desc id="economy-map-svg-desc">The 50 states are grouped by the 2024 presidential winner. With JavaScript, choose an economic measure and inspect exact state values.</desc>{map_svg}</svg><div class="map-tooltip" id="map-tooltip" role="tooltip" hidden></div><figcaption id="map-legend" class="map-legend"><span class="map-legend-item"><i class="map-swatch side-trump" aria-hidden="true"></i>Trump · 31 states</span><span class="map-legend-item"><i class="map-swatch side-harris" aria-hidden="true"></i>Harris · 19 states</span></figcaption></figure><aside class="map-detail" aria-live="polite"><span class="map-detail-kicker">Selected state</span><strong id="map-detail-name">California</strong><span id="map-detail-winner">Harris won in 2024</span><span class="map-detail-value" id="map-detail-value">Harris</span><span id="map-detail-rank">Election result is a grouping key, not a causal claim.</span></aside></div><noscript><p class="section-note">The default map shows the 2024 election grouping. The full data for every measure remains available in the ledger below.</p></noscript></section>
<section aria-labelledby="rule"><h2 id="rule">Classification rule</h2><p><strong>Trump states ({len(RED_STATES)}):</strong> {red_names}.</p><p><strong>Harris states (19):</strong> {blue_names}. DC appears in the ledger but not pooled state results.</p><p>Arizona, Georgia, Michigan, Nevada, Pennsylvania, and Wisconsin changed from Biden in 2020 to Trump in 2024. No purple category is used.</p></section>
<section class="stadium" aria-labelledby="score"><div class="score-label">NATIONAL BOX SCORE · SAME WEIGHT, SAME TYPE</div><h2 id="score">Red vs blue state economies: the scoreboard</h2><p class="section-note">Neutral slate and bronze replace emotional red/blue color coding. Each row answers a different question; no composite “winner” is calculated.</p>{scoreboard}</section>
<section aria-labelledby="flips"><h2 id="flips">The verdict flips when the measure changes</h2>{flips}</section>
<section aria-labelledby="sensitivity"><h2 id="sensitivity">Does the result depend on six close states?</h2><p class="section-note">Sensitivity check only: remove the six closest high-impact states from both groups, then recompute. This does not create a third “purple” category.</p>{sensitivity}</section>
<section class="page-break" aria-labelledby="ledger"><h2 id="ledger">The full 50-state ledger plus DC</h2><p class="section-note">Sorted by 2024 GDP. Every column keeps its year visible here; “federal BOP” means spending located in the state minus receipts allocated to it.</p>{ledger}</section>
<section aria-labelledby="migration"><h2 id="migration">Where are domestic movers actually going?</h2><p class="section-note">Census net domestic migration, July 1, 2023 to July 1, 2024. A mover count is not a policy score: IRS migration data can add adjusted gross income, while Census measures people.</p>{migration_table}</section>
<section aria-labelledby="federal"><h2 id="federal">Do blue states subsidize red states?</h2><div class="callout"><strong>Short answer:</strong> On this report's 2023 population-weighted average, Trump-won states received a larger positive federal balance per resident. That does not mean every red state is a recipient or every blue state a donor: only New Jersey, Massachusetts, and Washington were negative in 2023, while federal wages, procurement, bases, age, poverty, disasters, and progressive taxation drive the geography. Pandemic-era spending still affected the vintage.</div>{bop_table}</section>
<section aria-labelledby="mistakes"><h2 id="mistakes">Common mistakes</h2><div class="card-grid">{mistakes}</div></section>{map_script}'''
    theme = r'''
@layer base{:root{--accent:light-dark(#735a2a,#ffc85c);--accent2:light-dark(#41576b,#9db7cc);--paper:light-dark(#f4f0e7,#11161b);--panel:light-dark(#fffdf7,#1a2229);--ink:light-dark(#18212a,#f0f2f3);--line:light-dark(#9aa1a5,#3b464e)}body{font-variant-numeric:tabular-nums}.data-years{border:2px solid var(--line);background:var(--panel);padding:12px 14px;margin-bottom:22px}.score-label{font:900 .75rem ui-monospace,Consolas,monospace;letter-spacing:.14em;color:var(--accent)}.stadium{border:3px solid var(--line);padding:clamp(12px,3vw,28px);border-radius:16px;background:radial-gradient(circle at 50% 0,color-mix(in srgb,var(--accent) 12%,transparent),transparent 42%),var(--panel)}.scoreboard thead th:nth-child(2){box-shadow:inset 0 7px var(--accent2)}.scoreboard thead th:nth-child(3){box-shadow:inset 0 7px var(--accent)}.scoreboard td:nth-child(2),.scoreboard td:nth-child(3){font:800 1.05rem ui-monospace,Consolas,monospace;white-space:nowrap}.ledger-table{font-size:.78rem}.ledger-table td:not(:first-child){white-space:nowrap}.hero h1{max-width:15ch}}
@layer base{.map-stage{margin-top:0;padding:clamp(16px,3vw,30px);border:2px solid var(--line);border-radius:16px;background:var(--panel)}.map-stage .data-years{margin:-1px -1px 24px}.map-toolbar{display:none;gap:12px;flex-wrap:wrap;margin:20px 0}.js .map-toolbar{display:flex}.map-toolbar label{display:grid;gap:5px;color:var(--muted);font-size:.82rem;font-weight:800}.map-toolbar select{min-width:min(280px,80vw);padding:9px 34px 9px 10px;border:1px solid var(--line);border-radius:6px;background:var(--paper);color:var(--ink)}.map-toolbar select:focus-visible{outline:3px solid var(--accent);outline-offset:2px}.map-grid{display:grid;grid-template-columns:minmax(0,3fr) minmax(210px,1fr);gap:clamp(16px,3vw,30px);align-items:center}.map-figure{position:relative;margin:0;min-width:0}.economy-map{display:block;width:100%;height:auto;overflow:visible}.state-shape{stroke:var(--paper);stroke-width:1.25;vector-effect:non-scaling-stroke;cursor:pointer}.state-shape.side-trump,.map-swatch.side-trump{fill:var(--accent2);background:var(--accent2)}.state-shape.side-harris,.map-swatch.side-harris{fill:var(--accent);background:var(--accent)}.state-shape.q1,.map-swatch.q1{fill:color-mix(in srgb,var(--accent2) 85%,var(--panel));background:color-mix(in srgb,var(--accent2) 85%,var(--panel))}.state-shape.q2,.map-swatch.q2{fill:color-mix(in srgb,var(--accent2) 55%,var(--panel));background:color-mix(in srgb,var(--accent2) 55%,var(--panel))}.state-shape.q3,.map-swatch.q3{fill:color-mix(in srgb,var(--accent2) 22%,var(--accent) 22%,var(--panel));background:color-mix(in srgb,var(--accent2) 22%,var(--accent) 22%,var(--panel))}.state-shape.q4,.map-swatch.q4{fill:color-mix(in srgb,var(--accent) 55%,var(--panel));background:color-mix(in srgb,var(--accent) 55%,var(--panel))}.state-shape.q5,.map-swatch.q5{fill:color-mix(in srgb,var(--accent) 85%,var(--panel));background:color-mix(in srgb,var(--accent) 85%,var(--panel))}.state-shape.no-data{fill:var(--line)}.state-shape:hover,.state-shape:focus-visible,.state-shape.is-selected{stroke:var(--ink);stroke-width:3;outline:none}.map-legend{min-height:28px;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:.82rem}.map-legend-item{display:inline-flex;align-items:center;gap:6px}.map-swatch{display:inline-block;width:18px;height:12px;border:1px solid var(--line)}.map-detail{display:grid;gap:8px;padding:22px;border-left:3px solid var(--accent);background:color-mix(in srgb,var(--accent) 7%,var(--panel))}.map-detail-kicker{font:800 .75rem ui-monospace,Consolas,monospace;letter-spacing:.12em;color:var(--muted);text-transform:uppercase}.map-detail strong{font-size:clamp(1.45rem,3vw,2.25rem);line-height:1.05}.map-detail-value{font:900 clamp(1.5rem,4vw,2.7rem) ui-monospace,Consolas,monospace;color:var(--accent2);overflow-wrap:anywhere}.map-tooltip{position:absolute;z-index:2;max-width:260px;padding:7px 9px;border:1px solid var(--line);background:var(--ink);color:var(--paper);font-size:.8rem;pointer-events:none;box-shadow:0 6px 20px #0003}.map-tooltip[hidden]{display:none}@media(max-width:760px){.map-grid{grid-template-columns:1fr}.map-detail{border-left:0;border-top:3px solid var(--accent)}.map-toolbar label,.map-toolbar select{width:100%;min-width:0}}@media(prefers-reduced-motion:no-preference){.state-shape{transition:fill .18s ease,stroke-width .18s ease}}}
'''
    sources = f'''<ol>
<li><a href="https://www.bea.gov/data/gdp/gdp-state">BEA GDP by state</a>: 2024 current-dollar GDP and 2019–24 real GDP; <a href="https://apps.bea.gov/itable/?ReqID=70&amp;step=1">BEA RPP</a>: 2024 regional price levels.</li>
<li><a href="https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-r1901.xlsx">2024 ACS R1901 workbook</a>: median household income; <a href="https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-r1701.xlsx">ACS R1701 workbook</a>: official poverty; <a href="https://www2.census.gov/programs-surveys/popest/tables/2020-2024/state/totals/NST-EST2024-COMP.xlsx">Census Vintage 2024 components</a>: population and domestic migration.</li>
<li><a href="https://www.bls.gov/opub/ted/2025/annual-average-unemployment-rates-increased-in-21-states-in-2024.htm">BLS 2024 annual state unemployment</a>.</li>
<li><a href="https://taxfoundation.org/data/all/state/tax-burden-by-state-2022/">Tax Foundation 2022 state-local burden model</a>, built from Census state/local finance and BEA income data. This is a modeled burden, not a statutory rate.</li>
<li><a href="https://rockinst.org/issue-area/bop-2025/">Rockefeller Institute 2025 report</a>, Tables 5–6: FFY 2023 federal receipts, expenditures, and balance by state. DC is not ranked.</li>
<li><a href="https://www.fec.gov/resources/cms-content/documents/federalelections2024.pdf">Federal Election Commission, Federal Elections 2024</a> for the fixed classification.</li>
<li><a href="https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_us_state_20m.zip">Census 2024 Cartographic Boundary Files</a>, 1:20,000,000 KML, for the state map geometry.</li>
</ol><p><strong>Method:</strong> pooled totals sum states. Pooled rates and state-median measures are population-weighted descriptive averages, not microdata estimates. The generator downloads the official source files and rebuilds the table; tax and federal-balance vintages are intentionally labeled because they lag.</p>'''
    return document(
        title="Red State vs Blue State Economies: The Actual Numbers",
        description="Red and blue states compared on GDP, income, prices, growth, jobs, migration, taxes, poverty, and federal balance, with every state and data year shown.",
        keywords="red states vs blue states economy, total GDP red vs blue states, state migration, state tax burden, federal balance of payments",
        filename="red-vs-blue-state-economies.html", h1="Red vs Blue State Economies",
        eyebrow="Box score · every measure, sourced",
        lede="No thesis, no composite score, no purple-state escape hatch. Fix the teams by the 2024 presidential result, put every measure on the same board, and show exactly where the verdict changes.",
        theme_css=theme, content=content,
        image_alt="Neutral sports-style scoreboard comparing Trump-won and Harris-won state economies across ten sourced measures",
        sources=sources,
        related=[("US States vs Countries", "us-states-vs-countries-gdp.html"), ("Economic Systems Compared", "economic-systems-compared.html"), ("The Household Numbers", "the-household-numbers.html"), ("Housing Comparison", "housing-comparison.html"), ("Index Investing", "index-investing-tax-advantaged.html")],
    )


def main() -> int:
    print("Loading current primary-source tables...")
    states = load_states()
    countries = load_countries()
    if len(states) != 51:
        raise RuntimeError(f"expected 51 state/DC rows, got {len(states)}")
    if len(countries) < 150:
        raise RuntimeError(f"country filter looks wrong: only {len(countries)} economies")

    pages = {
        "economic-systems-compared.html": build_economic_systems(),
        "political-ideologies-compared.html": build_political_ideologies(),
        "us-states-vs-countries-gdp.html": build_states_vs_countries(states, countries),
        "red-vs-blue-state-economies.html": build_red_blue(states),
    }
    for filename, source in pages.items():
        marker = (
            "<!-- Generated by scripts/build_economics_batch.py; "
            f"primary-source data retrieved {VERIFIED}. -->\n"
        )
        path = ROOT / filename
        path.write_text(marker + source, encoding="utf-8", newline="\n")
        print(f"wrote {path.name}: {len(source):,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
