"""Frozen retrospective class-vs-global widening study; unmodified official scoring."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import json
import math
import subprocess
import numpy as np
import pandas as pd
try:
    from src.calibration_study import calibrate as current_calibrate
except ModuleNotFoundError:
    from calibration_study import calibrate as current_calibrate

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/group_calibration_study'
KEY=['series_id','origin_date','horizon_days']
RULE_HASH='09215e984505bd5996488e8d0a7a93ac167cdcdf28b3deb48de86bcbd2dfedb1'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def widen(forecasts, history, targets, grouped, archive=None):
    """Strict history-only residuals; one class pool with sparse global fallback."""
    meta=targets[['series_id','instrument_class']].drop_duplicates('series_id')
    def prepare(frame):
        f=frame.merge(meta,on='series_id',validate='many_to_one').copy()
        f['target_date']=(pd.to_datetime(f.origin_date)+pd.to_timedelta(f.horizon_days,unit='D')).dt.strftime('%Y-%m-%d')
        f['scale']=f.q50.abs().clip(lower=1e-9)
        return f
    current=prepare(forecasts)
    residuals=prepare(forecasts if archive is None else archive).merge(history[['series_id','date','value']].rename(columns={'date':'target_date','value':'y'}),on=['series_id','target_date'],validate='many_to_one')
    residuals['lower']=(residuals.q10-residuals.y)/residuals.scale
    residuals['upper']=(residuals.y-residuals.q90)/residuals.scale
    result=[]; audit=[]
    for row in current.itertuples(index=False):
        eligible=residuals[(residuals.origin_date<row.origin_date)&(residuals.target_date<row.origin_date)&(residuals.horizon_days==row.horizon_days)]
        class_pool=eligible[eligible.instrument_class==row.instrument_class]
        pools=([('class_horizon',class_pool)] if grouped else [])+[('global_horizon',eligible)]
        chosen=eligible.iloc[:0]; label='unchanged_insufficient_history'; lo=hi=0.
        for name,pool in pools:
            if len(pool)>=20 and pool.origin_date.nunique()>=2:
                chosen=pool; label=name; rank=min(len(pool),math.ceil((len(pool)+1)*.9))-1
                lo=max(0.,float(np.sort(pool.lower)[rank])); hi=max(0.,float(np.sort(pool.upper)[rank])); break
        result.append(dict(series_id=row.series_id,origin_date=row.origin_date,horizon_days=row.horizon_days,target_date=row.target_date,q10=max(0.,row.q10-row.scale*lo),q50=row.q50,q90=row.q90+row.scale*hi))
        audit.append(dict(series_id=row.series_id,origin_date=row.origin_date,horizon_days=row.horizon_days,instrument_class=row.instrument_class,pool=label,n=len(chosen),n_origins=chosen.origin_date.nunique(),class_n=len(class_pool),class_n_origins=class_pool.origin_date.nunique(),max_target_date=chosen.target_date.max() if len(chosen) else None,max_prior_origin=chosen.origin_date.max() if len(chosen) else None,lower_expansion=lo,upper_expansion=hi,rule_sha256=RULE_HASH))
    return pd.DataFrame(result),pd.DataFrame(audit)

def metrics(cells,official):
    out=official.aggregate(cells.to_dict('records'))
    series=[official.aggregate(c.to_dict('records')) for _,c in cells.groupby('series_id')]
    valid=[s for s in series if s['skill_pooled'] is not None]
    out.update(official.series_stats([s['skill_pooled'] for s in valid],[s['pinball']/s['baseline_pinball'] for s in valid]))
    out['mean_width']=float((cells.q90-cells.q10).mean())
    return out

def main():
    rule_path=OUT/'rule.json'; assert sha(rule_path)==RULE_HASH
    rule=json.loads(rule_path.read_text()); origins=rule['later_origins']
    protected={p:sha(ROOT/p) for p in ['forecasts.csv','forecasts_calibrated.csv']}
    cfg=json.loads((ROOT/'config.json').read_text()); scorer=ROOT/cfg['pack']/'starter/scorer.py'
    sys.path.insert(0,str(scorer.parent)); import scorer as official
    original=pd.read_csv(ROOT/'results/online_forecasts.csv')
    drift=pd.read_csv(ROOT/'results/forecast_drift.csv').merge(original[KEY],on=KEY,validate='one_to_one')
    history=pd.read_csv(ROOT/'data/history.csv'); targets=pd.read_csv(ROOT/'data/targets.csv')
    methods={'drift':drift}
    for name,grouped in [('global',False),('grouped',True)]:
        methods[name],audit=widen(drift,history,targets,grouped)
        audit.to_csv(OUT/(name+'_audit.csv'),index=False)
    methods['current_v1'],audit=current_calibrate(drift,history,targets,reference_forecasts=original)
    audit['rule_sha256']=RULE_HASH; audit.to_csv(OUT/'current_v1_audit.csv',index=False)
    origin_audits=[]
    for method in ['global','grouped','current_v1']:
        a=pd.read_csv(OUT/(method+'_audit.csv'))
        for origin, rows in a.groupby('origin_date'):
            used=rows[rows.n>0]
            origin_audits.append(dict(method=method,origin_date=origin,evaluation_origin=origin in origins,n_predictions=len(rows),n_calibrated=len(used),max_target_date=used.max_target_date.max() if len(used) else None,max_prior_origin=used.max_prior_origin.max() if len(used) else None,rule_sha256=RULE_HASH))
    pd.DataFrame(origin_audits).to_csv(OUT/'origin_audit.csv',index=False)
    reports={}; cells={}; keysets=[]
    for name,frame in methods.items():
        path=OUT/(name+'.csv'); frame[frame.origin_date.isin(origins)].to_csv(path,index=False); reports[name]={}
        for baseline in ['last_value','drift']:
            output=OUT/f'{name}_{baseline}.json'; percell=OUT/f'{name}_{baseline}_cells.csv'
            subprocess.run([sys.executable,'-B',str(scorer),'--forecast',str(path),'--truth',str(ROOT/'data/history.csv'),'--history',str(ROOT/'data/history.csv'),'--series-ids','@'+str(ROOT/'data/target_ids.txt'),'--horizons','1,3,7','--skill-baseline',baseline,'--no-missing-as-baseline','--out',str(output),'--per-cell',str(percell)],check=True)
            c=pd.read_csv(percell).sort_values(KEY).reset_index(drop=True); cells[name,baseline]=c
            keysets.append(set(map(tuple,c[KEY].values)))
            reports[name][baseline]=json.loads(output.read_text())['overall']
            reports[name][baseline]['mean_width']=float((c.q90-c.q10).mean())
    assert all(s==keysets[0] for s in keysets), 'Exact populations must match; no post hoc selection'
    assert set(cells['grouped','drift'].origin_date)==set(origins)
    groups=[]
    for (name,base),c in cells.items():
        c=c.merge(targets[['series_id','instrument_class','source_id']],on='series_id',validate='many_to_one')
        for dims in [['instrument_class'],['source_id'],['horizon_days'],['instrument_class','horizon_days'],['origin_date'],['series_id']]:
            for key,sub in c.groupby(dims):
                if not isinstance(key,tuple): key=(key,)
                m=metrics(sub,official); cov=m.pop('coverage'); m.pop('pinball_by_quantile');m.pop('baseline_pinball_by_quantile')
                groups.append(dict(method=name,baseline=base,grouping='+'.join(dims),group='|'.join(map(str,key)),**m,**cov))
    pd.DataFrame(groups).to_csv(OUT/'group_diagnostics.csv',index=False)
    rng=np.random.default_rng(42); sampled=rng.choice(len(origins),(2000,len(origins)),replace=True)
    ci={}; concentration=[]; g=cells['grouped','drift']; total=len(g); series_count=g.series_id.nunique()
    for comparator in ['global','current_v1','drift']:
        c=cells[comparator,'drift']; delta=g.loss.to_numpy()-c.loss.to_numpy()
        sums=np.array([delta[g.origin_date==o].sum() for o in origins]); counts=np.array([(g.origin_date==o).sum() for o in origins])
        draws=sums[sampled].sum(axis=1)/counts[sampled].sum(axis=1)
        ci[comparator]=dict(mean_pinball_change=float(delta.mean()),ci95=list(np.quantile(draws,[.025,.975])))
        for sid in sorted(g.series_id.unique()):
            mask=g.series_id==sid; gm=metrics(g[mask],official); cm=metrics(c[mask],official)
            leaveg=metrics(g[~mask],official); leavec=metrics(c[~mask],official)
            concentration.append(dict(comparator=comparator,series_id=sid,n_cells=int(mask.sum()),pooled_loss_change_contribution=float(delta[mask].sum()/total),series_skill_change=gm['skill_pooled']-cm['skill_pooled'],mean_series_skill_change_contribution=(gm['skill_pooled']-cm['skill_pooled'])/series_count,leave_one_out_pooled_loss_change=leaveg['pinball']-leavec['pinball'],leave_one_out_mean_series_skill_change=leaveg['skill_mean_of_series']-leavec['skill_mean_of_series']))
    pd.DataFrame(concentration).to_csv(OUT/'series_concentration.csv',index=False)
    mean=reports['grouped']['drift']['skill_mean_of_series']
    gate={f'ci_beats_{c}':bool(ci[c]['ci95'][1]<0) for c in ['global','current_v1']}
    gate.update({f'mean_series_at_least_{c}':mean>=reports[c]['drift']['skill_mean_of_series'] for c in ['global','current_v1']});gate['mean_series_nonnegative']=mean>=0
    promote=all(gate.values())
    if promote:
        frozen=pd.read_csv(ROOT/'forecasts.csv'); candidate,audit=widen(frozen,history,targets,True,archive=drift)
        candidate[list(frozen.columns)].to_csv(ROOT/'forecasts_group_calibrated.csv',index=False);audit.to_csv(OUT/'final_audit.csv',index=False)
        subprocess.run([sys.executable,'-B',str(scorer),'--forecast',str(ROOT/'forecasts_group_calibrated.csv'),'--truth',str(ROOT/'data/history.csv'),'--history',str(ROOT/'data/history.csv'),'--frozen-cutoff','2026-11-06','--horizons','1,3,7','--out',str(OUT/'final_validation.json')],check=True)
    after={p:sha(ROOT/p) for p in protected}; assert after==protected
    summary=dict(rule_sha256=RULE_HASH,scorer_sha256=sha(scorer),common_py_sha256=sha(scorer.parent/'_common.py'),protected_before=protected,protected_after=after,paired_cells=len(keysets[0]),origins=origins,archive_origin_count=int(drift.origin_date.nunique()),reports=reports,paired_origin_bootstrap=ci,promotion_checks=gate,promoted=promote,caveat=rule['design']+' Only five origin clusters; bootstrap descriptive, not proof of future improvement. Current-v1 comparison jointly changes archive and pooling.')
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
