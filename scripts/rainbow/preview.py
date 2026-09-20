"""Render a 1200x630 social preview from the finished page and signature SVG."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

root=Path(__file__).resolve().parents[2]
out=root/'.rainbow-qa'
out.mkdir(exist_ok=True)
hero=(root/'images/how-do-rainbows-work/rain-landscape.webp').as_uri()
plate=(root/'images/how-do-rainbows-work/signature.svg').as_uri()
html=f'''<!doctype html><html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}body{{margin:0;width:1200px;height:630px;background:#f7f4ec;color:#142538;font-family:system-ui}}
.left{{position:absolute;inset:0 auto 0 0;width:510px;background:linear-gradient(#182b43c9,#182b4390),url('{hero}') center/cover;color:#fffaf1;padding:48px}}
.tag{{font:13px monospace;letter-spacing:2px}}h1{{font:76px/.99 Georgia;margin:54px 0 28px;letter-spacing:-3px}}p{{font-size:21px;line-height:1.5}}.right{{position:absolute;left:510px;top:0;width:690px;height:630px;padding:35px 20px}}
.right h2{{font:31px Georgia;margin:0 0 12px 14px}}.right img{{position:absolute;left:0;top:95px;width:690px;height:452px}}.foot{{position:absolute;left:530px;bottom:34px;font-size:16px;color:#46566b}}
.arc{{position:absolute;left:110px;bottom:-185px;width:345px;height:345px;border:7px solid #D94B5480;border-radius:50%;box-shadow:inset 0 0 0 6px #E58A3770,inset 0 0 0 12px #E8BE4970,inset 0 0 0 18px #4AAB8270,inset 0 0 0 24px #478ED170,inset 0 0 0 30px #8A6BD170}}
</style><div class="left"><div class="tag">FOLLOW THE LIGHT</div><h1>How do<br>rainbows<br>work?</h1><p>From sunlight<br>to wave optics.</p><div class="arc"></div></div><div class="right"><h2>Your eye sets the geometry.</h2><img src="{plate}" alt="Linked observer cone, sky and drop path"></div><div class="foot">cheatsheets.davidveksler.com · Illustrated optics</div></html>'''
temp=out/'preview.html';temp.write_text(html,encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1200,'height':630},device_scale_factor=1,color_scheme='light')
    page.goto(temp.as_uri());page.screenshot(path=str(root/'images/how-do-rainbows-work.png'))
    browser.close()
im=Image.open(root/'images/how-do-rainbows-work.png')
assert im.size==(1200,630)
im.save(root/'images/how-do-rainbows-work.png',optimize=True)
print('Rendered and optimized images/how-do-rainbows-work.png (1200 x 630)')
