# Gravity diagram reference edits

These assets improve the existing diagrams on `artificial-gravity-calculator.html`.
They preserve their teaching content and layout. They are not new orbital environment
concept art or captures from the Concordia simulation.

`manifest.json` records the prompts, reference selectors, original revision, alt text,
and published dimensions. The built-in image_gen tool edited screenshots of the
original SVGs. The original ring's rotation arrow was corrected to agree with the
tangential velocity at the bottom. Its inward-force label was moved beside that force.

Twelve complete diagrams are lossless WebP. A transparent human symbol replaces the
stick figures in the six reference plates and the live rotor diagram. Their SVG
text, chart coordinates, geometry and calculated values remain native. Do not bake
calculator results into generated artwork.

To repeat an edit, capture the relevant diagram in the browser, provide it to the
image tool as the edit target, and use an approved diagram as the style reference.
Check labels, orientations, path endpoints and physical meaning individually. The
masthead should show counterclockwise rotation, rightward velocity at the bottom,
and inward floor push. Do not infer scientific accuracy from attractive rendering.

Import tool outputs with `python scripts/prepare_gravity_art.py <local-import.json>`.
Each record supplies `key`, `slug`, `source`, `prompt`, `selector`, and `index`.
Use the manifest keys and selectors; the human symbol has null selector/index.
The helper keeps PNG masters under ignored `.scratch/gravity-art/` and uses ffmpeg
for lossless WebP exports. It trims only the transparent symbol's empty margins.
Then regenerate with `python scripts/build_gravity_illustrations.py`, run its
`--check`, and run `scripts/check_gravity_illustrations.py` against a local server.
Inspect the light/dark mobile and desktop captures before publication.
