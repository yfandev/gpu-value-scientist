#!/usr/bin/env python3
"""Prespecified mechanism controls and persisted-artifact invariants."""
import math,sys,unittest,json
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb
sys.dont_write_bytecode=True
import study

class Controls(unittest.TestCase):
    def identity(self,b):
        self.assertAlmostEqual(b['D'],b['S']+b['C']+b['R'],places=13)
    def test_fixed_prices_membership(self):
        b=study.bridge({'a':1.,'b':3.},{'a':1.,'b':3.,'c':.5},2.,1.)
        self.identity(b);self.assertEqual(b['R'],0);self.assertEqual(b['S'],0)
        self.assertAlmostEqual(b['C'],math.log(.5))
    def test_uniform_repricing(self):
        b=study.bridge({'a':1.,'b':3.},{'a':1.1,'b':3.3},2.,2.2)
        self.identity(b);self.assertAlmostEqual(b['C'],0);self.assertAlmostEqual(b['S'],0)
        self.assertAlmostEqual(b['R'],math.log(1.1))
    def test_multiplicity_only(self):
        b=study.bridge({'a':1.,'b':3.},{'a':1.,'b':3.},1.,3.)
        self.identity(b);self.assertEqual(b['C'],0);self.assertEqual(b['R'],0)
        self.assertAlmostEqual(b['S'],math.log(3))
    def test_cancellation(self):
        b=study.bridge({'a':1.,'b':3.},{'a':2.,'b':4.,'c':.5},2.,2.)
        self.identity(b);self.assertEqual(b['D'],0);self.assertGreater(abs(b['R']),.4)
        self.assertAlmostEqual(b['C'],-b['R'])
    def test_no_overlap_unidentified(self):
        b=study.bridge({'a':1.},{'b':2.},1.,2.)
        self.assertTrue(math.isnan(b['C']));self.assertTrue(math.isnan(b['R']))
        self.assertEqual(b['n_common'],0)
    def test_order_invariance(self):
        a={'a':1.,'b':2.,'c':5.};b={'c':6.,'b':2.,'z':1.}
        x=study.bridge(a,b,2,2);y=study.bridge(dict(reversed(list(a.items()))),dict(reversed(list(b.items()))),2,2)
        self.assertEqual(x,y)
    def test_persisted_identity_and_stable_membership(self):
        for variant in ['primary','coarse','raw_provider']:
            z=pd.read_csv(study.OUT/f'transitions_{variant}.csv')
            self.assertLess((z.D-z.S-z.C-z.R).abs().max(),1e-12)
            self.assertLess(z.loc[z.stable_basket,'C'].abs().max(),1e-12)
            self.assertTrue((z.n_common<=z[['n_old','n_new']].min(axis=1)).all())
    def test_gap_and_cutoff(self):
        z=pd.read_csv(study.OUT/'transitions_primary.csv')
        self.assertTrue(((pd.to_datetime(z.date)-pd.to_datetime(z.old_date)).dt.days==1).all())
        self.assertGreaterEqual(z.old_date.min(),study.START);self.assertLessEqual(z.date.max(),study.END)
        self.assertFalse(((z.source_id=='gpurentalprices')&z.date.isin(['2026-10-15','2026-10-18','2026-10-25','2026-10-31','2026-11-02'])).any())
    def test_raw_key_excludes_observation_identity(self):
        con=duckdb.connect()
        # Independently rebuild the serialized primary key from observed contract fields.
        row=con.execute(f"select * from '{study.OUT}/raw_selected.parquet' limit 1").df().iloc[0]
        def scalar(v):
            if pd.isna(v):return None
            if isinstance(v,(int,np.integer)):return str(int(v))
            return str(v)
        def make(r):
            extra=json.loads(r.extra_json)
            return [scalar(r[f]) for f in study.BASE]+[None if extra.get(f) is None else json.dumps(extra[f],separators=(',',':'),ensure_ascii=False) for f in study.EXTRA]
        original=make(row);row['obs_id']='anything';row['snapshot_ts_utc']=pd.Timestamp('2030-01-01');row['usd_per_gpu_hour']=99999
        self.assertEqual(original,make(row));self.assertEqual(original,json.loads(row.key_primary))
        con.close()
    def test_raw_medians_and_counts(self):
        x=pd.read_csv(study.OUT/'median_reconciliation.csv')
        self.assertLessEqual(x.error.abs().max(),.00005000001)
        self.assertTrue((x.n_rows==x.n_obs).all())
    def test_protected_and_input_hashes(self):
        self.assertEqual({n:study.sha(study.ROOT/n) for n in study.EXPECTED},study.EXPECTED)
        for p,h in json.loads((study.OUT/'input_hashes.json').read_text()).items():
            self.assertEqual(study.sha(study.ROOT/p),h)
        self.assertEqual(study.sha(study.OUT/'protocol.json'),(study.OUT/'protocol.sha256').read_text().split()[0])

if __name__=='__main__':
    if '--negative-control' in sys.argv:
        b=study.bridge({'a':1.,'b':3.},{'a':1.,'b':3.,'c':.5},2.,1.)
        b['C']+=1 # known broken attribution must fail the same identity check
        Controls().identity(b)
        raise RuntimeError('corrupted bridge escaped detection')
    run=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    if not run.wasSuccessful():sys.exit(1)
    print('FRONTIER_CONTROLS_PASS')
