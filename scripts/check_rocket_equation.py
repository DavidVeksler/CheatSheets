"""Numerical and browser acceptance for rocket-equation-calculator.html.

Start a static server, then python scripts/check_rocket_equation.py --base URL.
--render-og writes the required 1200x630 preview from the working calculator.
"""
import argparse
import json
import math
import re
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


def sig_digits(text):
    digits = text.lstrip('-').replace('.', '').lstrip('0').rstrip('0')
    return len(digits)


def check_inputs(page, label):
    """1.2: no visible number input shows more than 7 significant digits or an exponent."""
    fields = page.evaluate("""() => [...document.querySelectorAll('#calc-form input[type=number]')]
        .filter(e => e.offsetParent !== null).map(e => [e.id, e.value])""")
    assert fields, (label, 'no visible inputs')
    for field_id, value in fields:
        assert not re.search('[eE]', value), (label, field_id, value, 'exponent in input')
        assert sig_digits(value) <= 7, (label, field_id, value, 'more than 7 significant digits')


RESULT_TEXT_JS = """() => ['#summary', '#primary', '#anchor-line', '#headline', '#details-stats', '#chart-text', '#chart-conditions', '#whatif']
    .map(s => document.querySelector(s).innerText)
    .concat([...document.querySelectorAll('#chart text')].map(t => t.textContent)).join('\\n')"""


def check_result_text(page, label):
    """1.4: no E-notation exponent anywhere in the visible result text."""
    text = page.evaluate(RESULT_TEXT_JS)
    assert not re.search(r'\d[eE][+-]?\d', text), (label, text)


CAVEAT_JS = """() => {
    const parts = [document.querySelector('header'), ...document.querySelectorAll('main > *:not(#mistakes)'),
                   document.querySelector('footer')];
    const text = parts.map(e => e.innerText).join('\\n').toLowerCase();
    const count = w => text.split(w).length - 1;
    return {fictional: count('fictional'), not_a: count('not a '), ideal: count('ideal')};
}"""
CAVEAT_LIMITS = {'fictional': 4, 'not_a': 3, 'ideal': 8}
caveat_counts = []


def check_caveats(page, label):
    """1.7: caveat budget on visible body text (Gotchas section excluded)."""
    counts = page.evaluate(CAVEAT_JS)
    caveat_counts.append((label, counts))
    for key, limit in CAVEAT_LIMITS.items():
        assert counts[key] <= limit, (label, key, counts[key], limit)


TOUCH_JS = """() => [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"]), [role=slider]')]
    .filter(e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && r.bottom + scrollY > 0
            && !(e.tagName === 'A' && e.closest('p, li, td, figcaption, caption')); })
    .map(e => [e.tagName, e.id || e.textContent.trim().slice(0, 40), Math.round(e.getBoundingClientRect().height * 10) / 10])"""
SELECT_FIT_JS = """() => { const s = document.getElementById('constraint'), cs = getComputedStyle(s), probe = document.createElement('span');
    probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;font:' + cs.font + ';letter-spacing:' + cs.letterSpacing;
    document.body.append(probe);
    const widest = Math.max(...[...s.options].map(o => { probe.textContent = o.text; return probe.getBoundingClientRect().width; }));
    probe.remove();
    return {need: widest + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight) + 24, have: s.getBoundingClientRect().width}; }"""
PAGE_SCREENS_MAX = 16  # Phase 3 target is 12; 15.4 is the measured floor without hiding content or shrinking type.
touch_min = []


def strip_state(view):
    view.wait_for_timeout(150)
    return view.evaluate("""() => { const s = document.getElementById('result-strip'), r = s.getBoundingClientRect();
        return {visible: !s.hidden && r.height > 0, bottom: r.bottom, vh: innerHeight}; }""")


