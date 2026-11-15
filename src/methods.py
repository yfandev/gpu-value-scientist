"""Bounded JSON-configured quantile library. All paths slice at forecast origin."""
import numpy as np
from baselines import forecast_one
from _common import h_step_changes, iso

COLUMNS = ['series_id','origin_date','horizon_days','q10','q50','q90','target_date']

def quantiles(store,sid,origin,h,method,params):
    days,vals=store.history(sid,origin)
    if not len(vals): return None
    last=float(vals[-1])
    if method in ('drift','last_value_empirical'):
        r=forecast_one(store,sid,origin,[h],method,int(params.get('min_samples',20)),None)[0]
        return np.array([r['q10'],r['q50'],r['q90']])
    window=int(params.get('window',56)); keep=days>origin-window
    rd,rv=days[keep],vals[keep]
    changes=h_step_changes(rd,rv,h,True)
    full=h_step_changes(days,vals,h,True)
    if method=='recent':
        use=changes if len(changes)>=int(params.get('min_samples',20)) else full
        q=last*np.exp(np.quantile(use,[.1,.5,.9])) if len(use)>=int(params.get('min_samples',20)) else np.repeat(last,3)
    elif method=='volatility':
        q=quantiles(store,sid,origin,h,'drift',{})
        a=h_step_changes(rd,rv,1,True); b=h_step_changes(days,vals,1,True)
        scale=1.0
        if len(a)>=10 and len(b)>=20 and np.std(b)>1e-12:
            scale=float(np.clip(np.std(a)/np.std(b),params.get('scale_min',.5),params.get('scale_max',2)))
        q=q[1]*np.exp(np.log(q/q[1])*scale)
    elif method=='step':
        q=quantiles(store,sid,origin,h,'drift',{})
        # Shrink log increments toward no change when recent one-day changes are rare.
        one=h_step_changes(rd,rv,1,True)
        if len(one)>=10:
            hazard=float(np.mean(np.abs(one)>1e-9)); weight=float(params.get('shrinkage',.5))+(1-float(params.get('shrinkage',.5)))*(1-(1-hazard)**h)
            q=last*np.exp(np.log(q/last)*weight)
    elif method=='conformal':
        q=quantiles(store,sid,origin,h,'recent',{'window':window,'min_samples':20})
        residuals=[]
        # Prequential residuals: fit at pseudo-origin, use truth only when it has matured.
        for d in days[(days>=origin-int(params.get('calibration_days',35))) & (days<=origin-h)]:
            y=store.value_at(sid,int(d)+h)
            if y is None: continue
            old=quantiles(store,sid,int(d),h,'recent',{'window':window,'min_samples':20})
            if old is not None: residuals.append([np.log(y/old[0]),np.log(y/old[2])])
        if len(residuals)>=int(params.get('min_calibration',12)):
            a=np.array(residuals)
            q[0]*=np.exp(np.quantile(a[:,0],.1,method='lower'))
            q[2]*=np.exp(np.quantile(a[:,1],.9,method='higher'))
    else: raise ValueError('Unsupported method '+method)
    q=np.maximum(q,1e-9); q[0]=min(q[0],q[1]);q[2]=max(q[2],q[1])
    if not np.isfinite(q).all(): raise ValueError('Non-finite quantiles')
    return q

def forecast(store,ids,origins,horizons,spec):
    import pandas as pd
    rows=[]
    for origin in origins:
        for sid in ids:
            if sid not in store: continue
            for h in horizons:
                q=quantiles(store,sid,origin,h,spec['method'],spec['parameters'])
                if q is not None: rows.append(dict(zip(COLUMNS,[sid,iso(origin),h,*map(float,q),iso(origin+h)])))
    return pd.DataFrame(rows,columns=COLUMNS)
