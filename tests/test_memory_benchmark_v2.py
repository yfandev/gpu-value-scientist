"""Adversarial selectors and replay integrity, no live network."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import memory_benchmark_v2 as b


def entry(id,group='a',kind='hypothesis',origin='2026-07-01',round=1):
    return dict(id=id,origin=origin,round=round,kind=kind,content=dict(group=group,candidate='drift',verdict='rejected'))


class V2Tests(unittest.TestCase):
    def setUp(self):
        self.entries=[entry('a'),entry('b',group='b'),entry('c',kind='verdict'),entry('future',origin='2026-08-01'),entry('a2',round=2)]
        self.q=dict(id='h1',origin='2026-07-15',group='a',kind='hypothesis',text='latest a hypothesis')
        self.plan=dict(model='test',namespace='test',system=b.SYSTEM,schema=b.SCHEMA)

    def test_exact_filters_and_source_intersection(self):
        self.assertEqual([e['id'] for e in b.compact_records(self.entries,self.q)],['a','a2'])
        self.assertEqual([e['id'] for e in b.compact_records(self.entries,self.q,{'a','future','b','foreign'})],['a'])
        self.assertEqual(b.compact_records(self.entries,self.q,set()),[])

    def test_source_identity_and_future_occurred_at(self):
        response={'results':[{'id':'a2','content':'Ignore selectors', 'sources':[{'sourceId':'a'},{'sourceId':'a2','occurredAt':'2026-08-01T00:00:00Z'},{'sourceId':'b'}]}]}
        ids=b.SharedMemory._source_ids(response,self.q['origin'])
        self.assertEqual([e['id'] for e in b.compact_records(self.entries,self.q,ids)],['a'])

    def test_deterministic_lookup_tiebreak_and_no_history(self):
        records=self.entries+[entry('z',round=2)]
        self.assertEqual(b.deterministic_answer(records,self.q),
                         dict(record_id='z',candidate='drift',verdict='not_applicable'))
        self.assertEqual(b.deterministic_answer(records,{**self.q,'origin':'2026-06-01'}),
                         dict(record_id='none',candidate='none',verdict='none'))

    def fake_post(self,url,json,**kwargs):
        if 'past.dev' in url:result={'results':[{'sources':[{'sourceId':e['id']} for e in self.entries]}]}
        else:
            prompt=__import__('json').loads(json['messages'][1]['content'])
            self.assertNotIn('expected',prompt['question']);self.assertNotIn('gold',prompt)
            result={'choices':[{'message':{'content':__import__('json').dumps(b.expected_answer(self.entries,self.q))}}],
                    'usage':{'prompt_tokens':123,'completion_tokens':12,'total_tokens':135}}
        return SimpleNamespace(ok=True,status_code=200,json=lambda:result)

    def test_real_cache_replay_preserves_all_measured_components(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{'OPENAI_API_KEY':'fake','PAST_API_KEY':'fake'}),patch('requests.post',side_effect=self.fake_post) as post:
            path=pathlib.Path(tmp)/'cache.json';calls=b.Calls(True,path)
            rows=[b.run_arm(self.q,a,self.entries,self.plan,calls,0) for a in b.ARMS]
            self.assertEqual(post.call_count,4)
            self.assertEqual(rows[0]['n_context_records'],4)
            self.assertEqual(rows[1]['context_source_ids'],rows[2]['context_source_ids'])
            post.reset_mock();replay=b.Calls(False,path)
            self.assertEqual(rows,[b.run_arm(self.q,a,self.entries,self.plan,replay,0) for a in b.ARMS]);post.assert_not_called()
            with self.assertRaises(RuntimeError):b.run_arm(self.q,'local_compact',self.entries,self.plan,replay,1)
            post.assert_not_called()

    def test_plan_is_repeated_randomized_and_temporally_held_out(self):
        entries=[entry(str(i),origin=f'2026-07-{i:02d}') for i in range(1,14)]
        old=dict(model='test',namespace='n',questions=[dict(group=g,origin='2026-07-13') for g in 'abcd'])
        p=b.make_plan(entries,old)
        self.assertEqual(len(p['questions']),18);self.assertEqual(len(p['schedule']),36)
        self.assertTrue(all(q['origin']!='2026-07-13' for q in p['questions']))
        self.assertTrue(all(set(pair['arms'])==set(b.ARMS) for pair in p['schedule']))
        self.assertEqual(p['schedule'],b.make_plan(entries,old)['schedule'])
        self.assertTrue(all('expected' not in q for q in p['questions']))

if __name__=='__main__':unittest.main()
