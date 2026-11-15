#!/usr/bin/env python3
"""Frozen observational index-decomposition study. Writes only beside this script."""
from pathlib import Path
import hashlib, json, math, datetime, sys
import duckdb
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
PACK=ROOT/'data/pack/gpu-price-pack-v0.1.1-handover'
START='2026-07-09'; END='2026-11-06'
EXPECTED={'forecasts.csv':'62ea5d18a77f4fd509ac96d9518c1d448ee777fa5839e380a0689d074a5eae31','forecasts_calibrated.csv':'226f58a63771488290a8073579853ec9e64189ac2e7a4c99d706db6c370fe59d','forecasts_extended.csv':'05db1f8d92814cde2af97e87f9a58c471e7c09c080c7bf8e7b32d3107cbcc3dd'}
BASE=['source_id','instrument_class','gpu_model','pricing_tier','provider','gpu_memory_gb','gpu_count','sku_raw','region_raw','region_canonical','country','price_basis']
EXTRA=['instance','commitment','min_gpus','rate_basis','vcpus','ram_gb','availability_zone','vcpus_per_gpu','memory_gib_per_gpu']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj): Path(p).write_text(json.dumps(obj,indent=2,allow_nan=False,default=str)+'\n')
def safe(x): return float(x) if np.isfinite(x) else None

def bridge(old,new,a0,a1):
    """Exact matched-cell median log bridge, no causal interpretation."""
    keys=sorted(old.keys() & new.keys())
    e0=float(np.median(list(old.values()))); e1=float(np.median(list(new.values())))
    ans={'A_old':a0,'A_new':a1,'E_old':e0,'E_new':e1,'n_old':len(old),'n_new':len(new),'n_common':len(keys),
         'overlap_old':len(keys)/len(old),'overlap_new':len(keys)/len(new),'D':math.log(a1/a0),
         'S':math.log(a1/e1)-math.log(a0/e0),'C':np.nan,'R':np.nan,'M_old':np.nan,'M_new':np.nan,
         'n_cell_changes':0,'stable_basket':old.keys()==new.keys()}
    if keys:
        m0=float(np.median([old[k] for k in keys]));m1=float(np.median([new[k] for k in keys]))
        ans.update(M_old=m0,M_new=m1,C=math.log(e1/m1)+math.log(m0/e0),R=math.log(m1/m0),
                   n_cell_changes=sum(abs(math.log(new[k]/old[k]))>1e-9 for k in keys))
    ans['high_overlap']=len(keys)>=3 and ans['overlap_old']>=.8 and ans['overlap_new']>=.8
    return ans

def summarize(z):
    q=z[z.n_common>0]
    s=q[['S','C','R']].abs().sum();den=float(s.sum())
    changed=q.D.abs()>1e-9
    return {'transitions':len(z),'identifiable':len(q),'no_overlap':int((z.n_common==0).sum()),
            'n_series':int(z.series_id.nunique()),'F':safe((s.S+s.C)/den) if den else None,
            'sum_abs_S':float(s.S),'sum_abs_C':float(s.C),'sum_abs_R':float(s.R),
            'sum_abs_D_identified':float(q.D.abs().sum()),'sum_abs_D_all':float(z.D.abs().sum()),
            'raw_motion_identified_fraction':safe(q.D.abs().sum()/z.D.abs().sum()) if z.D.abs().sum() else None,
            'cancellation_ratio':safe(1-q.D.abs().sum()/den) if den else None,
            'changed_index':int(changed.sum()),
            'changed_index_zero_matched_median':int((changed & (q.R.abs()<=1e-9)).sum()),
            'changed_index_zero_any_matched_cell':int((changed & (q.n_cell_changes==0)).sum()),
            'sign_reversal_D_R':int((changed & (q.R.abs()>1e-9) & (q.D*q.R<0)).sum()),
            'zero_index_nonzero_components':int(((q.D.abs()<=1e-9)&(q[['S','C','R']].abs().max(axis=1)>1e-9)).sum())}

