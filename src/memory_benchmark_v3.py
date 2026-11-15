"""Predeclared model-free structured retrieval against contemporaneous comparators."""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import json
import os
import random
import statistics
import time
import memory_benchmark_v2 as v2
from memory_benchmark import ROOT, Calls, SCHEMA, canonical, digest, expected_answer, save
from agents import SharedMemory

OUT=ROOT/'results/memory_benchmark_v3'
ARMS=['full_context','local_deterministic','past_dev_deterministic']


def resolve_recalled(entries, question, response):
    """Resolve only allowlisted canonical evidence; no local rescue for recall omissions.

    This answers an exact structured latest-record lookup, not arbitrary semantic QA.
    The caller supplies a canonical corpus from its own namespace and a parsed selector.
    """
    ids=SharedMemory._source_ids(response,question['origin'])
    records=v2.compact_records(entries,question,ids)
    if not records:return dict.fromkeys(SCHEMA['required'],'none'),[]
    last=records[-1]
    return {'record_id':last['id'],'candidate':last['candidate'],
            'verdict':last['verdict'] if last['kind']=='verdict' else 'not_applicable'},[r['id'] for r in records]


class RecordedCalls(Calls):
    def invoke(self,provider,payload,trial,local_elapsed=None):
        request={'provider':provider,'payload':payload,'trial':trial};key=digest(request)
        if key in self.cache or not self.live or provider=='local_context':
            return super().invoke(provider,payload,trial,local_elapsed)
        import requests
        urls={'openai':('https://api.openai.com/v1/chat/completions','OPENAI_API_KEY'),
              'past_dev':('https://api.past.dev/api/v1/recall','PAST_API_KEY')}
        url,env=urls[provider];credential=os.environ.get(env)
        if not credential:raise RuntimeError('Missing '+env)
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat();started=time.perf_counter()
        response=requests.post(url,json=payload,headers={'Authorization':'Bearer '+credential},timeout=120)
        elapsed=time.perf_counter()-started
        if not response.ok:raise RuntimeError(f'{provider} HTTP {response.status_code}; halted without fallback')
        body=response.json()
        if not isinstance(body,dict):raise ValueError('API object required')
        record={'request':copy.deepcopy(request),'response':body,'elapsed_seconds':elapsed,
                'started_utc':started_utc,'request_id':response.headers.get('X-Request-Id'),
                'response_status':response.status_code,'mode':'live','replayed':False}
        self.cache[key]=copy.deepcopy(record);save(self.path,self.cache);self.used.append(key)
        return record


def make_plan(old,entries):
    rng=random.Random(20261116);schedule=[]
    for repeat in range(3):
        qs=copy.deepcopy(old['questions']);rng.shuffle(qs)
        for q in qs:
            arms=ARMS.copy();rng.shuffle(arms)
            schedule.append({'question_id':q['id'],'repetition':repeat,'arms':arms})
    return {'protocol_version':3,'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'snapshot_sha256':digest(entries),'model':old['model'],'namespace':old['namespace'],
            'system':old['system'],'schema':old['schema'],'questions':old['questions'],
            'schedule':schedule,'seed':20261116,'repetitions':3,'arms':ARMS,'recall_level':'low',
            'recall_level_source':'https://past.dev/openapi.json RecallRequest: low default, 8000 tokens; medium may be plan-capped to same budget.',
            'question_status':'Previously evaluated v2 questions; operational replication, not held-out data.',
            'primary':'Exact match, full retrieval+local preparation+model latency, tokens; paired contemporaneous arms.',
            'cost_policy':'Zero model tokens is not zero total cost. Recall, ingestion and subscription billing required.',
            'latency_scope':'Request wall time plus canonical processing; excludes benchmark cache persistence.'}


