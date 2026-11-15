import sys
sys.dont_write_bytecode=True
import unittest
from pathlib import Path
import pandas as pd
from src.group_calibration_study import widen, KEY, RULE_HASH, sha
ROOT=Path(__file__).resolve().parents[1]

class GroupCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        online=pd.read_csv(ROOT/'results/online_forecasts.csv')
        cls.drift=pd.read_csv(ROOT/'results/forecast_drift.csv').merge(online[KEY],on=KEY,validate='one_to_one')
        cls.history=pd.read_csv(ROOT/'data/history.csv');cls.targets=pd.read_csv(ROOT/'data/targets.csv')
        cls.output={g:widen(cls.drift,cls.history,cls.targets,g) for g in [False,True]}

    def test_frozen_rule(self):
        self.assertEqual(sha(ROOT/'results/group_calibration_study/rule.json'),RULE_HASH)

    def test_maturity_and_sparse_fallback(self):
        for grouped,(forecast,audit) in self.output.items():
            used=audit[audit.n>0]
            self.assertTrue((used.max_target_date<used.origin_date).all())
            self.assertTrue((used.max_prior_origin<used.origin_date).all())
            self.assertTrue((used.n>=20).all());self.assertTrue((used.n_origins>=2).all())
            if grouped:
                fallback=audit[audit.pool=='global_horizon']
                self.assertTrue(((fallback.class_n<20)|(fallback.class_n_origins<2)).all())
                eligible=(audit.class_n>=20)&(audit.class_n_origins>=2)
                self.assertTrue((audit.loc[eligible,'pool']=='class_horizon').all())
            joined=self.drift.merge(forecast,on=KEY,suffixes=('_old','_new'))
            self.assertTrue((joined.q50_old==joined.q50_new).all())
            self.assertTrue((joined.q10_new<=joined.q10_old).all())
            self.assertTrue((joined.q90_new>=joined.q90_old).all())

    def test_future_truncation_every_later_origin(self):
        for origin in ['2026-09-23','2026-09-30','2026-10-07','2026-10-14','2026-10-21']:
            for grouped in [False,True]:
                f=self.drift[self.drift.origin_date<=origin]
                h=self.history[self.history.date<origin]
                got,audit=widen(f,h,self.targets,grouped)
                expected=self.output[grouped][0]
                pd.testing.assert_frame_equal(got,expected[expected.origin_date<=origin].reset_index(drop=True))
                changed=self.history.copy();changed.loc[changed.date>=origin,'value']=1e12
                perturbed,_=widen(f,changed,self.targets,grouped)
                pd.testing.assert_frame_equal(got,perturbed)

    def test_explicit_archive_unchanged(self):
        origin=self.drift.origin_date.max(); frozen=self.drift[self.drift.origin_date==origin]
        for grouped in [False,True]:
            got,_=widen(frozen,self.history,self.targets,grouped,archive=self.drift)
            expected=self.output[grouped][0]
            pd.testing.assert_frame_equal(got,expected[expected.origin_date==origin].reset_index(drop=True))

if __name__=='__main__':unittest.main()
