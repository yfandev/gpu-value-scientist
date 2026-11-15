"""One frozen price-reset distribution experiment; no parameter search.

Uses only exact observed dates. Official Pacific scorer supplies all scores.
Existing competition files are never written. This study is retrospective.
"""
from pathlib import Path
import datetime as dt
import hashlib,json,math,subprocess,sys
sys.dont_write_bytecode=True
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/price_reset_study'
PROTOCOL_SHA='577025ea38996e03eda04038a2ebba71b6074b5afea493be049a651d60b73c46'
PROTOCOL=json.loads((OUT/'protocol.json').read_text())
PACK=ROOT/json.loads((ROOT/'config.json').read_text())['pack']
sys.path.insert(0,str(PACK/'starter'))
from _common import SeriesStore,read_series_csv
from baselines import forecast_one
KEY=['series_id','origin_date','horizon_days']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def day(s):return dt.date.fromisoformat(str(s)[:10]).toordinal()
def iso(d):return dt.date.fromordinal(int(d)).isoformat()
def weighted_quantile(values,weights,qs=(.1,.5,.9)):
    v=np.asarray(values,float);w=np.asarray(weights,float)
    assert len(v)==len(w) and len(v)>0 and np.isfinite(v).all() and np.isfinite(w).all() and (w>=0).all() and w.sum()>0
    idx=np.argsort(v,kind='stable');v=v[idx];cdf=np.cumsum(w[idx])/w.sum()
    return v[np.minimum(np.searchsorted(cdf,qs,side='left'),len(v)-1)]
class ResetDistribution:
    def __init__(self,history,targets):
        self.meta=targets.set_index('series_id')[['source_id','instrument_class']].to_dict('index')
        history=history[history.series_id.isin(self.meta)].copy()
        if 'is_filled' in history:history=history[~history.is_filled.astype(str).str.lower().isin(['1','1.0','true'])]
        history=history[(history.value>0)&np.isfinite(history.value)]
        assert not history.duplicated(['series_id','date']).any()
        self.values={sid:{day(r.date):float(r.value) for r in frame.itertuples()} for sid,frame in history.groupby('series_id')}
        self.peers={sid:[p for p in self.meta if p!=sid and self.meta[p]==self.meta[sid]] for sid in self.meta}
        self.features={};self.ages={}
        for sid,vals in self.values.items():
            ages={}
            for d in sorted(vals):
                ages[d]=min(90,ages.get(d-1,0)+1) if d-1 in vals and abs(math.log(vals[d]/vals[d-1]))<=1e-9 else 0
            self.ages[sid]=ages
        for sid,vals in self.values.items():
            for d in sorted(vals):
                pairs=[math.log(vals[t]/vals[t-1]) for t in range(d-27,d+1) if t in vals and t-1 in vals]
                if len(pairs)<8:continue
                one=math.log(vals[d]/vals[d-1]) if d-1 in vals else 0.
                seven=math.log(vals[d]/vals[d-7]) if d-7 in vals else 0.
                changes=[];peer_seven=[]
                for p in self.peers[sid]:
                    pv=self.values.get(p,{})
                    if d in pv and d-1 in pv:changes.append(abs(math.log(pv[d]/pv[d-1]))>1e-9)
                    if d in pv and d-7 in pv:peer_seven.append(math.log(pv[d]/pv[d-7]))
                f=np.array([math.log1p(self.ages[sid][d])/math.log(31),np.clip(seven,-.5,.5)/.1,np.clip(one,-.25,.25)/.05,np.mean(changes) if changes else 0.,np.clip(np.median(peer_seven) if peer_seven else 0.,-.5,.5)/.1,np.mean(np.abs(pairs)>1e-9)],float)
                self.features[sid,d]=f
        self.samples={}
        for h in PROTOCOL['horizons']:
            rows=[]
            for (sid,d),features in sorted(self.features.items()):
                vals=self.values[sid]
                if d+h in vals:rows.append((features,math.log(vals[d+h]/vals[d]),d,d+h,self.meta[sid]['instrument_class']))
            self.samples[h]={'x':np.array([r[0] for r in rows]),'r':np.array([r[1] for r in rows]),'d':np.array([r[2] for r in rows]),'target':np.array([r[3] for r in rows]),'class':np.array([r[4] for r in rows])}
    def predict(self,sid,origin,h,with_peers=True):
        d=day(origin) if isinstance(origin,str) else int(origin)
        audit={'series_id':sid,'origin_date':iso(d),'horizon_days':h,'with_peers':with_peers,'method':'drift_fallback','reason':'current_feature_unavailable'}
        if (sid,d) not in self.features:return None,audit
        samples=self.samples[h];mask=(samples['target']<d)&(samples['d']>=d-180)&(samples['class']==self.meta[sid]['instrument_class'])
        x=samples['x'][mask];r=samples['r'][mask];dates=samples['d'][mask];targets=samples['target'][mask]
        audit.update(n_training=len(r),n_reset_labels=int((np.abs(r)>1e-9).sum()))
        if len(r)<64 or (np.abs(r)>1e-9).sum()<10:audit['reason']='sparse_training_or_resets';return None,audit
        columns=[0,1,2,3,4,5] if with_peers else [0,1,2,5]
        distance=np.sum((x[:,columns]-self.features[sid,d][columns])**2,axis=1)
        idx=np.argsort(distance,kind='stable')[:128]
        recency=np.exp(-math.log(2)*(d-dates)/90)
        nw=recency[idx]/(1+distance[idx]);nw=.8*nw/nw.sum();uw=.2*recency/recency.sum()
        weights=np.concatenate([nw,uw]);returns=np.concatenate([r[idx],r])
        quantiles=self.values[sid][d]*np.exp(weighted_quantile(returns,weights))
        assert np.isfinite(quantiles).all() and quantiles[0]>0 and np.all(np.diff(quantiles)>=0)
        audit.update(method='price_reset_distribution',reason='sufficient_support',max_training_target=iso(targets.max()),max_training_feature_date=iso(dates.max()),n_neighbors=len(idx),reset_probability=float(weights[np.abs(returns)>1e-9].sum()),current_price=self.values[sid][d])
        return quantiles,audit