def extract():
    con=duckdb.connect()
    con.execute("set threads=4; set memory_limit='3GB'")
    targets=pd.read_csv(ROOT/'data/targets.csv')
    assert len(targets)==37 and targets.series_id.nunique()==37
    con.register('targets',targets)
    con.execute(f"""create view selected as select r.*,t.series_id from read_parquet('{PACK}/rental_observations/*/*/*.parquet',hive_partitioning=false) r
      join targets t using(source_id,instrument_class,gpu_model,pricing_tier)
      where dt between date '{START}' and date '{END}'""")
    expressions=[]
    for variant in ['primary','coarse','raw_provider']:
        fields=[('provider_raw' if variant=='raw_provider' and f=='provider' else f) for f in BASE if not(variant=='coarse' and f=='sku_raw')]
        expr=[f'cast({f} as varchar)' for f in fields]
        if variant!='coarse':expr += [f"nullif(cast(json_extract(extra_json,'$.{f}') as varchar),'null')" for f in EXTRA]
        expressions.append('to_json(list_value('+','.join(expr)+f')) as key_{variant}')
    con.execute('create view keyed as select *, '+','.join(expressions)+' from selected')
    con.execute(f"copy (select * from keyed order by series_id,dt,obs_id) to '{OUT}/raw_selected.parquet' (format parquet,compression zstd)")
    raw=con.execute("""select series_id,source_id,instrument_class,dt as date,median(usd_per_gpu_hour) as A,count(*) as n_rows,
      count(distinct snapshot_ts_utc) as n_snapshots, count(distinct provider) as n_providers,
      count(*) filter(where sku_raw is null or sku_raw='') as missing_sku,
      count(*) filter(where gpu_count is null) as missing_gpu_count,
      count(*) filter(where region_raw is null or region_raw='') as missing_region
      from keyed group by all order by series_id,date""").df()
    raw['date']=pd.to_datetime(raw.date)
    raw.to_csv(OUT/'raw_daily.csv',index=False)
    for variant in ['primary','coarse','raw_provider']:
        # Count conflicts at a simultaneous key/snapshot, before reducing to daily cells.
        con.execute(f"""copy (with x as (select *, count(distinct usd_per_gpu_hour) over(partition by series_id,dt,key_{variant},snapshot_ts_utc) as snapshot_prices from keyed)
        select series_id,dt as date,key_{variant} as cell_key,median(usd_per_gpu_hour) as price,count(*) as n_rows,
        count(distinct usd_per_gpu_hour) as n_prices,count(distinct snapshot_ts_utc) as n_snapshots,
        max(snapshot_prices) as max_prices_same_snapshot
        from x group by all order by series_id,date,cell_key) to '{OUT}/cells_{variant}.parquet' (format parquet,compression zstd)""")
    quality=con.execute("select source_id,count(*) as rows,min(dt) as first_date,max(dt) as last_date,count(distinct series_id) as series from keyed group by source_id order by source_id").df().to_dict('records')
    con.close()
    return raw,quality

def transitions(raw,variant):
    con=duckdb.connect()
    cells=con.execute(f"select * from '{OUT}/cells_{variant}.parquet'").df();con.close()
    cells['date']=pd.to_datetime(cells.date)
    rs=raw.set_index(['series_id','date'])
    rows=[]
    for sid,g in cells.groupby('series_id',sort=True):
        prev=None
        for date,h in g.groupby('date',sort=True):
            current=dict(zip(h.cell_key,h.price))
            if prev is not None and (date-prev[0]).days==1:
                old_date,old,old_conf=prev
                r0=rs.loc[(sid,old_date)];r1=rs.loc[(sid,date)]
                b=bridge(old,current,float(r0.A),float(r1.A))
                b.update(variant=variant,series_id=sid,source_id=r1.source_id,instrument_class=r1.instrument_class,date=date.strftime('%Y-%m-%d'),old_date=old_date.strftime('%Y-%m-%d'),
                         rows_old=int(r0.n_rows),rows_new=int(r1.n_rows),snapshots_old=int(r0.n_snapshots),snapshots_new=int(r1.n_snapshots),
                         ambiguous_old=int(old_conf),ambiguous_new=int((h.max_prices_same_snapshot>1).sum()))
                rows.append(b)
            prev=(date,current,int((h.max_prices_same_snapshot>1).sum()))
    z=pd.DataFrame(rows)
    z.to_csv(OUT/f'transitions_{variant}.csv',index=False)
    return z

