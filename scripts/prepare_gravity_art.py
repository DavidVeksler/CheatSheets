"""Import reference-edited gravity diagrams and encode lossless WebP assets.

Usage: python scripts/prepare_gravity_art.py .visual-qa/gravity-art-import.json
Input records: key, slug, source (PNG), prompt, selector, index.
The original masters stay in ignored .scratch; published metadata has no local paths.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    if {r['key'] for r in records} != {'mast', 'person', *(f'field-{i}' for i in range(11))}:
        raise SystemExit('Expected the masthead, human symbol and eleven field-guide edits.')
    page = BeautifulSoup((ROOT/'artificial-gravity-calculator.html').read_text(encoding='utf-8'), 'html.parser')
    target = ROOT/'images/artificial-gravity'
    masters = ROOT/'.scratch/gravity-art'
    target.mkdir(exist_ok=True)
    masters.mkdir(parents=True, exist_ok=True)
    metadata = {'tool': 'Built-in image_gen, reference edits of existing diagrams',
                'created': '2026-11-04',
                'reference_revision': subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip(),
                'assets': {}}
    for r in records:
        original = page.select(r['selector'])[r['index']] if r['selector'] else None
        source = Path(r['source'])
        master = masters/(r['slug']+'.png')
        shutil.copy2(source, master)
        dest = target/(r['slug']+'.webp')
        width = 840 if r['key'] == 'mast' else 960
        filters = f'scale={width}:-1'
        if r['key'] == 'person':
            with Image.open(master) as im:
                if im.mode != 'RGBA':
                    raise SystemExit('The human symbol requires a transparent background.')
                x0, y0, x1, y1 = im.getchannel('A').getbbox()
            filters = f'crop={x1-x0}:{y1-y0}:{x0}:{y0},scale=-1:330'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(master), '-vf', filters,
                        '-c:v', 'libwebp', '-lossless', '1', '-compression_level', '6', str(dest)], check=True)
        with Image.open(dest) as im:
            w, h = im.size
            if im.format != 'WEBP':
                raise SystemExit('Expected WebP.')
        label = original.get('aria-label', original.get('alt', '')) if original else 'Enlarged standing person, upright with feet at the local floor.'
        text = original.get_text(' ', strip=True) if original else ''
        if text:
            label += ' Labels: '+text+'.'
        if r['key'] == 'mast':
            label = ('A person stands inside the bottom of a circular rotor. Counterclockwise rotation gives '
                     'rightward velocity at the bottom. The floor pushes inward toward the axis. Person enlarged.')
        metadata['assets'][r['key']] = {'src': dest.relative_to(ROOT).as_posix(), 'width': w, 'height': h,
                                        'alt': label, 'prompt': r['prompt'], 'reference_selector': r['selector'],
                                        'reference_index': r['index']}
    (ROOT/'design/gravity-art/manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Prepared {len(records)} lossless diagram assets; originals preserved in .scratch/gravity-art.')


if __name__ == '__main__':
    main()
