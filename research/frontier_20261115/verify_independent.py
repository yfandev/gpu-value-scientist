#!/usr/bin/env python3
"""Independent verification, no import of study.py and no new experiment.
Reconstructs the existing chosen cases from original pack with Python medians.
"""
from pathlib import Path
from collections import defaultdict
from statistics import median
import json, math, hashlib, sys
import numpy as np
import pandas as pd
import duckdb

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
PACK=ROOT/'data/pack/gpu-price-pack-v0.1.1-handover'

def close(a,b):
    assert abs(float(a)-float(b)) < 2e-12, (a,b)

def main():
    summary=json.loads((HERE/'summary.json').read_text())
    protocol=json.loads((HERE/'protocol.json').read_text())
    digest=hashlib.sha256((HERE/'protocol.json').read_bytes()).hexdigest()
    assert digest==summary['protocol_sha256']==(HERE/'protocol.sha256').read_text().split()[0]
    for file,h in summary['protected_sha256'].items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==h
    inputs=json.loads((HERE/'input_hashes.json').read_text())
    for file,h in inputs.items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==h, file
    all_variants={}
    for variant in ['primary','coarse','raw_provider']:
        t=pd.read_csv(HERE/f'transitions_{variant}.csv')
        assert not t.duplicated(['series_id','date']).any()
        assert ((pd.to_datetime(t.date)-pd.to_datetime(t.old_date)).dt.days==1).all()
        assert t.old_date.min()>='2026-07-09' and t.date.max()<='2026-11-06'
        assert (t.n_common>0).all()
        err=np.max(np.abs(t.D-t.S-t.C-t.R));assert err<2e-12
        sums=[math.fsum(abs(v) for v in t[c]) for c in ['S','C','R']]
        f=(sums[0]+sums[1])/sum(sums)
        expected=summary['variants'][variant]['F']
        if '--negative-control' in sys.argv:expected+=.01
        close(f,expected)
        assert len(t)==summary['variants'][variant]['transitions']
        close(t.loc[t.stable_basket,'C'].abs().max(),0)
        for group,z in t.groupby('source_id'):
            vals=[math.fsum(abs(v) for v in z[c]) for c in ['S','C','R']]
            close((vals[0]+vals[1])/sum(vals),summary['variants'][variant]['by_source'][group]['F'])
        all_variants[variant]={'F':f,'transitions':len(t),'identity_max_error':float(err)}
    t=pd.read_csv(HERE/'transitions_primary.csv')
    # Recompute calendar blocks and draws independently from saved transitions.
    blocks=defaultdict(lambda:[0.,0.])
    start=pd.Timestamp('2026-07-10')
    for r in t.itertuples():
        b=(pd.Timestamp(r.date)-start).days//7
        blocks[b][0]+=abs(r.S)+abs(r.C)
        blocks[b][1]+=abs(r.S)+abs(r.C)+abs(r.R)
    n=(pd.Timestamp('2026-11-06')-start).days//7+1
    rng=np.random.default_rng(20261115)
    boot=[]
    for i in range(2000):
        selected=rng.integers(0,n,size=n)
        num=math.fsum(blocks[int(b)][0] for b in selected)
        den=math.fsum(blocks[int(b)][1] for b in selected)
        boot.append(num/den)
    saved=pd.read_csv(HERE/'bootstrap_draws.csv').F.to_numpy()
    assert np.max(np.abs(saved-boot))<2e-12
    ci=np.quantile(boot,[.025,.975])
    for a,b in zip(ci,summary['bootstrap']['ci95']):close(a,b)
    assert ci[0]<.5 and ci[1]>.2
    con=duckdb.connect()
    targets=pd.read_csv(ROOT/'data/targets.csv');con.register('catalog',targets)
    # Original raw files, no derived raw_selected or cell parquet used here.
    raw=con.execute(f"""select t.series_id,r.dt,r.usd_per_gpu_hour from read_parquet('{PACK}/rental_observations/*/*/*.parquet',hive_partitioning=false) r join catalog t using(source_id,instrument_class,gpu_model,pricing_tier) where r.dt between date '2026-07-09' and date '2026-11-06'""").df()
    daily=raw.groupby(['series_id','dt']).usd_per_gpu_hour.agg(['median','size']).reset_index()
    daily['dt']=daily.dt.dt.strftime('%Y-%m-%d')
    saved_daily=pd.read_csv(HERE/'raw_daily.csv')
    merged=daily.merge(saved_daily,left_on=['series_id','dt'],right_on=['series_id','date'],validate='one_to_one')
    assert len(merged)==len(daily)==len(saved_daily)==2837
    assert np.max(np.abs(merged['median']-merged.A))<2e-12
    assert (merged['size']==merged.n_rows).all()
    cases=pd.read_csv(HERE/'case_studies.csv')
    primary_fields=protocol['key']['primary']
    ordinary=[s for s in primary_fields if not s.startswith('extra_json.')]
    extra=[s.split('.',1)[1] for s in primary_fields if s.startswith('extra_json.')]
    case_checks=[]
    for row in cases.itertuples():
        cat=targets.set_index('series_id').loc[row.series_id]
        paths=[str(PACK/'rental_observations'/f'source_id={row.source_id}'/f'dt={d}'/'part.parquet') for d in [row.old_date,row.date]]
        records=con.execute('select * from read_parquet(?,hive_partitioning=false) where instrument_class=? and gpu_model=? and pricing_tier=?',[paths,cat.instrument_class,cat.gpu_model,cat.pricing_tier]).df().to_dict('records')
        cell_rows=defaultdict(list);raw_days=defaultdict(list)
        for record in records:
            date=record['dt'].strftime('%Y-%m-%d')
            key=[]
            for field in ordinary:
                value=record[field]
                key.append(None if pd.isna(value) else str(value))
            specific=json.loads(record['extra_json'])
            for field in extra:
                key.append(('json',json.dumps(specific[field],sort_keys=True,separators=(',',':'))) if field in specific and specific[field] is not None else ('absent_or_null',))
            cell_rows[(date,tuple(key))].append(record['usd_per_gpu_hour'])
            raw_days[date].append(record['usd_per_gpu_hour'])
        cell_by_day=defaultdict(dict)
        for (date,key),values in cell_rows.items():cell_by_day[date][key]=median(values)
        p0=cell_by_day[row.old_date];p1=cell_by_day[row.date];common=p0.keys()&p1.keys()
        a0=median(raw_days[row.old_date]);a1=median(raw_days[row.date]);e0=median(p0.values());e1=median(p1.values())
        m0=median([p0[k] for k in common]);m1=median([p1[k] for k in common])
        values={'A_old':a0,'A_new':a1,'E_old':e0,'E_new':e1,'M_old':m0,'M_new':m1,
                'D':math.log(a1)-math.log(a0),'R':math.log(m1)-math.log(m0),
                'C':math.log(e1)-math.log(m1)+math.log(m0)-math.log(e0),
                'S':math.log(a1)-math.log(e1)-math.log(a0)+math.log(e0)}
        for field,value in values.items():close(value,getattr(row,field))
        assert (len(p0),len(p1),len(common))==(row.n_old,row.n_new,row.n_common)
        nchange=sum(abs(math.log(p1[k]/p0[k]))>1e-9 for k in common)
        assert nchange==row.n_cell_changes
        case_checks.append({'case_id':row.case_id,'original_rows_checked':len(records),'series_id':row.series_id,'date':row.date,**values})
    con.close()
    result={'status':'passed','method':'Independent Python statistics.median on original pack for selected cases; pandas raw-day reconstruction; no study.py import',
            'input_hashes_checked':len(inputs),'protocol_sha256':digest,'protected_forecast_hashes_checked':True,
            'raw_rows':len(raw),'raw_days_independently_rebuilt':len(daily),'variants':all_variants,
            'bootstrap_draws_reproduced':len(boot),'ci95':ci.tolist(),'original_parquet_case_checks':case_checks}
    (HERE/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('FRONTIER_INDEPENDENT_VERIFICATION_PASS')
if __name__=='__main__':main()
