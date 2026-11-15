"""Offline behavioral contracts for the optional Modal integration."""
import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gpu_modal_jobs', ROOT / 'src/modal_jobs.py')
jobs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jobs)


def sample():
    start = dt.date(2026, 1, 1)
    return {
        'history': [{'series_id': 'collector.neocloud_rate_card.H100.on_demand.median',
                     'date': (start + dt.timedelta(days=i)).isoformat(),
                     'value': round(3 + .01 * i + .02 * (i % 4), 6)} for i in range(45)],
        'series_ids': ['collector.neocloud_rate_card.H100.on_demand.median'],
        'origins': ['2026-01-30'], 'horizons': [1, 3, 7], 'cutoff': '2026-11-06',
        'spec': {'id': 'drift', 'method': 'drift', 'parameters': {}},
    }


class PayloadContract(unittest.TestCase):
    def test_accepts_valid_bounded_payload(self):
        self.assertEqual(jobs.validate_payload(sample())['spec']['method'], 'drift')

    def test_future_history_refused(self):
        payload = sample()
        payload['history'][0]['date'] = '2026-11-07'
        with self.assertRaisesRegex(ValueError, 'after cutoff'):
            jobs.validate_payload(payload)

    def test_arbitrary_code_and_unknown_parameters_refused(self):
        for change in ({'method': '__import__("os").system("id")'},
                       {'parameters': {'code': 'print(1)'}},
                       {'parameters': {'min_samples': '__import__("os")'}},
                       {'parameters': {'min_samples': -1}}):
            payload = sample(); payload['spec'].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                jobs.validate_payload(payload)

    def test_bad_origins_and_archive_targets_refused(self):
        for origins in (['2026-11-07'], ['2026-01-30', '2026-01-30'], ['2026-01-30', '2026-01-20']):
            payload = sample(); payload['origins'] = origins
            with self.subTest(origins=origins), self.assertRaises(ValueError):
                jobs.validate_payload(payload)
        payload = sample(); payload['series_ids'] = ['aws_spot.p5.az_median']
        with self.assertRaisesRegex(ValueError, 'posted-rental'):
            jobs.validate_payload(payload)

    def test_duplicates_and_nonfinite_refused(self):
        payload = sample(); payload['history'].append(payload['history'][0].copy())
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            jobs.validate_payload(payload)
        for value in (float('inf'), float('nan'), 0, -1, True):
            payload = sample(); payload['history'][0]['value'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                jobs.validate_payload(payload)

    def test_real_scorer_and_future_invariance(self):
        payload = sample()
        result = jobs.run_experiment(payload)
        self.assertEqual(len(result['forecasts']), 3)
        self.assertEqual(result['reports']['drift']['overall']['skill_pooled'], 0)
        self.assertEqual(result['reports']['last_value']['mode'], 'backtest')
        self.assertEqual(result['reports']['last_value']['overall']['n_cells'], 3)
        changed = copy.deepcopy(payload)
        for row in changed['history']:
            if row['date'] > changed['origins'][0]:
                row['value'] *= 100
        other = jobs.run_experiment(changed)
        self.assertEqual(result['forecasts_csv'], other['forecasts_csv'])
        self.assertNotEqual(result['reports']['last_value']['overall']['pinball'],
                            other['reports']['last_value']['overall']['pinball'])

    def test_missing_sdk_fallback_is_explicit(self):
        with patch.object(jobs, "modal", None):
            results, execution = jobs.execute_jobs([sample()], backend="modal")
            self.assertEqual(execution["actual_backend"], "local_fallback")
            self.assertEqual(execution["fallback_reason"], "RuntimeError")
            self.assertEqual(len(results), 1)
            with self.assertRaisesRegex(RuntimeError, "not installed"):
                jobs.execute_jobs([sample()], backend="modal", local_fallback=False)

    def test_checked_in_eight_job_contract(self):
        payloads = jobs.build_payloads(ROOT)
        self.assertEqual(len(payloads), 8)
        self.assertTrue(all(p['history'] for p in payloads))
        self.assertTrue(all(set(r) == {'series_id', 'date', 'value'}
                            for p in payloads for r in p['history']))

    @unittest.skipUnless(importlib.util.find_spec('fastapi') and importlib.util.find_spec('httpx'),
                         'Optional FastAPI/httpx not installed')
    def test_static_allowlist_blocks_secrets_and_writes(self):
        from fastapi.testclient import TestClient
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'index.html').write_text('<h1>GPU Value Scientist</h1>')
            Path(directory, '.env').write_text('NOT_PUBLIC')
            Path(directory, 'data.json').write_text('{"recorded":true}')
            client = TestClient(jobs.public_demo_app(directory))
            self.assertEqual(client.get('/').status_code, 200)
            self.assertEqual(client.get('/data.json').json(), {'recorded': True})
            self.assertEqual(client.get('/.env').status_code, 404)
            self.assertNotIn('.env', jobs.PUBLIC_FILES)
            self.assertEqual(client.get('/%2eenv').status_code, 404)
            self.assertEqual(client.get('/src/environment.py').status_code, 404)
            self.assertEqual(client.get('/src/modal_jobs.py').status_code, 404)
            self.assertEqual(client.post('/data.json', json={}).status_code, 404)


if __name__ == '__main__':
    unittest.main()