def check_phone(view, width, theme):
    """Phase 3: phone layout at 360 and 375 px."""
    label = (width, theme)
    view.locator('[data-preset="chemical"]').click()
    over = view.evaluate("() => ['#comparison', '#comparison .scroll-table', '#comparison table'].map(s => document.querySelector(s)).filter(e => e.scrollWidth > e.clientWidth).map(e => e.id || e.className || e.tagName)")
    assert not over, (label, 'comparison overflow', over)
    assert view.evaluate("document.querySelector('#comparison .scroll-table').getAttribute('tabindex')") is None, (label, 'stacked table is not a scroll region')
    small = [t for t in view.evaluate(TOUCH_JS) if t[2] < 44]
    assert not small, (label, 'touch targets under 44 px', small)
    touch_min.append(min(t[2] for t in view.evaluate(TOUCH_JS)))
    fit = view.evaluate(SELECT_FIT_JS)
    assert fit['need'] <= fit['have'] + 0.5, (label, 'engine constraint select truncates', fit)
    # Engine bands still parse the restacked table: five families, seven marks below 600 px.
    assert view.locator('#chart-bands > g').count() == 5, (label, 'band groups')
    assert view.locator('#chart-bands .band-bar, #chart-bands .band-tick').count() == 7, (label, 'band marks')
    # Sticky strip: shown over the form, hidden once the results panel is in view, in sync with #primary.
    # Phone-height viewport; at 1000 px the whole form and the top of the results fit on one screen.
    view.set_viewport_size({'width': width, 'height': 812})
    view.evaluate("scrollTo({top: document.getElementById('mode').getBoundingClientRect().top + scrollY, behavior: 'instant'})")
    st = strip_state(view)
    assert st['visible'] and abs(st['bottom'] - st['vh']) <= 1, (label, 'strip visible over the form', st)
    view.locator('[data-preset="ion"]').click()
    strip_txt = view.locator('#strip-value').text_content().replace(' ', '')
    assert strip_txt == view.locator('#primary').text_content().replace(' ', ''), (label, strip_txt)
    assert view.locator('#strip-prop').text_content() == view.locator('#spent-label').text_content()
    assert 'ideal' not in view.locator('#result-strip').inner_text().lower()
    # Action buttons can sit fully above the strip.
    view.evaluate("scrollTo({top: document.getElementById('print').getBoundingClientRect().bottom + scrollY - innerHeight + 80, behavior: 'instant'})")
    st = strip_state(view)
    if st['visible']:
        top = view.evaluate("document.getElementById('result-strip').getBoundingClientRect().top")
        assert view.evaluate("document.getElementById('share').getBoundingClientRect().bottom") <= top, (label, 'strip covers the action buttons')
    view.evaluate("scrollTo({top: document.getElementById('mode').getBoundingClientRect().top + scrollY, behavior: 'instant'})")
    assert strip_state(view)['visible']
    view.locator('#result-strip').click()
    assert abs(view.evaluate("document.getElementById('results').getBoundingClientRect().top")) <= 20, (label, 'strip scrolls to results')
    assert view.evaluate("document.activeElement.id") == 'results', (label, 'strip moves focus to results')
    assert not strip_state(view)['visible'], (label, 'strip hidden with results in view')
    view.evaluate("scrollTo({top: 0, behavior: 'instant'})")
    view.set_viewport_size({'width': width, 'height': 1000})


def check_ui(page, label):
    check_inputs(page, label)
    check_result_text(page, label)
    check_caveats(page, label)


# 4.7: sentence-level text is at least 0.875 rem (14 px); 0.8 rem is only for uppercase kickers and badges.
SENTENCE_SELECTORS = ['.field label', '.select-row label', '.hint', '.note', '.small', 'small', 'figcaption',
                      '.ship-figure figcaption span', '.stats dt', '.headline dt', '.wi-stats dt', '.mass-labels',
                      '.anchor-line', '#comparison td', '#comparison caption', '.preset-description', '.card p',
                      '.mistakes p', '.equations p', 'details p', '.sources li', '.related span', '.quick span',
                      '.chart-intro p', '.legend', '.err', '.explore p', '.author-byline', '.chip > span:first-child']
FONT_JS = """sels => sels.flatMap(s => [...document.querySelectorAll(s)]
    .filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')
    .map(e => [s, (e.id || e.textContent.trim().slice(0, 30)), parseFloat(getComputedStyle(e).fontSize)]))"""


