from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
url='https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/'
with sync_playwright() as p:
 browser=p.chromium.launch()
 context=browser.new_context(viewport={'width':1920,'height':1080},record_video_dir=str(ROOT/'artifacts/submission/raw'),record_video_size={'width':1920,'height':1080})
 page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);page.wait_for_function("document.querySelector('#metric-skill').textContent !== '—'")
 page.screenshot(path=str(ROOT/'artifacts/submission/project-screenshot.png'))
 def caption(text):
  page.evaluate('''text=>{let n=document.getElementById('recording-caption');if(!n){n=document.createElement('div');n.id='recording-caption';document.body.append(n)}n.textContent='RECORDED WALKTHROUGH · '+text;n.style.cssText='position:fixed;bottom:18px;left:8%;right:8%;z-index:99999;background:#07121ff0;color:#fff;border:1px solid #83e6ce;padding:16px 24px;font:24px Arial;text-align:center;border-radius:8px;pointer-events:none'}''',text)
 caption('The selected forecast widens price ranges: 75.42% historical coverage, with an uncertain improvement over Pacific’s baseline.')
 page.wait_for_timeout(10000)
 page.locator('#tour').click();caption('Replay of the original 14 agent tests, before calibration. These saved results do not run new experiments.')
 page.wait_for_timeout(21000)
 page.get_by_role('tab',name='Research log').click();page.locator('#verdict-filter').select_option('reject')
 caption('Rejected ideas stay visible. A critic checks later results before a method can be used.')
 page.wait_for_timeout(14000)
 page.get_by_role('tab',name='Sources & sponsors').click();page.locator('#sponsor-cards').scroll_into_view_if_needed()
 caption('Verified execution: Exa searches inside the loop; three agents write to past.dev and two read shared findings.')
 page.wait_for_timeout(16000)
 page.get_by_role('tab',name='Forecast explorer').click();page.locator('#series-search').fill('H100');page.locator('[data-series="gpurentalprices.neocloud_rate_card.H100_SXM_80GB.on_demand.median"]').click();page.locator('#price-history-chart').scroll_into_view_if_needed()
 caption('White shows observed prices through November 6. Forecast lines overlap because calibration only widens the uncertainty ranges.')
 page.wait_for_timeout(14000)
 page.get_by_role('tab',name='Economic view').click();page.locator('#economics').scroll_into_view_if_needed()
 caption('The 2–3 year outlook is an assumption-based scenario, not a scored resale prediction.')
 page.wait_for_timeout(12000)
 page.get_by_role('tab',name='Reproduce').click();page.locator('#reproduce').scroll_into_view_if_needed()
 caption('One command reproduces forecasts offline, using saved decisions and the unchanged Pacific data pack.')
 page.wait_for_timeout(12000)
 video=page.video
 context.close();video.save_as(str(ROOT/'artifacts/submission/demo.webm'));browser.close()
 assert not errors,errors
 (ROOT/'artifacts/submission/recording-check.json').write_text(json.dumps({'public_url':url,'browser_errors':errors,'recording':'actual browser with explanatory captions','audio':False},indent=2))
 print('PUBLIC_DEMO_RECORDING_PASSED')
