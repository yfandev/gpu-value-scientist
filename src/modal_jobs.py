"""Modal-hosted public demo and bounded, parallel CPU forecast experiments.

Offline: python -B src/modal_jobs.py --run-experiments --backend local
Remote:  python -B src/modal_jobs.py --run-experiments --backend modal
Deploy:  modal deploy src/modal_jobs.py

Only the static demo is public. Compute functions require the owner's Modal token.
No data gathering, arbitrary agent code, API agents, or Git operations run here.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
# Load only approved credentials before the Modal SDK initializes authentication.
# The loader source is bundled remotely; the local .env file is never bundled.
for source_directory in (Path(__file__).resolve().parent, Path('/gpu/src')):
    if source_directory.is_dir() and str(source_directory) not in sys.path:
        sys.path.insert(0, str(source_directory))
from environment import load_environment
load_environment()
SITE_DIR = Path(os.environ.get('GPU_VALUE_DEMO_DIR', str(ROOT / 'demo')))
PACK_REL = Path('data/pack/gpu-price-pack-v0.1.1-handover')
ALLOWED_METHODS = {
    'drift': {'min_samples'},
    'last_value_empirical': {'min_samples'},
    'recent': {'window', 'min_samples'},
    'volatility': {'window', 'scale_min', 'scale_max'},
    'step': {'window', 'shrinkage'},
    'conformal': {'window', 'calibration_days', 'min_calibration'},
}
PARAM_BOUNDS = {'window': (8, 365), 'min_samples': (2, 365),
                'scale_min': (.1, 3), 'scale_max': (.1, 5),
                'shrinkage': (0, 1), 'calibration_days': (7, 120),
                'min_calibration': (2, 120)}
INTEGER_PARAMS = {'window', 'min_samples', 'calibration_days', 'min_calibration'}
PUBLIC_FILES = {'price_history.json', 'index.html', 'data.json', 'forecasts.csv', 'findings.md',
                'README.md', 'targets.csv', 'DEMO_FLOW.md', 'ATTRIBUTION.md', 'sponsor_audit.json', 'headlines.csv', 'forecasts_extended.csv', 'forecasts_calibrated.csv', 'demo.webm', 'project-screenshot.png'}


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Dates must be YYYY-MM-DD')
    return dt.date.fromisoformat(value)


def validate_payload(payload):
    """Fail closed on execution scope, invalid prices, future history, and JSON code."""
    needed = {'history', 'series_ids', 'origins', 'horizons', 'cutoff', 'spec'}
    if set(payload) != needed:
        raise ValueError('Unexpected or missing experiment payload fields')
    cutoff = _date(payload['cutoff'])
    if cutoff > dt.date(2026, 11, 6):
        raise ValueError('Cutoff exceeds competition cutoff')
    spec = payload['spec']
    if set(spec) != {'id', 'method', 'parameters'}:
        raise ValueError('A candidate must contain only id, method, parameters')
    if not re.fullmatch(r'[a-z0-9_]{1,60}', str(spec['id'])):
        raise ValueError('Unsafe candidate identifier')
    method, params = spec['method'], spec['parameters']
    if method not in ALLOWED_METHODS or not isinstance(params, dict):
        raise ValueError('Method is not in the bounded library')
    if set(params) - ALLOWED_METHODS[method]:
        raise ValueError('Unknown method parameter')
    for key, value in params.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('Parameters must be finite numbers, never code')
        low, high = PARAM_BOUNDS[key]
        if not low <= value <= high or (key in INTEGER_PARAMS and int(value) != value):
            raise ValueError('Method parameter outside approved bounds')
    if params.get('scale_min', .5) > params.get('scale_max', 2):
        raise ValueError('Inverted volatility bounds')
    ids, origins, horizons = payload['series_ids'], payload['origins'], payload['horizons']
    if not isinstance(ids, list) or not 1 <= len(ids) <= 1000 or len(set(ids)) != len(ids):
        raise ValueError('Expected unique bounded target IDs')
    if any(not isinstance(s, str) or not s or s.startswith('aws_spot.') or '\n' in s for s in ids):
        raise ValueError('Only posted-rental target IDs are accepted')
    if not isinstance(origins, list) or not 1 <= len(origins) <= 52:
        raise ValueError('Expected 1 to 52 origins')
    parsed = [_date(o) for o in origins]
    if parsed != sorted(set(parsed)) or any(o > cutoff for o in parsed):
        raise ValueError('Origins must be unique, ordered, and within cutoff')
    if horizons != [1, 3, 7]:
        raise ValueError('Horizons must be exactly [1, 3, 7]')
    rows = payload['history']
    if not isinstance(rows, list) or not 1 <= len(rows) <= 200000:
        raise ValueError('History must contain 1 to 200000 rows')
    seen = set()
    for row in rows:
        if set(row) != {'series_id', 'date', 'value'} or row['series_id'] not in ids:
            raise ValueError('History must contain only selected posted targets and three columns')
        day = _date(row['date'])
        if day > cutoff:
            raise ValueError('History row after cutoff')
        value = row['value']
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError('History prices must be finite and positive')
        key = (row['series_id'], day)
        if key in seen:
            raise ValueError('Duplicate historical cell')
        seen.add(key)
    return payload


def run_experiment(payload):
    """Same implementation locally and remotely; official scorer owns every score."""
    validate_payload(payload)
    bundle = Path(os.environ.get('GPU_VALUE_BUNDLE_ROOT', str(ROOT)))
    starter = bundle / ('starter' if (bundle / 'starter').exists() else PACK_REL / 'starter')
    sys.dont_write_bytecode = True
    for path in (starter, bundle / 'src'):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    import pandas as pd
    from _common import SeriesStore, read_series_csv, validate_forecast
    from methods import forecast
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='gpu-value-experiment-') as temp:
        tmp = Path(temp)
        history = pd.DataFrame(payload['history'])
        history.to_csv(tmp / 'history.csv', index=False)
        store = SeriesStore(read_series_csv(tmp / 'history.csv'))
        origins = [_date(o).toordinal() for o in payload['origins']]
        forecasts = forecast(store, payload['series_ids'], origins, payload['horizons'], payload['spec'])
        forecasts.to_csv(tmp / 'forecasts.csv', index=False, float_format='%.10g')
        written = pd.read_csv(tmp / 'forecasts.csv')
        _, problems = validate_forecast(written, payload['horizons'])
        if problems:
            raise ValueError('Method produced invalid forecast rows')
        (tmp / 'ids.txt').write_text('\n'.join(payload['series_ids']) + '\n')
        reports, cell_csv = {}, {}
        for baseline in ('last_value', 'drift'):
            report_path, cells_path = tmp / f'{baseline}.json', tmp / f'{baseline}_cells.csv'
            command = [sys.executable, '-B', str(starter / 'scorer.py'),
                       '--forecast', str(tmp / 'forecasts.csv'), '--history', str(tmp / 'history.csv'),
                       '--truth', str(tmp / 'history.csv'), '--series-ids', '@' + str(tmp / 'ids.txt'),
                       '--horizons', '1,3,7', '--skill-baseline', baseline, '--missing-as-baseline',
                       '--out', str(report_path), '--per-cell', str(cells_path)]
            process = subprocess.run(command, capture_output=True, text=True, timeout=240)
            if process.returncode:
                raise RuntimeError(f'Official scorer failed ({baseline}): {process.stderr[-2000:]}')
            reports[baseline] = json.loads(report_path.read_text())
            cell_csv[baseline] = cells_path.read_text() if cells_path.exists() else ''
        return {'id': payload['spec']['id'], 'spec': payload['spec'], 'reports': reports,
                'forecasts': written.to_dict('records'), 'forecasts_csv': (tmp / 'forecasts.csv').read_text(),
                'cells_csv': cell_csv, 'elapsed_seconds': time.perf_counter() - start,
                'input_sha256': hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
                'scorer_sha256': hashlib.sha256((starter / 'scorer.py').read_bytes()).hexdigest()}


def public_demo_app(directory=None):
    """Read-only static publication; no compute or credentials exposed over HTTP."""
    from fastapi import FastAPI, Request
    from fastapi.staticfiles import StaticFiles
    site = Path(directory or '/gpu/demo')
    web = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @web.middleware('http')
    async def only_published_files(request: Request, call_next):
        name = request.url.path.lstrip('/') or 'index.html'
        if request.method not in ('GET', 'HEAD') or name not in PUBLIC_FILES:
            from starlette.responses import PlainTextResponse
            return PlainTextResponse('Not found', status_code=404)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-store, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response

    web.mount('/', StaticFiles(directory=str(site), html=True), name='demo')
    return web


# Importing validation/local code works without the optional Modal SDK.
try:
    import modal
except ImportError:
    modal = None
    app = None
else:
    app = modal.App('gpu-value-scientist')
    compute_image = modal.Image.debian_slim(python_version='3.11').pip_install(
        'numpy==2.2.6', 'pandas==2.3.1').env({'GPU_VALUE_BUNDLE_ROOT': '/gpu',
                                           'PYTHONDONTWRITEBYTECODE': '1'})
    for file_name in ('_common.py', 'baselines.py', 'scorer.py'):
        compute_image = compute_image.add_local_file(
            ROOT / PACK_REL / 'starter' / file_name, '/gpu/starter/' + file_name)
    compute_image = compute_image.add_local_file(ROOT / 'src/methods.py', '/gpu/src/methods.py')
    compute_image = compute_image.add_local_file(ROOT / 'src/environment.py', '/gpu/src/environment.py')
    site_image = modal.Image.debian_slim(python_version='3.11').pip_install('fastapi==0.115.12').add_local_dir(
        SITE_DIR, '/gpu/demo', copy=True, ignore=lambda p: not Path(p).is_dir() and Path(p).name not in PUBLIC_FILES)
    site_revision = hashlib.sha256(b''.join((SITE_DIR/name).read_bytes() for name in sorted(PUBLIC_FILES) if (SITE_DIR/name).is_file())).hexdigest()
    site_image = site_image.env({'GPU_VALUE_SITE_REVISION': site_revision})
    site_image = site_image.add_local_file(ROOT / 'src/environment.py', '/gpu/src/environment.py')

    @app.function(image=compute_image, cpu=2, memory=2048, timeout=600, max_containers=8)
    def experiment(payload: dict):
        return run_experiment(payload)

    @app.function(image=site_image, cpu=.25, memory=256, timeout=120, min_containers=1)
    @modal.concurrent(max_inputs=40)
    @modal.asgi_app()
    def demo_site():
        return public_demo_app()


def build_payloads(root=ROOT):
    config = json.loads((root / 'config.json').read_text())
    with (root / 'data/targets.csv').open() as handle:
        targets = list(csv.DictReader(handle))
    ids = sorted(t['series_id'] for t in targets)
    if any(t.get('table') != 'daily_statistics' for t in targets):
        raise ValueError('Modal jobs support only daily posted-rental targets')
    with (root / 'data/history.csv').open() as handle:
        rows = [{'series_id': r['series_id'], 'date': r['date'], 'value': float(r['value'])}
                for r in csv.DictReader(handle) if r['series_id'] in ids]
    payloads = [{'history': rows, 'series_ids': ids, 'origins': config['origins'],
                 'horizons': config['horizons'], 'cutoff': config['cutoff'], 'spec': spec}
                for spec in config['candidates']]
    if not 1 <= len(payloads) <= 8 or len({p['spec']['id'] for p in payloads}) != len(payloads):
        raise ValueError('Expected up to eight uniquely named bounded candidate jobs')
    for payload in payloads:
        validate_payload(payload)
    return payloads


def execute_jobs(payloads, backend='local', local_fallback=True):
    """Modal map is real parallel execution. Failures are explicitly recorded."""
    started = time.perf_counter()
    fallback_reason = None
    actual_backend = backend
    if backend == 'modal':
        try:
            if modal is None:
                raise RuntimeError('Modal SDK is not installed in this Python environment')
            with modal.enable_output():
                with app.run():
                    results = list(experiment.map(payloads))
        except Exception as error:
            if not local_fallback:
                raise
            fallback_reason = type(error).__name__
            print(f'MODAL DID NOT COMPLETE ({fallback_reason}); executing local fallback.', file=sys.stderr)
            actual_backend = 'local_fallback'
            results = [run_experiment(payload) for payload in payloads]
    else:
        results = [run_experiment(payload) for payload in payloads]
    return results, {'requested_backend': backend, 'actual_backend': actual_backend,
                     'fallback_reason': fallback_reason, 'n_jobs': len(results),
                     'wall_seconds': time.perf_counter() - started,
                     'modal_parallelism_limit': 8 if actual_backend == 'modal' else None,
                     'claim': 'Real Modal Function.map execution' if actual_backend == 'modal'
                     else 'Local execution only; no Modal performance claim'}


def save_results(results, execution, output):
    output.mkdir(parents=True, exist_ok=True)
    for result in results:
        folder = output / result['id']
        folder.mkdir(exist_ok=True)
        (folder / 'forecasts.csv').write_text(result['forecasts_csv'])
        for baseline, report in result['reports'].items():
            (folder / f'report_{baseline}.json').write_text(json.dumps(report, indent=2) + '\n')
            (folder / f'cells_{baseline}.csv').write_text(result['cells_csv'][baseline])
        manifest = {key: result[key] for key in ('id', 'spec', 'elapsed_seconds', 'input_sha256', 'scorer_sha256')}
        (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (output / 'execution.json').write_text(json.dumps(execution, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-experiments', action='store_true', required=True)
    parser.add_argument('--backend', choices=('local', 'modal'), default='local')
    parser.add_argument('--no-local-fallback', action='store_true')
    parser.add_argument('--out', type=Path, default=ROOT / 'results/modal')
    args = parser.parse_args()
    payloads = build_payloads()
    results, execution = execute_jobs(payloads, args.backend, not args.no_local_fallback)
    save_results(results, execution, args.out)
    print(json.dumps(execution, indent=2))


if __name__ == '__main__':
    main()