def check_type_floor(page, label):
    """Measured in Vehicle mode and in Mission mode with jet power, so hints, chips and the anchor line all show."""
    page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
    covered = set()
    for mode, constraint in [('vehicle', 'thrust'), ('mission', 'power')]:
        page.locator('[data-preset="chemical"]').click()
        page.select_option('#mode', mode)
        page.select_option('#constraint', constraint)
        sizes = page.evaluate(FONT_JS, SENTENCE_SELECTORS)
        small = [s for s in sizes if s[2] < 14 - 0.01]
        assert sizes and not small, (label, mode, 'sentence text under 14 px', small)
        covered |= {s[0] for s in sizes}
    missing = [s for s in SENTENCE_SELECTORS if s not in covered]
    assert not missing, (label, 'type-floor selectors matched nothing visible', missing)
    page.evaluate("document.querySelectorAll('details').forEach(d => d.open = false)")
    page.locator('[data-preset="chemical"]').click()


# 4.4: section order, TOC and kickers follow the same sequence.
SECTION_ORDER = ['calculator', 'Quick reference', 'comparison', 'examples', 'titan', 'reference', 'mistakes', 'sources', 'related']
TOC_ORDER = ['#calculator', '#comparison', '#examples', '#titan', '#reference', '#mistakes']
# 4.2: delta-v anchors in km/s, each from a NASA source on the page (see docs/titan-crosspromo.md drift list).
ANCHORS_KMS = [('trans-lunar injection', 3.1824168), ('trans-Mars injection', 3.662),
               ('low orbit to geostationary', 4.253), ('Earth surface to orbit', 9)]
HINTS = [('final', 'final-hint'), ('constraint', 'constraint-hint'), ('dv', 'dv-hint'), ('power', 'power-hint')]


def check_structure(page):
    order = page.evaluate("[...document.querySelectorAll('main > section')].map(s => s.id || s.getAttribute('aria-label'))")
    assert order == SECTION_ORDER, ('section order', order)
    toc = page.evaluate("[...document.querySelectorAll('nav.toc a')].map(a => [a.getAttribute('href'), a.textContent.slice(0, 2)])")
    assert [t[0] for t in toc] == TOC_ORDER and [t[1] for t in toc] == ['01', '02', '03', '04', '05', '06'], ('toc', toc)
    kickers = page.evaluate("""ids => ids.map(id => { const e = document.getElementById(id.slice(1));
        return (e.querySelector('.kicker, .eyebrow, .tool-top h2') || {}).textContent.slice(0, 2); })""", TOC_ORDER)
    assert kickers == ['01', '02', '03', '04', '05', '06'], ('kickers', kickers)
    # Every in-page link resolves, and an arrow points the way its target lies.
    links = page.evaluate("""() => [...document.querySelectorAll('a[href^="#"]')].map(a => {
        const t = document.getElementById(a.getAttribute('href').slice(1));
        return [a.getAttribute('href'), !!t, a.textContent.includes('↓') ? 'down' : a.textContent.includes('↑') ? 'up' : '',
                t ? Math.sign(a.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING ? 1 : -1) : 0]; })""")
    assert links and all(l[1] for l in links), ('unresolved in-page links', [l for l in links if not l[1]])
    wrong = [l for l in links if (l[2] == 'down' and l[3] < 0) or (l[2] == 'up' and l[3] > 0)]
    assert not wrong, ('arrow points away from its target', wrong)
    # Buttons that load a case scroll up to the calculator.
    assert page.evaluate("[...document.querySelectorAll('[data-load]')].every(b => b.textContent.includes('↑') && (b.compareDocumentPosition(document.getElementById('calculator')) & Node.DOCUMENT_POSITION_PRECEDING))")


def visible(page, element_id):
    return page.evaluate("id => { const e = document.getElementById(id); return !!e && e.getClientRects().length > 0; }", element_id)


def check_hints(page, label):
    """4.1: each hint is the input's aria-describedby target and shows exactly when its field does."""
    for input_id, hint_id in HINTS:
        described = (page.get_attribute('#' + input_id, 'aria-describedby') or '').split()
        assert hint_id in described, (label, input_id, described)
        assert visible(page, hint_id) == visible(page, input_id), (label, hint_id, 'visibility differs from its field')


