"""Publish measured follow-up reports without changing recorded agent decisions."""
import json
import csv
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'demo/data.json';data=json.loads(p.read_text())
study=ROOT/'results/calibration_study/summary.json'
if study.exists():
 data['calibration_study']=json.loads(study.read_text())
 candidate=ROOT/'forecasts_calibrated.csv'
 if candidate.exists():shutil.copyfile(candidate,ROOT/'demo/forecasts_calibrated.csv')
group_study=ROOT/'results/group_calibration_study/summary.json'
if group_study.exists():data['group_calibration_study']=json.loads(group_study.read_text())
if (ROOT/'forecasts_calibrated.csv').exists():
 data['selected_submission']={'file':'forecasts_calibrated.csv','metrics_basis':'historical calibration of original agent replay; November truth unavailable','original_file':'forecasts.csv'}
 with (ROOT/'forecasts_calibrated.csv').open() as f:
  data['forecasts']=[{**r,'horizon_days':int(r['horizon_days']),**{k:float(r[k]) for k in ['q10','q50','q90']}} for r in csv.DictReader(f)]
p.write_text(json.dumps(data,indent=2)+'\n')
for name in ['README.md','findings.md','config.json']:
 shutil.copyfile(ROOT/name,ROOT/'demo'/name)
print('Measured follow-up reports added to demo; original forecasts unchanged')

for source,target in [('forecasts_extended.csv','forecasts_extended.csv'),('data/headline_series_audit.csv','headlines.csv')]:
    if (ROOT/source).exists():shutil.copyfile(ROOT/source,ROOT/'demo'/target)
