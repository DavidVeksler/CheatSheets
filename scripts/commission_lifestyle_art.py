"""Commission the six stage illustrations for lifestyle-calculator.html.

Reuses the Codex-CLI image backend (with OpenAI Images API backup) from the sibling
freecapitalists.org repo, so that repo must be checked out next to this one.

    python scripts/commission_lifestyle_art.py generate            # all six stages
    python scripts/commission_lifestyle_art.py generate 3 5        # just stages 3 and 5
    python scripts/commission_lifestyle_art.py install             # PNG masters -> images/lifestyle/stage-N.webp

Masters (1536x1024 PNG) live in the gitignored-by-convention scratch dir
$LIFESTYLE_ART_DIR (default: <repo>/.scratch/lifestyle-art); only the WebP goes in git.
"""
from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FC = ROOT.parent / "freecapitalists.org" / "scripts"
sys.path.insert(0, str(FC))
MASTERS = Path(os.environ.get("LIFESTYLE_ART_DIR", ROOT / ".scratch" / "lifestyle-art"))
OUT = ROOT / "images" / "lifestyle"
PAGE_SIZE = (1200, 800)
WEBP_QUALITY = 70

STYLE = (
    "Use case: stylized-concept. One original wide editorial illustration for a personal-finance "
    "reference page, showing what a household's annual income buys. Modern flat editorial illustration "
    "with soft gouache texture and subtle paper grain, clean shapes, gentle gradients, warm natural light. "
    "The same recurring family appears in every picture in the series: two parents and two children "
    "(a girl about 9 and a boy about 6), stylised and friendly, faces simple and expressive, not photoreal. "
    "COMPOSITION: wide 3:2 landscape. The page crops it to a wide banner around the vertical middle, so keep the "
    "family and the key action inside the middle horizontal band (roughly 30% to 75% of the height); the top "
    "and bottom may be cropped away. One clear focal group, readable at small size, not a crowd. "
    "HARD EXCLUSIONS: no text, lettering, numbers, signage, logos, brand marks, watermark, border or frame. "
    "No photorealism, no waxy faces, no caricature, no clip-art look. "
)

STAGES = {
    1: "PALETTE: muted slate blue, grey, dusty teal, warm lamp yellow. SCENE: a small, tidy one-bedroom apartment "
       "kitchen at dusk. The family of four shares a modest dinner at a small folding table; a paper grocery bag, "
       "a bus-pass lanyard on a hook and a window showing a city bus stop and rain outside. Cosy but tight, "
       "dignified, warm lamp against a cool evening.",
    2: "PALETTE: clean sky blue, teal, white, a little coral. SCENE: a small rented townhouse living room on a "
       "weekend morning. Parents at a table with a notebook and coffee planning a budget while the two children do "
       "homework on the floor; through the window a used compact sedan sits in the driveway. Calm, steady, "
       "hopeful, breathing room.",
    3: "PALETTE: fresh green, sunny yellow, warm wood, sky blue. SCENE: a suburban backyard on a summer afternoon. "
       "The family has a barbecue on a wooden deck; children's bikes on the lawn, a comfortable two-storey house "
       "behind them, a family SUV in the driveway, a small vegetable garden. Relaxed abundance and choices.",
    4: "PALETTE: warm terracotta, apricot, cream, deep teal accents. SCENE: a modern architect-designed house "
       "with large glass walls at golden hour. The family sits at a long outdoor dining table on a terrace by a "
       "small pool, luggage and skis stacked by the door hinting at a trip, an electric car parked below, "
       "city hills in the distance. Polished, convenient, quality by default.",
    5: "PALETTE: rich gold, honey, burgundy, deep olive. SCENE: a private vineyard estate at sunset. The family "
       "walks the gravel drive between vines toward a grand stone house with a veranda and a guest cottage; "
       "a horse paddock and a classic car in the distance, an advisor-like older gentleman in conversation "
       "with the parents at a distance. Generous, unhurried, assets working quietly.",
    6: "PALETTE: deep midnight navy, electric cyan, silver, a few warm window lights. SCENE: twilight on a sea-cliff "
       "estate terrace. Three generations of the family (grandparents, parents, the two children) gather at the "
       "terrace rail looking over a moonlit bay where a large yacht rests at anchor and a distant lit coastline "
       "glows. Quiet, expansive, legacy and stewardship, cinematic but still warm.",
}


def paths(n: int) -> tuple[Path, Path]:
    return MASTERS / f"stage-{n}.png", OUT / f"stage-{n}.webp"


def cmd_generate(stages: list[int]) -> int:
    from commission_covers import generate_image  # noqa: E402  (sibling repo)
    MASTERS.mkdir(parents=True, exist_ok=True)
    failed = 0
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = {pool.submit(generate_image, "codex", STYLE + STAGES[n], MASTERS, "1536x1024",
                            "editorial illustration", "landscape 3:2"): n for n in stages}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                blob = fut.result()[0]
            except Exception as exc:  # noqa: BLE001
                failed += 1
                print(f"stage {n}: FAILED {exc}", flush=True)
                continue
            dest = MASTERS / f"stage-{n}-new.png"
            dest.write_bytes(blob)
            print(f"stage {n}: wrote {dest}", flush=True)
    return 1 if failed else 0


def cmd_install(stages: list[int]) -> int:
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    for n in stages:
        master, dest = paths(n)
        if not master.exists():
            print(f"stage {n}: no master at {master}")
            continue
        im = Image.open(master).convert("RGB").resize(PAGE_SIZE, Image.LANCZOS)
        im.save(dest, "WEBP", quality=WEBP_QUALITY, method=6)
        print(f"stage {n}: {dest} ({dest.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"generate", "install"}:
        raise SystemExit(__doc__)
    nums = [int(a) for a in sys.argv[2:]] or sorted(STAGES)
    raise SystemExit(cmd_generate(nums) if sys.argv[1] == "generate" else cmd_install(nums))
