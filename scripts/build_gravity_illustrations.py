"""Regenerate embedded spin-gravity illustrations from the companion Habitat source.

The published sheet remains one self-contained HTML file. The sibling repo is
only an authoring dependency, as with check_concordia_links.py. No fetches or
simulation embed. Use --check in QA, HABITAT_REPO to override the sibling path.
"""
from pathlib import Path
from html import escape
import os
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


def figure(key, caption):
    return '<figure class="gravity-art"><div class="gravity-art-scroll" tabindex="0" role="group" aria-label="Illustration; scroll horizontally on a narrow screen">'+palette(drawings[key])+'</div><figcaption>'+caption+'</figcaption></figure>'


def card(i):
    b=''
    if i==0:
        b+=path('M25 60 Q160 160 295 60',TEAL,5)
        b+=person(75,90,.65,INK,35)+person(245,90,.65,INK,-35)
        b+=text(160,146,'Down follows the local floor',15,MUTED,'middle')
    elif i==1:
        b+=train(22,66)+train(184,66,GOLD)+arrow(120,44,32,44,TEAL)+arrow(190,44,280,44,GOLD)
        b+=text(75,143,'0.66 g',20,TEAL,'middle',700)+text(235,143,'1.33 g',20,GOLD,'middle',700)
    elif i==2:
        b+=person(179,140,1.6)+path('M25 140 H295',TEAL,3)+path('M146 49 Q146 90 111 136',GOLD,3)
        for x,y in [(146,49),(144,78),(135,106),(111,136)]: b+=circle(x,y,4,GOLD,'none')
        b+=path('M147 49 V140',MUTED,1,stroke_dasharray='4 5')+text(30,31,'Sideways lag enlarged',14,MUTED)
    elif i==3:
        b+=rect(140,20,30,120,SOFT,INK,2)+rect(130,61,50,44,PAPER,TEAL,3)+arrow(105,120,105,41,TEAL)
        b+=text(195,54,'Climb',18,TEAL)+text(195,80,'Weight falls',16,MUTED)+text(195,106,'1 g → 0.82 g',16,INK)
    elif i==4:
        b+=path('M30 140 H290 M30 20 H290',TEAL,3)+person(160,139,1)+person(160,21,1,INK,180)
        b+=arrow(73,120,73,39,GOLD,2)+text(245,84,'Inward',17,MUTED,'middle')
    elif i==5:
        b+=path('M38 100 L160 42 L282 100 L160 76 Z',TEAL,3,SOFT)+person(160,130,.7)
        b+=arrow(55,134,55,94,GOLD)+text(245,140,'Less lift aloft',16,MUTED,'middle')
    elif i==6:
        b+=circle(160,80,65,SOFT,TEAL,3)+circle(160,80,8,GOLD,'none')+person(155,104,.75,INK,30)
        b+=text(44,29,'Near-zero g',16,TEAL)+path('M54 35 L126 64',MUTED,1)
    elif i==7:
        b+=circle(91,81,49,SOFT,TEAL,5)+circle(227,81,49,SOFT,GOLD,5)
        b+=arrow(62,18,123,18,TEAL,2)+arrow(258,18,197,18,GOLD,2)
        b+=text(160,153,'Opposing angular momentum',16,MUTED,'middle')
    elif i==8:
        b+=path('M25 130 H295',TEAL,3)+path('M44 103 Q110 105 168 130',GOLD,3)+path('M44 102 Q150 25 272 75',TEAL,3)
        b+=circle(44,103,5,INK,'none')+text(160,157,'Spinward / antispinward paths',15,MUTED,'middle')
    elif i==9:
        b+=path('M79 35 h67 v34 h-67 Z M146 39 q34 0 27 24 h-27',INK,3,SOFT)
        b+=path('M145 69 Q153 93 187 118',TEAL,3)+path('M167 112 v32 h52 v-32',INK,3)+text(28,158,'Stream bends more at small radius',15,MUTED)
    else:
        b+=rect(38,30,244,105,SOFT,INK,3)
        for xx,yy in [(65,110),(87,100),(112,116),(137,101),(165,114),(192,102),(222,111),(252,102),(78,80),(110,75),(141,81),(175,71),(218,76),(252,78),(98,52),(150,51),(208,51)]:b+=circle(xx,yy,3,TEAL,'none')
        b+=text(160,158,'Lower pressure ≠ vacuum',16,MUTED,'middle')
    titles=['Local down around the curved floor','Trains in opposing directions change apparent weight','A dropped coin lags behind the floor','A lift ascends as apparent weight falls','People on opposite sides both stand toward the axis','A glider needs less lift at altitude','A person floats close to the axis','Opposing rotors cancel angular momentum','Throws in opposite directions follow different curves','A pouring stream curves sideways','Air remains near the axis despite near-zero weight']
    return palette(f'<svg class="field-art" viewBox="0 0 320 175" role="img" aria-label="{escape(titles[i],quote=True)}" xmlns="http://www.w3.org/2000/svg">{b}</svg>')


