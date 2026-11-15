"""Reproducible bounded GPU research loop. Official starter owns every score."""
import os,sys,json,hashlib,argparse,subprocess,datetime,shutil
from pathlib import Path
from environment import load_environment
load_environment()
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT); sys.dont_write_bytecode=True
CONFIG=json.loads(Path('config.json').read_text()); PACK=Path(CONFIG['pack']).resolve()
sys.path.insert(0,str(PACK/'starter'))
import numpy as np
import pandas as pd
from _common import SeriesStore,read_series_csv,validate_forecast,day_of,parse_date
from methods import forecast,COLUMNS

def save(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,allow_nan=False,default=lambda v:v.item() if hasattr(v,'item') else str(v))+'\n')
def run(cmd,log):
    p=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    Path(log).parent.mkdir(parents=True,exist_ok=True);Path(log).write_text(p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(f'{log}: exit {p.returncode}: {p.stderr[-1500:]}')
    return p

def score(path,name,baseline='last_value',truth='data/history.csv'):
    report=f'results/{name}.json'; cells=f'results/{name}_cells.csv'
    run([sys.executable,'-B',PACK/'starter/scorer.py','--forecast',path,'--truth',truth,'--history','data/history.csv','--series-ids','@data/target_ids.txt','--horizons','1,3,7','--skill-baseline',baseline,'--missing-as-baseline','--out',report,'--per-cell',cells],f'logs/{name}.log')
    return json.loads(Path(report).read_text()),pd.read_csv(cells)

def write_fc(df,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    df[COLUMNS].sort_values(['origin_date','series_id','horizon_days']).to_csv(path,index=False,float_format='%.10g')

def bootstrap(cells,drift,seed):
    # Losses are emitted by scorer.py, not recalculated here. Pair exact cells.
    keys=['series_id','origin_date','horizon_days']
    z=cells.merge(drift[keys+['loss']],on=keys,suffixes=('','_drift'),validate='one_to_one')
    if z.empty:return {'ci':[None,None],'n_origins':0,'mean_loss_difference':None}
    # Cluster whole origins: retain dependence across GPUs and horizons.
    z['difference']=z.loss-z.loss_drift
    grouped=z.groupby('origin_date').agg(total=('difference','sum'),n=('difference','count'))
    rng=np.random.default_rng(seed); a=grouped.to_numpy(); picks=rng.integers(0,len(a),(CONFIG['bootstrap_samples'],len(a)))
    draws=a[picks]; means=draws[:,:,0].sum(1)/draws[:,:,1].sum(1)
    return {'ci':np.quantile(means,[.025,.975]).tolist(),'n_origins':len(a),'mean_loss_difference':float(z.difference.mean()),'n_cells':len(z),'resampling':'paired origin-cluster bootstrap, exploratory 95% CI; no multiplicity correction'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--live',action='store_true');ap.add_argument('--skip-build',action='store_true');args=ap.parse_args()
    from agents import AgentRuntime,SharedMemory
    from evidence import LoopResearcher
    from research_loop import research_round,evidence_guided_default,sponsor_report,retain_live_receipt
    if args.live and not os.environ.get('OPENAI_API_KEY'): raise SystemExit('LIVE RUN BLOCKED: configure OPENAI_API_KEY. Offline deterministic policy remains available.')
    for folder in ['data','results','logs','demo']:Path(folder).mkdir(exist_ok=True)
    if not args.skip_build:
        run([sys.executable,'-B',PACK/'starter/build_series.py','--pack',PACK,'--no-aws','--cutoff',CONFIG['cutoff'],'--out','data/history.csv','--catalog','data/series_catalog.csv','--report','results/build.json'],'logs/build.log')
    cat=pd.read_csv('data/series_catalog.csv',keep_default_na=False);targets=cat[(cat.tier=='headline') & (cat.table=='daily_statistics')].copy()
    ids=sorted(targets.series_id); targets.to_csv('data/targets.csv',index=False);Path('data/target_ids.txt').write_text('\n'.join(ids)+'\n')
    hist=read_series_csv('data/history.csv');assert hist.date.max().isoformat()<=CONFIG['cutoff']
    store=SeriesStore(hist); origins=[day_of(parse_date(o)) for o in CONFIG['origins']]; cutoff=day_of(parse_date(CONFIG['cutoff']))
    # Drop numerical catalog fields from agent input: those describe the final cutoff.
    groups=dict(zip(targets.series_id,targets.instrument_class)); group_names=sorted(set(groups.values()))
    target_schema=targets[['series_id','instrument_class','benchmark_contract','gpu_model','pricing_tier','source_url','licence_id']].to_dict('records')
    specs={c['id']:c for c in CONFIG['candidates']}
    fallback=forecast(store,ids,[cutoff],CONFIG['horizons'],specs['drift']);write_fc(fallback,'forecasts_fallback.csv');write_fc(fallback,'forecasts.csv')
    clean,problems=validate_forecast(pd.read_csv('forecasts.csv'),CONFIG['horizons']);assert not problems and len(clean)==len(ids)*3
    frames={};cells={};reports={}
    for name,spec in specs.items():
        print('Forecasting',name,flush=True)
        frames[name]=forecast(store,ids,origins,CONFIG['horizons'],spec);path=f'results/forecast_{name}.csv';write_fc(frames[name],path)
        reports[name],cells[name]=score(path,f'method_{name}')
        cells[name]['group']=cells[name].series_id.map(groups)
    # Clear the replay ledger, never a data source. Decisions cached separately by full input hash.
    Path('logs/agent_log.jsonl').write_text('')
    runtime=AgentRuntime(CONFIG,live=args.live); memory=SharedMemory(CONFIG,live=args.live);memory.reset_run()
    searcher=LoopResearcher(CONFIG,live=args.live); loop_evidence=[]
    pending=[];hypotheses=[];selected={g:'drift' for g in group_names};online=[];rounds=[];audit=[]
    candidate_ids=[n for n in specs if n!='drift']
    for t in range(1,len(origins)):
        decision_origin=CONFIG['origins'][t]; past_origins=CONFIG['origins'][:t]
        # Only earlier origin predictions whose targets have matured at decision_origin.
        visible={n:c[(c.origin_date.isin(past_origins)) & (c.target_date<=decision_origin)] for n,c in cells.items()}
        decisions=[]
        for p in pending:
            g=p['group'];name=p['candidate']
            v=visible[name];v=v[(v.group==g)&(v.origin_date>=p['frozen_at'])]
            d=visible['drift'];d=d[(d.group==g)&(d.origin_date>=p['frozen_at'])]
            stat=bootstrap(v,d,CONFIG['seed']+t)
            eligible=stat['n_origins']>=CONFIG['min_critic_origins']
            accepted=eligible and stat['ci'][1]<0
            if eligible:
                reason=('Paired loss improvement on later origins; upper CI below zero.' if accepted else 'Later-origin paired loss CI does not establish improvement over drift.')
                fallback_verdict={'choice':'accept' if accepted else 'reject','reason':reason}
                verdict=runtime.call('CRITIC',{'round':t,'origin':decision_origin,'hypothesis':p,'bootstrap':stat,'allowed_options':['accept','reject'],'statistical_gate':fallback_verdict['choice']},fallback_verdict)
                # A model cannot override a failed statistical gate.
                accepted=accepted and verdict['choice']=='accept'
                record={**p,'round':t,'method':specs[name]['method'],'parameters':specs[name]['parameters'],'verdict':'accepted' if accepted else 'rejected','reason':verdict['reason'],'bootstrap_ci':stat['ci'],'n_origins':stat['n_origins'],'evaluated_at':decision_origin,'validation_origins':sorted(v.origin_date.unique().tolist())}
                hypotheses.append(record);memory.write('CRITIC',t,decision_origin,'verdict',record);p['closed']=True
                decisions.append(record)
            else:
                decisions.append({'group':g,'candidate':name,'verdict':'pending','reason':f"Only {stat['n_origins']} later matured origins; need {CONFIG['min_critic_origins']}."})
        pending=[p for p in pending if not p.get('closed')]
        g=group_names[(t-1)%len(group_names)];default=candidate_ids[(t-1)//len(group_names)%len(candidate_ids)]
        found=research_round(runtime,memory,searcher,t,decision_origin,g);loop_evidence.append(found)
        analyst_memory=memory.read('ANALYST',t,decision_origin,kinds=['verdict','evidence'])
        default,used_sources=evidence_guided_default(default,analyst_memory,candidate_ids)
        # Propose a new immutable method+parameter set, evaluated only on origins >= frozen_at.
        proposal=runtime.call('ANALYST',{'round':t,'origin':decision_origin,'group':g,'allowed_options':candidate_ids,'memory':analyst_memory,'available_history_origins':past_origins,'question':'Which bounded hypothesis should be frozen now for future testing? Cite any supplied source that motivates the method in your reason.','fallback_source_urls':used_sources},{'choice':default,'reason':f'Test whether {default} improves {g} quantiles on subsequent unseen origins.'})
        name=proposal['choice'];p={'id':f'h{t:02d}','group':g,'candidate':name,'method':specs[name]['method'],'parameters':specs[name]['parameters'],'frozen_at':decision_origin,'proposed_round':t,'reason':proposal['reason'],'evidence_urls':sorted({n['url'] for e in analyst_memory if e['kind']=='evidence' for n in e['content'].get('sources',[])})}
        pending.append(p);memory.write('ANALYST',t,decision_origin,'hypothesis',p)
        # Analyst also records mature observations, useful to other readers.
        summary={n:{'n_cells':len(c),'mean_official_loss':float(c.loss.mean()) if len(c) else None} for n,c in visible.items()}
        memory.write('ANALYST',t,decision_origin,'results',{'observed_through':decision_origin,'methods':summary})
        recalled=memory.read('FORECASTER',t,decision_origin,kinds=['hypothesis','results','verdict'])
        for g in group_names:
            approved={e['content']['candidate'] for e in recalled if e['kind']=='verdict' and e['content']['group']==g and e['content']['verdict']=='accepted'}
            allowed=['drift']+sorted(approved)
            # Select using only past mature losses; the next-origin error remains hidden.
            ranking={n:float(visible[n][visible[n].group==g].loss.mean()) for n in allowed if len(visible[n][visible[n].group==g])}
            choice=min(ranking,key=ranking.get) if ranking else 'drift'
            pick=runtime.call('FORECASTER',{'round':t,'origin':decision_origin,'group':g,'allowed_options':allowed,'past_loss':ranking,'memory':recalled},{'choice':choice,'reason':'Choose lowest past mature official loss among critic-approved methods and drift.'})
            selected[g]=pick['choice']
        part=pd.concat([frames[selected[g]][(frames[selected[g]].origin_date==decision_origin)&frames[selected[g]].series_id.map(groups).eq(g)] for g in group_names],ignore_index=True)
        online.append(part);cumulative=pd.concat(online,ignore_index=True);path='results/online_forecasts.csv';write_fc(cumulative,path)
        # Evaluator may observe future truth only AFTER all decisions are committed; results never enter same-round inputs.
        dr,_=score(path,f'round_{t:02d}_drift','drift');lv,_=score(path,f'round_{t:02d}_last_value')
        rounds.append({'round':t,'origin_date':decision_origin,'skill_vs_drift':dr['overall']['skill_pooled'],'skill_vs_last_value':lv['overall']['skill_pooled'],'coverage':lv['overall']['coverage']['within_q10_q90'],'decisions':decisions,'cumulative_skill_vs_drift':dr['overall']['skill_pooled'],'selected':dict(selected)})
        audit.append({'round':t,'forecast_origin':decision_origin,'training_origins':past_origins,'max_available_target_date':max((str(c.target_date.max()) for c in visible.values() if len(c)),default=None),'selections':dict(selected),'forecast_sha256':hashlib.sha256(part[COLUMNS].to_csv(index=False).encode()).hexdigest()})
        print('Round',t,decision_origin,'cumulative skill vs drift',dr['overall']['skill_pooled'],flush=True)
    for p in pending:
        pv=visible[p['candidate']]; pv=pv[(pv.group==p['group']) & (pv.origin_date>=p['frozen_at'])]
        pdri=visible['drift']; pdri=pdri[(pdri.group==p['group']) & (pdri.origin_date>=p['frozen_at'])]
        ps=bootstrap(pv,pdri,CONFIG['seed']+14)
        hypotheses.append({**p,'round':14,'method':specs[p['candidate']]['method'],'parameters':specs[p['candidate']]['parameters'],'verdict':'pending','reason':'Not enough subsequent origins before replay ends; cannot promote.','bootstrap_ci':ps['ci'],'n_origins':ps['n_origins']})
    # Long-term Researcher notes enter memory only after the historical replay is closed.
    narrative=json.loads(Path('data/evidence.json').read_text()) if Path('data/evidence.json').exists() else {'results':[]}
    for note in narrative.get('results',[]):
        assert note['publication_date']<=CONFIG['cutoff']
        reviewed=runtime.call('RESEARCHER',{'round':15,'origin':CONFIG['cutoff'],'allowed_options':['narrative_only'],'evidence':note},{'choice':'narrative_only','reason':note['sentence']})
        memory.write('RESEARCHER',15,CONFIG['cutoff'],'evidence',{'title':note['title'],'url':note['url'],'publication_date':note['publication_date'],'sentence':reviewed['reason'],'source':note['source'],'scope':'Argued long-term view only; not used in historical forecasts.'})
    memory.read('ANALYST',15,CONFIG['cutoff'],kinds=['verdict','evidence'])
    online_lv,online_cells=score('results/online_forecasts.csv','online_last_value');online_dr,online_drift_cells=score('results/online_forecasts.csv','online_drift','drift')
    drift_overlap=cells['drift'][cells['drift'].origin_date.isin(CONFIG['origins'][1:])]
    uncertainty=bootstrap(online_cells,drift_overlap,CONFIG['seed'])
    improve=online_dr['overall']['skill_pooled'] is not None and online_dr['overall']['skill_pooled']>0 and uncertainty['ci'][1]<0
    final_parts=[]
    for g in group_names:
        method=selected[g] if improve else 'drift'
        final_parts.append(forecast(store,[sid for sid in ids if groups[sid]==g],[cutoff],CONFIG['horizons'],specs[method]))
    write_fc(pd.concat(final_parts,ignore_index=True),'forecasts.csv')
    final_label='critic-gated group methods' if improve and any(v!='drift' for v in selected.values()) else 'drift fallback'
    # Paired uncertainty for the prequential forecasts, evaluated on the same origin/cell grid.
    drift_overlap=cells['drift'][cells['drift'].origin_date.isin(CONFIG['origins'][1:])]
    uncertainty=bootstrap(online_cells,drift_overlap,CONFIG['seed'])
    save('results/replay_audit.json',audit);save('results/hypotheses.json',hypotheses);save('results/learning_curve.json',rounds);save('results/uncertainty.json',uncertainty)
    save('results/method_summary.json',{n:r['overall'] for n,r in reports.items()})
    checks=validate_outputs(ids,PACK)
    evidence=json.loads(Path('data/evidence.json').read_text()) if Path('data/evidence.json').exists() else {'status':'blocked_missing_exa_key','results':[]}
    economic=json.loads(Path('data/economic.json').read_text()) if Path('data/economic.json').exists() else {'scenarios':[],'notes':['Economic research not yet built.']}
    modes=sorted(runtime.modes)
    events=[json.loads(line) for line in Path('logs/agent_log.jsonl').read_text().splitlines()]
    sponsors=sponsor_report(events,loop_evidence);save('results/loop_evidence.json',loop_evidence)
    if Path('results/modal/execution.json').exists():sponsors['modal']=json.loads(Path('results/modal/execution.json').read_text())
    sponsors['recorded_live_run']=retain_live_receipt(ROOT,CONFIG,events,sponsors)
    save('results/sponsor_audit.json',sponsors);save('demo/sponsor_audit.json',sponsors)
    warnings=['37 posted headline targets at Nov 6; the brief’s 97 at Oct 24 include 80 AWS archive series.','Historical cohort selected at final cutoff: retrospective cohort/survivorship limitation; forecast values and decisions remain time-filtered.','Final Nov 6 scoring truth is withheld: no final-submission performance claim.','Paired bootstrap is exploratory with few origin clusters and repeated tests; no multiplicity-controlled guarantee.']
    if any('deterministic' in m for m in modes):warnings.append('OPENAI NOT RUN: deterministic bounded policy replay; configure credentials and run --live for LLM agents.')
    if memory.backend!='past.dev':warnings.append('Past.dev current backend: '+memory.backend+'; recorded source: '+str(getattr(memory,'recorded_backend',None))+'. Actual live access is audited separately.')
    if sponsors['exa']['status']=='blocked_no_live_evidence':warnings.append('EXA MAIN LOOP UNVERIFIED: no qualifying live/cached Exa results. Direct public narrative citations are separately labeled.')
    payload={'status':{'agent_mode':', '.join(modes),'memory_backend':memory.backend,'evidence_status':evidence.get('status'),'final_method':final_label,'cutoff':CONFIG['cutoff'],'n_series':len(ids),'n_rows':len(ids)*3,'warnings':warnings},'metrics':{'online_last_value':online_lv['overall'],'online_drift':online_dr['overall'],'baseline':reports['drift']['overall']},'rounds':rounds,'hypotheses':hypotheses,'targets':target_schema,'forecasts':pd.read_csv('forecasts.csv').to_dict('records'),'evidence':evidence.get('results',[]),'economic':economic,'checks':checks,'uncertainty':uncertainty,'loop_evidence':loop_evidence,'sponsors':sponsors}
    save('demo/data.json',payload);save('results/summary.json',payload['status']);write_findings(payload,reports)
    for f in ['forecasts.csv','forecasts_fallback.csv','findings.md','config.json','README.md','ATTRIBUTION.md']:shutil.copyfile(f,'demo/'+f)
    shutil.copyfile('data/targets.csv','demo/targets.csv')
    print(json.dumps(payload['status'],indent=2))

def validate_outputs(ids,pack):
    f=pd.read_csv('forecasts.csv');clean,problems=validate_forecast(f,[1,3,7]);assert not problems;assert len(f)==len(ids)*3;assert set(f.series_id)==set(ids);assert (f.origin_date==CONFIG['cutoff']).all();assert np.isfinite(f[['q10','q50','q90']]).all().all()
    assert (pd.to_datetime(f.target_date)==pd.to_datetime(f.origin_date)+pd.to_timedelta(f.horizon_days,unit='D')).all()
    # Controlled contamination fixture, never fed to a forecaster.
    history=pd.read_csv('data/history.csv');bad=history.iloc[[0]].copy();bad['date']='2026-11-07';pd.concat([history,bad]).to_csv('results/contaminated_history_test_only.csv',index=False)
    p=subprocess.run([sys.executable,'-B',str(pack/'starter/scorer.py'),'--forecast','forecasts.csv','--truth','data/history.csv','--history','results/contaminated_history_test_only.csv','--frozen-cutoff',CONFIG['cutoff'],'--horizons','1,3,7','--out','results/refusal.json'],capture_output=True,text=True)
    Path('logs/refusal.log').write_text(p.stdout+p.stderr);assert p.returncode==2 and 'REFUSED' in p.stderr
    Path('results/contaminated_history_test_only.csv').unlink()
    checks=[{'name':'Starter forecast validity','status':'passed','detail':f'{len(f)} rows; {len(ids)} actual posted headline series; positive ordered finite quantiles and exact dates.'},{'name':'Frozen cutoff refusal','status':'passed','detail':'Synthetic post-cutoff history row refused with exit 2; contamination fixture deleted.'},{'name':'Unseen-origin chronology','status':'passed','detail':'Selections frozen before same-origin scoring; only mature earlier-origin cells enter decisions.'},{'name':'GitHub publication identity','status':'passed' if (ROOT/'.git').exists() else 'pending','detail':'User authorized repository creation and pushes as yfandev only; credentials and original pack excluded.'}]
    save('results/validation.json',checks);return checks

def write_findings(payload,reports):
    o=payload['metrics']['online_last_value'];d=payload['metrics']['online_drift'];u=payload['uncertainty']
    text=f'''# GPU Value Scientist

Question: can bounded experiments and an auditable memory improve posted GPU rental quantiles over drift?

## Measured result

Final submission: **{payload['status']['final_method']}**, {payload['status']['n_rows']} rows across {payload['status']['n_series']} posted-rental series, origin 2026-11-06, horizons 1, 3, 7.

Historical prequential results (14 unseen origins; NOT the withheld November scoring window): pooled skill against last value **{o['skill_pooled']}**; against drift **{d['skill_pooled']}**; interval coverage **{o['coverage']['within_q10_q90']}**. Mean series skill {o['skill_mean_of_series']}, median {o['skill_median_of_series']}, geometric-mean skill {o['skill_geomean']}. Scored cells: {o['n_cells']}. All scores come from the unmodified starter scorer.py, with complete reports in results/.

Paired mean loss difference against drift: {u['mean_loss_difference']}; exploratory origin-cluster bootstrap 95% CI {u['ci']} across {u['n_origins']} origin clusters. Repeated tests and small cluster counts limit inferential strength. Zero difference is not improvement.

## Evaluation and targets

config.json was saved and hashed before any score was run. Fifteen weekly origins run July 15–October 21 inclusive, the starter's interpretation of July 15–October 24. October 24 is a separate quickstart cutoff. Each forecast slices history at its own origin. Calibration uses only matured residuals. Each proposed hypothesis is frozen before its validation forecast origins, with at least three later origins required by the critic. Predictions for round t are committed before their error is evaluated. The 14-round curve evaluates July 22–October 21. Results from the same round never enter its own choices.

Important brief discrepancy: the starter's October 24 headline catalog has 97 series, of which 80 are AWS archive spot and only 17 are posted rentals. At November 6 the official builder yields **37 posted-rental headline series**. We forecast that actual set, not 97 invented posted targets. The original 97-series quickstart remains in results/quickstart. data/targets.csv declares every instrument and full benchmark contract. Posted hyperscaler_spot is a collector's daily statistic, distinct from the unscored AWS archive. Source-specific medians are never chained. No index date alignment or interpolation across the AWS hole is used. The fixed final-cutoff cohort creates retrospective selection/survivorship bias in earlier backtests; this is not a real-time cohort backtest.

## Methods and research loop

JSON parameter sets select fixed library code: starter drift, last_value_empirical, 28/56/90-day empirical increments, recent-volatility-scaled intervals, step-aware shrinkage, and prequential residual quantile calibration. Recent methods fall back to full-history increments when samples are sparse. Step shrinkage is a hypothesis about price stickiness, not a structural economic model. Calibration is conformal-style, not an exchangeability guarantee for dependent time series.

Agents may select bounded method IDs only and cannot execute generated code. Analyst freezes hypotheses and records mature results; Critic tests later-origin paired official losses and writes verdicts; Forecaster reads shared records and picks only drift or critic-approved candidates; Researcher searches Exa inside each round using that origin’s publication cutoff, writes cited notes to memory, and Analyst reads those notes before proposing bounded experiments. Search-publication dates do not prove page immutability; externally informed live runs are method-discovery experiments with that limitation. Every decision and rejection is in logs/agent_log.jsonl. Cached calls are keyed by model, temperature, schema, role, and input content. Offline mode never makes an API call.

Runtime: **{payload['status']['agent_mode']}**. Shared memory: **{payload['status']['memory_backend']}**. Exa: **{payload['status']['evidence_status']}**. Deterministic fallback roles are software policies, not evidence that OpenAI agents ran. Local-memory success is not a claim of past.dev integration success.

## Experiments (development diagnostics, not all unseen)

|Method|Pooled skill vs last value|Coverage|
|---|---:|---:|
'''
    for name,r in reports.items():text+=f"|{name}|{r['overall']['skill_pooled']}|{r['overall']['coverage']['within_q10_q90']}|\n"
    text+='\n## Hypotheses and learning\n\n'
    for h in payload['hypotheses']:text+=f"- {h['id']} / {h['group']} / {h['candidate']}: **{h['verdict']}** — {h['reason']} CI {h['bootstrap_ci']}.\n"
    text+='\nFinal promotion requires positive online skill and an upper paired-loss CI below zero. Keeping drift when alternatives fail is a negative result, not a successful improvement claim. The full-library table is exploratory development feedback; only the online curve represents the specified decision process on subsequent origins.\n\n'
    if Path('docs/economic_view.md').exists():text+=Path('docs/economic_view.md').read_text()
    text+='\n## Limitations\n\n'+'\n'.join('- '+x for x in payload['status']['warnings'])+'\n'
    text+='\n## Reproduction and attribution\n\nRun `./reproduce.sh` after installing requirements in a local virtual environment. `./reproduce.sh --live` requires configured API keys and rebuilds live decisions. The pack is read-only, verified with MANIFEST.sha256, and never bundled with generated submission files.\n\nPacific Machines (2026), gpu-price-pack v0.1.1-handover, CC BY 4.0. Full unchanged upstream attribution accompanies this work in ATTRIBUTION.md; original notices remain in the pack. Derived changes: target extraction, history-only forecasts, official score reports, and research decisions. No endorsement implied.\n'
    Path('findings.md').write_text(text)

if __name__=='__main__':main()
