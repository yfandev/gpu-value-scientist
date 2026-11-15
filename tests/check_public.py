"""Verify a deployed site over unauthenticated HTTPS, without workspace cookies."""
import hashlib,json,sys
from pathlib import Path
from urllib.parse import urlsplit
import requests

def verify_public(url):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.query:
        raise ValueError('Expected an HTTPS deployment URL without credentials or query')
    base=url.rstrip('/')
    session=requests.Session();session.trust_env=False
    home=session.get(base+'/',allow_redirects=False,timeout=60)
    if home.status_code!=200 or 'GPU Value Scientist' not in home.text or 'id="overview"' not in home.text:
        raise RuntimeError(f'Anonymous homepage did not serve the app directly: HTTP {home.status_code}')
    response=session.get(base+'/data.json',allow_redirects=False,timeout=60)
    if response.status_code!=200:raise RuntimeError('Anonymous demo data unavailable')
    data=response.json()
    if not data.get('forecasts') or not data.get('rounds'):raise RuntimeError('Demo lacks real forecast/research data')
    forecast=session.get(base+'/forecasts.csv',allow_redirects=False,timeout=60)
    if forecast.status_code!=200 or not forecast.text.startswith('series_id,origin_date,horizon_days,q10,q50,q90,target_date'):
        raise RuntimeError('Anonymous forecast download unavailable')
    for path in ['/.env','/src/environment.py','/data/agent_cache.json','/../.env']:
        r=session.get(base+path,allow_redirects=False,timeout=60)
        if r.status_code!=404:raise RuntimeError('Unpublished path did not return 404')
    result={'status':'passed','url':base,'authentication':'none; no cookies or authorization headers; redirects refused','homepage_status':home.status_code,'rows':len(data['forecasts']),'forecast_sha256':hashlib.sha256(forecast.content).hexdigest(),'secret_paths':'404'}
    Path('artifacts').mkdir(exist_ok=True);Path('artifacts/public-access.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    print(json.dumps(verify_public(sys.argv[1]),indent=2));print('ANONYMOUS_PUBLIC_DEMO_PASSED')
