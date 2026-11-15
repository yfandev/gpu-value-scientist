"""Exercise the real generated demo, without mocked data or service responses.

Usage: .venv/bin/python -B tests/browser_check.py --url http://127.0.0.1:8080
The server must serve demo/ only. Does not start a server or publish a site.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def check(url: str, artifacts: Path):
    url = url.rstrip('/')
    artifacts.mkdir(parents=True, exist_ok=True)
    checks, errors = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1100}, device_scale_factor=1)
        page.on('pageerror', lambda error: errors.append(str(error)))
        response = page.goto(url + '/')
        assert response and response.ok, 'Demo did not load'
        page.wait_for_function("document.getElementById('metric-skill').textContent !== '—'")
        data = page.request.get(url + '/data.json').json()
        assert page.get_by_role('tab').count() == 6, 'Six navigation tabs required'
        assert not page.locator('#load-error').is_visible()
        checks.append('Real generated data loaded; six tabs available')

        for tab in ('Overview', 'Research log', 'Forecast explorer', 'Economic view', 'Reproduce', 'Sources & sponsors'):
            button = page.get_by_role('tab', name=tab, exact=False)
            button.click()
            assert button.get_attribute('aria-selected') == 'true'
            panel_id = button.get_attribute('aria-controls')
            assert page.locator('#' + panel_id).is_visible()
        checks.append('All six tabs display their panels')

        overview = page.get_by_role('tab', name='Overview')
        overview.click(); overview.focus(); page.keyboard.press('ArrowRight')
        assert page.get_by_role('tab', name='Research log').get_attribute('aria-selected') == 'true'
        page.keyboard.press('End')
        assert page.get_by_role('tab', name='Sources & sponsors').get_attribute('aria-selected') == 'true'
        page.keyboard.press('Home')
        assert overview.get_attribute('aria-selected') == 'true'
        checks.append('Accessible arrow/Home/End keyboard navigation')

        rounds = data.get('rounds', [])
        if rounds:
            assert page.locator('#learning-chart svg').count() == 1
            page.locator('#reset').click()
            assert 'READY TO REPLAY' in page.locator('#round-label').inner_text()
            page.locator('#step').click()
            assert 'TEST 1 OF' in page.locator('#round-label').inner_text()
            if len(rounds) > 2:
                page.locator('#play').click()
                page.wait_for_timeout(1550)
                page.locator('#play').click()
                assert 'TEST 3 OF' in page.locator('#round-label').inner_text()
            checks.append('Recorded learning curve reset, step, play, pause')

        page.get_by_role('tab', name='Research log').click()
        page.locator('#verdict-filter').select_option('reject')
        rejected = [h for h in data.get('hypotheses', []) if 'reject' in str(h.get('verdict', '')).lower()]
        assert page.locator('#research-table tbody tr').count() == len(rejected)
        page.locator('#hypothesis-search').fill('no-such-hypothesis-7fcd1819')
        assert 'No matching' in page.locator('#research-table').inner_text()
        page.locator('#hypothesis-search').fill('')
        checks.append('Rejected hypothesis filtering and empty search state')

        page.get_by_role('tab', name='Forecast explorer').click()
        targets = data.get('targets', [])
        if targets:
            query = targets[0].get('gpu_model') or targets[0]['series_id']
            page.locator('#series-search').fill(query)
            assert page.locator('.series-item').count() > 0
            page.locator('.series-item').first.click()
            assert page.locator('#forecast-chart svg').count() == 1
            assert page.locator('#series-contract').inner_text().strip()
            page.locator('#series-search').fill('')
            instrument = targets[0]['instrument_class']
            page.locator('#instrument-filter').select_option(instrument)
            assert page.locator('.series-item').count() == sum(t['instrument_class'] == instrument for t in targets)
            checks.append('Forecast search, instrument filter, declared contract and quantile chart')

        page.get_by_role('tab', name='Sources & sponsors').click()
        sponsors = data.get('sponsors')
        if sponsors:
            assert page.locator('#sponsor-cards article').count() == 4
            backend = (sponsors.get('modal') or {}).get('actual_backend')
            if backend:
                assert backend in page.locator('#sponsor-cards').inner_text()
            checks.append('Four sponsor audit cards reflect generated service status')
        else:
            assert 'No sponsor audit' in page.locator('#sponsor-cards').inner_text()
            checks.append('Missing sponsor audit explicitly unavailable')
        trail = data.get('loop_evidence', [])
        if trail:
            assert page.locator('.source-round').count() == len(trail)
            page.locator('.source-round summary').first.click()
            assert page.locator('.source-round').first.get_attribute('open') is not None
            page.locator('#source-status-filter').select_option('sources')
            assert page.locator('.source-round').count() == sum(bool(r.get('results')) for r in trail)
            page.locator('#source-status-filter').select_option('empty')
            assert page.locator('.source-round').count() == sum(not r.get('results') for r in trail)
            page.locator('#source-status-filter').select_option('all')
            page.locator('#source-search').fill('no-such-evidence-7fcd1819')
            assert 'No research rounds match' in page.locator('#loop-sources').inner_text()
            page.locator('#source-search').fill('')
            checks.append('Actual per-round source trail expands and filters')
        else:
            assert 'No main-loop source trail' in page.locator('#loop-sources').inner_text()
            checks.append('Missing source trail explicitly unavailable')

        downloads = ['forecasts.csv', 'findings.md', 'README.md', 'data.json']
        if sponsors:
            downloads.append('sponsor_audit.json')
        for name in downloads:
            assert page.request.get(url + '/' + name).ok, 'Download failed: ' + name
        assert page.request.get(url + '/.env').status == 404, 'Secret path exposed'
        checks.append('All displayed downloads respond; /.env returns 404')

        page.get_by_role('tab', name='Overview').click()
        page.reload(); page.wait_for_function("document.getElementById('metric-skill').textContent !== '—'")
        page.screenshot(path=str(artifacts / 'demo-desktop.png'), full_page=True)
        page.get_by_role('tab', name='Sources & sponsors').click()
        page.screenshot(path=str(artifacts / 'demo-sponsors.png'), full_page=True)

        mobile = browser.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=1,
                                  is_mobile=True, has_touch=True)
        mobile.on('pageerror', lambda error: errors.append(str(error)))
        mobile.goto(url + '/')
        mobile.wait_for_function("document.getElementById('metric-skill').textContent !== '—'")
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile page overflow'
        mobile.screenshot(path=str(artifacts / 'demo-mobile.png'), full_page=True)
        for tab in ('Forecast explorer', 'Sources & sponsors', 'Reproduce'):
            mobile.get_by_role('tab', name=tab).click()
            assert mobile.get_by_role('tab', name=tab).get_attribute('aria-selected') == 'true'
            assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile tab overflow: ' + tab
        checks.append('Mobile navigation and layout without horizontal page overflow')
        assert not errors, 'Browser JavaScript errors: ' + '; '.join(errors)
        checks.append('No browser JavaScript errors')
        browser.close()
    record = {'status': 'passed', 'url': url, 'page_errors': errors,
              'desktop': [1440, 1100], 'mobile': [390, 844], 'checks': checks}
    (artifacts / 'demo-browser-check.json').write_text(json.dumps(record, indent=2) + '\n')
    print('BROWSER_CHECK_PASSED')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8080')
    parser.add_argument('--artifacts', type=Path, default=Path('artifacts'))
    args = parser.parse_args()
    check(args.url, args.artifacts)