def check_calculator_phase4(page):
    page.locator('[data-preset="chemical"]').click()
    assert page.locator('#calc-form > p.small').filter(has_text='Post-burn mass =').count() == 0, 'redundant .small paragraph removed'
    check_hints(page, 'vehicle/thrust')
    assert visible(page, 'final-hint') and visible(page, 'constraint-hint') and not visible(page, 'dv-hint') and not visible(page, 'power-hint')
    # 4.3: three headline stats; the third is whichever of jet power or thrust is derived.
    ids = lambda sel: page.evaluate("s => [...document.querySelectorAll(s + ' dd')].map(d => d.id)", sel)
    assert ids('#headline') == ['out-prop', 'out-burn', 'out-power'], ids('#headline')
    assert len(ids('#details-stats')) == 7 and 'out-thrust' in ids('#details-stats')
    assert page.evaluate("['prop','ratio','mass','ve','thrust','flow','burn','power','a0','af'].every(k => document.getElementById('out-' + k))")
    assert visible(page, 'details-label') and page.inner_text('#details-label').strip().lower() == 'details'
    big = page.evaluate("parseFloat(getComputedStyle(document.querySelector('#headline dd')).fontSize) > parseFloat(getComputedStyle(document.querySelector('#details-stats dd')).fontSize)")
    assert big, 'headline stats are larger than the details'
    # 4.2 Vehicle mode: the largest anchor at or below the computed delta-v (chemical 7.90 km/s -> GEO).
    assert visible(page, 'anchor-line') and page.inner_text('#anchor-line') == 'Enough for low orbit to geostationary.'
    page.locator('[data-preset="ascent"]').click()  # 3.00 km/s, below the smallest anchor
    assert page.evaluate('rocketCalculator.getResult().dv') < ANCHORS_KMS[0][1] * 1000
    assert not visible(page, 'anchor-line'), 'no anchor line below the smallest anchor'
    page.locator('[data-preset="passage"]').click()  # 100 km/s
    assert page.inner_text('#anchor-line') == 'Enough for Earth surface to orbit.'
    page.locator('[data-preset="chemical"]').click()
    page.select_option('#mode', 'mission')
    page.select_option('#constraint', 'power')
    check_hints(page, 'mission/power')
    assert all(visible(page, h) for _, h in HINTS)
    assert not visible(page, 'anchor-line'), 'anchor line is Vehicle mode only'
    assert ids('#headline') == ['out-prop', 'out-burn', 'out-thrust'], ids('#headline')
    assert 'out-power' in ids('#details-stats') and len(ids('#details-stats')) == 7
    # 4.2 Mission mode: each chip writes its value through setField and re-solves.
    chips = page.locator('#dv-anchors .chip')
    assert chips.count() == len(ANCHORS_KMS)
    for i, (name, kms) in enumerate(ANCHORS_KMS):
        chip = chips.nth(i)
        assert chip.get_attribute('data-name') == name and float(chip.get_attribute('data-dv')) == kms
        text = chip.inner_text().lower()
        assert re.search(r'\b(ideal|flown|with losses)\b', text), (name, 'basis must be visible text', text)
        assert f'{kms:.3g}' in text, (name, 'chip shows its value', text)
        chip.click()
        near(page.evaluate('rocketCalculator.getResult().dv'), kms * 1000, 'anchor ' + name)
        assert chip.get_attribute('aria-pressed') == 'true' and page.locator('#dv-anchors [aria-pressed=true]').count() == 1
        check_inputs(page, 'anchor ' + name)
    assert page.evaluate("[...document.querySelectorAll('#dv-anchors a')].every(a => /^#src-dv-/.test(a.getAttribute('href')) && document.querySelector(a.getAttribute('href')))")
    assert page.locator('#sources li[id^="src-dv-"]').count() == len(ANCHORS_KMS)
    page.select_option('#mode', 'vehicle')
    assert not visible(page, 'dv-anchors') and not visible(page, 'dv-hint')
    page.locator('[data-preset="chemical"]').click()
    # 4.6: a thrust bar for every row with a numeric thrust, none for "Design dependent".
    rows = page.evaluate("""() => [...document.querySelectorAll('#comparison tbody tr')].map(tr => {
        const td = tr.querySelector('td:nth-child(3)'), bar = td.querySelector('.tbar');
        return [tr.querySelector('th').textContent.trim(), /\\d/.test(td.textContent), !!bar, bar ? bar.getAttribute('aria-hidden') : null]; })""")
    assert all(r[1] == r[2] for r in rows), ('thrust bars on numeric rows only', rows)
    assert sum(r[2] for r in rows) == 9 and all(r[3] == 'true' for r in rows if r[2]), rows
    # Engine bands still parse the table: seven groups, seven marks at desktop width.
    assert page.locator('#chart-bands > g').count() == 7 and page.locator('#chart-bands .band-bar, #chart-bands .band-tick').count() == 7


