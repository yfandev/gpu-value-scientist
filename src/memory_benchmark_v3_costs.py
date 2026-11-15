"""Authorized read-only reconciliation of v3 request IDs; list-price estimates only."""
import sys,os,json,math,datetime as dt
from pathlib import Path
import requests
import memory_benchmark_v3 as b
from environment import load_environment
load_environment()
cache=json.load(open(b.ROOT/'data/memory_benchmark_v3_cache.json'))
recalls=[r for r in cache.values() if r['request']['provider']=='past_dev'];ids={r['request_id'] for r in recalls}
params={'first':100,'from':min(r['started_utc'] for r in recalls),'endpoint':'/api/v1/recall'}
matched=[]
while True:
 response=requests.get('https://api.past.dev/api/v1/requests',params=params,headers={'Authorization':'Bearer '+os.environ['PAST_API_KEY']},timeout=30);response.raise_for_status();page=response.json()
 matched += [{k:r[k] for k in ['requestId','receivedAt','path','status','durationMs','credits']} for r in page['requests'] if r['requestId'] in ids]
 if not page['hasMore']:break
 params['after']=page['endCursor']
assert {r['requestId'] for r in matched}==ids,'Incomplete request ID reconciliation'
usage=[r['response']['usage'] for r in cache.values() if r['request']['provider']=='openai']
prompt=sum(u['prompt_tokens'] for u in usage);completion=sum(u['completion_tokens'] for u in usage)
assert all('cached_tokens' in u.get('prompt_tokens_details',{}) for u in usage),'Missing cached token breakdown'
cached=sum(u['prompt_tokens_details']['cached_tokens'] for u in usage)
model=((prompt-cached)*.4+cached*.1+completion*1.6)/1e6
entries=json.load(open(b.OUT/'snapshot.json'))
ingest=sum(math.ceil(len(b.canonical(e).encode())/350) for e in entries)
credits=sum(r['credits'] for r in matched);recall_cost=credits*.0003
result={'status':'list_price_estimate_not_invoice','accessed_date':'2026-11-15','recall_requests':matched,'matched_requests':len(matched),'actual_recall_credits':credits,
 'model_pricing_source':'https://developers.openai.com/api/docs/models/gpt-4.1-mini','past_pricing_source':'https://past.dev/pricing.md',
 'assumptions':{'openai_usd_per_million':{'uncached_input':.4,'cached_input':.1,'output':1.6},'past_usd_per_credit':.0003,
 'ingestion_basis':'Estimated ceil(canonical UTF-8 content bytes/350) per source; actual original billed ingestion not reconciled.',
 'exclusions':'Taxes, discounts, subscription allocation and local compute excluded equally; actual invoice/paid credit grant unknown.'},
 'model_usage':{'prompt_tokens':prompt,'cached_tokens':cached,'completion_tokens':completion},
 'full_context_model_list_usd':model,'past_recall_list_usd':recall_cost,'estimated_corpus_ingestion_credits':ingest,'estimated_corpus_ingestion_list_usd':ingest*.0003,
 'sensitivity':[{'amortization_queries':n,'past_54_queries_list_usd':recall_cost+ingest*.0003*54/n,'savings_vs_full_context':model-(recall_cost+ingest*.0003*54/n)} for n in [54,100,1000,10000]],
 'actual_dollar_savings_verified':False}
b.save(b.OUT/'cost_estimate.json',result)
print({k:result[k] for k in ['matched_requests','actual_recall_credits','model_usage','full_context_model_list_usd','past_recall_list_usd','estimated_corpus_ingestion_credits','sensitivity']})
