"""Adversarial checks for the frozen price-reset experiment."""
import numpy as np
import pandas as pd

def validate_guards(history,targets,keys,candidate,store):
    from price_reset_study import ResetDistribution,weighted_quantile,make_forecasts,day,SeriesStore
    assert np.array_equal(weighted_quantile([0,0,0],[1,1,1]),[0,0,0])
    assert np.array_equal(weighted_quantile([-1,0,1],[.2,.6,.2]),[-1,0,1])
    assert np.array_equal(weighted_quantile([-1,0,1],[.05,.9,.05]),[0,0,0])
    mini=pd.DataFrame([{'series_id':'test','date':d,'value':10,'is_filled':0} for d in ['2026-01-01','2026-01-02','2026-01-04','2026-01-05']])
    meta=pd.DataFrame([{'series_id':'test','source_id':'source','instrument_class':'type'}])
    age=ResetDistribution(mini,meta).ages['test'];assert age[day('2026-01-02')]==1 and age[day('2026-01-04')]==0 and age[day('2026-01-05')]==1
    expected=candidate.set_index(['series_id','origin_date','horizon_days'])[['q10','q50','q90']]
    checks=[]
    # Removing future rows and adversarially changing all future values are different checks.
    for origin in sorted(keys.origin_date.unique()):
        origin_keys=keys[keys.origin_date==origin]
        for kind in ['truncated','perturbed']:
            h=history[history.date<=origin].copy() if kind=='truncated' else history.copy()
            if kind=='perturbed':h.loc[h.date>origin,'value']*=1e6
            model=ResetDistribution(h,targets)
            guard_store=SeriesStore(h.assign(day=h.date.map(day)).sort_values(['series_id','day']))
            actual,audit=make_forecasts(model,origin_keys,guard_store,True)
            got=actual.set_index(['series_id','origin_date','horizon_days'])[['q10','q50','q90']]
            wanted=expected.loc[got.index]
            assert np.allclose(got.values,wanted.values,rtol=1e-12,atol=1e-12),(origin,kind)
            used=audit[audit.method=='price_reset_distribution']
            if len(used):assert (used.max_training_target<origin).all()
            checks.append({'origin':origin,'check':kind,'predictions':len(actual),'equal':True})
    return {'passed':True,'checks':checks,'no_change_atom':True,'signed_jump_quantiles':True,'missing_day_resets_age':True,'note':'Future rows removed and separately perturbed at all14origins; existing official baseline fallback independently remains origin-truncated.'}