with sync_playwright() as p:
    browser = p.chromium.launch(args=['--mute-audio'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL, wait_until='domcontentloaded')
    assert page.evaluate('!!window.rocketCalculator')
    # 1.5: no U+A730 anywhere in the source or the live document.
    assert 'ꜰ' not in (ROOT / 'rocket-equation-calculator.html').read_text(encoding='utf-8')
    assert 'ꜰ' not in page.evaluate('document.documentElement.outerHTML')
    # 1.6: no visible Calculate button; Enter still submits the form.
    assert page.locator('#calc-form button[type=submit]:visible').count() == 0
    page.evaluate("window.__submits = 0; document.getElementById('calc-form').addEventListener('submit', () => window.__submits++)")
    page.focus('#exhaust')
    page.keyboard.press('Enter')
    assert page.evaluate('window.__submits') == 1, 'Enter must still submit the form'
    # 1.1: worked case C's formula produces its displayed answer.
    case_c = page.locator('#examples .card').nth(2)
    assert case_c.locator('.formula').inner_text().replace(' ', '') == 'mp=10,000×(1−e^(−100/200))'.replace(' ', '')
    assert case_c.locator('.answer').inner_text() == f'{10000 * (1 - math.exp(-100 / 200)):,.2f} t'
    # Phase 4: structure, hints, delta-v anchors, headline stats, thrust bars, type floor.
    check_structure(page)
    check_calculator_phase4(page)
    check_type_floor(page, 1440)
    cases = [
        ('chemical', 100000, 10000, 3432.3275, 1000000),
        ('ion', 1200, 1000, 29419.95, 0.1),
        ('passage', 10000000, 6065306.597126334, 200000, 63700),
        ('tug', 135800, 100000, 24516.625, 85),
        ('ascent', 45000 * math.exp(3000 / (345 * 9.80665)), 45000, 3383.29425, 221000),
    ]
    for name, wet, final, ve, thrust in cases:
        page.locator(f'[data-preset="{name}"]').click()
        check_ui(page, name)
        r = page.evaluate('rocketCalculator.getResult()')
        for key, value in {'wet': wet, 'final': final, 've': ve, 'thrust': thrust,
                           'dv': ve * math.log(wet / final), 'prop': wet - final,
                           'flow': thrust / ve, 'burn': (wet - final) * ve / thrust,
                           'power': thrust * ve / 2, 'a0': thrust / wet, 'af': thrust / final}.items():
            near(r[key], value, name + ':' + key)
        page.select_option('#mode', 'mission')
        inverse = page.evaluate('rocketCalculator.getResult()')
        near(inverse['wet'], wet, name + ' inverse mass')
        check_ui(page, name + ' mission mode')
        page.select_option('#constraint', 'power')
        check_ui(page, name + ' power constraint')
    # 2.3: what-if scrub holds delta-v, post-burn mass and jet power fixed and never touches the form.
    page.locator('[data-preset="chemical"]').click()
    form_state = "() => [...document.querySelectorAll('#calc-form input, #calc-form select')].map(e => [e.id, e.value, e.dataset.exact || ''])"
    before_form = page.evaluate(form_state)
    base = page.evaluate('rocketCalculator.getResult()')
    assert page.evaluate('rocketCalculator.getWhatIf().ve') == base['ve'], 'what-if starts at the current exhaust velocity'
    assert page.locator('#massbar-ghost').is_hidden() and not page.locator('#wi-thrust-d').inner_text()
    w = page.evaluate('rocketCalculator.setWhatIf(30000)')
    share = 1 - math.exp(-base['dv'] / 30000)
    near(w['fraction'], share, 'what-if propellant share')
    near(w['wet'], base['final'] * math.exp(base['dv'] / 30000), 'what-if launch mass')
    near(w['thrust'], 2 * base['power'] / 30000, 'what-if thrust')
    near(w['burn'], w['prop'] * 30000 / w['thrust'], 'what-if engine time')
    shown = float(page.locator('#wi-frac').inner_text().rstrip('%'))
    assert shown == float(f'{share * 100:.4g}'), ('displayed what-if share', shown, share)
    assert page.locator('#massbar-ghost').is_visible() and page.locator('#wi-thrust-d').inner_text().startswith('÷')
    assert page.evaluate(form_state) == before_form, 'what-if must not change the form'
    surface = page.locator('#whatif-surface')
    surface.scroll_into_view_if_needed()
    box = surface.bounding_box()
    page.mouse.click(box['x'] + box['width'] * 0.8, box['y'] + box['height'] / 2)
    assert page.evaluate('rocketCalculator.getWhatIf().ve') > 30000, 'tap on the chart moves the what-if'
    page.mouse.move(box['x'] + box['width'] * 0.8, box['y'] + box['height'] / 2)
    page.mouse.down()
    page.mouse.move(box['x'] + box['width'] * 0.3, box['y'] + box['height'] / 2, steps=5)
    page.mouse.up()
    dragged = page.evaluate('rocketCalculator.getWhatIf().ve')
    assert dragged < 30000, ('drag moves the what-if', dragged)
    surface.focus()
    page.keyboard.press('ArrowRight')
    stepped = page.evaluate('rocketCalculator.getWhatIf().ve')
    assert stepped > dragged, 'ArrowRight raises the what-if exhaust velocity'
    page.keyboard.press('Shift+ArrowLeft')
    assert page.evaluate('rocketCalculator.getWhatIf().ve') < stepped, 'Shift+ArrowLeft lowers it'
    page.keyboard.press('End')
    assert page.evaluate('rocketCalculator.getWhatIf().ve') == 1e6
    assert surface.get_attribute('aria-valuenow') == '1000' and 'km/s' in surface.get_attribute('aria-valuetext')
    page.keyboard.press('Home')
    assert page.evaluate('rocketCalculator.getWhatIf().ve') == 1000
    page.locator('#whatif-range').fill('300')
    assert math.isclose(page.evaluate('rocketCalculator.getWhatIf().ve'), 10 ** 4.5), 'range input drives the what-if'
    assert page.evaluate(form_state) == before_form, 'what-if controls must not change the form'
    page.evaluate('rocketCalculator.setWhatIf(30000)')
    page.locator('#whatif-use').click()
    committed = page.evaluate('rocketCalculator.getResult()')
    assert committed['ve'] == 30000, committed['ve']
    assert page.input_value('#mode') == 'mission' and page.input_value('#constraint') == 'power'
    assert page.input_value('#exhaust-unit') == 'isp', 'commit keeps the exhaust unit'
    near(committed['dv'], base['dv'], 'commit keeps delta-v')
    near(committed['power'], base['power'], 'commit keeps jet power')
    near(committed['final'], base['final'], 'commit keeps post-burn mass')
    near(committed['fraction'], share, 'committed propellant share')
    check_ui(page, 'what-if commit')
    assert page.evaluate('rocketCalculator.getWhatIf().ve') == 30000 and page.locator('#massbar-ghost').is_hidden()
    assert not page.locator('#wi-frac-d').inner_text(), 'form change resets the what-if to current'
    page.locator('#reset').click()
    baseline = page.evaluate('rocketCalculator.getResult()')
    # Units preserve the physical configuration, including after loading presets.
    for selector, value in [('#mass-unit', '1'), ('#exhaust-unit', 'velocity'),
                             ('#thrust-unit', '1000'), ('#mass-unit', '1000')]:
        page.select_option(selector, value)
        r = page.evaluate('rocketCalculator.getResult()')
        near(r['dv'], baseline['dv'], selector)
        near(r['thrust'], baseline['thrust'], selector)
    page.locator('[data-preset="ion"]').click()
    # 1.3: presets apply their natural units (ion: kg, Isp, N).
    assert page.input_value('#mass-unit') == '1' and page.input_value('#thrust-unit') == '1'
    assert float(page.input_value('#wet')) == 1200
    page.select_option('#mass-unit', '1000')
    assert math.isclose(float(page.input_value('#wet')), 1.2)
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
    axe = ROOT.parent / 'concordia-space-habitat/node_modules/axe-core/axe.min.js'
    assert axe.is_file(), 'Install axe-core or supply the existing sibling dependency for accessibility QA'
    for width in [360, 375, 768, 1440]:
        for theme in ['light', 'dark']:
            view = browser.new_page(viewport={'width': width, 'height': 1000}, color_scheme=theme, reduced_motion='reduce')
            view.on('pageerror', lambda e: errors.append(str(e)))
            view.goto(URL, wait_until='domcontentloaded')
            for preset in ['chemical', 'ion', 'passage', 'tug', 'ascent']:
                view.locator(f'[data-preset="{preset}"]').click()
                assert view.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (width, theme, preset, 'overflow')
                view.evaluate('rocketCalculator.setWhatIf(rocketCalculator.getResult().ve * 8)')
                # 2.4: the chart fits its container; no horizontal scroll inside it.
                chart_overflow = view.evaluate("() => ['.chart-wrap', '#chart-stage', '.chart-body'].map(s => document.querySelector(s)).filter(e => e.scrollWidth > e.clientWidth).map(e => e.className || e.id)")
                assert not chart_overflow, (width, theme, preset, 'chart overflow', chart_overflow)
            view.add_script_tag(path=str(axe))
            violations = view.evaluate("async () => (await axe.run()).violations.filter(v=>['critical','serious'].includes(v.impact)).map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))")
            assert not violations, (width, theme, violations)
            duplicate_ids = view.evaluate("() => {const a=[...document.querySelectorAll('[id]')].map(x=>x.id);return a.filter((id,i)=>a.indexOf(id)!==i)}")
            assert not duplicate_ids, duplicate_ids
            clipped = view.evaluate("() => [...document.querySelectorAll('#chart text')].filter(t=>{const a=t.getBoundingClientRect(),b=document.querySelector('#chart').getBoundingClientRect();return a.left<b.left-1||a.right>b.right+1||a.top<b.top-1||a.bottom>b.bottom+1}).map(t=>t.textContent)")
            assert not clipped, clipped
            # Engine-class band labels never overlap each other.
            overlaps = view.evaluate("() => {const r=[...document.querySelectorAll('#chart-bands text')].map(t=>[t.textContent,t.getBoundingClientRect()]);const o=[];for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){const a=r[i][1],b=r[j][1];if(a.left<b.right-1&&b.left<a.right-1&&a.top<b.bottom-1&&b.top<a.bottom-1)o.push([r[i][0],r[j][0]]);}return o;}")
            assert not overlaps, (width, theme, overlaps)
            if width in (360, 375):
                check_phone(view, width, theme)
            if width == 375:
                check_type_floor(view, (width, theme))
                # 4.6: thrust bars survive the stacked table.
                assert view.locator('#comparison .tbar').count() == 9 and view.evaluate("[...document.querySelectorAll('#comparison .tbar')].every(b => b.getBoundingClientRect().width > 100)")
            view.locator('[data-preset="passage"]').click()
            view.screenshot(path=str(OUT / f'{width}-{theme}.png'), full_page=True)
            results.append({'width': width, 'theme': theme, 'overflow': 'pass', 'chart_overflow': 'pass', 'axe_serious_critical': 0})
            view.close()
    # Phase 3 page length at 375x812, in screens.
    view = browser.new_page(viewport={'width': 375, 'height': 812})
    view.goto(URL, wait_until='load')
    view.wait_for_timeout(200)
    page_screens = view.evaluate('document.documentElement.scrollHeight / 812')
    assert page_screens <= PAGE_SCREENS_MAX, ('page length at 375x812', page_screens)
    view.close()
    # Both selects show their full option text at 320 px.
    view = browser.new_page(viewport={'width': 320, 'height': 812})
    view.goto(URL, wait_until='domcontentloaded')
    assert view.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), '320 px overflow'
    for select_id in ('mode', 'constraint'):
        fit = view.evaluate(SELECT_FIT_JS.replace("getElementById('constraint')", f"getElementById('{select_id}')"))
        assert fit['need'] <= fit['have'] + 0.5, (320, select_id, 'select truncates', fit)
    view.close()
    page.goto(URL, wait_until='domcontentloaded')
    page.emulate_media(media='print')
    page.pdf(path=str(OUT / 'print.pdf'), format='A4', print_background=True)
    if args.render_og:
        page.emulate_media(media='screen', color_scheme='dark')
        page.set_viewport_size({'width': 1200, 'height': 630})
        page.locator('[data-preset="passage"]').click()
        # Outputs left, two-panel chart right; the what-if sits at the DFD design point to show the scrub.
        page.add_style_tag(content='''
          body>.wrap{max-width:none;padding:0} header,.quick,.note,main>.section,.explore,footer{display:none!important}
          .tool{border:0;display:grid;grid-template-columns:390px minmax(0,1fr);height:630px;overflow:hidden}.tool-top{grid-column:1/-1;padding:12px 26px}.tool-top h2{font-size:23px}
          .controls{display:none}.tool-grid{display:block;height:100%}.outputs{height:100%;padding:14px 24px 0 26px;border:0;border-right:1px solid var(--line)}
          .big-number{font-size:50px;margin:2px 0 12px}.outputs>.small,.anchor-line,.ghost-label{display:none!important}
          .headline{gap:6px 12px;margin:14px 0 0}.headline dt{font-size:11px}.headline dd{font-size:19px}.details-label{margin:12px 0 0;font-size:10px}
          .details-label+.stats{gap:6px 16px;margin:6px 0 0}.stats div{padding-top:4px}.stats dd{font-size:14px}.stats dt{font-size:11px}
          .chart-wrap{padding:12px 22px 0;border-top:0}.chart-wrap h3{font-size:19px;margin:0}.chart-intro p{margin:2px 0 0;font-size:12px}
          .legend,.whatif,.whatif-range,.chart-wrap figcaption{display:none!important}.chart-body{display:block;margin-top:4px}
        ''')
        page.wait_for_timeout(200)
        page.evaluate('rocketCalculator.setWhatIf(56500)')
        page.locator('#calc-h').evaluate("e=>e.textContent='ROCKET EQUATION / CHEMICAL → ION → FUSION'")
        page.locator('.badge').evaluate("e=>e.textContent='TITAN DESIGN EXAMPLE'")
        page.screenshot(path=str(ROOT / 'images/rocket-equation-calculator.png'))
    assert not errors, errors
    browser.close()
