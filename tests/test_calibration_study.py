import unittest
from pathlib import Path
import pandas as pd
from src.calibration_study import calibrate

ROOT=Path(__file__).resolve().parents[1]


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forecasts=pd.read_csv(ROOT/'results/online_forecasts.csv')
        cls.history=pd.read_csv(ROOT/'data/history.csv')
        cls.targets=pd.read_csv(ROOT/'data/targets.csv')
        cls.calibrated,cls.audit=calibrate(cls.forecasts,cls.history,cls.targets)

    def test_widening_and_unchanged_median(self):
        cols=['series_id','origin_date','horizon_days']
        joined=self.forecasts.merge(self.calibrated,on=cols,suffixes=('_old','_new'))
        self.assertTrue((joined.q10_new<=joined.q10_old).all())
        self.assertTrue((joined.q90_new>=joined.q90_old).all())
        self.assertTrue((joined.q50_new==joined.q50_old).all())
        self.assertTrue((joined.q10_new>=0).all())

    def test_strict_maturity_and_fallback(self):
        used=self.audit[self.audit.n>0]
        self.assertTrue((used.max_target_date<used.origin_date).all())
        self.assertTrue((used.max_prior_origin<used.origin_date).all())
        self.assertTrue((used.n>=20).all())
        self.assertTrue((used.n_origins>=2).all())
        first=self.audit[self.audit.origin_date==self.forecasts.origin_date.min()]
        self.assertTrue((first.n==0).all())

    def test_all_origins_future_truth_invariance(self):
        # Change truth ON the origin as well as after: neither may enter calibration.
        for origin in sorted(self.forecasts.origin_date.unique()):
            prefix=self.forecasts[self.forecasts.origin_date<=origin]
            changed=self.history.copy()
            changed.loc[changed.date>=origin,'value']=1e9
            got,_=calibrate(prefix,changed,self.targets)
            expected=self.calibrated[self.calibrated.origin_date<=origin].reset_index(drop=True)
            pd.testing.assert_frame_equal(got,expected)

    def test_future_forecast_invariance(self):
        origin=sorted(self.forecasts.origin_date.unique())[6]
        changed=self.forecasts.copy()
        changed.loc[changed.origin_date>origin,['q10','q50','q90']]=1e8
        got,_=calibrate(changed,self.history,self.targets)
        pd.testing.assert_frame_equal(got[got.origin_date<=origin],self.calibrated[self.calibrated.origin_date<=origin])

    def test_explicit_residual_archive_is_preserved(self):
        origin=sorted(self.forecasts.origin_date.unique())[-1]
        changed=self.forecasts.copy()
        changed.loc[changed.origin_date<origin,['q10','q50','q90']]=1e8
        got,_=calibrate(changed,self.history,self.targets,reference_forecasts=self.forecasts)
        pd.testing.assert_frame_equal(got[got.origin_date==origin],self.calibrated[self.calibrated.origin_date==origin])


if __name__=='__main__': unittest.main()
