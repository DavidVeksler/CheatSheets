"""Render the keyspace sheet's deterministic 1200x630 Open Graph image."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "images" / "bitcoin-key-derivation-bips.png"
W, H = 1200, 630
im = Image.new("RGB", (W, H), "#07111F")
d = ImageDraw.Draw(im)
for x in range(0, W, 38):
    d.line((x, 0, x, H), fill="#10273A", width=1)
for y in range(0, H, 38):
    d.line((0, y, W, y), fill="#10273A", width=1)
font_dir = Path("C:/Windows/Fonts")
def font(name, size):
    try:
        return ImageFont.truetype(str(font_dir / name), size)
    except OSError:
        return ImageFont.load_default()

display = font("segoeuib.ttf", 74)
subtitle = font("segoeui.ttf", 27)
mono = font("consola.ttf", 25)
tiny = font("consola.ttf", 19)
d.text((66, 56), "BITCOIN / BEGINNER WALKTHROUGH", fill="#4CC9F0", font=tiny)
d.text((62, 96), "How 12 words become", fill="#EDF6F9", font=display)
d.text((62, 176), "a Bitcoin address", fill="#EDF6F9", font=display)
d.text((67, 283), "One real example, six steps", fill="#9BB0C1", font=subtitle)

steps = [("Words", "#FF5D73"), ("Seed", "#FF5D73"), ("Master key", "#FF5D73"),
         ("Your key", "#FF5D73"), ("Public key", "#7AE582"), ("Address", "#7AE582")]
x0, y, gap = 90, 430, 196
for i, (label, color) in enumerate(steps):
    x = x0 + i * gap
    if i:
        d.line((x - gap + 16, y, x - 16, y), fill="#31516A", width=4)
    d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=color)
    d.text((x, y + 34), label, fill="#EDF6F9", font=mono, anchor="ma")
d.text((90, 540), "red = keep secret   green = safe to share", fill="#9BB0C1", font=tiny)
d.text((1134, 584), "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu", fill="#C7F9CC", font=tiny, anchor="ra")
OUT.parent.mkdir(exist_ok=True)
im.save(OUT, optimize=True)
print(OUT)