def make_forecasts(model,keys,store,with_peers=True):
    rows=[];audit=[]
    for k in keys.itertuples(index=False):
        origin=day(k.origin_date);h=int(k.horizon_days);q,a=model.predict(k.series_id,origin,h,with_peers)
        if q is None:
            f=forecast_one(store,k.series_id,origin,[h],'drift',20,None)
            if not f:raise ValueError('No fallback history for requested forecast')
            q=np.array([f[0][v] for v in ['q10','q50','q90']])
        rows.append({'series_id':k.series_id,'origin_date':k.origin_date,'horizon_days':h,'q10':q[0],'q50':q[1],'q90':q[2],'target_date':iso(origin+h)})
        audit.append(a)
    return pd.DataFrame(rows),pd.DataFrame(audit)

def score(fc,label,baseline_fc=None):
    report=OUT/f'{label}.json';cells=OUT/f'{label}_cells.csv'
    cmd=[sys.executable,'-B',str(PACK/'starter/scorer.py'),'--forecast',str(fc),'--truth',str(ROOT/'data/history.csv'),'--history',str(ROOT/'data/history.csv'),'--series-ids','@'+str(ROOT/'data/target_ids.txt'),'--horizons','1,3,7','--skill-baseline','drift','--no-missing-as-baseline','--out',str(report),'--per-cell',str(cells)]
    if baseline_fc:cmd+=['--baseline-forecast',str(baseline_fc)]
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    result=json.loads(report.read_text());assert result['forecast_validation']['n_problems']==0
    if baseline_fc:assert result['baseline_forecast_validation']['n_problems']==0
    data=pd.read_csv(cells);assert set(data.status)=={'scored'}
    return result['overall'],data

def bootstrap(cells,loss='loss',base='baseline_loss'):
    grouped=cells.groupby('origin_date')[[loss,base]].sum()
    rng=np.random.default_rng(20261115);idx=rng.integers(0,len(grouped),size=(5000,len(grouped)))
    a=grouped[loss].to_numpy()[idx].sum(axis=1);b=grouped[base].to_numpy()[idx].sum(axis=1)
    if (b<=0).any():return {'ci':[None,None],'n_origins':len(grouped),'status':'zero_baseline_loss_prevents_claim'}
    vals=1-a/b
    return {'ci':np.quantile(vals,[.025,.975]).tolist(),'n_origins':len(grouped),'draws':5000,'status':'computed'}

