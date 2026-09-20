"""Local browser acceptance checks for the standalone rainbow page.

Uses installed Chrome via Playwright. Run from repository root. Screenshots and
print PDF stay in ignored .rainbow-qa; the compact report is committed.
"""
import gzip
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / 'how-do-rainbows-work.html'
OUT = ROOT / '.rainbow-qa'
OUT.mkdir(exist_ok=True)
html = PAGE.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')
if '--accessibility' in sys.argv:
    # Install the optional test dependency in the ignored QA directory:
    # npm install --prefix .rainbow-qa axe-core --no-package-lock --ignore-scripts
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        page=browser.new_page(viewport={'width':375,'height':812})
        results=[]
        for theme in ['light','dark']:
            page.emulate_media(color_scheme=theme)
            page.goto(PAGE.as_uri())
            page.add_script_tag(path=str(OUT/'node_modules/axe-core/axe.min.js'))
            result=page.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','best-practice']}});return {version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})),incomplete:r.incomplete.map(v=>v.id)}}""")
            results.append({'theme':theme,**result})
        browser.close()
    (ROOT/'scripts/rainbow/accessibility-validation.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))
    assert not any(r['violations'] for r in results)
    sys.exit(0)
if '--links' in sys.argv:
    urls=sorted({e['href'] for e in soup.select('#sources a[href^="https:"]')})
    def fetch(url):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CheatSheets source verification'}),timeout=30) as response:
                return {'url':url,'status':response.status,'final_url':response.url}
        except Exception as error:
            return {'url':url,'error':str(error)}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(fetch,urls))
    (ROOT/'scripts/rainbow/source-validation.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))
    assert all(r.get('status')==200 for r in results)
    sys.exit(0)
ids = [e['id'] for e in soup.select('[id]')]
assert not [i for i, n in Counter(ids).items() if n > 1]
assert len(soup.select('article.entry')) == 32
assert len(soup.select('table')) == 2
assert len(soup.select('.mistakes li')) == 8
assert len(soup.title.text) <= 60
assert 150 <= len(soup.select_one('meta[name=description]')['content']) <= 200
for e in soup.select('a[href^="#"]'):
    assert e['href'][1:] in ids, e['href']
for e in soup.select('script[type="application/ld+json"]'):
    json.loads(e.string)
assert 'dateModified' not in html and 'Last verified' not in html

def overflow(page):
    return page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')

def finite(page):
    assert not page.locator('svg').evaluate_all('(els)=>els.some(e=>/NaN|Infinity/.test(e.innerHTML))')

def check_labels(page):
    # Any visible SVG annotation must remain within its own viewBox and retain
    # the spec's 14px rendered font target. 1px tolerance allows glyph bearings.
    return page.locator('svg text').evaluate_all('''els => els.flatMap(e=>{
      if(!e.checkVisibility()) return [];
      const s=e.ownerSVGElement, b=e.getBBox(), v=s.viewBox.baseVal;
      const rect=s.getBoundingClientRect();
      const size=parseFloat(getComputedStyle(e).fontSize)*Math.min(rect.width/v.width,rect.height/v.height);
      const clipped=b.x < v.x-1 || b.y < v.y-1 || b.x+b.width>v.x+v.width+1 || b.y+b.height>v.y+v.height+1;
      return clipped || size<13.9 ? [{text:e.textContent,clipped,size}] : [];
    })''')

report = {'structural': {'entries':32,'tables':2,'mistakes':8,'ids_unique':True}, 'screens':[]}
errors=[]
expected_missing_image=False
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    report['browser']=browser.version
    page=browser.new_page(viewport={'width':1440,'height':1000},color_scheme='light')
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m: errors.append(m.text) if m.type=='error' and not expected_missing_image and 'favicon.ico' not in m.text else None)
    page.add_init_script('''window.rainbowMetrics={cls:0,lcp:0,event_durations_ms:[]};
      new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)rainbowMetrics.cls+=e.value})).observe({type:'layout-shift',buffered:true});
      new PerformanceObserver(l=>l.getEntries().forEach(e=>rainbowMetrics.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});
      new PerformanceObserver(l=>l.getEntries().forEach(e=>rainbowMetrics.event_durations_ms.push(e.duration))).observe({type:'event',buffered:true,durationThreshold:16});''')
    page.goto(PAGE.as_uri())
    page.evaluate('document.fonts.ready')
    page.screenshot(path=str(OUT/'hero-desktop.png'))
    assert page.locator('.hero-art').evaluate('e=>e.complete && e.naturalWidth===1536')
    assert page.locator('#observer-a').get_attribute('aria-pressed')=='true'
    before=page.locator('#cone-figure').inner_html()
    page.locator('#observer-b').click()
    assert page.locator('#cone-figure').inner_html()!=before
    assert 'Observer B' in page.locator('#observer-summary').inner_text()
    for elevation in [0,30,60]:
        page.locator('#sun').fill(str(elevation))
        finite(page)
        assert f'Sun {elevation}°' in page.locator('#observer-summary').inner_text()
    page.locator('#reset-observer').click()
    page.locator('#sun').focus()
    page.keyboard.press('ArrowRight')
    assert page.locator('#sun').input_value()=='16'
    page.locator('#reset-observer').click()
    for wave in ['0','1','2']:
        page.locator('#wavelength').select_option(wave)
        for value in ['0','0.5','0.99']:
            page.locator('#impact').fill(value)
            finite(page)
    page.locator('#wavelength').select_option('0')
    page.locator('#reset-ray').click()
    for radius in ['25','50','100']:
        page.locator('#radius').select_option(radius)
        assert f'a = {radius} μm' in page.locator('#wave-summary').inner_text()
        assert f'{radius} μm radius' in page.locator('#polarization-caption').inner_text()
    page.locator('#show-airy').uncheck()
    assert page.locator('#wave-figure .airy').count()==0
    page.locator('#show-mie').uncheck()
    assert page.locator('#wave-figure .mie').count()==0
    page.locator('#show-airy').check();page.locator('#show-mie').check()
    for width,height,theme,name in [(1440,1000,'light','desktop'),(375,812,'light','mobile'),(375,812,'dark','mobile-dark'),(1280,500,'light','short'),(640,400,'light','zoom-equivalent')]:
        page.set_viewport_size({'width':width,'height':height});page.emulate_media(color_scheme=theme,reduced_motion='reduce')
        assert not overflow(page), name
        issues=check_labels(page)
        report['screens'].append({'name':name,'viewport':[width,height],'theme':theme,'overflow':False,'label_issues':issues})
        # Disable sticky navigation only during element capture: it otherwise
        # appears mid-way through a tall locator screenshot due to page scroll.
        page.add_style_tag(content='.depth-nav{position:static!important}')
        page.locator('#your-rainbow').screenshot(path=str(OUT/f'signature-{name}.png'))
        if name in ['mobile','mobile-dark']:
            page.locator('#derive').screenshot(path=str(OUT/f'derive-{name}.png'))
            page.locator('#wave-mobile').screenshot(path=str(OUT/f'wave-{name}.png'))
    page.set_viewport_size({'width':1440,'height':1000});page.emulate_media(color_scheme='light',media='print')
    page.evaluate("dispatchEvent(new Event('beforeprint'))")
    assert page.locator('details:not([open])').count()==0
    assert page.locator('.hero-art').is_hidden()
    assert page.locator('#observer-controls').is_hidden()
    page.pdf(path=str(OUT/'rainbow-print.pdf'),format='A4',print_background=True,margin={'top':'12mm','bottom':'12mm','left':'12mm','right':'12mm'})
    page.locator('#your-rainbow').screenshot(path=str(OUT/'signature-print.png'))
    page.emulate_media(media='screen')
    report['local_file_metrics']=page.evaluate('rainbowMetrics')
    durations=report['local_file_metrics'].pop('event_durations_ms')
    report['local_file_metrics']['maximum_observed_event_ms']=max(durations,default=0)
    report['local_file_metrics']['event_sample_count']=len(durations)
    # Check no-JS initial scientific figures and hidden inactive controls.
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':375,'height':812})
    q=nojs.new_page();q.goto(PAGE.as_uri())
    assert q.locator('#cone-figure svg').count()==1
    assert q.locator('#wave-mobile svg').count()==1
    assert q.locator('#observer-controls').is_hidden()
    assert q.locator('#ray-figure svg').count()==1
    q.locator('#your-rainbow').screenshot(path=str(OUT/'signature-nojs.png'))
    # A failed decorative raster must leave text and calculated figures usable.
    expected_missing_image=True
    page.emulate_media(media='screen');page.evaluate("document.querySelector('.hero-art').src='missing-rainbow-image.webp'")
    assert page.locator('h1').is_visible()
    assert not overflow(page)
    page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/'missing-image.png'))
    touch=browser.new_context(viewport={'width':375,'height':812},has_touch=True,is_mobile=True)
    t=touch.new_page();t.goto(PAGE.as_uri());t.locator('#observer-b').tap()
    assert t.locator('#observer-b').get_attribute('aria-pressed')=='true'
    report['interaction_checks']=['observer A/B','Sun 0/30/60 degrees','keyboard range','ray endpoints and three wavelengths','all wave presets','model toggles','touch button','no-JS static state','missing image','print expanded derivation','reduced motion']
    browser.close()
assert not errors,errors
report['console_errors']=errors
report['payload']={'html_bytes':len(PAGE.read_bytes()),'html_gzip_bytes':len(gzip.compress(PAGE.read_bytes())),
 'hero_bytes':(ROOT/'images/how-do-rainbows-work/rain-landscape.webp').stat().st_size,
 'app_js_bytes':sum((ROOT/'scripts/rainbow'/n).stat().st_size for n in ['optics.js','app.js'])}
report['payload']['initial_compressed_estimate']=report['payload']['html_gzip_bytes']+report['payload']['hero_bytes']
report['payload']['complete_page_raw']=report['payload']['html_bytes']+report['payload']['hero_bytes']
assert report['payload']['initial_compressed_estimate']<=700000
assert report['payload']['complete_page_raw']<=1500000
assert report['payload']['hero_bytes']<=250000
assert report['payload']['app_js_bytes']<=60000
(ROOT/'scripts/rainbow/browser-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
assert not any(s['label_issues'] for s in report['screens']), 'SVG labels need attention; inspect report'
