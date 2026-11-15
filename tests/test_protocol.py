"""Behavioral safeguards for temporal forecasting, strict calls and shared memory.

Run: .venv/bin/python -B -m unittest discover -s tests -v
These checks run without network or modifying the frozen data pack.
"""
import copy
import datetime as dt
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text())
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / CONFIG['pack'] / 'starter'))
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
import pandas as pd
from _common import SeriesStore, h_step_changes, validate_forecast
from methods import quantiles, forecast
import agents


def store_for(days, values):
    return SeriesStore(pd.DataFrame({'series_id': ['synthetic'] * len(days),
                                    'day': days, 'value': values}))


class ForecastProtocolTests(unittest.TestCase):
    def setUp(self):
        self.start = dt.date(2026, 1, 1).toordinal()
        self.days = np.arange(self.start, self.start + 160)
        # Deliberate steps and recent volatility changes exercise all methods.
        values = np.exp(np.arange(160) * 0.001 + np.floor(np.arange(160) / 11) * -.025)
        values[80:] *= np.exp(np.sin(np.arange(80)) * 0.045)
        self.values = values
        self.origin = self.start + 120
        self.store = store_for(self.days, values)

    def test_every_method_ignores_arbitrarily_changed_future(self):
        changed = self.values.copy()
        changed[self.days > self.origin] *= np.exp(np.arange((self.days > self.origin).sum()) + 5)
        future_changed = store_for(self.days, changed)
        truncated = store_for(self.days[self.days <= self.origin], self.values[self.days <= self.origin])
        for spec in CONFIG['candidates']:
            for h in [1, 3, 7]:
                with self.subTest(method=spec['method'], params=spec['parameters'], horizon=h):
                    q = quantiles(self.store, 'synthetic', self.origin, h, spec['method'], spec['parameters'])
                    np.testing.assert_array_equal(q, quantiles(future_changed, 'synthetic', self.origin, h, spec['method'], spec['parameters']))
                    np.testing.assert_array_equal(q, quantiles(truncated, 'synthetic', self.origin, h, spec['method'], spec['parameters']))
                    self.assertTrue(np.isfinite(q).all())
                    self.assertGreater(q[0], 0)
                    self.assertTrue(np.all(q[:-1] <= q[1:]))

    def test_sparse_and_missing_origin_history_is_valid(self):
        days = np.array([self.start, self.start+2, self.start+5])
        store = store_for(days, np.array([1.0, 1.0, 1.2]))
        for spec in CONFIG['candidates']:
            f = forecast(store, ['synthetic'], [self.start+6], [1, 3, 7], spec)
            clean, errors = validate_forecast(f, [1, 3, 7])
            self.assertFalse(errors, (spec, errors))
            self.assertEqual(len(clean), 3)
        self.assertIsNone(quantiles(store, 'synthetic', self.start-1, 1, 'drift', {}))

    def test_rejects_invalid_quantiles_and_wrong_target(self):
        base = {'series_id':'synthetic', 'origin_date':'2026-11-06', 'horizon_days':1,
                'q10':1.0, 'q50':2.0, 'q90':3.0, 'target_date':'2026-11-07'}
        for update in [{'q10':0}, {'q10':2.5}, {'q90':1.5}, {'target_date':'2026-11-09'}, {'horizon_days':2}]:
            with self.subTest(update=update):
                clean, errors = validate_forecast(pd.DataFrame([{**base, **update}]), [1,3,7])
                self.assertEqual(len(clean), 0)
                self.assertTrue(errors)
        clean, errors = validate_forecast(pd.DataFrame([base,base]), [1,3,7])
        self.assertEqual(len(clean), 0)
        self.assertTrue(any('duplicate' in e['reason'] for e in errors))

    def test_archive_gap_never_creates_short_horizon_returns(self):
        a = dt.date(2026,2,27).toordinal()
        b = dt.date(2026,7,1).toordinal()
        days = np.array([a,a+1,b,b+1])
        values = np.array([1.,2.,1000.,2000.])
        np.testing.assert_allclose(h_step_changes(days, values, 1, True), [np.log(2),np.log(2)])
        self.assertEqual(len(h_step_changes(days, values, 3, True)),0)
        self.assertEqual(len(h_step_changes(days, values, 7, True)),0)


class AgentAndMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root_patch = patch.object(agents, 'ROOT', pathlib.Path(self.temp.name))
        self.root_patch.start()
        self.config = {'cutoff':'2026-11-06','model':'gpt-4.1-mini','temperature':0}

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def test_strict_bounded_choices_cache_and_roles(self):
        runtime = agents.AgentRuntime(self.config)
        for role in agents.ROLES:
            request = {'allowed_options':['drift'], 'history_cutoff':'2026-07-15'}
            expected = {'choice':'drift', 'reason':'No accepted alternative'}
            self.assertEqual(runtime.call(role, request, expected), expected)
            self.assertEqual(runtime.call(role, request, {'choice':'bad', 'reason':'not used'}),expected)
        self.assertEqual(runtime.modes, {'deterministic_policy'})
        self.assertEqual(len(runtime.cache), 4)
        for record in runtime.cache.values():
            self.assertEqual(record['request']['temperature'],0)
            self.assertFalse(record['request']['schema']['additionalProperties'])
        with self.assertRaises(ValueError):
            runtime.call('UNKNOWN', {}, {'choice':'drift','reason':'bad role'})
        with self.assertRaises(ValueError):
            runtime.call('ANALYST', {'allowed_options':['drift'],'new':True}, {'choice':'execute arbitrary code','reason':'invalid'})
        with self.assertRaises(ValueError):
            runtime.call('ANALYST', {'different':True}, {'choice':'drift','reason':'bad schema','extra':1})

    def test_mutating_caller_input_cannot_corrupt_persisted_cache(self):
        runtime = agents.AgentRuntime(self.config)
        pending = {'candidate':'drift', 'details':{'window':28}, 'origins':['2026-07-15']}
        inputs = {'allowed_options':['accept','reject'], 'hypothesis':pending}
        original = copy.deepcopy(inputs)
        expected = {'choice':'reject','reason':'Insufficient later origins'}
        runtime.call('CRITIC', inputs, expected)
        pending['closed'] = True
        pending['details']['window'] = 99
        pending['origins'].append('2026-07-22')
        inputs['allowed_options'].append('arbitrary')
        # A later save used to serialize the now-mutated request under its OLD hash.
        runtime.call('ANALYST', {'allowed_options':['drift']}, {'choice':'drift','reason':'Other call triggers save'})
        persisted = json.loads(runtime.path.read_text())
        for key,record in persisted.items():
            self.assertEqual(agents.digest(record['request']),key)
        replay = agents.AgentRuntime(self.config)
        self.assertEqual(replay.call('CRITIC', original, {'choice':'accept','reason':'Must not run'}),expected)

    def test_mutating_written_memory_content_cannot_change_history(self):
        memory = agents.SharedMemory(self.config)
        pending = {'candidate':'drift', 'details':{'window':28}}
        entry = memory.write('ANALYST',1,'2026-07-15','hypothesis',pending)
        pending['closed'] = True
        pending['details']['window'] = 99
        memory.write('CRITIC',2,'2026-07-22','verdict',{'accepted':False})
        self.assertEqual(memory.read('FORECASTER',1,'2026-07-15'),[entry])
        persisted = json.loads(memory.path.read_text())
        self.assertEqual(persisted[0],entry)

    def test_two_writers_two_readers_and_future_exclusion(self):
        memory = agents.SharedMemory(self.config)
        memory.reset_run()
        analyst = memory.write('ANALYST',1,'2026-07-15','hypothesis',{'method':'drift'})
        critic = memory.write('CRITIC',2,'2026-07-22','verdict',{'accept':False})
        future = memory.write('RESEARCHER',3,'2026-07-29','evidence',{'fact':'must not appear early'})
        self.assertEqual(memory.read('FORECASTER',1,'2026-07-15'),[analyst])
        self.assertEqual(memory.read('ANALYST',2,'2026-07-22',kinds=['verdict']),[critic])
        self.assertNotIn(future,memory.read('FORECASTER',2,'2026-07-22'))
        self.assertNotIn(future,memory.read('FORECASTER',2,'2026-11-06'))
        self.assertNotIn(future,memory.read('FORECASTER',14,'2026-07-22'))
        with self.assertRaises(ValueError):
            memory.write('RESEARCHER',15,'2026-11-07','evidence',{})
        log = [json.loads(s) for s in (agents.ROOT/'logs/agent_log.jsonl').read_text().splitlines()]
        writers = {r['who'] for r in log if r['what']=='memory_write'}
        readers = {r['who'] for r in log if r['what']=='memory_read'}
        self.assertGreaterEqual(len(writers),2)
        self.assertGreaterEqual(len(readers),2)

    def test_remote_recall_never_admits_future_or_untrusted_summary(self):
        memory = agents.SharedMemory(self.config)
        past = memory.write('ANALYST',1,'2026-07-15','hypothesis',{'method':'drift'})
        future = memory.write('CRITIC',3,'2026-07-29','verdict',{'accept':True})
        memory.remote_ready = True
        response = {'results':[{'content':'untrusted future market price', 'sources':[
            {'sourceId':past['id']},{'sourceId':future['id']},{'sourceId':'foreign-project'}]}]}
        with patch.object(memory,'_request',return_value=response):
            result = memory.read('FORECASTER',1,'2026-07-15')
        self.assertEqual(result,[past])
        self.assertNotIn('untrusted',json.dumps(result))
        memory.remote_ready = False
        self.assertEqual(memory.read('FORECASTER',1,'2026-07-15'),[past])


