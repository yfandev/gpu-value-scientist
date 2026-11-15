from pathlib import Path
import json
import time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
url='https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/'
with sync_playwright() as p:
 browser=p.chromium.launch()
 context=browser.new_context(viewport={'width':1920,'height':1080},record_video_dir=str(ROOT/'artifacts/submission/raw'),record_video_size={'width':1920,'height':1080})
 started=time.monotonic();scenes=[]
 page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);page.wait_for_function("document.querySelector('#metric-skill').textContent !== '—'")
 page.screenshot(path=str(ROOT/'artifacts/submission/project-screenshot.png'))
 def caption(text):
  scenes.append({"start":time.monotonic()-started,"caption":text})
  page.evaluate('''text=>{let n=document.getElementById('recording-caption');if(!n){n=document.createElement('div');n.id='recording-caption';document.body.append(n)}n.textContent='RECORDED WALKTHROUGH · '+text;n.style.cssText='position:fixed;bottom:18px;left:8%;right:8%;z-index:99999;background:#07121ff0;color:#fff;border:1px solid #83e6ce;padding:16px 24px;font:24px Arial;text-align:center;border-radius:8px;pointer-events:none'}''',text)
 caption('4.323% less historical forecast error than Pacific’s drift forecast. The uncertainty includes no gain; later checks did not confirm improvement.')
 page.wait_for_timeout(12000)
 page.locator('#measurement-discovery').scroll_into_view_if_needed()
 caption('A matching H100 price record stayed at $0.94 while the reported middle price changed. Changing observed entries can move a price index.')
 page.wait_for_timeout(8000)
 page.locator('#tour').click();caption('Green shows predictions after broadening their ranges; blue shows them before. This is a retrospective comparison, not proof of future improvement.')
 page.wait_for_timeout(21000)
 page.get_by_role('tab',name='Research log').click();page.locator('#verdict-filter').select_option('reject')
 caption('Rejected ideas remain visible. The Critic checks later prices before an idea can be used.')
 page.wait_for_timeout(10000)
 page.get_by_role('tab',name='Sources & sponsors').click();page.locator('#sponsor-cards').scroll_into_view_if_needed()
 caption('Saved records show Exa searches during research. Three agents saved findings in past.dev, and two read them.')
 page.wait_for_timeout(10000)
 page.get_by_role('tab',name='Forecast explorer').click();page.locator('#series-search').fill('H100');page.locator('[data-series="gpurentalprices.neocloud_rate_card.H100_SXM_80GB.on_demand.median"]').click();page.locator('#price-history-chart').scroll_into_view_if_needed()
 caption('White shows recorded prices through November 6. Green and gold show future estimates; widening the range did not change the middle prediction.')
 page.wait_for_timeout(12000)
 page.get_by_role('tab',name='Economic view').click();page.locator('#economics').scroll_into_view_if_needed()
 caption('By 2029, our central scenario has H100 rents falling to $0.98–$2.59 and A100 to $0.42–$1.20 per GPU-hour. These are assumptions, not tested future prices.')
 page.wait_for_timeout(14000)
 page.get_by_role('tab',name='Reproduce').click();page.locator('#reproduce').scroll_into_view_if_needed()
 caption('After setup, one command rebuilds the saved forecasts without internet access.')
 page.wait_for_timeout(10000)
 video=page.video
 context.close();video.save_as(str(ROOT/'artifacts/submission/demo.webm'));browser.close()
 assert not errors,errors
 (ROOT/'artifacts/submission/recording-check.json').write_text(json.dumps({'public_url':url,'browser_errors':errors,'recording':'actual browser with explanatory captions','audio':False},indent=2))
 (ROOT/'artifacts/submission/recording-scene-times.json').write_text(json.dumps(scenes,indent=2)+'\n')
 print('PUBLIC_DEMO_RECORDING_PASSED')
