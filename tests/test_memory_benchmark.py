"""Benchmark protocol tests, no real API calls or main-loop artifact changes."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import memory_benchmark as b


def record(group,kind,round,origin,candidate='drift',verdict='rejected'):
    return {'id':f'{group}-{kind}-{round}','origin':origin,'round':round,
            'agent':'CRITIC' if kind=='verdict' else 'ANALYST','kind':kind,
            'content':{'group':group,'candidate':candidate,**({'verdict':verdict} if kind=='verdict' else {})}}


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.entries=[record(g,k,r,d) for g in ['a','b','c','d'] for k in ['hypothesis','verdict']
                      for r,d in [(1,'2026-07-15'),(2,'2026-07-22')]]
        self.config={'cutoff':'2026-11-06','model':'test-model'}
        self.plan=b.make_plan(self.entries,self.config)
        self.temp=tempfile.TemporaryDirectory()
        self.cache=pathlib.Path(self.temp.name)/'cache.json'

    def tearDown(self):self.temp.cleanup()

    def test_predeclared_questions_and_randomized_paired_order(self):
        self.assertEqual(len(self.plan['questions']),8)
        p2=b.make_plan(self.entries,self.config)
        self.assertEqual(self.plan['schedule'],p2['schedule'])
        self.assertEqual({tuple(p['arms']) for p in self.plan['schedule']},
                         {('past_dev','full_context'),('full_context','past_dev')})
        for q in self.plan['questions']:
            self.assertTrue(q['expected']['record_id'].endswith('-2'))
        self.assertEqual(self.plan['snapshot_sha256'],b.digest(self.entries))

    def test_expected_answers_and_retrieval_obey_same_temporal_scope(self):
        q={**self.plan['questions'][0],'origin':'2026-07-15'}
        self.assertTrue(b.expected_answer(self.entries,q)['record_id'].endswith('-1'))
        response={'results':[{'sources':[{'sourceId':e['id']} for e in self.entries]+[{'sourceId':'foreign'}]}]}
        actual=b.select_recalled(self.entries,response,'2026-07-15')
        self.assertTrue(all(e['round']==1 for e in actual))
        self.assertEqual(len(actual),8)

    def fake_post(self,url,json,headers,timeout):
        if 'past.dev' in url:
            result={'results':[{'sources':[{'sourceId':e['id']} for e in self.entries]}],'usedEvidenceTokens':100}
        else:
            prompt=__import__('json').loads(json['messages'][1]['content'])
            self.assertNotIn('expected',prompt['question'])
            self.assertTrue(json['response_format']['json_schema']['strict'])
            answer=b.expected_answer(prompt['records'],prompt['question'])
            result={'choices':[{'message':{'content':__import__('json').dumps(answer)}}],
                    'usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120}}
        return SimpleNamespace(ok=True,status_code=200,json=lambda:result)

    def test_live_recording_then_offline_replay_preserves_answers_usage_latency(self):
        with patch.dict('os.environ',{'OPENAI_API_KEY':'fake','PAST_API_KEY':'fake'}),patch('requests.post',side_effect=self.fake_post) as post:
            live=b.Calls(True,self.cache);q=self.plan['questions'][0]
            rows=[b.run_arm(q,a,self.entries,self.plan,live,0) for a in ['full_context','past_dev']]
            self.assertTrue(all(r['exact_match'] for r in rows))
            self.assertEqual(post.call_count,3)
            post.reset_mock();offline=b.Calls(False,self.cache)
            replay=[b.run_arm(q,a,self.entries,self.plan,offline,0) for a in ['full_context','past_dev']]
            post.assert_not_called()
            for actual,old in zip(replay,rows):
                for key in ['answer','openai_usage','retrieval_seconds','model_seconds','end_to_end_seconds']:
                    self.assertEqual(actual[key],old[key])
                self.assertEqual(actual['model_measurement'],'recorded')
            self.assertEqual(live.used,offline.used)

    def test_full_context_is_complete_without_baseline_handicapping(self):
        with patch.dict('os.environ',{'OPENAI_API_KEY':'fake'}),patch('requests.post',side_effect=self.fake_post):
            row=b.run_arm(self.plan['questions'][0],'full_context',self.entries,self.plan,b.Calls(True,self.cache),0)
            self.assertEqual(row['n_context_records'],len(self.entries))
            self.assertEqual(set(row['context_source_ids']),{e['id'] for e in self.entries})

    def test_offline_missing_response_fails_without_fake_numbers(self):
        with patch('requests.post') as post:
            with self.assertRaises(RuntimeError):
                b.run_arm(self.plan['questions'][0],'full_context',self.entries,self.plan,b.Calls(False,self.cache),0)
            post.assert_not_called()

    def test_http_failure_is_not_recorded_as_success(self):
        with patch.dict('os.environ',{'PAST_API_KEY':'fake'}),patch('requests.post',return_value=SimpleNamespace(ok=False,status_code=503)):
            calls=b.Calls(True,self.cache)
            with self.assertRaises(RuntimeError):calls.invoke('past_dev',{},'trial')
            self.assertFalse(calls.cache)

    def test_summary_never_equates_tokens_with_total_cost(self):
        with patch.dict('os.environ',{'OPENAI_API_KEY':'fake','PAST_API_KEY':'fake'}),patch('requests.post',side_effect=self.fake_post):
            calls=b.Calls(True,self.cache);rows=[]
            for q in self.plan['questions']:
                for arm in ['full_context','past_dev']:rows.append(b.run_arm(q,arm,self.entries,self.plan,calls,0))
        summary=b.summarize(rows,self.plan)
        self.assertFalse(summary['accuracy_improved'])
        self.assertFalse(summary['total_cost_reduction_verified'])
        self.assertFalse(summary['all_three_sponsor_gains_verified'])
        self.assertEqual(summary['arms']['full_context']['exact_match_accuracy'],1)


if __name__=='__main__':unittest.main()
