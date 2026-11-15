"""Present the existing calibration study as cumulative official scores.

No forecasts, parameters, hypotheses or selection decisions are changed.
This is retrospective visualization, not a new independent validation.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    config=json.loads((ROOT/'config.json').read_text())
    source=ROOT/'results/calibration_study/forecasts.csv'
    forecasts=pd.read_csv(source)
    scorer=ROOT/config['pack']/'starter/scorer.py'
    out=ROOT/'results/presentation_calibration_curve';out.mkdir(exist_ok=True)
    rows=[]
    for i,origin in enumerate(sorted(forecasts.origin_date.unique()),1):
        prefix=out/f'prefix_{i:02d}.csv';forecasts[forecasts.origin_date<=origin].to_csv(prefix,index=False,float_format='%.10g')
        report=out/f'prefix_{i:02d}_official.json'
        subprocess.run([sys.executable,'-B',str(scorer),'--forecast',str(prefix),'--truth',str(ROOT/'data/history.csv'),'--history',str(ROOT/'data/history.csv'),'--series-ids','@'+str(ROOT/'data/target_ids.txt'),'--horizons','1,3,7','--skill-baseline','drift','--no-missing-as-baseline','--out',str(report)],check=True,capture_output=True,text=True)
        r=json.loads(report.read_text());assert r['forecast_validation']['n_problems']==0
        rows.append({'origin_date':origin,'cumulative_skill_vs_drift':r['overall']['skill_pooled'],'n_cells':r['overall']['n_cells']})
    expected=json.loads((ROOT/'results/calibration_study/calibrated_drift.json').read_text())['overall']
    assert rows[-1]['cumulative_skill_vs_drift']==expected['skill_pooled']
    assert rows[-1]['n_cells']==expected['n_cells']
    payload={'status':'retrospective_existing_study','source_forecast_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scorer_sha256':hashlib.sha256(scorer.read_bytes()).hexdigest(),'caveat':'Widening was designed after inspecting original errors. This curve re-presents the existing retrospective study, not untouched validation or autonomous improvement.','rounds':rows}
    (ROOT/'demo/calibration_curve.json').write_text(json.dumps(payload,indent=2)+'\n')
    print('OFFICIAL_CALIBRATION_CURVE_VALIDATED',len(rows),rows[-1])
if __name__=='__main__':main()
