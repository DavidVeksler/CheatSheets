"""Regenerate spin-gravity diagrams and integrate reference-edited image assets.

The sheet keeps embedded CSS/JS and loads local optimized illustration assets. The sibling repo is
only an authoring dependency, as with check_concordia_links.py. No fetches or
simulation embed. Use --check in QA, HABITAT_REPO to override the sibling path.
"""
from pathlib import Path
from html import escape
import os
import json
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
HABITAT = Path(os.environ.get('HABITAT_REPO', ROOT.parent / 'Habitat'))
lib = runpy.run_path(str(HABITAT / 'scripts/site/build-editorial-graphics.py'))
drawings = lib['DRAWINGS']
for fn in ['text','lines','path','rect','circle','arrow','person','tree','building','train','ship','tag']:
    globals()[fn] = lib[fn]
INK, PAPER, SOFT, TEAL, GOLD, MUTED = [lib[k] for k in ['INK','PAPER','SOFT','TEAL','GOLD','MUTED']]


def palette(s):
    return s.replace('--text,','--ink,').replace('--surface-2,','--paper,').replace('--accent-2,','--accent,').replace('--accent, #28798a','--blue, #28798a')


def block(key, content):
    if key in ('styles', 'live-script'):
        return f'/* gravity-art:{key} */\n{content}\n/* /gravity-art:{key} */'
    return f'<!-- gravity-art:{key} -->\n{content}\n<!-- /gravity-art:{key} -->'



ART = json.loads((ROOT/'design/gravity-art/manifest.json').read_text(encoding='utf-8'))['assets']


def polish(svg, key):
    """Improve human symbols without moving any chart data or labels."""
    def person_group(m):
        if 'M0 -38 V-16' not in m.group(2):
            return m.group(0)
        transform = m.group(1)
        if key == 'same-gravity-four-sizes':
            # Put the feet on each existing quadratic floor curve at its midpoint.
            pos = re.search(r'translate\(([\d.]+) 350\)', transform)
            if pos:
                i = round((float(pos.group(1))-147)/244)
                floor_y = 365 if i == 0 else 347.5 if i == 1 else 342.5
                transform = transform.replace(' 350)', f' {floor_y})', 1)
        return (f'<g transform="{transform}"><image href="{ART["person"]["src"]}" '
                'x="-15" y="-55" width="30" height="55" preserveAspectRatio="xMidYMax meet"/></g>')
    svg = re.sub(r'<g transform="([^"]+)">((?:(?!</g>)[\s\S])*?)</g>', person_group, svg)
    return svg


def figure(key, caption):
    return '<figure class="gravity-art"><div class="gravity-art-scroll" tabindex="0" role="group" aria-label="Illustration; scroll horizontally on a narrow screen">'+polish(palette(drawings[key]), key)+'</div><figcaption>'+caption+'</figcaption></figure>'


def art_image(key, css_class, eager=False):
    item = ART[key]
    src = item['src']
    if not (ROOT/src).is_file():
        raise SystemExit('Missing gravity illustration: '+src)
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img class="{css_class}" src="{escape(src, quote=True)}" '
            f'width="{item["width"]}" height="{item["height"]}" '
            f'alt="{escape(item["alt"], quote=True)}" {loading} decoding="async">')


def card(i):
    return art_image(f'field-{i}', 'field-art')


MAST = ('<figure class="mast-art">'+art_image('mast', 'mast-diagram', eager=True)+
        '<figcaption>Spin gravity, seen from outside. Person enlarged.</figcaption></figure>')


live = '<figure class="gravity-art live-art"><svg id="rotorDiagram" viewBox="0 0 800 440" role="img" aria-labelledby="live-rotor-title live-rotor-desc"><title id="live-rotor-title">Your rotating habitat</title><desc id="live-rotor-desc">A schematic ring shows the radius, person, velocity and inward floor push. Values update with the calculator.</desc>'+palette(circle(218,215,151,SOFT,TEAL,5)+circle(218,215,6,INK,'none')+person(218,364,1.05)+arrow(218,308,218,248,GOLD,4)+arrow(246,363,334,363,TEAL,3)+arrow(218,215,360,215,INK,2)+path('M368 249 Q394 171 344 115',TEAL,3)+arrow(352,124,344,115,TEAL,2))+'<text x="475" y="115" class="rotor-label">YOUR DESIGN</text><text id="rd-radius" x="475" y="160" class="rotor-value">Radius</text><text id="rd-rpm" x="475" y="204" class="rotor-value">Spin</text><text id="rd-gravity" x="475" y="248" class="rotor-value">Weight</text><text id="rd-speed" x="475" y="292" class="rotor-value">Rim speed</text><text x="250" y="202" class="rotor-small">radius</text><text x="250" y="282" class="rotor-small">floor push</text><text x="260" y="394" class="rotor-small">velocity</text><text x="475" y="348" class="rotor-small">Person enlarged; ring is schematic.</text><text id="rd-head" x="475" y="380" class="rotor-small">Head-to-foot gradient</text></svg><figcaption>Velocity runs along the rim. The floor pushes inward, bending your path into a circle. The same force is felt as weight.</figcaption></figure>'

live = polish(live, 'live')

live = live.replace('<svg id=', '<div class="gravity-art-scroll" tabindex="0" role="group" aria-label="Live calculator illustration; scroll horizontally on narrow screens"><svg id=').replace('</svg><figcaption>', '</svg></div><figcaption>')

