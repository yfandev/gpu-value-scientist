#!/usr/bin/env python3
"""Audit catalog snapshots and extend forecasts with archived AWS headline targets.

Read-only pack access. Uses its unchanged builder, baseline CLI and validator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'data/pack/gpu-price-pack-v0.1.1-handover'
OUT = ROOT / 'results/series_audit'
CUTOFF = '2026-11-06'
HORIZONS = [1, 3, 7]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reuse-built-history', action='store_true', help='reuse already rebuilt full cutoff history')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    original_path = ROOT / 'forecasts.csv'
    original_bytes = original_path.read_bytes()
    original_hash = sha(original_path)
    source_hashes = {str(p.relative_to(PACK)): sha(p) for p in [PACK/'DATA.md', PACK/'starter/build_series.py', PACK/'starter/baselines.py', PACK/'starter/_common.py']}
    commands = []
    def run(arguments):
        command = [sys.executable, '-B', *map(str, arguments)]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
        commands.append({'command': command, 'stdout': result.stdout, 'stderr': result.stderr})
    if not args.reuse_built_history:
        run([PACK/'starter/build_series.py', '--pack', PACK, '--cutoff', CUTOFF,
             '--members-from', ROOT/'results/quickstart/series_catalog.csv',
             '--out', OUT/'series_daily.csv', '--catalog', OUT/'series_catalog.csv'])
    old = pd.read_csv(ROOT/'results/quickstart/series_catalog.csv', keep_default_na=False)
    posted = pd.read_csv(ROOT/'data/series_catalog.csv', keep_default_na=False)
    full = pd.read_csv(OUT/'series_catalog.csv', keep_default_na=False)
    old_ids = set(old.loc[old.tier.eq('headline'), 'series_id'])
    posted_ids = set(posted.loc[posted.tier.eq('headline'), 'series_id'])
    full_ids = set(full.loc[full.tier.eq('headline'), 'series_id'])
    union = old_ids | posted_ids | full_ids
    original = pd.read_csv(original_path)
    assert len(original) == 111 and set(original.series_id) == posted_ids
    history = pd.read_csv(OUT/'series_daily.csv')
    assert history.date.max() <= CUTOFF
    assert not history.duplicated(['series_id', 'date']).any()
    aws = history[history.series_id.str.startswith('aws_spot.')]
    assert not aws.date.between('2026-03-01', '2026-06-30').any()
    assert aws.date.max() == '2026-10-31'
    old_map, posted_map, full_map = [d.set_index('series_id').to_dict('index') for d in [old,posted,full]]
    records=[]
    for sid in sorted(union):
        meta=full_map[sid]
        hist=history[(history.series_id==sid)&(history.date<=CUTOFF)]
        latest=hist.date.max() if len(hist) else ''
        is_posted=meta['table']=='daily_statistics'
        included=sid in posted_ids
        reason='' if included else ('AWS omitted from posted-only catalog; latest archive close 2026-10-31 is six days stale, fails headline stale>3d gate; November truth unavailable in shipped archive')
        records.append(dict(series_id=sid, table=meta['table'], instrument_class=meta['instrument_class'],
            headline_oct24=sid in old_ids, headline_nov6_posted=sid in posted_ids, headline_nov6_full=sid in full_ids,
            tier_oct24=old_map.get(sid,{}).get('tier','absent'),
            tier_nov6_posted=posted_map.get(sid,{}).get('tier','absent'), tier_nov6_full=meta['tier'],
            tier_reason_nov6_full=meta['tier_reason'], has_exact_nov6_observation=bool(hist.date.eq(CUTOFF).any()),
            latest_usable_date_le_cutoff=latest, stale_days=(pd.Timestamp(CUTOFF)-pd.Timestamp(latest)).days,
            history_rows_le_cutoff=len(hist), included_in_forecasts_csv=included,
            eligible_posted_headline_scope=included, eligible_forecast_with_cutoff_history=bool(len(hist)),
            exclusion_reason_from_posted_submission=reason,
            november_truth_in_shipped_pack=False,
            sunday_scoring_status=('posted headline target; requires separately published withheld truth' if is_posted else 'not in posted scored scope; requires authorised November live truth or December archive'),
            added_to_forecasts_extended=not included,
            truth_availability=meta['truth_availability'], benchmark_contract=meta['benchmark_contract'],
            source_url=meta['source_url'], licence_id=meta['licence_id']))
    audit=pd.DataFrame(records)
    audit.to_csv(ROOT/'data/headline_series_audit.csv',index=False)
    added_ids=sorted(set(audit.loc[audit.eligible_forecast_with_cutoff_history,'series_id'])-set(original.series_id))
    (OUT/'added_series_ids.txt').write_text('\n'.join(added_ids)+'\n')
    run([PACK/'starter/baselines.py','--history', OUT/'series_daily.csv','--origin',CUTOFF,
         '--horizons','1,3,7','--method','drift','--series-ids','@'+str(OUT/'added_series_ids.txt'),
         '--frozen','--out',OUT/'aws_starter_drift.csv'])
    added=pd.read_csv(OUT/'aws_starter_drift.csv')
    # Preserve all original forecast bytes as the leading rows, including numeric spelling.
    append=added[original.columns].to_csv(index=False,header=False,float_format='%.10g').encode()
    assert original_bytes.endswith(b'\n')
    extended_path=ROOT/'forecasts_extended.csv'
    extended_path.write_bytes(original_bytes+append)
    extended=pd.read_csv(extended_path)
    sys.path.insert(0,str(PACK/'starter'))
    from _common import validate_forecast, read_series_csv, SeriesStore, day_of, parse_date
    from baselines import make_forecasts
    clean,problems=validate_forecast(extended,HORIZONS)
    assert not problems and len(clean)==len(extended)
    assert np.isfinite(extended[['q10','q50','q90']]).all().all()
    expected={(sid,CUTOFF,h) for sid in union for h in HORIZONS}
    actual=set(extended[['series_id','origin_date','horizon_days']].itertuples(index=False,name=None))
    assert expected==actual and len(actual)==len(extended)
    store=SeriesStore(read_series_csv(str(OUT/'series_daily.csv')))
    direct=make_forecasts(store,added_ids,[day_of(parse_date(CUTOFF))],HORIZONS,'drift')
    np.testing.assert_allclose(added[['q10','q50','q90']],direct[['q10','q50','q90']],rtol=1e-9,atol=1e-10)
    assert extended_path.read_bytes().startswith(original_bytes)
    assert sha(original_path)==original_hash
    assert all(sha(PACK/p)==h for p,h in source_hashes.items())
    summary=dict(cutoff=CUTOFF, oct24_headline=len(old_ids), oct24_aws_headline=sum(s.startswith('aws_spot.') for s in old_ids),
        oct24_posted_headline=sum(not s.startswith('aws_spot.') for s in old_ids), nov6_posted_headline=len(posted_ids),
        nov6_full_headline=len(full_ids), headline_union=len(union), overlap_oct24_nov6=len(old_ids & posted_ids),
        new_nov6_posted=len(posted_ids-old_ids), original_rows=len(original), added_series=len(added_ids),
        added_rows=len(added), extended_rows=len(extended), exact_nov6_series=int(audit.has_exact_nov6_observation.sum()),
        original_forecasts_sha256=original_hash, extended_sha256=sha(extended_path),
        input_source_sha256=source_hashes, validation='PASS: exact117x3 grid; starter validator; positive finite ordered quantiles; exact starter drift; frozen history; archive gap absent; original111 rows byte-preserved',
        no_november_truth=True, commands=commands)
    (OUT/'audit_report.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['commands','input_source_sha256']},indent=2))

if __name__=='__main__':
    main()
