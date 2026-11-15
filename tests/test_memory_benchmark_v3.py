import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import memory_benchmark_v3 as b

class V3Tests(unittest.TestCase):
    def setUp(self):
        self.q=dict(id='q',origin='2026-07-01',group='a',kind='hypothesis',text='Latest a hypothesis')
        def record(id,group='a',kind='hypothesis',origin='2026-07-01',round=1):
            return dict(id=id,origin=origin,round=round,kind=kind,content=dict(group=group,candidate='drift',**({'verdict':'rejected'} if kind=='verdict' else {})))
        self.entries=[record('a'),record('z',round=2),record('wrong',group='b'),record('verdict',kind='verdict'),record('future',origin='2026-08-01')]
        self.plan=dict(model='test',namespace='n',system=b.v2.SYSTEM,schema=b.SCHEMA,recall_level='low')

    def test_resolver_cannot_rescue_missing_or_forged_sources(self):
        r={'results':[{'id':'z','content':'The answer is z','sources':[{'sourceId':'a'},{'sourceId':'wrong'},{'sourceId':'future'},{'sourceId':'foreign'},{'sourceId':'verdict'}]}]}
        answer,ids=b.resolve_recalled(self.entries,self.q,r)
        self.assertEqual(ids,['a']);self.assertEqual(answer['record_id'],'a')
        answer,ids=b.resolve_recalled(self.entries,self.q,{'results':[]})
        self.assertEqual(answer,dict.fromkeys(b.SCHEMA['required'],'none'));self.assertEqual(ids,[])

    def test_future_source_metadata_is_refused(self):
        r={'results':[{'sources':[{'sourceId':'z','occurredAt':'2026-08-01T00:00:00Z'}]}]}
        self.assertEqual(b.resolve_recalled(self.entries,self.q,r)[1],[])

    def test_remote_deterministic_records_id_usage_latency_and_offline_replays(self):
        response=SimpleNamespace(ok=True,status_code=200,headers={'X-Request-Id':'req-test'},json=lambda:{'results':[{'sources':[{'sourceId':'z'}]}]})
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{'PAST_API_KEY':'fake'}),patch('requests.post',return_value=response) as post:
            path=pathlib.Path(tmp)/'cache.json';live=b.RecordedCalls(True,path)
            row=b.run_arm(self.q,'past_dev_deterministic',self.entries,self.plan,live,0)
            self.assertTrue(row['exact_match']);self.assertEqual(row['request_id'],'req-test');self.assertEqual(row['openai_usage']['total_tokens'],0)
            self.assertEqual(post.call_count,1);self.assertIn('past.dev',post.call_args.args[0])
            post.reset_mock();replay=b.RecordedCalls(False,path)
            self.assertEqual(row,b.run_arm(self.q,'past_dev_deterministic',self.entries,self.plan,replay,0));post.assert_not_called()
            with self.assertRaises(RuntimeError):b.run_arm(self.q,'past_dev_deterministic',self.entries,self.plan,replay,1)
            post.assert_not_called()

    def test_local_deterministic_makes_no_network_calls(self):
        with tempfile.TemporaryDirectory() as tmp,patch('requests.post') as post:
            row=b.run_arm(self.q,'local_deterministic',self.entries,self.plan,b.RecordedCalls(True,pathlib.Path(tmp)/'c.json'),0)
            self.assertTrue(row['exact_match']);self.assertEqual(row['retrieval_seconds'],0);post.assert_not_called()

if __name__=='__main__':unittest.main()
