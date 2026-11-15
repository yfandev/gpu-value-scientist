"""Automated build-agent self-review: physical availability replay, not perturbation."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.calibration_study import calibrate, KEY
OUT = ROOT / 'artifacts/falsification'
STUDY = ROOT / 'results/calibration_study'

def read(path):
    return pd.read_csv(ROOT / path)

def same(a, b):
    a=a.copy();b=b.copy()
    for col in ['max_target_date','max_prior_origin']:
        if col in a:
            a[col]=a[col].fillna('').astype(str);b[col]=b[col].fillna('').astype(str)
    pd.testing.assert_frame_equal(a.sort_values(KEY).reset_index(drop=True), b.sort_values(KEY).reset_index(drop=True), check_dtype=False, atol=1e-12, rtol=1e-12)

def valid(frame):
    assert not frame.duplicated(KEY).any()
    assert np.isfinite(frame[['q10','q50','q90']]).all().all()
    assert (frame.q10 >= 0).all()
    assert (frame.q10 <= frame.q50).all() and (frame.q50 <= frame.q90).all()
    dates=(pd.to_datetime(frame.origin_date)+pd.to_timedelta(frame.horizon_days,unit='D')).dt.strftime('%Y-%m-%d')
    if 'target_date' in frame: assert (frame.target_date == dates).all()

def main():
    OUT.mkdir(exist_ok=True, parents=True)
    original=read('results/online_forecasts.csv'); history=read('data/history.csv'); targets=read('data/targets.csv')
    origins=sorted(original.origin_date.unique()); records=[]
    for label, source, calibrated, auditfile in [
        ('selected_policy','results/online_forecasts.csv','results/calibration_study/forecasts.csv','results/calibration_study/audit.csv'),
        ('drift_base','results/calibration_study/drift_base.csv','results/calibration_study/drift_base_calibrated.csv','results/calibration_study/drift_base_audit.csv')]:
        base=read(source); saved=read(calibrated); saved_audit=read(auditfile)
        valid(base);valid(saved)
        merged=base.merge(saved,on=KEY,suffixes=('_base','_cal'),validate='one_to_one')
        assert len(merged)==len(base)==len(saved)
        assert np.allclose(merged.q50_base,merged.q50_cal,rtol=0,atol=1e-12)
        assert (merged.q10_cal <= merged.q10_base+1e-12).all() and (merged.q90_cal >= merged.q90_base-1e-12).all()
        for origin in origins:
            # Neither unavailable truth nor current/future archive rows exist in the call.
            available=history.loc[history.date < origin].copy()
            archive=original.loc[original.origin_date < origin].copy()
            current=base.loc[base.origin_date == origin].copy()
            got,audit=calibrate(current,available,targets,reference_forecasts=archive)
            same(got,saved.loc[saved.origin_date==origin]);same(audit,saved_audit.loc[saved_audit.origin_date==origin])
            used=audit[audit.n>0]
            assert (used.max_target_date < origin).all() and (used.max_prior_origin < origin).all()
            assert (used.n>=20).all() and (used.n_origins>=2).all()
            records.append(dict(method=label,origin=origin,rows=len(got),available_history_rows=len(available),archive_rows=len(archive),unchanged=True))
    frozen=read('forecasts.csv'); candidate=read('forecasts_calibrated.csv');valid(frozen);valid(candidate)
    got,audit=calibrate(frozen,history[history.date<'2026-11-06'],targets,reference_forecasts=original[original.origin_date<'2026-11-06'])
    same(got[candidate.columns],candidate)
    same(audit,read('results/calibration_study/final_audit.csv'))
    assert hashlib.sha256((ROOT/'forecasts.csv').read_bytes()).hexdigest()=='62ea5d18a77f4fd509ac96d9518c1d448ee777fa5839e380a0689d074a5eae31'
    # Negative control: historical available labels must matter, or invariance is vacuous.
    last=origins[-1]; altered=history[history.date<last].copy();altered['value']=altered.value*100
    changed,_=calibrate(original[original.origin_date==last],altered,targets,reference_forecasts=original[original.origin_date<last])
    saved=read('results/calibration_study/forecasts.csv');expected=saved[saved.origin_date==last]
    assert not np.allclose(changed.q90,expected.q90)
    cfg=json.loads((ROOT/'config.json').read_text()); scorer=ROOT/cfg['pack']/'starter/scorer.py'
    official=[]
    for label,source,previous in [
        ('original','results/online_forecasts.csv','original'),('calibrated','results/calibration_study/forecasts.csv','calibrated'),
        ('drift_base','results/calibration_study/drift_base.csv','drift_base'),('drift_base_calibrated','results/calibration_study/drift_base_calibrated.csv','drift_base_calibrated')]:
        for baseline in ['last_value','drift']:
            path=OUT/f'{label}_{baseline}.json'; cells=OUT/f'{label}_{baseline}_cells.csv'
            subprocess.run([sys.executable,'-B',str(scorer),'--forecast',str(ROOT/source),'--truth',str(ROOT/'data/history.csv'),'--history',str(ROOT/'data/history.csv'),'--series-ids','@'+str(ROOT/'data/target_ids.txt'),'--horizons','1,3,7','--skill-baseline',baseline,'--no-missing-as-baseline','--out',str(path),'--per-cell',str(cells)],check=True,capture_output=True,text=True)
            report=json.loads(path.read_text());old=json.loads((STUDY/f'{previous}_{baseline}.json').read_text())
            assert report['overall']==old['overall']
            c=pd.read_csv(cells);same(c,pd.read_csv(STUDY/f'{previous}_{baseline}_cells.csv'))
            official.append(dict(method=label,baseline=baseline,overall=report['overall']))
    report=dict(review_type='automated self-review by build agent, not external certification',status='passed',physical_truncation=records,final_candidate_rows=len(candidate),negative_control_detected=True,official_reports=official,limitations=['Calibration layer only: base forecast generation and retrospective cohort selection are not certified by this replay.','Retrospective rule selection remains; 14 origins are not an untouched holdout.','No final November outcome observations; validation is not performance.'])
    (OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('FALSIFICATION_AUDIT_PASS: 28 physical-truncation replays, final candidate, negative control, 8 official report and cell reproductions')

if __name__=='__main__':main()
