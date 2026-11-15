# Modal execution and public demo

This application has two separate Modal functions:

- `demo_site`: an independently deployed, read-only public ASGI static website. It serves the allowlisted files from `demo/`, including the recorded results and forecast download. It does not proxy the ori preview or expose the workspace.
- `experiment`: an authenticated CPU job for the bounded forecasting method library. Eight configured candidates run through real `Function.map` calls, with up to eight containers. Each container returns forecast rows, two unmodified official scorer reports (last-value and drift denominators), per-cell losses, timing, and input/scorer hashes.

**Current execution must be read from `results/modal/execution.json`, not inferred from this integration existing.** Local execution or missing credentials is not sponsor usage. There is no measured Modal speedup until the jobs actually run remotely. The static site is recorded research, not an interactive live agent service.

## Authentication and deployment

Install the optional SDK into the Python environment used for remote experiments:

```bash
.venv/bin/pip install -r requirements-modal.txt
```

Set `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` securely in the workspace environment or the project-root `.env` file, or use an authenticated Modal token configuration. `deploy_modal.sh` runs the CLI through `src/with_env.py` so `.env` is loaded before Modal authentication. The experiment runner likewise loads approved local credentials before initializing the SDK. Only the credential loader source is bundled in the container; `.env` is never uploaded. Never commit credentials or put them into demo JSON or a chat message. The CLI already installed in this workspace also supports deploying the app.

Generate the demo first, then deploy:

```bash
./reproduce.sh
./deploy_modal.sh
```

`modal deploy` prints the persistent public `demo_site` URL. Copy that exact URL; do not construct or guess one. The endpoint uses Modal's default public ASGI access: no ori login, cookie, or preview share link is required. This is a standalone deployment under the owner's Modal account. Re-run deployment after rebuilding the demo to publish the new static results. No commit or GitHub integration is required.

If credentials are absent, deployment fails and no public deployment is claimed. There is no tunnel or access-control workaround.

## Verify anonymous access

Use the actual URL from the deployment log:

```bash
DEMO_URL='https://<exact-host-printed-by-modal>.modal.run'
curl --fail --silent --show-error "$DEMO_URL/" -o /tmp/gpu-value-demo.html
curl --fail --silent --show-error "$DEMO_URL/data.json" -o /tmp/gpu-value-data.json
curl --fail --silent --show-error "$DEMO_URL/forecasts.csv" -o /tmp/gpu-value-forecasts.csv
```

These commands send no authentication header or browser cookie. Confirm the downloaded CSV matches the local `forecasts.csv` hash and open the URL in a private browser window. Test the recorded replay, all tabs, a forecast search, and the download. `/.env`, `/src/modal_jobs.py`, and `/data/agent_cache.json` must return 404; POST requests must not launch jobs.

## Run the real parallel experiment sweep

```bash
.venv/bin/python -B src/modal_jobs.py --run-experiments --backend modal
```

The eight method specifications and fixed origins come from `config.json`. Inputs are only three columns (`series_id`, `date`, `value`) from the already-generated posted-target history. Only selected posted-rental targets are sent. Every history row is validated against the November 6 cutoff. Each forecast uses the method library's origin-truncated history; the official scorer may read later historical truth for development evaluation. The jobs do not fetch November scoring truth, run agents, read secrets, or alter the chosen submission.

The image bundles three unchanged starter Python files and `src/methods.py`. It never uploads the 300 MB pack, raw rental offers, or the AWS archive. Runtime history is a validated JSON payload. The public site's image is separate and bundles only an explicit allowlist of static demo artifacts.

On remote failure, the default behavior prints `MODAL DID NOT COMPLETE` and executes the same methods locally. `execution.json` records `actual_backend: local_fallback` and the exception class. To make a cloud failure fatal instead:

```bash
.venv/bin/python -B src/modal_jobs.py --run-experiments --backend modal --no-local-fallback
```

For an explicit offline run, with no network or Modal credentials:

```bash
.venv/bin/python -B src/modal_jobs.py --run-experiments --backend local
```

Outputs live in `results/modal/<candidate>/`: `forecasts.csv`, `report_last_value.json`, `report_drift.json`, matching `cells_*.csv`, and `manifest.json`. `results/modal/execution.json` records the actual backend, job count, and elapsed wall time. Scores are never reimplemented by the Modal integration. Local runtime includes both official scorer subprocesses per candidate; do not compare that duration with another benchmark that omits scoring.

## Offline contract tests

```bash
.venv/bin/python -B -m unittest discover -s tests -p test_modal_contract.py -v
```

Tests reject future history, arbitrary methods/code-like parameters, duplicate rows, AWS archive targets, and invalid origins. They run a real tiny forecast and the actual starter scorer, check the drift candidate is exactly zero skill against drift, and prove that changing future truth cannot change an earlier forecast. If FastAPI and httpx are installed, they also test the static-site allowlist and blocked write requests.

## Official documentation read

- [Web functions and ASGI apps](https://modal.com/docs/guide/webhooks): `@modal.asgi_app`, persistent `modal deploy`, and public endpoints.
- [Scaling out](https://modal.com/docs/guide/scale): parallel `Function.map`, ordered results, and exception behavior.
- [Image reference](https://modal.com/docs/reference/modal.Image): `add_local_dir` and `add_local_file` for explicit image inputs.
- [Function reference](https://modal.com/docs/reference/modal.Function): `map` contract.
