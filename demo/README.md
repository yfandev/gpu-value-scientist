# GPU Value Scientist

An auditable GPU rental forecasting experiment and static research demo for the Pacific challenge. Published to GitHub as yfandev with explicit user authorization. Credentials and the original data pack are excluded.

Public demo: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./reproduce.sh
```

The unchanged pack must be at `data/pack/gpu-price-pack-v0.1.1-handover/` (or set its path in config.json before starting a new experiment). This workspace already has the verified pack and installed dependencies. Normal reproduction is offline: it rebuilds posted series, all candidate forecasts, official score reports, the 14-round research replay, findings, and demo data. No API calls are made. `forecasts.csv` is the final submission; `forecasts_fallback.csv` is starter drift. Exact columns: series_id,origin_date,horizon_days,q10,q50,q90,target_date.

Start the demo with `.venv/bin/python -m http.server 8080 --directory demo` and open its workspace preview. See `demo/DEMO_FLOW.md` for a three-minute presentation. The UI contains only computed results and explicitly labels recorded replay and unavailable integrations.

## Target mismatch discovered in the actual pack

The October 24 starter catalog's 97 headline targets include 80 AWS archive spot series and **17 posted-rental series**. The November 6 posted-only catalog has **37 headline posted-rental series**. The original submission covers all 37 (111 rows). The 80 October-headline AWS archive series can also be forecast from their older observations, but are outside Sunday’s posted-rental scoring; see `data/headline_series_audit.csv` and `forecasts_extended.csv`. The full rebuilt catalog has 725 series; the union of October/November headline membership is 117. Original 97-series quickstart artifacts remain in `results/quickstart`. `data/targets.csv` gives every target's instrument class, benchmark contract, source URL and license. Sources and instruments are never chained. The historical evaluation cohort is defined at the final cutoff, so cohort-selection/survivorship bias is a disclosed limitation.

## Agent integrations and live mode

Configure environment secrets securely:

- `OPENAI_API_KEY`: four strict-JSON roles, model configured in config.json (gpt-4.1-mini), temperature 0.
- `PAST_API_KEY`: past.dev project key for shared research memory.
- `EXA_API_KEY`: dated external evidence searches.

Then `./reproduce.sh --live`. Agent calls are cached by canonical request hash in `data/agent_cache.json`; live mode upgrades deterministic fallback records but reuses actual API responses. To force a fresh experiment, archive caches and results first and use a new config namespace. Calls may incur API charges. Missing OpenAI credentials stop live execution. Failed/missing past.dev uses a conspicuous local fallback. Missing Exa is recorded as blocked, never shown as a successful search. The original run used deterministic policies. Live OpenAI, Exa, and past.dev execution is now supported and verified through production logs; inspect the current sponsor audit and any matching recorded live receipt for exact run provenance.

The method library accepts JSON parameter sets only. Agents choose bounded candidate IDs; candidate definitions map to method and parameters, and no generated code executes. Analyst proposes hypotheses and logs mature results. Critic reviews paired official losses on later origins. Forecaster reads Analyst/Critic memory and chooses among admitted methods. Researcher writes dated evidence-boundary notes. Per-origin Exa notes enter the historical Analyst through shared memory; final-cutoff narrative sources remain separate.

### What is stored where

- **past.dev in live mode:** timestamped Analyst hypotheses/results, Critic verdicts, and Researcher notes; isolated audience and agent identities. At least Analyst and Forecaster recall shared entries. Retrieved source IDs are matched to canonical records and filtered by round/date; generated remote summaries cannot bypass the cutoff.
- **Local canonical memory:** `data/memory.json`; the same records for audit and outage fallback. `data/memory_recall_cache.json` records actual remote selections for offline replay.
- **Local files:** pack, series, forecasts, full official scoring reports and per-cell losses, evidence, cached decisions, `logs/agent_log.jsonl`, and `results/replay_audit.json`. These are not all uploaded to past.dev.

## Evaluation protocol

Config and its initial hash were written before running any score (`logs/config-preregistered.sha256`). Fifteen weekly origins are July 15 through October 21, the starter's interpretation of a range ending October 24. Round t chooses at the next origin using only earlier-origin outcomes whose target date has matured. Hypotheses must be frozen before their validation origins, and at least three later origins are required. The online curve comprises 14 subsequent origins. Final promotion requires positive online skill against drift **and** a paired loss CI wholly below zero; otherwise submit drift.

All pooled, mean, median, and geometric-mean skill values and coverage come from the unchanged starter `scorer.py`. Paired bootstrap resamples whole origins from its emitted per-cell losses, retaining cross-series/horizon dependence within origins. Its intervals are exploratory: few clusters, serial dependence across origins, and repeated tests limit inference. Conformal-style calibration uses prequential residuals, not an exchangeability guarantee. Rate-card steps make exact 80% deterministic coverage difficult.

Final November truth is not in the pack. Historical performance must never be presented as a score for the submission. A zero or tiny learning gain is not a demonstrated improvement.

## Validation

```bash
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B tests/acceptance.py
```

Acceptance validates official forecast checks and exact target grid, a controlled post-cutoff history refusal, byte-identical network-disabled offline reproduction, temporal decision audit, actual shared-memory writers/readers, and authorized GitHub identity where a repository exists. It separately reports live integrations as blocked if unexecuted. The known-bad history fixture is deleted after the refusal check and never enters forecasts.

`./reproduce.sh` rebuilds generated reports; official reports carry runtime timestamps, so report bytes can change while scores and forecast bytes remain identical. The pack manifest is verified unchanged. Eight actual Modal parallel jobs have completed, with all official score reports matching local results exactly. No speedup is claimed: cold-start and local timings are not a controlled benchmark.

## Data and attribution

Pacific Machines (2026), gpu-price-pack v0.1.1-handover, cutoff November 6, CC BY 4.0 on the compilation. The full upstream wording is in ATTRIBUTION.md and the pack's sources_register.csv and licences/. Derived changes include target extraction, forecasts, evaluation and analysis. Keep the pack unchanged and attribution with derived work. Direct public citations in data/evidence.json are labeled separately from Exa results. Long-term economic ranges in findings.md are argued assumptions-based sensitivities, not scored or calibrated forecasts.

## Sponsor challenges and public hosting

Create `.env` using `.env.example` and set OPENAI_API_KEY, EXA_API_KEY, PAST_API_KEY, MODAL_TOKEN_ID, and MODAL_TOKEN_SECRET. The loader treats values as literal text, never shell commands, and does not overwrite existing environment variables. `.env` stays local, mode 0600, and is excluded from the static site, Modal images, and submission bundle. Never paste credentials into chat.

Exa is now called inside each round by `src/research_loop.py:research_round`, through `src/evidence.py:LoopResearcher.research`. Before Analyst proposes, Researcher searches with an exclusive publication end date at the next UTC midnight after that round's origin, rejects undated/later/restricted results, and writes cited notes to shared memory. Analyst reads those notes and chooses only fixed method-library candidates. The demo's Sources & sponsors tab links the results, dates, excerpts, and hypotheses. Offline replay uses exact cached searches; a cache miss is unavailable, never a fabricated Exa result. Current-source publication metadata does not prove that an older article was never revised: this limits historical claims, and sources are hypothesis context, never evaluation truth or unverified numerical targets.

Actual production use is audited in `results/sponsor_audit.json`: API fixture tests do not count. past.dev requires multiple successful live writers/readers and evidence that decisions received another agent's retrieved records. We make no accuracy, latency, or cost-gain claim for memory. The public repository is https://github.com/yfandev/gpu-value-scientist. The original paired memory benchmark and its negative results are in docs/MEMORY_BENCHMARK.md; optimizations are evaluated separately without replacing that record.

For Modal, install `requirements-modal.txt`, then run `./deploy_modal.sh` after setting its token pair. This deploys an independent public static site on Modal, not a tunnel or an Ori private-preview workaround. Run `.venv/bin/python -B tests/check_public.py '<exact URL printed by Modal>'` to verify the homepage, data and forecast download without cookies, authorization, or redirects, and verify secret paths return 404. The current Ori preview fails this anonymous-access test with HTTP 401 and must not be described as a public judges URL.

Run `.venv/bin/python -B src/modal_jobs.py --run-experiments --backend modal` for eight parallel bounded forecast/scoring jobs. Missing credentials or cloud failures are labeled local fallback. `results/modal/execution.json` states the actual backend. Real Modal cloud execution is recorded in results/modal/execution.json. The public static demo is https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/ and is independent of this workspace.

This work is already conducted on hackwithori.com, satisfying the stated platform-use direction for Originator. We have not verified registration, an automated pre-score, finalist status, or an award.


The unchanged Pacific pack is available from the organiser’s [Google Drive folder](https://drive.google.com/drive/folders/14zWi964QlLh3mZeWGrBI85J31-SqfGHN). Extract its zip to `data/pack/`, preserving the enclosed `gpu-price-pack-v0.1.1-handover` directory. The original pack is not stored in this repository.

## past.dev challenge: measured result

**Writers:** Analyst writes hypotheses and results; Critic writes verdicts; Researcher writes dated evidence. **Readers:** Analyst and Forecaster read shared records, including records written by other agents. The recorded live run verifies these past.dev API calls.

In the structured lookup benchmark, past.dev matched the local lookup’s accuracy (**54/54**) but was slower: **0.8234 seconds** per query versus **0.000426 seconds** locally. **No cost savings are established.** Token reductions and list-price scenarios are not proof of lower total cost. This benchmark measures memory lookup, not GPU forecast accuracy.

Reviews in this project are **automated self-review by the build agent**, including delegated agents in the same system. They are not external certification or official judging scores.

## Additional submission files and calibration

`forecasts.csv` remains the original 111-row posted-rental submission. `forecasts_calibrated.csv` is the optional 111-row version with wider history-only price ranges; `forecasts_extended.csv` preserves the original rows and adds 240 AWS forecasts (117 total series, 351 rows). AWS is not Sunday-scored and its latest observation is October 31. `data/headline_series_audit.csv` lists all 117 series and reasons.

The fixed calibration follow-up improves historical coverage from 64.70% to 75.42%, and pooled skill against drift from 0.057% to 4.323%. Applying the same adjustment to drift itself improves measured skill from zero to 4.266%. Mean series skill worsens and the uncertainty interval includes no improvement. We recommend the optional calibrated file for the observed pooled-loss and coverage objectives, with those limits; this is not a proven November improvement. See docs/CALIBRATION_STUDY.md for the fixed-rule timing disclosure, all group breakdowns and validity checks. The original file stays unchanged.

`./reproduce.sh` also rebuilds these follow-up files and replays the three memory benchmarks offline. All reviews are automated self-review by the build agent.
