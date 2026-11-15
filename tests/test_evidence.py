"""Synthetic API fixtures only: these are not collected research evidence.

Tests write caches only inside temporary directories and never call Exa.
"""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import evidence


# Deliberately fabricated fixture content, never saved in project evidence files.
FIXTURE = {'title': 'SYNTHETIC TEST FIXTURE: quantile methodology',
           'url': 'https://example.org/synthetic-test-fixture',
           'publishedDate': '2026-07-15T23:59:59Z',
           'highlights': ['SYNTHETIC TEST FIXTURE, not a real research finding.']}


def response(rows):
    result = Mock()
    result.json.return_value = {'requestId': 'synthetic-request-id', 'results': rows}
    return result


class LoopEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = {'cutoff': '2026-11-06', 'loop_evidence_cache': str(self.root / 'loop-cache.json')}

    def test_live_request_origin_end_filter_and_main_loop_schema(self):
        with patch.dict(os.environ, {'EXA_API_KEY': 'synthetic-test-key'}), patch('requests.post', return_value=response([FIXTURE])) as post:
            out = evidence.LoopResearcher(self.config, live=True).research('2026-07-15', 1, 'neocloud_rate_card')
        post.assert_called_once()
        request = post.call_args.kwargs['json']
        self.assertEqual(request['endPublishedDate'], '2026-07-16T00:00:00Z')
        self.assertIn('neocloud_rate_card', request['query'])
        self.assertIn('endPublishedDate', request)
        self.assertEqual(out['status'], 'live_exa')
        self.assertTrue(out['executed_live'])
        self.assertEqual(out['origin'], '2026-07-15')
        self.assertEqual(out['round'], 1)
        self.assertEqual(out['group'], 'neocloud_rate_card')
        self.assertEqual(len(out['cache_key']), 64)
        self.assertEqual(out['results'][0]['source'], 'exa')
        self.assertTrue(out['results'][0]['evidence_id'])
        self.assertIn('sentence', out['results'][0])
        self.assertEqual(out['results'][0]['publication_date'], '2026-07-15')
        self.assertTrue(Path(self.config['loop_evidence_cache']).exists())

    def test_per_origin_filter_rejects_later_undated_and_restricted(self):
        variants = [dict(FIXTURE, publishedDate='2026-07-16T00:00:00Z'),
                    dict(FIXTURE, publishedDate=None),
                    dict(FIXTURE, url='https://www.vast.ai/synthetic-test-fixture'),
                    dict(FIXTURE, highlights=[])]
        with patch.dict(os.environ, {'EXA_API_KEY': 'synthetic-test-key'}), patch('requests.post', return_value=response([FIXTURE] + variants)):
            out = evidence.LoopResearcher(self.config, True).research('2026-07-15', 2, 'hyperscaler_spot')
        self.assertEqual(len(out['results']), 1)
        self.assertEqual(len(out['rejected']), 4)
        reasons = ' '.join(row['reason'] for row in out['rejected'])
        self.assertIn('publication after cutoff', reasons)
        self.assertIn('missing or invalid publication date', reasons)
        self.assertIn('restricted source', reasons)
        self.assertIn('no cited excerpt', reasons)
        text = Path(self.config['loop_evidence_cache']).read_text()
        # Blocked result body is not stored; only its URL and rejection reason.
        cached = json.loads(text)[out['cache_key']]
        self.assertEqual(len(cached['results']), 1)
        self.assertTrue(all('sentence' not in row for row in cached['rejected']))

    def test_offline_cache_replay_makes_zero_network_calls(self):
        with patch.dict(os.environ, {'EXA_API_KEY': 'synthetic-test-key'}), patch('requests.post', return_value=response([FIXTURE])):
            original = evidence.LoopResearcher(self.config, True).research('2026-07-15', 1, 'neocloud_rate_card')
        before = Path(self.config['loop_evidence_cache']).read_bytes()
        with patch('requests.post', side_effect=AssertionError('offline tried network')) as post:
            replay = evidence.LoopResearcher(self.config).research('2026-07-15', 1, 'neocloud_rate_card')
        post.assert_not_called()
        self.assertEqual(replay['status'], 'cached_exa')
        self.assertFalse(replay['executed_live'])
        self.assertEqual(replay['results'], original['results'])
        self.assertEqual(before, Path(self.config['loop_evidence_cache']).read_bytes())

    def test_offline_miss_and_missing_key_do_not_substitute_direct_sources(self):
        with patch.dict(os.environ, {}, clear=True), patch('requests.post', side_effect=AssertionError('unexpected network')) as post:
            offline = evidence.LoopResearcher(self.config).research('2026-07-15', 1, 'neocloud_rate_card')
            live = evidence.LoopResearcher(self.config, True).research('2026-07-15', 1, 'neocloud_rate_card')
        post.assert_not_called()
        self.assertEqual(offline['status'], 'unavailable_cache_miss')
        self.assertEqual(live['status'], 'blocked_missing_exa_key')
        for out in [offline, live]:
            self.assertEqual(out['results'], [])
            self.assertFalse(out['executed_live'])
        self.assertFalse(Path(self.config['loop_evidence_cache']).exists())

    def test_empty_qualifying_result_is_never_complete_live_or_cached(self):
        late = dict(FIXTURE, publishedDate='2026-07-16')
        with patch.dict(os.environ, {'EXA_API_KEY': 'synthetic-test-key'}), patch('requests.post', return_value=response([late])):
            out = evidence.LoopResearcher(self.config, True).research('2026-07-15', 1, 'neocloud_rate_card')
        self.assertEqual(out['status'], 'no_qualifying_evidence')
        self.assertEqual(out['results'], [])
        replay = evidence.LoopResearcher(self.config).research('2026-07-15', 1, 'neocloud_rate_card')
        self.assertEqual(replay['status'], 'no_qualifying_evidence')
        self.assertFalse(replay['executed_live'])

    def test_distinct_origins_rounds_and_groups_have_distinct_cache_keys(self):
        worker = evidence.LoopResearcher(self.config)
        keys = {worker.research(origin, round, group)['cache_key'] for origin, round, group in
                [('2026-07-15', 1, 'neocloud_rate_card'), ('2026-07-22', 1, 'neocloud_rate_card'),
                 ('2026-07-15', 2, 'neocloud_rate_card'), ('2026-07-15', 1, 'hyperscaler_spot')]}
        self.assertEqual(len(keys), 4)

    def test_cache_rejects_forged_provenance_and_later_evidence(self):
        worker = evidence.LoopResearcher(self.config)
        missed = worker.research('2026-07-15', 1, 'neocloud_rate_card')
        path = Path(self.config['loop_evidence_cache'])
        path.write_text(json.dumps({missed['cache_key']: {'source': 'direct_public_source', 'results': evidence.DIRECT}}))
        out = worker.research('2026-07-15', 1, 'neocloud_rate_card')
        self.assertEqual(out['status'], 'unavailable_invalid_cache')
        self.assertEqual(out['results'], [])

    def test_origin_and_timezone_boundaries(self):
        self.assertIsNone(evidence.safe_result(dict(FIXTURE, publishedDate='2026-07-15T23:30:00-02:00'), '2026-07-15')[0])
        self.assertIsNotNone(evidence.safe_result(dict(FIXTURE, publishedDate='2026-07-16T01:00:00+02:00'), '2026-07-15')[0])
        self.assertEqual(evidence.safe_result(dict(FIXTURE, publishedDate='2026-07-16T01:00:00+02:00'), '2026-07-15')[0]['publication_date'], '2026-07-15')
        worker = evidence.LoopResearcher(self.config)
        for origin, round, group in [('2026-11-07',1,'rate_card'), ('bad-date',1,'rate_card'), ('2026-07-15',0,'rate_card'), ('2026-07-15',1,'')]:
            with self.assertRaises(ValueError): worker.research(origin, round, group)

    def test_failed_live_request_is_visible_and_not_cached(self):
        with patch.dict(os.environ, {'EXA_API_KEY': 'synthetic-test-key'}), patch('requests.post', side_effect=TimeoutError('synthetic timeout')):
            out = evidence.LoopResearcher(self.config, True).research('2026-07-15', 1, 'neocloud_rate_card')
        self.assertEqual(out['status'], 'exa_request_failed')
        self.assertTrue(out['executed_live'])
        self.assertEqual(out['results'], [])
        self.assertFalse(Path(self.config['loop_evidence_cache']).exists())

    def test_long_term_collection_does_not_report_success_for_empty_results(self):
        with patch.object(evidence, 'ROOT', self.root), patch.dict(os.environ, {'EXA_API_KEY': 'synthetic-test-key'}), patch('requests.post', return_value=response([])):
            (self.root / 'data').mkdir()
            out = evidence.collect(live=True)
        self.assertEqual(out['status'], 'exa_no_qualifying_results')
        self.assertFalse(any(row['source'] == 'exa' for row in out['results']))


if __name__ == '__main__':
    unittest.main()
