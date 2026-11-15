"""Credential-free contract tests; these are NOT evidence of live sponsor use."""
import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import agents

UUID = '11111111-2222-4333-8444-555555555555'


def response(data=None, status=200):
    return SimpleNamespace(ok=200 <= status < 300, status_code=status, json=lambda: copy.deepcopy(data))


class PastContract:
    """Tiny test double matching fields in past.dev/openapi.json, not a service."""
    def __init__(self):
        self.calls=[]
        self.sources={}
        self.ingest_status='queued'
        self.poll_status='completed'
        self.recall_status=200
        self.audience_status=201
        self.override_receipt=None
        self.extra_sources=[]

    def __call__(self, method,url,headers,json=None,timeout=None):
        self.calls.append((method,url,copy.deepcopy(json)))
        assert headers['Authorization']=='Bearer test-only-past-key'
        assert timeout > 0
        path=url.removeprefix('https://api.past.dev/api/v1')
        if method=='PUT' and path.startswith('/audiences/'):
            assert set(json)=={'kind','name','identities'}
            assert json['kind']=='fixed' and len(json['identities'])==4
            return response({'slug':path.rsplit('/',1)[1]},self.audience_status)
        if method=='POST' and path=='/ingest':
            assert set(json)<= {'content','label','id','timestamp','metadata','audience','identity','idempotencyKey'}
            assert json['audience'].startswith('gvs-')
            assert json['identity'].startswith(json['audience'])
            entry=__import__('json').loads(json['content'])
            assert entry['id']==json['id']
            self.sources[json['id']]={'sourceId':json['id'],'occurredAt':json['timestamp'],'excerpts':[]}
            receipt={'projectId':1,'ingestionId':UUID,'sourceId':json['id'],'status':self.ingest_status}
            receipt.update(self.override_receipt or {})
            return response(receipt,202 if self.ingest_status=='queued' else 200)
        if method=='GET' and path=='/ingest/'+UUID:
            return response({'status':self.poll_status,'settled':True,'blocked':False,
                             'readiness':{'raw':1,'comprehension':1,'consolidation':1,'failed':0},
                             'sources':{'current':1,'deleted':0,'superseded':0}})
        if method=='POST' and path=='/recall':
            assert set(json)<= {'query','identity','queryTimestamp','occurredTo','limit','level','occurredFrom','sort','maxTokens'}
            assert json['queryTimestamp']==json['occurredTo']
            assert json['limit']==200
            return response({'asOf':json['queryTimestamp'],'usedEvidenceTokens':10,
                             'results':[{'id':UUID,'rank':1,'occurredAt':json['queryTimestamp'],
                                         'content':'UNTRUSTED GENERATED TEXT',
                                         'artifact':{'id':UUID,'kind':'claim','occurredAt':json['queryTimestamp']},
                                         'sources':list(self.sources.values())+self.extra_sources}]},self.recall_status)
        raise AssertionError((method,path))


class IntegrationContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.patch_root=patch.object(agents,'ROOT',pathlib.Path(self.temp.name));self.patch_root.start()
        self.env=patch.dict('os.environ',{'PAST_API_KEY':'test-only-past-key','OPENAI_API_KEY':'test-only-openai-key'});self.env.start()
        self.config={'cutoff':'2026-11-06','model':'gpt-4.1-mini','temperature':0}
        self.api=PastContract()
        self.http=patch('requests.request',side_effect=self.api);self.mock_http=self.http.start()
        self.sleep=patch.object(agents.time,'sleep');self.sleep.start()

    def tearDown(self):
        self.sleep.stop();self.http.stop();self.env.stop();self.patch_root.stop();self.temp.cleanup()

    def events(self):
        return [json.loads(s) for s in (agents.ROOT/'logs/agent_log.jsonl').read_text().splitlines()]

    def test_audience_ingestion_poll_recall_and_two_agent_contract(self):
        m=agents.SharedMemory(self.config,live=True)
        a=m.write('ANALYST',1,'2026-07-15','hypothesis',{'method':'drift'})
        c=m.write('CRITIC',2,'2026-07-22','verdict',{'accepted':False})
        self.assertEqual(m.read('FORECASTER',2,'2026-07-22'),[a,c])
        self.assertEqual(m.read('ANALYST',2,'2026-07-22',kinds=['verdict']),[c])
        self.assertEqual(m.backend,'past.dev')
        audit=agents.sponsor_audit(self.events())
        self.assertTrue(audit['multi_agent_live_access']) # Synthetic test log only.
        self.assertFalse(audit['performance_gains_verified'])
        self.assertEqual(audit['live_writers'],['ANALYST','CRITIC'])
        self.assertEqual(audit['live_readers'],['ANALYST','FORECASTER'])
        self.assertEqual(sum(method=='GET' for method,_,_ in self.api.calls),2)
        self.assertNotIn('UNTRUSTED',json.dumps(m.read('FORECASTER',2,'2026-07-22')))

    def test_completed_unchanged_receipt_needs_no_poll(self):
        self.api.ingest_status='completed'
        m=agents.SharedMemory(self.config,live=True)
        m.write('ANALYST',1,'2026-07-15','hypothesis',{})
        self.assertFalse(any(method=='GET' for method,_,_ in self.api.calls))
        self.assertEqual(m.backend,'past.dev')

    def test_bad_receipt_or_failed_ingestion_stays_local(self):
        for override in [{'ingestionId':'00000000-0000-0000-0000-000000000000'},
                         {'ingestionId':'bad'}, {'sourceId':'someone-elses-source'}, {'status':'unknown'}]:
            with self.subTest(override=override):
                self.api.override_receipt=override
                m=agents.SharedMemory(self.config,live=True)
                e=m.write('ANALYST',1,'2026-07-15','hypothesis',override)
                self.assertEqual(m.backend,'local_json')
                self.assertNotIn(e['id'],m.remote_ids)
        self.api.override_receipt=None;self.api.poll_status='failed'
        m=agents.SharedMemory(self.config,live=True)
        m.write('CRITIC',1,'2026-07-15','verdict',{})
        self.assertEqual(m.backend,'local_json')

    def test_incomplete_ingestion_has_bounded_wait_and_no_remote_success(self):
        m=agents.SharedMemory(self.config,live=True)
        with patch.object(agents.time,'monotonic',side_effect=[0,31]):
            m.write('ANALYST',1,'2026-07-15','hypothesis',{})
        self.assertEqual(m.backend,'local_json')
        self.assertFalse(m.remote_ids)
        self.assertTrue(any('TimeoutError' in w for w in m.warnings))

    def test_http_failure_and_recall_failure_label_mixed_backend(self):
        self.api.audience_status=403
        m=agents.SharedMemory(self.config,live=True)
        self.assertFalse(m.remote_ready)
        self.assertEqual(m.backend,'local_json')
        self.api.audience_status=201
        m=agents.SharedMemory(self.config,live=True)
        a=m.write('ANALYST',1,'2026-07-15','hypothesis',{})
        self.api.recall_status=503
        self.assertEqual(m.read('FORECASTER',1,'2026-07-15'),[a])
        self.assertEqual(m.backend,'past.dev+local_json_fallback')
        last=self.events()[-1]
        self.assertEqual(last['current_backend'],'local_json')
        self.assertTrue(last['network_call'])
        self.assertFalse(agents.sponsor_audit(self.events())['multi_agent_live_access'])

    def test_offline_recorded_recall_has_no_live_backend_or_network(self):
        live=agents.SharedMemory(self.config,live=True)
        a=live.write('ANALYST',1,'2026-07-15','hypothesis',{})
        expected=live.read('FORECASTER',1,'2026-07-15')
        self.mock_http.reset_mock()
        offline=agents.SharedMemory(self.config,live=False)
        self.assertEqual(offline.read('FORECASTER',1,'2026-07-15'),expected)
        self.mock_http.assert_not_called()
        self.assertEqual(offline.backend,'local_json')
        self.assertEqual(offline.recorded_backend,'past.dev')
        event=self.events()[-1]
        self.assertEqual(event['mode'],'past.dev_recorded')
        self.assertEqual(event['recorded_backend'],'past.dev')
        self.assertFalse(event['network_call'])
        self.assertFalse(agents.sponsor_audit([event])['multi_agent_live_access'])

    def test_failed_live_recall_overwrites_old_success_for_exact_replay(self):
        m=agents.SharedMemory(self.config,live=True)
        a=m.write('ANALYST',1,'2026-07-15','hypothesis',{})
        b=m.write('CRITIC',1,'2026-07-15','verdict',{})
        del self.api.sources[b['id']]
        self.assertEqual(m.read('FORECASTER',1,'2026-07-15'),[a])
        self.api.recall_status=503
        expected=m.read('FORECASTER',1,'2026-07-15')
        self.assertEqual(expected,[a,b])
        offline=agents.SharedMemory(self.config)
        self.assertEqual(offline.read('FORECASTER',1,'2026-07-15'),expected)
        self.assertEqual(self.events()[-1]['recorded_backend'],'local_json')

    def test_setup_failure_replaces_old_recorded_remote_selection(self):
        m=agents.SharedMemory(self.config,live=True)
        a=m.write('ANALYST',1,'2026-07-15','hypothesis',{})
        b=m.write('CRITIC',1,'2026-07-15','verdict',{})
        del self.api.sources[b['id']]
        self.assertEqual(m.read('FORECASTER',1,'2026-07-15'),[a])
        self.api.audience_status=403
        failed=agents.SharedMemory(self.config,live=True)
        expected=failed.read('FORECASTER',1,'2026-07-15')
        self.assertEqual(expected,[a,b])
        offline=agents.SharedMemory(self.config)
        self.assertEqual(offline.read('FORECASTER',1,'2026-07-15'),expected)
        self.assertEqual(self.events()[-1]['recorded_backend'],'local_json')

    def test_canonical_source_allowlist_excludes_foreign_future_and_artifact_ids(self):
        m=agents.SharedMemory(self.config,live=True)
        a=m.write('ANALYST',1,'2026-07-15','hypothesis',{})
        future=m.write('CRITIC',3,'2026-07-29','verdict',{})
        self.api.extra_sources=[{'sourceId':'foreign','occurredAt':'2026-07-01T00:00:00Z','excerpts':[]}]
        self.assertEqual(m.read('FORECASTER',1,'2026-07-15'),[a])
        self.assertNotIn(future,m.read('FORECASTER',1,'2026-07-15'))
        ids=m._source_ids({'results':[{'id':a['id'],'artifact':{'id':a['id']},'sources':[]}]},'2026-07-15')
        self.assertEqual(ids,set())
        for bad_date in ['2026-11-07T00:00:00Z','not-a-date','2026-07-15T00:00:00']:
            self.assertEqual(m._source_ids({'results':[{'sources':[{'sourceId':a['id'],'occurredAt':bad_date}]}]},'2026-07-15'),set())

    def test_openai_strict_contract_and_recorded_mode(self):
        answer={'choice':'drift','reason':'No accepted alternative'}
        with patch('requests.post',return_value=response({'choices':[{'message':{'content':json.dumps(answer)}}]})) as post:
            runtime=agents.AgentRuntime(self.config,live=True)
            expected=runtime.call('FORECASTER',{'allowed_options':['drift']},answer)
            payload=post.call_args.kwargs['json']
            self.assertEqual(payload['temperature'],0)
            self.assertTrue(payload['response_format']['json_schema']['strict'])
            self.assertFalse(payload['response_format']['json_schema']['schema']['additionalProperties'])
            post.reset_mock()
            offline=agents.AgentRuntime(self.config)
            self.assertEqual(offline.call('FORECASTER',{'allowed_options':['drift']},{'choice':'drift','reason':'unused'}),expected)
            post.assert_not_called()
            self.assertEqual(offline.modes,{'openai_recorded'})
            self.assertEqual(self.events()[-1]['recorded_mode'],'openai_live')

    def test_complete_live_agent_memory_run_replays_exactly_without_network(self):
        """All four roles consume actual retrieved canonical records, then replay."""
        evidence = {'source':'exa_sources', 'sources':[{'url':'https://example.org/dated',
                    'publication_date':'2026-07-01', 'sentence':'A cited historical fact.'}]}

        def openai_answer(url, headers, json, timeout):
            request = __import__('json').loads(json['messages'][1]['content'])
            choice = request['allowed_options'][-1]
            result = {'choice':choice, 'reason':'Recorded model choice using supplied chronological sources.'}
            return response({'choices':[{'message':{'content':__import__('json').dumps(result)}}]})

        def experiment(live):
            runtime = agents.AgentRuntime(self.config,live=live)
            memory = agents.SharedMemory(self.config,live=live)
            memory.reset_run()
            researcher = runtime.call('RESEARCHER', {'allowed_options':['history_only'], 'evidence':evidence},
                                      {'choice':'history_only','reason':'OFFLINE MISS MUST FAIL THIS TEST'})
            memory.write('RESEARCHER',1,'2026-07-15','evidence',{'evidence':evidence,'note':researcher})
            known = memory.read('ANALYST',1,'2026-07-15',kinds=['evidence'])
            analyst = runtime.call('ANALYST', {'allowed_options':['drift','recent'], 'memory':known},
                                   {'choice':'drift','reason':'OFFLINE MISS MUST FAIL THIS TEST'})
            hypothesis = memory.write('ANALYST',1,'2026-07-15','hypothesis',analyst)
            critic = runtime.call('CRITIC', {'allowed_options':['reject','accept'], 'hypothesis':hypothesis,
                                            'statistical_gate':'accept'},
                                  {'choice':'reject','reason':'OFFLINE MISS MUST FAIL THIS TEST'})
            memory.write('CRITIC',2,'2026-07-22','verdict',critic)
            # A real retrieval need not return all eligible records. Replay must
            # preserve precisely this remote selection, not return all local data.
            if live:
                del self.api.sources[hypothesis['id']]
            recalled = memory.read('FORECASTER',2,'2026-07-22',kinds=['hypothesis','verdict'])
            self.assertEqual([r['kind'] for r in recalled],['verdict'])
            forecaster = runtime.call('FORECASTER', {'allowed_options':['drift','recent'], 'memory':recalled},
                                      {'choice':'drift','reason':'OFFLINE MISS MUST FAIL THIS TEST'})
            return [researcher,analyst,critic,forecaster], runtime, memory

        with patch('requests.post',side_effect=openai_answer) as post:
            live_decisions,live_runtime,live_memory = experiment(True)
            self.assertEqual(post.call_count,4)
            self.assertEqual(live_runtime.modes,{'openai_live'})
            live_keys = [e['cache_key'] for e in self.events() if e['what']=='decision']
            live_archive = live_memory.path.read_bytes()
            live_cache = live_runtime.path.read_bytes()
            (agents.ROOT/'logs/agent_log.jsonl').write_text('')
            post.reset_mock();self.mock_http.reset_mock()
            recorded_decisions,recorded_runtime,recorded_memory = experiment(False)
            self.assertEqual(recorded_decisions,live_decisions)
            self.assertEqual(recorded_runtime.modes,{'openai_recorded'})
            self.assertEqual(recorded_memory.backend,'local_json')
            self.assertEqual(recorded_memory.recorded_backend,'past.dev')
            self.assertEqual(recorded_memory.path.read_bytes(),live_archive)
            self.assertEqual(recorded_runtime.path.read_bytes(),live_cache)
            self.assertEqual([e['cache_key'] for e in self.events() if e['what']=='decision'],live_keys)
            post.assert_not_called();self.mock_http.assert_not_called()
            self.assertFalse(agents.sponsor_audit(self.events())['multi_agent_live_access'])

    def test_openai_error_never_turns_into_fake_success(self):
        with patch('requests.post',return_value=response({},status=429)):
            runtime=agents.AgentRuntime(self.config,live=True)
            with self.assertRaises(RuntimeError):
                runtime.call('ANALYST',{'allowed_options':['drift']},{'choice':'drift','reason':'fallback'})
            self.assertFalse(runtime.cache)
            self.assertEqual(self.events()[-1]['mode'],'openai_error')


if __name__=='__main__':
    unittest.main()
