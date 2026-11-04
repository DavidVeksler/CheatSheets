"""Numerical and browser acceptance for rocket-equation-calculator.html.

Start a static server, then python scripts/check_rocket_equation.py --base URL.
--render-og writes the required 1200x630 preview from the working calculator.
"""
import argparse
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.visual-qa/rocket-equation'
OUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', default='http://127.0.0.1:8766')
parser.add_argument('--render-og', action='store_true')
args = parser.parse_args()
URL = args.base.rstrip('/') + '/rocket-equation-calculator.html'


def near(actual, expected, label):
    assert math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-9), (label, actual, expected)


with sync_playwright() as p:
    browser = p.chromium.launch(args=['--mute-audio'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL, wait_until='domcontentloaded')
    assert page.evaluate('!!window.rocketCalculator')
    cases = [
        ('chemical', 100000, 10000, 3432.3275, 1000000),
        ('ion', 1200, 1000, 29419.95, 0.1),
        ('passage', 10000000, 6065306.597126334, 200000, 63700),
        ('tug', 135800, 100000, 24516.625, 85),
        ('ascent', 45000 * math.exp(3000 / (345 * 9.80665)), 45000, 3383.29425, 221000),
    ]
    for name, wet, final, ve, thrust in cases:
        page.locator(f'[data-preset="{name}"]').click()
        r = page.evaluate('rocketCalculator.getResult()')
        for key, value in {'wet': wet, 'final': final, 've': ve, 'thrust': thrust,
                           'dv': ve * math.log(wet / final), 'prop': wet - final,
                           'flow': thrust / ve, 'burn': (wet - final) * ve / thrust,
                           'power': thrust * ve / 2, 'a0': thrust / wet, 'af': thrust / final}.items():
            near(r[key], value, name + ':' + key)
        page.select_option('#mode', 'mission')
        inverse = page.evaluate('rocketCalculator.getResult()')
        near(inverse['wet'], wet, name + ' inverse mass')
    page.locator('#reset').click()
    baseline = page.evaluate('rocketCalculator.getResult()')
    # Units preserve the physical configuration, including after loading presets.
    for selector, value in [('#mass-unit', '1'), ('#exhaust-unit', 'velocity'),
                             ('#thrust-unit', '1000000'), ('#mass-unit', '1000')]:
        page.select_option(selector, value)
        r = page.evaluate('rocketCalculator.getResult()')
        near(r['dv'], baseline['dv'], selector)
        near(r['thrust'], baseline['thrust'], selector)
    page.locator('[data-preset="ion"]').click()
    page.select_option('#mass-unit', '1')
    assert float(page.input_value('#wet')) == 1200
    page.select_option('#mass-unit', '1000')
    page.select_option('#constraint', 'power')
    r = page.evaluate('rocketCalculator.getResult()')
    old_thrust, old_ve = r['thrust'], r['ve']
    page.fill('#exhaust', '6000')
    r = page.evaluate('rocketCalculator.getResult()')
    near(r['ve'], old_ve * 2, 'doubled Isp')
    near(r['thrust'], old_thrust / 2, 'fixed-power thrust')
    page.select_option('#power-unit', '1000')
    near(page.evaluate('rocketCalculator.getResult().thrust'), old_thrust / 2, 'power units')
    # Blank/negative/non-physical/overflow inputs retain valid output and explain why.
    for selector, value in [('#exhaust', ''), ('#exhaust', '-1'), ('#exhaust', '1e12')]:
        page.fill(selector, value)
        assert page.locator('#error').inner_text()
        near(page.evaluate('rocketCalculator.getResult().thrust'), old_thrust / 2, 'invalid preserves output')
    page.locator('#reset').click()
    page.fill('#wet', '1')
    assert 'at least' in page.locator('#error').inner_text()
    page.locator('#reset').click()
    page.select_option('#mode', 'mission')
    page.fill('#dv', '1000')
    assert 'mass ratio' in page.locator('#error').inner_text()
    page.fill('#dv', '0')
    assert not page.locator('#error').inner_text()
    r = page.evaluate('rocketCalculator.getResult()')
    near(r['burn'], 0, 'zero delta-v burn')
    near(r['prop'], 0, 'zero propellant')
    page.fill('#dv', '0.000000001')
    assert page.evaluate('rocketCalculator.getResult().prop > 0')
    # Deliberately unavailable clipboard exercises the usable fallback and URL reload.
    page.locator('[data-preset="passage"]').click()
    page.select_option('#exhaust-unit', 'velocity')
    page.select_option('#mode', 'mission')
    page.select_option('#constraint', 'power')
    page.evaluate("Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true})")
    page.locator('#share').click()
    assert page.locator('#share-fallback').is_visible()
    shared = page.input_value('#share-url')
    before = page.evaluate('rocketCalculator.getResult()')
    page.goto(shared, wait_until='domcontentloaded')
    after = page.evaluate('rocketCalculator.getResult()')
    for key in before:
        near(after[key], before[key], 'URL reload:' + key)
    page.goto(URL + '?mode=mission&dv=1e12', wait_until='domcontentloaded')
    assert page.locator('#error').inner_text()
    assert page.evaluate('!!rocketCalculator.getResult()'), 'invalid shared link needs valid baseline'
    results = []
    axe = ROOT.parent / 'Habitat/node_modules/axe-core/axe.min.js'
    assert axe.is_file(), 'Install axe-core or supply the existing sibling dependency for accessibility QA'
    for width in [360, 375, 768, 1440]:
        for theme in ['light', 'dark']:
            view = browser.new_page(viewport={'width': width, 'height': 1000}, color_scheme=theme, reduced_motion='reduce')
            view.on('pageerror', lambda e: errors.append(str(e)))
            view.goto(URL, wait_until='domcontentloaded')
            for preset in ['chemical', 'ion', 'passage', 'tug', 'ascent']:
                view.locator(f'[data-preset="{preset}"]').click()
                assert view.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (width, theme, preset, 'overflow')
            view.add_script_tag(path=str(axe))
            violations = view.evaluate("async () => (await axe.run()).violations.filter(v=>['critical','serious'].includes(v.impact)).map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))")
            assert not violations, (width, theme, violations)
            duplicate_ids = view.evaluate("() => {const a=[...document.querySelectorAll('[id]')].map(x=>x.id);return a.filter((id,i)=>a.indexOf(id)!==i)}")
            assert not duplicate_ids, duplicate_ids
            clipped = view.evaluate("() => [...document.querySelectorAll('#chart text')].filter(t=>{const a=t.getBoundingClientRect(),b=document.querySelector('#chart').getBoundingClientRect();return a.left<b.left-1||a.right>b.right+1}).map(t=>t.textContent)")
            assert not clipped, clipped
            view.locator('[data-preset="passage"]').click()
            view.screenshot(path=str(OUT / f'{width}-{theme}.png'), full_page=True)
            results.append({'width': width, 'theme': theme, 'overflow': 'pass', 'axe_serious_critical': 0})
            view.close()
    page.goto(URL, wait_until='domcontentloaded')
    page.emulate_media(media='print')
    page.pdf(path=str(OUT / 'print.pdf'), format='A4', print_background=True)
    if args.render_og:
        page.emulate_media(media='screen', color_scheme='dark')
        page.set_viewport_size({'width': 1200, 'height': 630})
        page.locator('[data-preset="passage"]').click()
        page.add_style_tag(content='''
          body>.wrap{max-width:none;padding:0} header,.quick,.note,main>.section,.explore,footer{display:none!important}
          .tool{border:0}.controls{display:none}.tool-grid{display:block}.tool-top{padding:12px 26px}.tool-top h2{font-size:23px}
          .outputs{padding:10px 26px;border:0}.big-number{font-size:48px;margin:0}.stats{grid-template-columns:repeat(5,1fr);gap:6px 15px;margin:10px 0}.stats dd{font-size:14px}.stats dt{font-size:11px}.outputs>.small{display:none}.massbar{height:8px}.mass-labels{margin-top:6px}
          .chart-wrap{padding:10px 26px}.chart-wrap h3{font-size:18px}.chart-wrap p{margin:0;font-size:11px}.chart-wrap svg{height:245px}.chart-wrap figcaption{font-size:11px}.chart-intro{align-items:center}.legend{font-size:11px}
        ''')
        page.locator('#calc-h').evaluate("e=>e.textContent='ROCKET EQUATION / CHEMICAL → ION → FUSION'")
        page.locator('.badge').evaluate("e=>e.textContent='TITAN DESIGN EXAMPLE'")
        page.screenshot(path=str(ROOT / 'images/rocket-equation-calculator.png'))
    assert not errors, errors
    browser.close()
report = {'status': 'pass', 'numerical_cases': [c[0] for c in cases], 'checks':
          ['inverse mode', 'unit preservation', 'fixed jet power', 'invalid input', 'zero delta-v', 'small delta-v',
           'clipboard fallback', 'URL round-trip', 'invalid shared URL', 'print', 'no console errors'], 'layouts': results}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Rocket equation: numerical, interaction, 8 layout/accessibility cases and print checks passed.')
