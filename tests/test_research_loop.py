"""Main-loop wiring tests use explicit fixtures, never production evidence."""
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import agents
from research_loop import research_round,evidence_guided_default,sponsor_report
from environment import load_environment
class SourceFixture:
    def research(self,origin,round,group):
        return {'status':'cached_exa','origin':origin,'round':round,'group':group,'query':'fixture query','results':[{'title':'Rolling window method','url':'https://example.org/paper','publication_date':'2020-01-01','sentence':'Use rolling window empirical quantiles for nonstationary series.','source':'exa'}],'cache_key':'fixture','executed_live':False,'request':{'endPublishedDate':'2026-07-23T00:00:00Z'}}
class MainLoopTests(unittest.TestCase):
    def test_sources_cross_agents_and_change_bounded_hypothesis(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(agents,'ROOT',Path(tmp)):
            cfg={'cutoff':'2026-11-06','temperature':0,'model':'fixture'}
            r=agents.AgentRuntime(cfg);m=agents.SharedMemory(cfg)
            found=research_round(r,m,SourceFixture(),1,'2026-07-22','neocloud_rate_card')
            read=m.read('ANALYST',1,'2026-07-22',kinds=['evidence'])
            choice,sources=evidence_guided_default('drift',read,['drift','recent_28'])
            self.assertEqual(choice,'recent_28');self.assertEqual(sources,['https://example.org/paper'])
            self.assertEqual(read[0]['agent'],'RESEARCHER')
            r.call('ANALYST',{'allowed_options':['recent_28'],'memory':read},{'choice':choice,'reason':'Source motivates bounded recent-window experiment.'})
            events=[json.loads(x) for x in (Path(tmp)/'logs/agent_log.jsonl').read_text().splitlines()]
            audit=sponsor_report(events,[found]);self.assertEqual(audit['exa']['live_main_loop_calls'],0)
            self.assertFalse(audit['past_dev']['multi_agent_live_access'])
    def test_later_source_rejected_before_agent_or_memory(self):
        fixture=SourceFixture();original=fixture.research
        def bad(*a):
            result=original(*a);result['results'][0]['publication_date']='2026-11-07';return result
        fixture.research=bad
        with self.assertRaises(ValueError):research_round(None,None,fixture,1,'2026-07-22','rate_card')
    def test_direct_notes_cannot_count_as_exa(self):
        fixture=SourceFixture();original=fixture.research
        def bad(*a):
            result=original(*a);result['results'][0]['source']='direct_public_source';return result
        fixture.research=bad
        with self.assertRaises(ValueError):research_round(None,None,fixture,1,'2026-07-22','rate_card')
class EnvironmentTests(unittest.TestCase):
    def test_local_secrets_load_without_shell_execution(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{},clear=True):
            p=Path(tmp)/'.env';p.write_text('OPENAI_API_KEY="fixture-only"\nEXA_API_KEY=$(touch should-never-exist)\nPAST_API_KEY=\n')
            load_environment(p);self.assertEqual(os.environ['OPENAI_API_KEY'],'fixture-only');self.assertEqual(os.environ['EXA_API_KEY'],'$(touch should-never-exist)');self.assertNotIn('PAST_API_KEY',os.environ)
            self.assertFalse(Path('should-never-exist').exists())
    def test_environment_takes_precedence_and_errors_omit_secret(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'OPENAI_API_KEY':'existing'},clear=True):
            p=Path(tmp)/'.env';p.write_text('OPENAI_API_KEY=other\n');load_environment(p);self.assertEqual(os.environ['OPENAI_API_KEY'],'existing')
            p.write_text('HOME=private-fixture-secret')
            with self.assertRaises(ValueError) as ctx:load_environment(p)
            self.assertNotIn('private-fixture-secret',str(ctx.exception))
if __name__=='__main__':unittest.main()