class RecordedArtifactAuditTests(unittest.TestCase):
    @unittest.skipUnless((ROOT/'results/replay_audit.json').exists(), 'Run pipeline before artifact audit')
    def test_recorded_chronology_and_memory_boundaries(self):
        audit = json.loads((ROOT/'results/replay_audit.json').read_text())
        self.assertEqual(len(audit), len(CONFIG['origins'])-1)
        self.assertEqual([r['forecast_origin'] for r in audit], CONFIG['origins'][1:])
        for row in audit:
            self.assertTrue(all(o < row['forecast_origin'] for o in row['training_origins']))
            self.assertLessEqual(row['max_available_target_date'], row['forecast_origin'])
        hypotheses = json.loads((ROOT/'results/hypotheses.json').read_text())
        for h in hypotheses:
            if h['verdict'] != 'pending':
                self.assertGreaterEqual(h['n_origins'], CONFIG['min_critic_origins'])
                self.assertTrue(all(h['frozen_at'] <= o < h['evaluated_at'] for o in h['validation_origins']))
        log = [json.loads(s) for s in (ROOT/'logs/agent_log.jsonl').read_text().splitlines()]
        self.assertGreaterEqual(len({r['who'] for r in log if r['what']=='memory_write'}),2)
        self.assertGreaterEqual(len({r['who'] for r in log if r['what']=='memory_read'}),2)
        for event in log:
            if event['what']=='memory_read':
                for entry in event['outcome']['entries']:
                    self.assertLessEqual(entry['origin'],event['inputs']['origin'])
                    self.assertLessEqual(entry['round'],event['inputs']['round'])

    @unittest.skipUnless((ROOT/'forecasts.csv').exists(), 'Run pipeline before artifact audit')
    def test_submission_matches_actual_declared_posted_targets(self):
        targets = pd.read_csv(ROOT/'data/targets.csv')
        f = pd.read_csv(ROOT/'forecasts.csv')
        self.assertTrue((targets['table']=='daily_statistics').all())
        self.assertTrue((targets['tier']=='headline').all())
        self.assertTrue(targets.benchmark_contract.notna().all())
        self.assertTrue(targets.instrument_class.notna().all())
        self.assertEqual(set(f.series_id),set(targets.series_id))
        self.assertEqual(len(f),len(targets)*len(CONFIG['horizons']))
        self.assertEqual(set(f.origin_date),{CONFIG['cutoff']})
        self.assertEqual(set(f.horizon_days),set(CONFIG['horizons']))
        self.assertTrue(np.isfinite(f[['q10','q50','q90']].to_numpy()).all())
        clean, errors = validate_forecast(f,CONFIG['horizons'])
        self.assertFalse(errors)
        self.assertEqual(len(clean),len(f))
        self.assertTrue((pd.to_datetime(f.target_date)==pd.to_datetime(f.origin_date)+pd.to_timedelta(f.horizon_days,unit='D')).all())
        self.assertIn('REFUSED',(ROOT/'logs/refusal.log').read_text())
        self.assertFalse((ROOT/'results/contaminated_history_test_only.csv').exists())


if __name__ == '__main__':
    unittest.main()