def main():
    assert sha(OUT/'protocol.json')==PROTOCOL_SHA
    protected={p:sha(ROOT/p) for p in ['forecasts.csv','forecasts_calibrated.csv','forecasts_extended.csv']}
    history=pd.read_csv(ROOT/'data/history.csv');assert history.date.max()<='2026-11-06'
    targets=pd.read_csv(ROOT/'data/targets.csv');model=ResetDistribution(history,targets)
    store=SeriesStore(read_series_csv(ROOT/'data/history.csv'))
    selected=pd.read_csv(ROOT/'results/calibration_study/forecasts.csv')
    keys=selected[KEY].drop_duplicates().sort_values(KEY)
    assert sorted(keys.origin_date.unique())==PROTOCOL['origins']
    candidate,audit=make_forecasts(model,keys,store,True)
    ablation,ablation_audit=make_forecasts(model,keys,store,False)
    audit.to_csv(OUT/'audit.csv',index=False);ablation_audit.to_csv(OUT/'ablation_audit.csv',index=False)
    summaries={}
    for scope,origins in [('all',PROTOCOL['origins']),('primary',PROTOCOL['primary_evaluation_origins'])]:
        frames={'candidate':candidate,'no_peer':ablation,'selected':selected};reports={};cells={}
        for name,frame in frames.items():
            path=OUT/f'{scope}_{name}.csv';frame[frame.origin_date.isin(origins)].to_csv(path,index=False,float_format='%.10g')
            reports[name],cells[name]=score(path,f'{scope}_{name}_vs_drift')
        for name in ['no_peer','selected']:
            assert set(map(tuple,cells['candidate'][KEY].values))==set(map(tuple,cells[name][KEY].values))
        reports['candidate_vs_selected'],selected_cells=score(OUT/f'{scope}_candidate.csv',f'{scope}_candidate_vs_selected',OUT/f'{scope}_selected.csv')
        reports['candidate_vs_no_peer'],no_peer_cells=score(OUT/f'{scope}_candidate.csv',f'{scope}_candidate_vs_no_peer',OUT/f'{scope}_no_peer.csv')
        expected_keys=set(map(tuple,cells['candidate'][KEY].values))
        assert expected_keys==set(map(tuple,selected_cells[KEY].values))==set(map(tuple,no_peer_cells[KEY].values))
        summaries[scope]={'reports':reports,'uncertainty_vs_drift':bootstrap(cells['candidate']),'uncertainty_vs_selected':bootstrap(selected_cells),'peer_ablation_uncertainty':bootstrap(no_peer_cells),'middle_vs_drift':bootstrap(cells['candidate'],'loss_q50','baseline_loss_q50'),'middle_vs_selected':bootstrap(selected_cells,'loss_q50','baseline_loss_q50'),'middle_observed_beats_both':bool(cells['candidate'].loss_q50.mean()<cells['candidate'].baseline_loss_q50.mean() and selected_cells.loss_q50.mean()<selected_cells.baseline_loss_q50.mean())}
    primary=summaries['primary'];r=primary['reports']
    def positive_ci(x):return x['ci'][0] is not None and x['ci'][0]>0
    gates={'pooled_beats_both':r['candidate']['skill_pooled']>0 and r['candidate_vs_selected']['skill_pooled']>0,'bootstrap_supports_both':positive_ci(primary['uncertainty_vs_drift']) and positive_ci(primary['uncertainty_vs_selected']),'mean_series_not_harmed':r['candidate']['skill_mean_of_series']>=max(0,r['selected']['skill_mean_of_series']),'coverage_no_farther_from_target':abs(r['candidate']['coverage']['within_q10_q90']-.8)<=abs(r['selected']['coverage']['within_q10_q90']-.8)}
    changed=candidate.merge(selected,on=KEY,suffixes=('_new','_old'))
    middle_claim=primary['middle_observed_beats_both'] and positive_ci(primary['middle_vs_drift']) and positive_ci(primary['middle_vs_selected'])
    from price_reset_guards import validate_guards
    guards=validate_guards(history,targets,keys,candidate,store)
    gates['leakage_and_distribution_checks']=guards['passed']
    (OUT/'guards.json').write_text(json.dumps(guards,indent=2)+'\n')
    final_path=None
    if all(gates.values()):
        final_keys=pd.read_csv(ROOT/'forecasts.csv')[KEY]
        final,final_audit=make_forecasts(model,final_keys,store,True)
        final_path='forecasts_price_reset.csv';final.to_csv(ROOT/final_path,index=False,float_format='%.10g');final_audit.to_csv(OUT/'final_audit.csv',index=False)
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    summary={'protocol_sha256':PROTOCOL_SHA,'status':'passes_predeclared_gates_pending_independent_review' if all(gates.values()) else 'rejected','promotion_gates':gates,'middle_prediction_improvement_supported':middle_claim,'changed_median_count':int((~np.isclose(changed.q50_new,changed.q50_old,rtol=1e-10,atol=1e-12)).sum()),'n_predictions':len(candidate),'candidate_file':final_path,'protected_sha256':protected,'evaluations':summaries,'caveat':PROTOCOL['design_status']}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'status':summary['status'],'gates':gates,'middle_improvement_supported':middle_claim,'changed_medians':summary['changed_median_count'],'primary_candidate':r['candidate'],'primary_selected':r['selected'],'CI_vs_drift':primary['uncertainty_vs_drift'],'CI_vs_selected':primary['uncertainty_vs_selected']},indent=2))
if __name__=='__main__':main()
