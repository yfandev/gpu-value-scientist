"""Export observed rental prices for display; never generates forecasts."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def export():
    with (ROOT/'forecasts.csv').open() as f: baseline=list(csv.DictReader(f))
    with (ROOT/'forecasts_fallback.csv').open() as f: drift=list(csv.DictReader(f))
    key=lambda r:(r['series_id'],int(r['horizon_days']))
    assert sorted(baseline,key=key)==sorted(drift,key=key), 'Original forecast is not drift; do not mislabel the chart'
    ids={r['series_id'] for r in baseline}
    history={s:[] for s in sorted(ids)}
    with (ROOT/'data/history.csv').open() as f:
        for r in csv.DictReader(f):
            if r['series_id'] in ids and '2026-10-07'<=r['date']<='2026-11-06' and r.get('is_filled','0') not in ('1','True','true'):
                history[r['series_id']].append({'date':r['date'],'value':float(r['value'])})
    for rows in history.values():rows.sort(key=lambda r:r['date'])
    (ROOT/'demo/price_history.json').write_text(json.dumps({'cutoff':'2026-11-06','history':history,'baseline':baseline},sort_keys=True)+'\n')
if __name__=='__main__':export()
