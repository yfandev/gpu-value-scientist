"""Frozen sequential follow-up: learned reset median, existing calibrated bounds."""
from pathlib import Path
import json,sys,subprocess
sys.dont_write_bytecode=True
import numpy as np
import pandas as pd
from price_reset_study import ROOT,PACK,ResetDistribution,SeriesStore,read_series_csv,forecast_one,make_forecasts,sha,day,iso,bootstrap,KEY
from calibration_study import calibrate
OUT=ROOT/'results/reset_median_followup'
HASH='baa340570fab8c722698ff536808142af1e5a60687b516e0c77bc2304920f4aa'
P=json.loads((OUT/'protocol.json').read_text())
COLS=['series_id','origin_date','horizon_days','q10','q50','q90','target_date']
def combine(reset,selected):
    z=selected.merge(reset[KEY+['q50']],on=KEY,how='inner',suffixes=('_selected','_reset'),validate='one_to_one')
    assert len(z)==len(selected)==len(reset)
    z['q50']=z.q50_reset;z['q10']=np.maximum(1e-9,np.minimum(z.q10,z.q50));z['q90']=np.maximum(z.q90,z.q50)
    assert np.isfinite(z[['q10','q50','q90']]).all().all() and (z.q10>0).all() and (z.q10<=z.q50).all() and (z.q50<=z.q90).all()
    return z[COLS]
def drift_forecasts(store,targets,origins,horizons):
    rows=[]
    for origin in origins:
        for sid in sorted(targets.series_id):
            rows+=forecast_one(store,sid,day(origin),horizons,'drift',20,None) if sid in store else []
    return pd.DataFrame(rows)[COLS]
def official(fc,label,horizons,base=None):
    path=OUT/f'{label}_forecasts.csv';fc[COLS].to_csv(path,index=False,float_format='%.10g')
    report=OUT/f'{label}.json';cells=OUT/f'{label}_cells.csv'
    cmd=[sys.executable,'-B',str(PACK/'starter/scorer.py'),'--forecast',str(path),'--truth',str(ROOT/'data/history.csv'),'--history',str(ROOT/'data/history.csv'),'--series-ids','@'+str(ROOT/'data/target_ids.txt'),'--horizons',','.join(map(str,horizons)),'--skill-baseline','drift','--no-missing-as-baseline','--out',str(report),'--per-cell',str(cells)]
    if base is not None:
        bpath=OUT/f'{label}_baseline.csv';base[COLS].to_csv(bpath,index=False,float_format='%.10g');cmd+=['--baseline-forecast',str(bpath)]
    subprocess.run(cmd,capture_output=True,text=True,check=True);r=json.loads(report.read_text());assert r['forecast_validation']['n_problems']==0
    if base is not None:assert r['baseline_forecast_validation']['n_problems']==0
    c=pd.read_csv(cells);assert set(c.status)=={'scored'}
    return r['overall'],c

