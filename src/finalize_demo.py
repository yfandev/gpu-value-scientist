"""Publish measured follow-up reports without changing recorded agent decisions."""
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'demo/data.json';data=json.loads(p.read_text())
study=ROOT/'results/calibration_study/summary.json'
if study.exists():
 data['calibration_study']=json.loads(study.read_text())
 candidate=ROOT/'forecasts_calibrated.csv'
 if candidate.exists():shutil.copyfile(candidate,ROOT/'demo/forecasts_calibrated.csv')
p.write_text(json.dumps(data,indent=2)+'\n')
for name in ['README.md','findings.md','config.json']:
 shutil.copyfile(ROOT/name,ROOT/'demo'/name)
print('Measured follow-up reports added to demo; original forecasts unchanged')

for source,target in [('forecasts_extended.csv','forecasts_extended.csv'),('data/headline_series_audit.csv','headlines.csv')]:
    if (ROOT/source).exists():shutil.copyfile(ROOT/source,ROOT/'demo'/target)