def bootstrap(z):
    q=z[z.n_common>0].copy()
    q['block']=((pd.to_datetime(q.date)-pd.Timestamp('2026-07-10')).dt.days//7).astype(int)
    g=q.assign(a=q.S.abs()+q.C.abs(),b=q.S.abs()+q.C.abs()+q.R.abs()).groupby('block')[['a','b']].sum()
    # Include every fixed block, even if none of its transitions were identifiable.
    n_blocks=((pd.Timestamp(END)-pd.Timestamp('2026-07-10')).days//7)+1
    g=g.reindex(range(n_blocks),fill_value=0)
    rng=np.random.default_rng(20261115);idx=rng.integers(0,n_blocks,size=(2000,n_blocks))
    sums=g.to_numpy()[idx].sum(axis=1);f=sums[:,0]/sums[:,1]
    pd.DataFrame({'draw':np.arange(2000),'F':f}).to_csv(OUT/'bootstrap_draws.csv',index=False)
    g.to_csv(OUT/'bootstrap_blocks.csv')
    ci=np.quantile(f,[.025,.975]).tolist()
    return {'blocks':n_blocks,'draws':2000,'seed':20261115,'ci95':ci,'decision':'H_basket' if ci[0]>.5 else ('H_price' if ci[1]<.2 else 'H_mixed_or_inconclusive')}

def main():
    protocol_hash=sha(OUT/'protocol.json')
    assert protocol_hash==(OUT/'protocol.sha256').read_text().split()[0]
    assert {n:sha(ROOT/n) for n in EXPECTED}==EXPECTED
    inputs=[ROOT/'data/targets.csv',PACK/'daily_statistics.csv',PACK/'MANIFEST.sha256']+sorted((PACK/'rental_observations').glob('*/*/*.parquet'))
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    dump(OUT/'input_hashes.json',hashes)
    raw,quality=extract();print('Extracted',sum(q['rows'] for q in quality),'rows',flush=True)
    official=pd.read_csv(PACK/'daily_statistics.csv')
    targets=pd.read_csv(ROOT/'data/targets.csv')
    official=official.merge(targets[['series_id','source_id','instrument_class','gpu_model','pricing_tier']],on=['source_id','instrument_class','gpu_model','pricing_tier'])
    official['date']=pd.to_datetime(official.date)
    rec=raw.merge(official[['series_id','date','median_usd_per_gpu_hour','n_obs']],on=['series_id','date'],how='left',validate='one_to_one')
    assert rec.median_usd_per_gpu_hour.notna().all()
    rec['error']=rec.A-rec.median_usd_per_gpu_hour
    assert rec.error.abs().max()<=.00005000001
    assert (rec.n_rows==rec.n_obs).all()
    rec.to_csv(OUT/'median_reconciliation.csv',index=False)
    summary={'protocol_sha256':protocol_hash,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'sources':quality,'raw_days':len(raw),'median_reconciliation_max_absolute_error':float(rec.error.abs().max()),'protected_sha256':EXPECTED,'variants':{}}
    primary=None
    for variant in ['primary','coarse','raw_provider']:
        z=transitions(raw,variant)
        err=(z.D-z.S-z.C-z.R).dropna().abs().max()
        assert err<1e-12
        assert z.loc[z.stable_basket,'C'].abs().max()<1e-12
        ss=summarize(z);ss['identity_max_error']=float(err)
        ss['high_overlap']=summarize(z[z.high_overlap])
        ss['unambiguous']=summarize(z[(z.ambiguous_old==0)&(z.ambiguous_new==0)])
        ss['material_moves_1pct']=summarize(z[z.D.abs()>=math.log(1.01)])
        ss['by_source']={s:summarize(g) for s,g in z.groupby('source_id')}
        ss['leave_one_source_out']={s:summarize(z[z.source_id!=s]) for s in z.source_id.unique()}
        summary['variants'][variant]=ss
        pd.DataFrame([dict(series_id=s,**summarize(g)) for s,g in z.groupby('series_id')]).to_csv(OUT/f'by_series_{variant}.csv',index=False)
        if variant=='primary':primary=z
        print(variant,json.dumps({k:ss[k] for k in ['F','transitions','identifiable','sum_abs_S','sum_abs_C','sum_abs_R']}),flush=True)
    summary['bootstrap']=bootstrap(primary)
    # Deterministic examples: largest raw changes, largest membership components, largest matched components, strongest reversals.
    ids=set()
    for metric in ['D','C','R','S']:
        ids.update(primary[metric].abs().nlargest(3).index)
    reversals=primary[primary.D*primary.R< -1e-12]
    ids.update(reversals.D.abs().nlargest(3).index)
    cases=primary.loc[sorted(ids)].copy();cases.insert(0,'case_id',[f'case_{i:02d}' for i in range(len(cases))])
    cases.to_csv(OUT/'case_studies.csv',index=False)
    con=duckdb.connect()
    for _,row in cases.iterrows():
        sub=con.execute(f"select * from '{OUT}/raw_selected.parquet' where series_id=? and dt in (cast(? as date),cast(? as date)) order by dt,key_primary,usd_per_gpu_hour",[row.series_id,row.old_date,row.date]).df()
        sub.to_csv(OUT/f'{row.case_id}_raw.csv',index=False)
    con.close()
    assert {n:sha(ROOT/n) for n in EXPECTED}==EXPECTED
    assert {str(p.relative_to(ROOT)):sha(p) for p in inputs}==hashes
    dump(OUT/'summary.json',summary)
    print(json.dumps(summary['bootstrap']),flush=True)
    print('FRONTIER_STUDY_COMPLETE')
if __name__=='__main__':main()