CSS = '''@layer components {
  .gravity-art { margin: 1.4rem 0; border: 1px solid var(--rule); background: var(--surface); }
  .gravity-art-scroll { overflow-x: auto; }
  .mast-diagram { width: 100%; height: auto; border: 1px solid var(--rule); border-radius: 4px; }
  .field-art { background: #fcf7ed; border-radius: 4px; }
  .gravity-art svg, .mast-art svg { display: block; width: 100%; height: auto; }
  .gravity-art .editorial-graphic { min-width: 660px; }
  .gravity-art figcaption, .mast-art figcaption { padding: .6rem .9rem; color: var(--muted); font-size: .8rem; }
  .mast-art { margin: 1rem 0 0; max-width: 420px; justify-self: center; }
  .card { grid-template-columns: 1fr; }
  .card h3, .card .big { grid-column: 1 / -1; }
  .field-art { grid-column: 1 / -1; width: 100%; height: auto; margin: .5rem 0; border-block: 1px solid var(--rule-soft); }
  .rotor-value { fill: var(--ink); font: 600 25px var(--mono); }
  .rotor-label { fill: var(--blue); font: 700 16px var(--mono); }
  .rotor-small { fill: var(--muted); font: 17px var(--sans); }
  @media (min-width: 900px) {
    .mast .wrap { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(280px, 1fr); gap: 0 2rem; }
    .mast .eyebrow, .mast h1 { grid-column: 1 / -1; }
    .mast .lede, .mast .stamp { grid-column: 1; }
    .mast-art { grid-column: 2; grid-row: 3 / 5; align-self: center; }
  }
  @media (max-width: 600px) { .live-art svg { min-width: 610px; } .live-art { overflow-x: auto; } }
}'''

JS = '''function drawRotorDiagram(g, d) {
  $('rd-radius').textContent = f(state.r, 4) + ' m radius';
  $('rd-rpm').textContent = f(d.rpm, 3) + ' rpm';
  $('rd-gravity').textContent = f(g, 3) + ' g at the feet';
  $('rd-speed').textContent = f(d.rimSpeedMs, 4) + ' m/s at the rim';
  $('rd-head').textContent = f(d.gradientPct, 3) + '% head-to-foot gradient';
  $('live-rotor-desc').textContent = 'Your design: ' + f(state.r, 4) + ' m radius, ' + f(d.rpm, 3) + ' rpm, ' + f(g, 3) + ' g at the floor. Velocity is tangential. The floor pushes inward. Person enlarged.';
}'''


def main():
    page=ROOT/'artificial-gravity-calculator.html'
    original=page.read_text(encoding='utf-8'); s=original
    def put(key,body,anchor,before=True):
        nonlocal s
        content=block(key,body)
        pattern=rf'(?:<!--|/\*) gravity-art:{re.escape(key)} (?:-->|\*/)[\s\S]*?(?:<!--|/\*) /gravity-art:{re.escape(key)} (?:-->|\*/)'
        if re.search(pattern,s):s=re.sub(pattern,lambda _:content,s,count=1)
        else:
            if anchor not in s:raise ValueError('Missing insertion anchor: '+anchor)
            s=s.replace(anchor,content+'\n'+anchor if before else anchor+'\n'+content,1)
    put('styles',CSS,'</style>')
    put('mast',MAST,'  </div>\n</header>')
    put('live',live,'<section class="plate" id="weight"')
    put('sizes',figure('same-gravity-four-sizes','Computed 1 g examples. Human figures are enlarged; local floor views have different scales.'),'<section class="plate" id="height"')
    put('height',figure('gravity-pressure-height','Concordia design geometry. Pressure is a derived isothermal estimate at 293 K.'),'<section class="plate" id="coriolis"')
    put('motion',figure('motion-directions','Travel direction matters: the Coriolis term vanishes for motion parallel to the axis.'),'<section class="plate" id="tolerance"')
    put('evidence',figure('rotation-evidence','Selected experimental setups; see the cited studies in Comfort limits and Sources.'),'<section class="plate" id="designs"')
    put('shapes',figure('habitat-shapes','Schematic detail views at independent scales. Historical proposals and Concordia’s fictional design are distinguished in the table.'),'<h3>What each design traded</h3>')
    put('coin',figure('release-two-frames','Concordia’s 2 m drop with no air drag. Sideways lag is enlarged in the floor view.'),'<section class="plate" id="engineering"')
    # Replace the eleven repeated placeholder glyphs, without touching their text.
    start=s.index('<section class="plate" id="field-guide"'); end=s.index('</section>',start)
    field=s[start:end]; index=iter(range(11))
    field=re.sub(r'<svg class="(?:glyph|field-art)"[\s\S]*?</svg>|<img class="field-art"[^>]*>',lambda m:card(next(index)),field)
    if field.count('class="field-art"')!=11:raise ValueError('Expected eleven field-guide illustrations')
    s=s[:start]+field+s[end:]
    put('live-script',JS,'function render() {')
    if '  drawRotorDiagram(g, d);' not in s:s=s.replace('  const rpm = d.rpm;','  const rpm = d.rpm;\n  drawRotorDiagram(g, d);',1)
    # Existing comparison tables also scroll on phones. Let keyboard users reach them.
    s=s.replace('<div class="tw">','<div class="tw" tabindex="0" role="group" aria-label="Reference table; scroll horizontally on narrow screens">')
    if '--check' in sys.argv:
        if s!=original:raise SystemExit('Embedded gravity illustrations are stale; regenerate first.')
        print('Embedded illustrations match the source.')
    else:
        page.write_text(s,encoding='utf-8',newline='\n');print('Integrated 12 reference-edited diagrams, 6 exact SVG plates and live calculator symbols.')


if __name__=='__main__':main()
