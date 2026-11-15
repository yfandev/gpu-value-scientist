"""One predeclared retrospective calibration follow-up; official scoring only."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import sys
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/calibration_study'
KEY = ['series_id', 'origin_date', 'horizon_days']


def calibrate(forecasts, history, targets, reference_forecasts=None):
    """Each prediction reads only matured prior original forecasts and dated truth."""
    meta = targets[['series_id', 'source_id', 'instrument_class']].drop_duplicates('series_id')
    original = forecasts.merge(meta, on='series_id', validate='many_to_one')
    original['target_date'] = (pd.to_datetime(original.origin_date) + pd.to_timedelta(original.horizon_days, unit='D')).dt.strftime('%Y-%m-%d')
    original['scale'] = original.q50.abs().clip(lower=1e-9)
    truth = history[['series_id', 'date', 'value']].rename(columns={'date': 'target_date', 'value': 'y'})
    archive = original
    if reference_forecasts is not None:
        archive = reference_forecasts.merge(meta, on='series_id', validate='many_to_one')
        archive['target_date'] = (pd.to_datetime(archive.origin_date) + pd.to_timedelta(archive.horizon_days, unit='D')).dt.strftime('%Y-%m-%d')
        archive['scale'] = archive.q50.abs().clip(lower=1e-9)
    residuals = archive.merge(truth, on=['series_id', 'target_date'], validate='many_to_one')
    residuals['lower'] = (residuals.q10 - residuals.y) / residuals.scale
    residuals['upper'] = (residuals.y - residuals.q90) / residuals.scale
    result, audit = [], []
    for row in original.itertuples(index=False):
        eligible = residuals[(residuals.origin_date < row.origin_date) & (residuals.target_date < row.origin_date) & (residuals.horizon_days == row.horizon_days)]
        pools = [('source_class_horizon', eligible[(eligible.source_id == row.source_id) & (eligible.instrument_class == row.instrument_class)]),
                 ('class_horizon', eligible[eligible.instrument_class == row.instrument_class]), ('horizon', eligible)]
        lower = upper = 0.; chosen = eligible.iloc[:0]; name = 'unchanged_insufficient_history'
        for label, pool in pools:
            if len(pool) >= 20 and pool.origin_date.nunique() >= 2:
                chosen, name = pool, label
                rank = min(len(pool), math.ceil((len(pool) + 1) * .9)) - 1
                lower = max(0., float(np.sort(pool.lower)[rank]))
                upper = max(0., float(np.sort(pool.upper)[rank]))
                break
        result.append(dict(series_id=row.series_id, origin_date=row.origin_date, horizon_days=row.horizon_days,
                           target_date=row.target_date, q10=max(0., row.q10-row.scale*lower), q50=row.q50, q90=row.q90+row.scale*upper))
        audit.append(dict(series_id=row.series_id, origin_date=row.origin_date, horizon_days=row.horizon_days,
                          pool=name, n=len(chosen), n_origins=chosen.origin_date.nunique(),
                          max_target_date=chosen.target_date.max() if len(chosen) else None,
                          max_prior_origin=chosen.origin_date.max() if len(chosen) else None,
                          lower_relative_expansion=lower, upper_relative_expansion=upper))
    return pd.DataFrame(result), pd.DataFrame(audit)


def official_score(path, label, baseline, scorer):
    report = OUT / f'{label}_{baseline}.json'; cells = OUT / f'{label}_{baseline}_cells.csv'
    subprocess.run([sys.executable, '-B', str(scorer), '--forecast', str(path), '--truth', str(ROOT/'data/history.csv'),
                    '--history', str(ROOT/'data/history.csv'), '--series-ids', '@'+str(ROOT/'data/target_ids.txt'),
                    '--horizons', '1,3,7', '--skill-baseline', baseline, '--no-missing-as-baseline',
                    '--out', str(report), '--per-cell', str(cells)], check=True)
    return json.loads(report.read_text()), pd.read_csv(cells)


def final_candidate():
    """Generate an optional Nov 6 candidate without overwriting original submission."""
    source = ROOT/'forecasts.csv'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    frozen = pd.read_csv(source)
    history = pd.read_csv(ROOT/'data/history.csv')
    prior = pd.read_csv(ROOT/'results/online_forecasts.csv')
    targets = pd.read_csv(ROOT/'data/targets.csv')
    forecast, audit = calibrate(pd.concat([prior, frozen], ignore_index=True), history, targets)
    candidate = forecast[forecast.origin_date == '2026-11-06'][list(frozen.columns)]
    candidate.to_csv(ROOT/'forecasts_calibrated.csv', index=False)
    audit[audit.origin_date == '2026-11-06'].to_csv(OUT/'final_audit.csv', index=False)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    cfg = json.loads((ROOT/'config.json').read_text())
    subprocess.run([sys.executable, '-B', str(ROOT/cfg['pack']/'starter/scorer.py'),
                    '--forecast', str(ROOT/'forecasts_calibrated.csv'),
                    '--truth', str(ROOT/'data/history.csv'), '--history', str(ROOT/'data/history.csv'),
                    '--frozen-cutoff', '2026-11-06', '--horizons', '1,3,7',
                    '--out', str(OUT/'final_validation.json')], check=True)
    (OUT/'final_provenance.json').write_text(json.dumps(dict(original_sha256=before,
        candidate_sha256=hashlib.sha256((ROOT/'forecasts_calibrated.csv').read_bytes()).hexdigest(),
        rows=len(candidate), cutoff='2026-11-06',
        caveat='Optional candidate, not a proven final-window improvement. Calibration errors use the original mixed-policy prequential forecasts, whereas final original forecasts use drift fallback. November truth unavailable.'),indent=2)+'\n')


def drift_diagnostic():
    """Same rule/errors, but current base forecasts are drift, as in final candidate."""
    original = pd.read_csv(ROOT/'results/online_forecasts.csv')
    drift = pd.read_csv(ROOT/'results/forecast_drift.csv').merge(original[KEY], on=KEY, validate='one_to_one')
    history = pd.read_csv(ROOT/'data/history.csv'); targets = pd.read_csv(ROOT/'data/targets.csv')
    calibrated, audit = calibrate(drift, history, targets, reference_forecasts=original)
    drift.to_csv(OUT/'drift_base.csv',index=False)
    calibrated.to_csv(OUT/'drift_base_calibrated.csv',index=False)
    audit.to_csv(OUT/'drift_base_audit.csv',index=False)
    cfg=json.loads((ROOT/'config.json').read_text()); scorer=ROOT/cfg['pack']/'starter/scorer.py'
    reports={}; keysets=[]
    for name in ['drift_base','drift_base_calibrated']:
        reports[name]={}
        for baseline in ['last_value','drift']:
            report,cells=official_score(OUT/(name+'.csv'), name, baseline, scorer)
            reports[name][baseline]=report['overall']
            reports[name]['mean_width']=float((cells.q90-cells.q10).mean())
            keysets.append(set(map(tuple,cells[KEY].values)))
    main_cells=pd.read_csv(OUT/'original_drift_cells.csv')
    assert all(k==set(map(tuple,main_cells[KEY].values)) for k in keysets)
    (OUT/'drift_base_summary.json').write_text(json.dumps(dict(reports=reports,paired_cells=len(keysets[0]),
        caveat='Secondary diagnostic requested after main results; no rule tuning. Current base is drift, but calibration residual archive remains original selected-policy online forecasts, matching final candidate construction.'),indent=2)+'\n')
    print(json.dumps(reports,indent=2))


def main():
    rule_path = OUT/'rule.json'
    if not rule_path.exists():
        raise RuntimeError('Predeclare rule.json before running study')
    cfg = json.loads((ROOT/'config.json').read_text())
    assert cfg['calibration_study']['rule'] == json.loads(rule_path.read_text()), 'Config must match predeclared rule exactly'
    scorer = ROOT/cfg['pack']/'starter/scorer.py'
    sys.path.insert(0, str(scorer.parent))
    import scorer as official
    original_path = ROOT/'results/online_forecasts.csv'
    original = pd.read_csv(original_path); history = pd.read_csv(ROOT/'data/history.csv'); targets = pd.read_csv(ROOT/'data/targets.csv')
    calibrated, audit = calibrate(original, history, targets)
    calibrated.to_csv(OUT/'forecasts.csv', index=False); audit.to_csv(OUT/'audit.csv', index=False)
    reports, cells = {}, {}
    for label, path in [('original', original_path), ('calibrated', OUT/'forecasts.csv')]:
        reports[label] = {}
        for base in ['last_value', 'drift']:
            report, c = official_score(path, label, base, scorer)
            reports[label][base] = report['overall']
            cells[label, base] = c
    # All comparisons use intersection of exact official scored cells, with no baseline fillers.
    sets = [set(map(tuple, c[KEY].values)) for c in cells.values()]
    assert all(s == sets[0] for s in sets), 'Scorer populations differ'
    meta = targets[['series_id','source_id','instrument_class','gpu_model','pricing_tier']]
    groups = []
    for label in ['original', 'calibrated']:
        for base in ['last_value','drift']:
            c = cells[label, base].merge(meta, on='series_id', validate='many_to_one')
            for dimensions in [['instrument_class'], ['source_id'], ['source_id','instrument_class'], ['horizon_days'], ['instrument_class','horizon_days'], ['series_id'], ['origin_date'], ['gpu_model'], ['pricing_tier']]:
                for key, subset in c.groupby(dimensions):
                    if not isinstance(key, tuple): key = (key,)
                    agg = official.aggregate(subset.to_dict('records'))
                    groups.append(dict(method=label, baseline=base, grouping='+'.join(dimensions), group='|'.join(map(str,key)),
                                       **{k:agg[k] for k in ['n_cells','pinball','baseline_pinball','skill_pooled']},
                                       **agg['coverage'], mean_width=float((subset.q90-subset.q10).mean()),
                                       zero_width_share=float((subset.q90 == subset.q10).mean())))
    pd.DataFrame(groups).to_csv(OUT/'group_diagnostics.csv',index=False)
    for label in reports:
        c = cells[label,'drift']; reports[label]['mean_width'] = float((c.q90-c.q10).mean())
    # Paired origin bootstrap uses official loss output and official aggregate, never a replacement scorer.
    rng = np.random.default_rng(42); origins = sorted(original.origin_date.unique()); draws=[]
    a = cells['original','drift']; b=cells['calibrated','drift']
    for _ in range(2000):
        sampled = rng.choice(origins, len(origins), replace=True)
        aa=pd.concat([a[a.origin_date == o] for o in sampled]); bb=pd.concat([b[b.origin_date == o] for o in sampled])
        ag=official.aggregate(aa.to_dict('records')); bg=official.aggregate(bb.to_dict('records'))
        draws.append([bg['skill_pooled'], bg['pinball']-ag['pinball'], bg['coverage']['within_q10_q90']-ag['coverage']['within_q10_q90']])
    intervals = {name: list(np.quantile(np.array(draws)[:,i],[.025,.975])) for i,name in enumerate(['calibrated_skill_vs_drift','calibrated_minus_original_pinball','coverage_gain'])}
    summary = dict(rule_sha256=hashlib.sha256(rule_path.read_bytes()).hexdigest(), scorer_sha256=hashlib.sha256(scorer.read_bytes()).hexdigest(),
                   original_sha256=hashlib.sha256(original_path.read_bytes()).hexdigest(), paired_cells=len(sets[0]), origins=origins,
                   reports=reports, bootstrap_95_percentile=intervals,
                   caveat='Retrospective rule designed after original coverage observed; no untouched external holdout. Whole-origin bootstrap only descriptive: origins and series dependent, 14 origins. November truth unavailable.')
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if reports['calibrated']['drift']['skill_pooled'] >= reports['original']['drift']['skill_pooled'] and abs(reports['calibrated']['drift']['coverage']['within_q10_q90']-.8) < abs(reports['original']['drift']['coverage']['within_q10_q90']-.8):
        final_candidate()
    drift_diagnostic()
    print(json.dumps(summary,indent=2))


if __name__ == '__main__': main()
