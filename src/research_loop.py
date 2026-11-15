"""Main-loop source discovery and bounded method hypotheses, with traceable use."""
from agents import log_event

def research_round(runtime,memory,searcher,round,origin,group):
    found=searcher.research(origin,round,group)
    notes=found.get('results',[])
    if any(n.get('source')!='exa' or n.get('publication_date','9999')>origin for n in notes):
        raise ValueError('Main-loop evidence must be dated Exa sources available at the origin')
    log_event('RESEARCHER','exa_main_loop_search',{'round':round,'origin':origin,'group':group,'query':found['query'],'request':found['request']},
              {'status':found['status'],'results':notes,'cache_key':found['cache_key'],'request_id':found.get('request_id')},
              network_call=found.get('executed_live',False),mode=found['status'])
    mode='dated_sources' if notes else 'history_only'
    # Execution transport is logged separately; it must not alter cached agent inputs.
    semantic_status='exa_sources' if found['status'] in ('live_exa','cached_exa') else 'no_eligible_sources'
    fallback={'choice':mode,'reason':('Use these dated sources to suggest bounded hypotheses, never as price truth: '+ '; '.join(n['title'] for n in notes)) if notes else 'No eligible cached Exa evidence. Propose from historical errors only; do not claim a successful web search.'}
    reviewed=runtime.call('RESEARCHER',{'round':round,'origin':origin,'allowed_options':[mode],'evidence':notes,'search_status':semantic_status,'instruction':'Summarize only these dated sources and their relevance to forecasting methods.'},fallback)
    content={'title':'Main-loop Exa research','date':origin,'sentence':reviewed['reason'],'search_status':semantic_status,'sources':notes,'query':found['query'],'group':group,'scope':'Hypothesis context only; price truth remains the frozen pack.'}
    memory.write('RESEARCHER',round,origin,'evidence',content)
    return {**found,'researcher_note':reviewed['reason']}

def evidence_guided_default(default,entries,allowed):
    """Transparent fallback policy; real agents receive the same source records."""
    sources=[s for e in entries if e['kind']=='evidence' for s in e['content'].get('sources',[])]
    text=' '.join(s.get('title','')+' '+s.get('sentence','') for s in sources).lower()
    for terms,candidate in [(('conformal','calibration'),'calibrated'),(('volatility',),'volatility'),(('sticky','stepwise','step prices'),'step_shrink'),(('rolling window','nonstationary'),'recent_28')]:
        if candidate in allowed and any(term in text for term in terms):return candidate,[s['url'] for s in sources]
    return default,[]

def sponsor_report(events,loop_evidence):
    from agents import sponsor_audit
    memory=sponsor_audit(events)
    cross_reads=[e for e in events if e.get('what')=='memory_read' and e.get('mode')=='past.dev' and e.get('network_call') and any(item.get('agent')!=e.get('who') for item in e.get('outcome',{}).get('entries',[]))]
    admitted={item['id'] for e in cross_reads for item in e['outcome']['entries'] if item.get('agent')!=e['who']}
    using=[e for e in events if e.get('what')=='decision' and any(item.get('id') in admitted and item.get('agent')!=e.get('who') for item in e.get('inputs',{}).get('memory',[]))]
    memory['cross_agent_live_reads']=len(cross_reads);memory['decisions_receiving_cross_agent_live_memory']=len(using)
    memory['sponsor_requirements_verified']=memory['multi_agent_live_access'] and bool(using)
    searches=[e for e in events if e.get('what')=='exa_main_loop_search']
    actual=[e for e in searches if e.get('network_call') and e['outcome']['status']=='live_exa']
    recorded=[r for r in loop_evidence if r['status'] in ('live_exa','cached_exa') and r.get('results')]
    used=[e for e in events if e.get('who')=='ANALYST' and e.get('what')=='decision' and any(s.get('content',{}).get('sources') for s in e.get('inputs',{}).get('memory',[]) if s.get('kind')=='evidence')]
    return {'exa':{'status':'live_verified' if actual and used else 'recorded_verified' if recorded and used else 'blocked_no_live_evidence','live_main_loop_calls':len(actual),'source_bearing_rounds':len(recorded),'analyst_decisions_receiving_sources':len(used),'code':'src/research_loop.py:research_round -> src/evidence.py:LoopResearcher.research','repo_link':'pending user authorization; no Git commits or remote created'},'past_dev':memory,'modal':{'status':'not_run_on_modal','report':'results/modal/execution.json'},'originator':{'status':'built_in_ori','note':'Work conducted in this hackwithori.com cloud workspace; judging and session submission not verified.'}}

def retain_live_receipt(root,config,events,sponsors):
    """Keep original execution evidence after offline replay replaces current logs."""
    import hashlib,json
    from pathlib import Path
    root=Path(root)
    keys=[e['cache_key'] for e in events if e.get('what')=='decision']
    identity={'config':config,'ordered_decision_keys':keys,'forecast_sha256':hashlib.sha256((root/'forecasts.csv').read_bytes()).hexdigest(),'online_sha256':hashlib.sha256((root/'results/online_forecasts.csv').read_bytes()).hexdigest()}
    fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    folder=root/'results/live_runs'/fingerprint
    actual=any(e.get('mode')=='openai_live' and not e.get('replayed') for e in events if e.get('what')=='decision')
    if actual:
        folder.mkdir(parents=True,exist_ok=True)
        receipt={'fingerprint':fingerprint,'identity':identity,'sponsors':sponsors,'status':'recorded_actual_execution','note':'Preserved original production log; no secrets or credentials are stored.'}
        (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (folder/'agent_log.jsonl').write_text((root/'logs/agent_log.jsonl').read_text())
    if (folder/'receipt.json').exists() and not any(e.get('mode')=='deterministic_policy' for e in events if e.get('what')=='decision'):
        receipt=json.loads((folder/'receipt.json').read_text())
        if receipt['identity']!=identity:raise ValueError('Live execution receipt identity mismatch')
        return {'status':'matched_exact_live_run','fingerprint':fingerprint,'path':str(folder.relative_to(root)/'receipt.json'),'sponsors':receipt['sponsors']}
    return {'status':'no_matching_live_run','fingerprint':fingerprint}
