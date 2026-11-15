"""Dated evidence collection. Offline is the default; Exa requires --live and a key.
Long-term evidence is narrative context. LoopResearcher provides origin-filtered
Exa evidence for bounded research decisions; it never supplies target prices.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from environment import load_environment
load_environment()
ROOT = Path(__file__).resolve().parents[1]
CUTOFF = '2026-11-06'
QUERIES = [
    ('launches', 'NVIDIA H100 H200 Blackwell product announcement launch'),
    ('capacity', 'data center capacity GPU supply electricity infrastructure expansion'),
    ('electricity', 'BLS electricity distribution producer price index data center electricity costs'),
    ('resale', 'GPU resale depreciation H100 A100 hardware economic useful life'),
]
# Do not collect pricing data from sources the pack excludes, including via snippets.
BLOCKED = ['vast.ai', 'runpod.io', 'ebay.com', 'reddit.com', 'gpulist.ai', 'cloud-gpus.com',
           'silicondata.com', 'semianalysis.com', 'ornn.com', 'amcompute.com', 'ccir.io',
           'compute.exchange', 'skypilot.co', 'dstack.ai']
DIRECT = [
    {'title': 'NVIDIA Blackwell Platform Arrives to Power a New Era of Computing',
     'url': 'https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing',
     'publication_date': '2024-03-18',
     'sentence': 'NVIDIA announced the Blackwell platform on March 18, 2024; the launch establishes a newer competing generation, not an observed depreciation rate for H100.',
     'source': 'direct_public_source', 'note_type': 'source-supported paraphrase',
     'date_verified': 'Date displayed on the fetched release: March 18, 2024.',
     'use': 'Narrative citation only; not a numeric forecasting input.'},
    {'title': 'NVIDIA Supercharges Hopper, the World’s Leading AI Computing Platform',
     'url': 'https://nvidianews.nvidia.com/news/nvidia-supercharges-hopper-the-worlds-leading-ai-computing-platform',
     'publication_date': '2023-11-13',
     'sentence': 'NVIDIA announced H200 with 141 GB of HBM3e memory and 4.8 TB/s memory bandwidth, with systems expected to begin shipping in the second quarter of 2024.',
     'source': 'direct_public_source', 'note_type': 'source-supported paraphrase',
     'date_verified': 'Date displayed on the fetched release: November 13, 2023.',
     'use': 'Narrative citation only; vendor specifications are not a workload-matched price ratio.'},
    {'title': 'DOE Releases New Report Evaluating Increase in Electricity Demand from Data Centers',
     'url': 'https://www.energy.gov/articles/doe-releases-new-report-evaluating-increase-electricity-demand-data-centers',
     'publication_date': '2024-12-20',
     'sentence': 'DOE reported that data centers consumed about 4.4% of U.S. electricity in 2023 and were projected to consume approximately 6.7–12% by 2028.',
     'source': 'direct_public_source', 'note_type': 'source-supported paraphrase',
     'date_verified': 'article:published_time is 2024-12-20T09:08:32-0500; displayed date December 20, 2024.',
     'use': 'Narrative infrastructure constraint; this is a demand projection, not an electricity-price forecast.'},
]


def safe_result(row, cutoff=CUTOFF):
    """A date and an allowed source are mandatory; never accept an undated hit."""
    if not isinstance(row, dict):
        return None, 'invalid result object'
    url = row.get('url', '')
    if not isinstance(url, str):
        return None, 'invalid URL'
    try:
        parsed_url = urlsplit(url)
        host = (parsed_url.hostname or '').lower()
    except ValueError:
        return None, 'invalid URL'
    if not host or parsed_url.scheme not in ('http', 'https'):
        return None, 'invalid URL'
    if ('ebay' in host.split('.') or any(host == d or host.endswith('.' + d) for d in BLOCKED)):
        return None, 'restricted source: pointer only; no content retained'
    date = str(row.get('publishedDate') or '')
    try:
        published = dt.datetime.fromisoformat(date.replace('Z', '+00:00')) if 'T' in date else dt.datetime.combine(dt.date.fromisoformat(date), dt.time(), dt.timezone.utc)
        if published.tzinfo is None: published = published.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None, 'missing or invalid publication date'
    end = dt.datetime.combine(dt.date.fromisoformat(cutoff) + dt.timedelta(days=1), dt.time(), dt.timezone.utc)
    if published.astimezone(dt.timezone.utc) >= end:
        return None, 'publication after cutoff'
    excerpts = row.get('highlights') or []
    if not isinstance(excerpts, list) or not excerpts or not isinstance(excerpts[0], str):
        return None, 'no cited excerpt'
    sentence = str(excerpts[0]).strip()[:1200]
    restricted_mentions = ('vast.ai', 'vastai', 'runpod', 'silicon data', 'silicondata', 'american compute', 'ccir', 'semianalysis', 'ornn')
    if any(term in sentence.lower() for term in restricted_mentions):
        return None, 'secondary excerpt references a restricted pricing source; citation pointer only'
    if not sentence:
        return None, 'empty excerpt'
    return {'title': str(row.get('title') or url), 'url': url, 'publication_date': published.astimezone(dt.timezone.utc).date().isoformat(),
            'sentence': sentence, 'source': 'exa', 'note_type': 'search result excerpt',
            'use': 'Narrative context only; publication metadata is search-provider supplied.'}, None


def collect(live=False):
    path = ROOT / 'data/evidence.json'
    if not live and path.exists():
        return json.loads(path.read_text())
    out = {'status': 'blocked_missing_exa_key', 'cutoff': CUTOFF,
           'queries': [], 'results': DIRECT.copy(), 'rejected': [], 'errors': [],
           'notice': 'Direct public-source notes are verified citations, not Exa search results. Exa searches have not run without a configured key.'}
    key = os.getenv('EXA_API_KEY')
    if live and key:
        import requests
        cache_path = ROOT / 'data/evidence_search_cache.json'
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        successful = 0
        qualifying_categories = 0
        for category, query in QUERIES:
            payload = {'query': query, 'type': 'auto', 'numResults': 5,
                       'endPublishedDate': '2026-11-07T00:00:00Z',
                       'excludeDomains': BLOCKED, 'contents': {'highlights': True}}
            digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            out['queries'].append({'category': category, 'request': payload, 'cache_key': digest})
            try:
                if digest not in cache:
                    r = requests.post('https://api.exa.ai/search', headers={'x-api-key': key}, json=payload, timeout=45)
                    r.raise_for_status()
                    response = r.json()
                    accepted, rejected = [], []
                    for item in response.get('results', []):
                        row, reason = safe_result(item)
                        if row:
                            row['category'] = category; accepted.append(row)
                        else:
                            rejected.append({'url': item.get('url'), 'reason': reason})
                    # Persist only filtered evidence, never blocked snippets or full pages.
                    cache[digest] = {'request': payload, 'results': accepted, 'rejected': rejected,
                                     'request_id': response.get('requestId')}
                    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + '\n')
                out['results'].extend(cache[digest]['results'])
                out['rejected'].extend(cache[digest]['rejected'])
                successful += 1
                qualifying_categories += bool(cache[digest]['results'])
            except Exception as exc:
                out['errors'].append({'category': category, 'error': type(exc).__name__ + ': ' + str(exc)[:200]})
        out['status'] = ('exa_complete' if successful == len(QUERIES) and qualifying_categories == len(QUERIES)
                         else 'exa_no_qualifying_results' if successful == len(QUERIES) and qualifying_categories == 0
                         else 'exa_partial_or_failed')
        out['notice'] = 'Only accepted, dated excerpts retained. Restricted sources remain pointer-only. Exa evidence is not used by historical backtest agents.'
    elif live:
        out['errors'].append({'error': 'EXA_API_KEY is not configured; live searches did not run.'})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    return out



class LoopResearcher:
    """Search inside a historical research round, or replay its exact Exa cache.

    Live mode issues an actual request even if an older response is cached.
    Offline mode never opens a network connection or substitutes direct notes.
    Date metadata cannot prove an article was never revised: citations remain
    hypothesis context, not numeric observations or evaluation truth.
    """

    def __init__(self, config, live=False):
        self.config = config
        self.live = bool(live)
        path = Path(config.get('loop_evidence_cache', 'data/loop_evidence_cache.json'))
        self.cache_path = path if path.is_absolute() else ROOT / path

    def research(self, origin, round, group):
        origin = str(origin)
        day = dt.date.fromisoformat(origin)
        if day > dt.date.fromisoformat(self.config.get('cutoff', CUTOFF)):
            raise ValueError('research origin is after the configured data cutoff')
        if not isinstance(round, int) or isinstance(round, bool) or round < 1:
            raise ValueError('round must be a positive integer')
        if not isinstance(group, str) or not group.strip():
            raise ValueError('group must be a nonempty instrument-group string')
        group = group.strip()
        topics = [
            'empirical quantile forecast rolling window nonstationary prices',
            'sticky posted prices change point shrinkage forecast',
            'volatility scaling quantile interval calibration time series',
            'GPU generation supply capacity rental prices forecasting',
        ]
        topic = topics[(round - 1) % len(topics)]
        query = f'{group} GPU rental {topic} research published by {origin}'
        payload = {'query': query, 'type': 'auto', 'numResults': 5,
                   'endPublishedDate': (day + dt.timedelta(days=1)).isoformat() + 'T00:00:00Z',
                   'excludeDomains': BLOCKED, 'contents': {'highlights': True}}
        key_input = {'origin': origin, 'round': round, 'group': group, 'request': payload}
        digest = hashlib.sha256(json.dumps(key_input, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        out = {'status': 'unavailable_cache_miss', 'origin': origin, 'round': round,
               'group': group, 'query': query, 'results': [], 'cache_key': digest,
               'executed_live': False, 'request': payload, 'rejected': [],
               'limitation': 'Publication metadata is not an immutable historical article snapshot.'}
        cache = json.loads(self.cache_path.read_text()) if self.cache_path.exists() else {}
        if not self.live:
            entry = cache.get(digest)
            if entry is None:
                return out
            # Verify both provenance and date policy when replaying an old cache.
            if entry.get('source') != 'exa' or entry.get('key_input') != key_input:
                out['status'] = 'unavailable_invalid_cache'
                return out
            accepted = []
            for row in entry.get('results', []):
                checked, reason = safe_result({'title': row.get('title'), 'url': row.get('url'),
                    'publishedDate': row.get('publication_date'), 'highlights': [row.get('sentence')]}, origin)
                if checked and row.get('source') == 'exa':
                    accepted.append(row)
                else:
                    out['rejected'].append({'url': row.get('url'), 'reason': reason or 'invalid provenance'})
            out['results'] = accepted
            out['rejected'].extend(entry.get('rejected', []))
            out['status'] = 'cached_exa' if accepted else 'no_qualifying_evidence'
            out['request_id'] = entry.get('request_id')
            return out
        api_key = os.getenv('EXA_API_KEY')
        if not api_key:
            out['status'] = 'blocked_missing_exa_key'
            return out
        import requests
        try:
            # True records an attempted API call, even when the endpoint fails.
            out['executed_live'] = True
            response = requests.post('https://api.exa.ai/search', headers={'x-api-key': api_key},
                                     json=payload, timeout=45)
            response.raise_for_status()
            raw = response.json()
            if not isinstance(raw, dict) or not isinstance(raw.get('results'), list):
                raise ValueError('Exa returned no valid results list')
            for item in raw['results']:
                row, reason = safe_result(item, origin)
                if row:
                    row['use'] = 'Origin-filtered evidence for a bounded forecasting hypothesis; never target truth.'
                    row['evidence_id'] = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()[:16]
                    out['results'].append(row)
                else:
                    out['rejected'].append({'url': item.get('url') if isinstance(item, dict) else None, 'reason': reason})
            out['request_id'] = raw.get('requestId')
            out['status'] = 'live_exa' if out['results'] else 'no_qualifying_evidence'
            cache[digest] = {'source': 'exa', 'key_input': key_input, 'results': out['results'],
                             'rejected': out['rejected'], 'request_id': raw.get('requestId')}
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.cache_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + '\n')
            temporary.replace(self.cache_path)
        except Exception as exc:
            out['status'] = 'exa_request_failed'
            out['error'] = type(exc).__name__ + ': ' + str(exc)[:200]
        return out


def build_economics():
    """Transparent sensitivities, not fitted or scored long-horizon predictions."""
    import csv
    pack = ROOT / 'data/pack/gpu-price-pack-v0.1.1-handover'
    rows = list(csv.DictReader((pack / 'daily_statistics.csv').open()))
    scenarios = []
    assumptions = {'utilization': [0.35, 0.65], 'operating_cost_per_calendar_gpu_hour': [0.15, 0.50],
                   'annual_discount_rate': [0.15, 0.30], 'gpu_share_of_net_system_cashflow': [0.50, 0.80],
                   'sale_and_refurbishment_cost_usd': [200, 1000], 'remaining_years_at_resale': 2,
                   'terminal_value': 0}
    def residual(price, decay, adverse):
        u, c, r, a, friction = (0.35, 0.50, 0.30, 0.50, 1000) if adverse else (0.65, 0.15, 0.15, 0.80, 200)
        return max(0, a * sum(8760 * max(0, u * price * (1 + decay)**year - c) / (1+r)**year for year in [1, 2]) - friction)
    for gpu, bands in [('H100', [('stress',[-0.50,-0.35]),('central',[-0.35,-0.10]),('capacity-constrained',[-0.10,0.0])]),
                       ('A100', [('stress',[-0.55,-0.40]),('central',[-0.40,-0.15]),('capacity-constrained',[-0.15,0.0])])]:
        candidates = [r for r in rows if r['source_id']=='gpurentalprices' and r['gpu_model']==gpu+' SXM 80GB' and r['instrument_class']=='neocloud_rate_card' and r['pricing_tier']=='on_demand' and r['date']<=CUTOFF]
        if not candidates:
            # GPU vocabulary uses underscores in some copies; retain exact matching semantics.
            candidates = [r for r in rows if r['source_id']=='gpurentalprices' and r['gpu_model'].replace('_',' ')==gpu+' SXM 80GB' and r['instrument_class']=='neocloud_rate_card' and r['pricing_tier']=='on_demand' and r['date']<=CUTOFF]
        anchor = max(candidates, key=lambda r:r['date'])
        p = float(anchor['median_usd_per_gpu_hour'])
        for name, band in bands:
            item = {'gpu':gpu, 'scenario':name, 'annual_rental_change':band,
                    'anchor_usd_per_gpu_hour':p, 'anchor_date':anchor['date'],
                    'series_id':f'gpurentalprices.neocloud_rate_card.{gpu}_SXM_80GB.on_demand.median',
                    'instrument_class':'neocloud_rate_card',
                    'benchmark_contract':f'{gpu} SXM 80GB; on-demand; median posted USD per GPU-hour of gpurentalprices shipped offers; all regions pooled; no commitment.',
                    'source_url':anchor['source_url'], 'licence_id':anchor['licence_id'],
                    'resale_assumption':'Illustrative GPU-allocated two-year net cash-flow value at resale, with zero terminal value; not a resale observation or prediction interval.'}
            for years, date in [(2,'2028'),(3,'2029')]:
                multiples = [(1+x)**years for x in band]
                item['rental_'+date+'_multiple'] = [round(x,4) for x in multiples]
                prices = [p*x for x in multiples]
                item['rental_'+date+'_usd_per_gpu_hour'] = [round(x,2) for x in prices]
                item['resale_'+date+'_usd'] = [round(residual(prices[0],band[0],True)),round(residual(prices[1],band[1],False))]
            scenarios.append(item)
    economic = {'status':'argued_not_scored','cutoff':CUTOFF,'scenarios':scenarios,'assumptions':assumptions,
                'notes':['These are scenario sensitivities, not calibrated 80% intervals and not observed resale prices.',
                         'The annual rental changes and utilization/cost assumptions are analyst choices, not estimates from the short backtest.',
                         'GPU resale allocation is not identified from rental prices; server configuration, condition, liquidity, and buyer economics can invalidate the DCF.',
                         'No price values from restricted resale pointers were collected. H100 launch price in Epoch is an allocated server quote, not official MSRP.',
                         'Historical AWS spot prices are administered prices; no interpolation across the March–June 2026 gap.'],
                'capability':{'h100_to_a100_inference_ratio':2.464960,'basis':'SXM 80GB, precision-matched cross-benchmark inference median, v3.0/v3.1; derived, not an official MLPerf score.'}}
    (ROOT/'data/economic.json').write_text(json.dumps(economic,indent=2)+'\n')
    return economic


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    result = collect(args.live)
    build_economics()
    print(f"Evidence: {result['status']}; {len(result['results'])} dated notes")