def main():
    assert sha(OUT/'protocol.json')==HASH
    assert sha(ROOT/'results/price_reset_study/protocol.json')==P['immutable_model_protocol_sha256']
    protected={p:sha(ROOT/p) for p in ['forecasts.csv','forecasts_calibrated.csv','forecasts_extended.csv']}
    history=pd.read_csv(ROOT/'data/history.csv');targets=pd.read_csv(ROOT/'data/targets.csv');prior=pd.read_csv(ROOT/'results/online_forecasts.csv')
    assert sorted(prior.origin_date.unique())==json.loads((ROOT/'results/price_reset_study/protocol.json').read_text())['origins']
    model=ResetDistribution(history,targets);store=SeriesStore(read_series_csv(ROOT/'data/history.csv'))
    old_reset=pd.read_csv(ROOT/'results/price_reset_study/all_candidate.csv');old_selected=pd.read_csv(ROOT/'results/calibration_study/forecasts.csv');old_hybrid=combine(old_reset,old_selected)
    nov_drift=drift_forecasts(store,targets,P['additional_check_origins'],P['additional_check_horizons'])
    nov_reset,nov_audit=make_forecasts(model,nov_drift[KEY],store,True)
    nov_selected,cal_audit=calibrate(nov_drift,history,targets,reference_forecasts=prior)
    nov_selected.q10=nov_selected.q10.clip(lower=1e-9)
    nov_hybrid=combine(nov_reset,nov_selected)
    nov_audit.to_csv(OUT/'november_reset_audit.csv',index=False);cal_audit.to_csv(OUT/'november_calibration_audit.csv',index=False)
    summaries={}
    for name,hybrid,selected,horizons in [('all_old',old_hybrid,old_selected,[1,3,7]),('primary_old',old_hybrid[old_hybrid.origin_date.isin(P['primary_old_dates'])],old_selected[old_selected.origin_date.isin(P['primary_old_dates'])],[1,3,7]),('november',nov_hybrid,nov_selected,[1,3])]:
        rh,ch=official(hybrid,name+'_hybrid_vs_drift',horizons)
        rs,cs=official(selected,name+'_selected_vs_drift',horizons)
        rr,cr=official(hybrid,name+'_hybrid_vs_selected',horizons,selected)
        assert set(map(tuple,ch[KEY].values))==set(map(tuple,cs[KEY].values))==set(map(tuple,cr[KEY].values))
        summaries[name]={'hybrid_vs_drift':rh,'selected_vs_drift':rs,'hybrid_vs_selected':rr,'CI_vs_drift':bootstrap(ch) if name!='november' else None,'CI_vs_selected':bootstrap(cr) if name!='november' else None,'n_scored_cells':len(ch)}
    checks=[]
    for origin in P['additional_check_origins']:
        base=nov_drift[nov_drift.origin_date==origin];expected=nov_hybrid[nov_hybrid.origin_date==origin].set_index(KEY)[['q10','q50','q90']]
        for kind in ['truncate_future','perturb_future']:
            hh=history[history.date<=origin].copy() if kind=='truncate_future' else history.copy()
            if kind=='perturb_future':hh.loc[hh.date>origin,'value']*=1e6
            guard_store=SeriesStore(hh.assign(day=hh.date.map(day)).sort_values(['series_id','day']))
            rr,_=make_forecasts(ResetDistribution(hh,targets),base[KEY],guard_store,True)
            ss,aa=calibrate(base,hh,targets,reference_forecasts=prior);ss.q10=ss.q10.clip(lower=1e-9)
            got=combine(rr,ss).set_index(KEY)[['q10','q50','q90']]
            assert np.allclose(got.values,expected.loc[got.index].values,rtol=1e-12,atol=1e-12)
            used=aa[aa.n>0];assert (used.max_target_date<origin).all()
            checks.append({'origin':origin,'check':kind,'passed':True,'n_predictions':len(got)})
    old=summaries['primary_old'];nov=summaries['november']
    def ci_good(x):return x['ci'][0] is not None and x['ci'][0]>0
    gates={'old_pooled_beats_both':old['hybrid_vs_drift']['skill_pooled']>0 and old['hybrid_vs_selected']['skill_pooled']>0,'old_intervals_positive':ci_good(old['CI_vs_drift']) and ci_good(old['CI_vs_selected']),'old_mean_not_harmed':old['hybrid_vs_drift']['skill_mean_of_series']>=max(0,old['selected_vs_drift']['skill_mean_of_series']),'old_coverage_not_harmed':abs(old['hybrid_vs_drift']['coverage']['within_q10_q90']-.8)<=abs(old['selected_vs_drift']['coverage']['within_q10_q90']-.8),'november_pooled_beats_both':nov['hybrid_vs_drift']['skill_pooled']>0 and nov['hybrid_vs_selected']['skill_pooled']>0,'november_mean_not_harmed':nov['hybrid_vs_drift']['skill_mean_of_series']>=nov['selected_vs_drift']['skill_mean_of_series'],'leakage_checks_pass':all(c['passed'] for c in checks)}
    final_file=None
    if all(gates.values()):
        frozen=pd.read_csv(ROOT/'forecasts_calibrated.csv');rr,aa=make_forecasts(model,frozen[KEY],store,True);final=combine(rr,frozen)
        # Validate using the untouched starter. November truth is deliberately unavailable.
        preview=OUT/'final_candidate.csv';final.to_csv(preview,index=False,float_format='%.10g')
        subprocess.run([sys.executable,'-B',str(PACK/'starter/scorer.py'),'--forecast',str(preview),'--truth',str(ROOT/'data/history.csv'),'--history',str(ROOT/'data/history.csv'),'--frozen-cutoff','2026-11-06','--horizons','1,3,7','--out',str(OUT/'final_validation.json')],capture_output=True,text=True,check=True)
        validation=json.loads((OUT/'final_validation.json').read_text());assert validation['forecast_validation']['n_problems']==0 and validation['forecast_validation']['rows_valid']==111
        final_file='forecasts_reset_median.csv';(ROOT/final_file).write_bytes(preview.read_bytes());aa.to_csv(OUT/'final_audit.csv',index=False)
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    result={'status':'passes_predeclared_gates_pending_independent_review' if all(gates.values()) else 'rejected','protocol_sha256':HASH,'gates':gates,'evaluations':summaries,'guards':checks,'new_file':final_file,'protected_sha256':protected,'caveat':P['reason_for_followup']+' '+P['additional_check_status']}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
