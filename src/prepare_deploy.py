"""Freeze a consistent public snapshot; refuse intermediate reproduction output."""
import csv
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'demo'
data=json.loads((source/'data.json').read_text())
assert data['metrics']['online_last_value']==json.loads((ROOT/'results/online_last_value.json').read_text())['overall']
calibration=ROOT/'results/calibration_study/summary.json'
if calibration.exists():
 assert data.get('calibration_study')==json.loads(calibration.read_text()),'Reproduction is incomplete: finalize demo before deployment'
for name in ['forecasts.csv','forecasts_calibrated.csv','forecasts_extended.csv','findings.md','README.md']:
 if (ROOT/name).exists():assert (source/name).read_bytes()==(ROOT/name).read_bytes(),f'Outdated public artifact: {name}'
for name in ['forecasts.csv','forecasts_calibrated.csv']:
 if (source/name).exists():
  with (source/name).open() as f:rows=list(csv.DictReader(f))
  assert len(rows)==111 and all(r['origin_date']=='2026-11-06' for r in rows)
assert data['sponsors']['recorded_live_run']['status']=='matched_exact_live_run'
out=ROOT/'deliverables/deploy_demo';temp=ROOT/'deliverables/deploy_demo.tmp'
if temp.exists():shutil.rmtree(temp)
shutil.copytree(source,temp)
if out.exists():shutil.rmtree(out)
temp.rename(out)
print('Consistent public snapshot frozen')
