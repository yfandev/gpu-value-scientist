import json,time,hashlib,datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('artifacts/automated-self-review'); url='https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/'
report={'tested_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'trials':[],'errors':[]}
with sync_playwright() as p:
 b=p.chromium.launch(); c=b.new_context(viewport={'width':1366,'height':768}); page=c.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
 for i in range(3):
  start=time.perf_counter();r=page.goto(url,timeout=90000);page.wait_for_function("document.getElementById('metric-skill').textContent !== '—'",timeout=90000)
  report['trials'].append({'trial':i+1,'ready_seconds':time.perf_counter()-start,'status':r.status,'navigation':page.evaluate('performance.getEntriesByType("navigation")[0].toJSON()')})
 data=page.request.get(url+'data.json').body();(out/'public-data.json').write_bytes(data)
 report['data_sha256']=hashlib.sha256(data).hexdigest();report['data_bytes']=len(data);report['status']=json.loads(data).get('status')
 report['tabs']={}
 for tab in page.get_by_role('tab').all():
  tab.click();name=tab.inner_text();report['tabs'][name]={'overflow':page.evaluate('document.documentElement.scrollWidth > innerWidth'),'text':page.locator('.panel.active').inner_text()};page.screenshot(path=str(out/('stage-'+tab.get_attribute('data-tab')+'.png')),full_page=True)
 cdp=c.new_cdp_session(page);cdp.send('Network.enable');cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':150,'downloadThroughput':200000,'uploadThroughput':100000});cdp.send('Network.setCacheDisabled',{'cacheDisabled':True})
 start=time.perf_counter();page.goto(url,timeout=90000);page.wait_for_function("document.getElementById('metric-skill').textContent !== '—'",timeout=90000);report['weak_network_ready_seconds']=time.perf_counter()-start
 b.close()
(out/'stage-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='tabs'},indent=2))