mast = circle(210,185,133,SOFT,TEAL,5)+circle(210,185,6,INK,'none')+person(210,316,1.1)
mast += arrow(210,274,210,218,GOLD,4)+arrow(235,315,310,315,TEAL,3)
mast += text(210,37,'A FLOOR THAT TURNS',18,INK,'middle',700)
mast += text(293,211,'Floor push',16,GOLD)+text(274,344,'Velocity',16,TEAL)
mast += path('M330 153 Q347 197 324 238',TEAL,3)+arrow(331,228,324,238,TEAL,2)
mast += text(210,384,'Down is toward the rim.',18,INK,'middle')
mast += text(210,410,'The floor pushes toward the axis.',17,MUTED,'middle')
MAST = palette('<figure class="mast-art"><svg viewBox="0 0 420 440" role="img" aria-label="A person stands inside a rotating ring. Velocity is tangential; the floor pushes inward toward the axis." xmlns="http://www.w3.org/2000/svg">'+mast+'</svg><figcaption>Spin gravity, seen from outside. Person enlarged.</figcaption></figure>')

live = '<figure class="gravity-art live-art"><svg id="rotorDiagram" viewBox="0 0 800 440" role="img" aria-labelledby="live-rotor-title live-rotor-desc"><title id="live-rotor-title">Your rotating habitat</title><desc id="live-rotor-desc">A schematic ring shows the radius, person, velocity and inward floor push. Values update with the calculator.</desc>'+palette(circle(218,215,151,SOFT,TEAL,5)+circle(218,215,6,INK,'none')+person(218,364,1.05)+arrow(218,308,218,248,GOLD,4)+arrow(246,363,334,363,TEAL,3)+arrow(218,215,360,215,INK,2)+path('M344 115 Q394 171 368 249',TEAL,3)+arrow(372,239,368,249,TEAL,2))+'<text x="475" y="115" class="rotor-label">YOUR DESIGN</text><text id="rd-radius" x="475" y="160" class="rotor-value">Radius</text><text id="rd-rpm" x="475" y="204" class="rotor-value">Spin</text><text id="rd-gravity" x="475" y="248" class="rotor-value">Weight</text><text id="rd-speed" x="475" y="292" class="rotor-value">Rim speed</text><text x="250" y="202" class="rotor-small">radius</text><text x="250" y="282" class="rotor-small">floor push</text><text x="260" y="394" class="rotor-small">velocity</text><text x="475" y="348" class="rotor-small">Person enlarged; ring is schematic.</text><text id="rd-head" x="475" y="380" class="rotor-small">Head-to-foot gradient</text></svg><figcaption>Velocity runs along the rim. The floor pushes inward, bending your path into a circle. The same force is felt as weight.</figcaption></figure>'

live = live.replace('<svg id=', '<div class="gravity-art-scroll" tabindex="0" role="group" aria-label="Live calculator illustration; scroll horizontally on narrow screens"><svg id=').replace('</svg><figcaption>', '</svg></div><figcaption>')

CSS = '''@layer components {
  .gravity-art { margin: 1.4rem 0; border: 1px solid var(--rule); background: var(--surface); }
  .gravity-art-scroll { overflow-x: auto; }
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
    field=re.sub(r'<svg class="(?:glyph|field-art)"[\s\S]*?</svg>',lambda m:card(next(index)),field)
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
        page.write_text(s,encoding='utf-8',newline='\n');print('Embedded 11 field scenes, 6 reference plates, masthead and live calculator diagram.')


if __name__=='__main__':main()