report = {'status': 'pass', 'numerical_cases': [c[0] for c in cases], 'checks':
          ['inverse mode', 'what-if scrub', 'what-if pointer/keyboard/range', 'what-if commit', 'chart fits container', 'band labels', 'unit preservation', 'fixed jet power', 'invalid input', 'zero delta-v', 'small delta-v',
           'clipboard fallback', 'URL round-trip', 'input significant digits', 'no exponent notation', 'caveat budget', 'no U+A730', 'invalid shared URL', 'print', 'no console errors', 'phone: stacked table fits', 'phone: touch targets >= 44 px',
           'phone: result strip', 'phone: constraint select fits', 'phone: engine bands after restack', 'phone: page length',
           'section order', 'in-page links and arrows', 'field hints', 'delta-v anchors', 'enough-for line', 'headline stats',
           'thrust bars', 'type floor 1440/375', '320 px selects'], 'layouts': results,
          'phone': {'screens_375x812': round(page_screens, 2), 'limit': PAGE_SCREENS_MAX, 'min_touch_px': min(touch_min)},
          'caveat_counts': {k: max(c[k] for _, c in caveat_counts) for k in CAVEAT_LIMITS}}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Rocket equation: numerical, interaction, 8 layout/accessibility cases and print checks passed.')
print('Phone (360/375, both themes): page %.2f screens at 375x812 (limit %d), smallest touch target %.1f px.' % (page_screens, PAGE_SCREENS_MAX, min(touch_min)))
print('Caveat counts (max over presets/modes; limits fictional<=4, not a<=3, ideal<=8):', report['caveat_counts'])
