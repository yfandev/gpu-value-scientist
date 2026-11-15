"""Bounded retries for transient service errors; never print credentials/bodies."""
import time
import requests

def request_with_retry(call,*args,attempts=6,sleep=None,**kwargs):
    sleep=sleep or time.sleep
    for attempt in range(attempts):
        try:
            response=call(*args,**kwargs)
        except (requests.Timeout,requests.ConnectionError):
            if attempt+1==attempts:raise
            sleep(min(30,2**attempt));continue
        if response.status_code not in (429,500,502,503,504) or attempt+1==attempts:return response
        try:delay=float(getattr(response,'headers',{}).get('Retry-After',2**attempt))
        except (TypeError,ValueError):delay=2**attempt
        sleep(max(.1,min(30,delay)))
    raise RuntimeError('Request retry loop exhausted')