def run_arm(q,arm,entries,plan,calls,repeat):
    if arm=='full_context':return v2.run_arm(q,arm,entries,plan,calls,repeat)
    trial={'plan_sha256':digest(plan),'question':q['id'],'arm':arm,'repetition':repeat}
    remote=0.;request_id=None
    start=time.perf_counter()
    payload={'query':q['text']+' Return original canonical source records with this exact group and kind, including the latest eligible source.',
             'identity':plan['namespace']+'-forecaster','queryTimestamp':q['origin']+'T23:59:59Z',
             'occurredTo':q['origin']+'T23:59:59Z','limit':200,'level':plan['recall_level']}
    preparation=time.perf_counter()-start
    if arm=='past_dev_deterministic':
        rec=calls.invoke('past_dev',payload,trial);remote=rec['elapsed_seconds'];request_id=rec.get('request_id')
        start=time.perf_counter();answer,ids=resolve_recalled(entries,q,rec['response'])
    elif arm=='local_deterministic':
        start=time.perf_counter();records=v2.compact_records(entries,q);ids=[r['id'] for r in records]
        if records:
            last=records[-1];answer={'record_id':last['id'],'candidate':last['candidate'],
                'verdict':last['verdict'] if last['kind']=='verdict' else 'not_applicable'}
        else:answer=dict.fromkeys(SCHEMA['required'],'none')
    else:raise ValueError('Unknown arm')
    local_seconds=time.perf_counter()-start+preparation
    local=calls.invoke('local_context',{'source_ids':ids,'answer':answer},trial,local_seconds)
    gold=expected_answer(entries,q)
    return {'question_id':q['id'],'repetition':repeat,'arm':arm,'answer':answer,'expected':gold,
            'exact_match':answer==gold,'context_source_ids':ids,'n_context_records':len(ids),
            'gold_source_present':gold['record_id'] in ids if gold['record_id']!='none' else None,
            'retrieval_seconds':remote,'local_preparation_seconds':local['elapsed_seconds'],'model_seconds':0.,
            'end_to_end_seconds':remote+local['elapsed_seconds'],'request_id':request_id,
            'openai_usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0},'monetary_cost_usd':None}


def summarize(rows,plan):
    arms={}
    for arm in ARMS:
        rs=[r for r in rows if r['arm']==arm]
        arms[arm]={'n_trials':len(rs),'correct':sum(r['exact_match'] for r in rs),
          'accuracy':statistics.mean(r['exact_match'] for r in rs),
          'mean_seconds':statistics.mean(r['end_to_end_seconds'] for r in rs),
          'median_seconds':statistics.median(r['end_to_end_seconds'] for r in rs),
          'prompt_tokens':sum(r['openai_usage']['prompt_tokens'] for r in rs),
          'completion_tokens':sum(r['openai_usage']['completion_tokens'] for r in rs),
          'retrieval_misses':sum(r['gold_source_present'] is False for r in rs)}
    paired=[]
    for pair in plan['schedule']:
        rs={r['arm']:r for r in rows if r['question_id']==pair['question_id'] and r['repetition']==pair['repetition']}
        for base in ['full_context','local_deterministic']:
            a,b=rs['past_dev_deterministic'],rs[base]
            paired.append({'question_id':pair['question_id'],'repetition':pair['repetition'],'baseline':base,
              'accuracy_difference':int(a['exact_match'])-int(b['exact_match']),
              'latency_difference_seconds':a['end_to_end_seconds']-b['end_to_end_seconds']})
    return {'arms':arms,'paired_differences':paired,'total_cost_reduction_verified':False,
      'all_three_sponsor_gains_verified':False,'failures':[r for r in rows if not r['exact_match']]}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--live',action='store_true');args=ap.parse_args()
    from environment import load_environment
    load_environment()
    if args.prepare:
        if (OUT/'plan.json').exists():raise SystemExit('Declared plan exists')
        old=json.loads((v2.OUT/'plan.json').read_text());entries=json.loads((v2.OUT/'snapshot.json').read_text());plan=make_plan(old,entries)
        save(OUT/'snapshot.json',entries);save(OUT/'gold.json',{q['id']:expected_answer(entries,q) for q in plan['questions']});save(OUT/'plan.json',plan)
        print('Declared plan',digest(plan));return
    plan=json.loads((OUT/'plan.json').read_text());entries=json.loads((OUT/'snapshot.json').read_text())
    if digest(entries)!=plan['snapshot_sha256']:raise ValueError('Snapshot mismatch')
    calls=RecordedCalls(args.live,ROOT/'data/memory_benchmark_v3_cache.json');rows=[];qs={q['id']:q for q in plan['questions']}
    try:
        for pair in plan['schedule']:
            for arm in pair['arms']:
                rows.append(run_arm(qs[pair['question_id']],arm,entries,plan,calls,pair['repetition']));save(OUT/'trials.json',rows)
            print('Completed pair',len(rows)//3,'/',len(plan['schedule']),flush=True)
    except Exception as exc:
        save(OUT/'failure.json',{'type':type(exc).__name__,'message':str(exc),'completed_trials':len(rows)});raise
    result={'status':'complete','mode':'live_or_cached' if args.live else 'recorded','plan_sha256':digest(plan),
      'api_request_counts':{p:sum(calls.cache[k]['request']['provider']==p for k in calls.used) for p in ['openai','past_dev','local_context']},
      'request_keys':calls.used,'summary':summarize(rows,plan)}
    save(OUT/'report.json',result);print(canonical(result['summary']['arms']))

if __name__=='__main__':main()
