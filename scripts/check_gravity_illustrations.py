"""Browser acceptance checks for the calculator's embedded graphics.

Requires a local static server, e.g. python -m http.server 8765.
Usage: python scripts/check_gravity_illustrations.py [--base http://127.0.0.1:8765]
"""
from pathlib import Path
import argparse
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--base', default='http://127.0.0.1:8765')
args=parser.parse_args()
out=ROOT/'.visual-qa/gravity-illustrations'
out.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width in [360,1440]:
        for theme in ['light','dark']:
            page=browser.new_page(viewport={'width':width,'height':900},color_scheme=theme,reduced_motion='reduce')
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            # Production analytics can keep the network active after the sheet is ready.
            page.goto(args.base+'/artificial-gravity-calculator.html',wait_until='domcontentloaded')
            page.locator('#rotorDiagram').wait_for(state='visible')
            assert page.locator('.field-art').count()==11
            assert page.locator('img.field-art').count()==11
            assert page.locator('img.mast-diagram').count()==1
            assert page.locator('.editorial-graphic').count()==6
            # Lazy assets must decode, and symbols inside SVG must also resolve.
            page.evaluate('''async () => { await Promise.all(Array.from(document.images, async img => { img.loading='eager'; await img.decode(); })); }''')
            for src in set(page.locator('.gravity-art image').evaluate_all("els => els.map(e => e.getAttribute('href'))")):
                assert page.request.get(args.base+'/'+src).ok,src
            titan=page.locator('#field-guide a[href*="titan.davidveksler.com/system/spin-gravity/"]')
            assert titan.count()==1
            assert titan.get_attribute('href').endswith('#why-the-drums-come-in-pairs')
            assert 'fictional ship' in titan.locator('..').text_content()
            # The illustration must follow both presets and direct edits.
            page.get_by_role('button',name='Concordia',exact=True).click()
            assert '2,500 m radius, 0.598 rpm, 1 g' in page.locator('#live-rotor-desc').text_content()
            page.get_by_role('button',name='10 m centrifuge',exact=True).click()
            assert '10 m radius, 9.46 rpm, 1 g' in page.locator('#live-rotor-desc').text_content()
            page.locator('#inR').fill('224')
            page.locator('#inR').dispatch_event('change')
            assert '224 m radius, 2 rpm, 1 g' in page.locator('#live-rotor-desc').text_content()
            before=page.locator('#live-rotor-desc').text_content()
            page.locator('#inR').fill('-1')
            page.locator('#inR').dispatch_event('change')
            assert page.locator('#inR').get_attribute('aria-invalid')=='true'
            assert page.locator('#live-rotor-desc').text_content()==before
            page.get_by_role('button',name='Concordia',exact=True).click()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), 'page overflow'
            clipped=page.evaluate('''() => { const out=[]; for(const svg of document.querySelectorAll('.gravity-art svg,.mast-art svg,.field-art')) {const v=svg.getBoundingClientRect(); for(const t of svg.querySelectorAll('text')) {const b=t.getBoundingClientRect(); if(b.left<v.left-1 || b.right>v.right+1 || b.top<v.top-1 || b.bottom>v.bottom+1) out.push(t.textContent);}} return out;}''')
            assert not clipped,clipped
            ids=page.evaluate('''() => {const ids=Array.from(document.querySelectorAll('[id]'),e=>e.id);return ids.filter((id,i)=>ids.indexOf(id)!==i);}''')
            assert not ids,ids
            axe=ROOT.parent/'Habitat/node_modules/axe-core/axe.min.js'
            if axe.exists():
                page.add_script_tag(path=str(axe))
                violations=page.evaluate("async () => (await axe.run()).violations.filter(v=>['serious','critical'].includes(v.impact)).map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))")
                assert not violations,violations
            assert not errors,errors
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(out/f'{width}-{theme}-header.png'))
            page.locator('.gravity-art').nth(1).screenshot(path=str(out/f'{width}-{theme}-sizes.png'))
            page.locator('#field-guide').evaluate("el => el.scrollIntoView({block: 'start'})")
            page.screenshot(path=str(out/f'{width}-{theme}-field.png'))
            results.append({'width':width,'theme':theme,'status':'pass'})
            page.close()
    browser.close()
(out/'report.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print('Gravity illustrations: calculator behavior, 12 edited images, SVG symbols/labels, Titan link, mobile layout and light/dark accessibility passed.')
