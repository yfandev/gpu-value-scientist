# Independent preliminary review — GPU Value Scientist

Reviewed 2026-11-15, public deployment fetched at 17:56 UTC. This is a preliminary review, not final-deployment signoff or an official judging score. No product files or Git state were changed. Evidence is in `artifacts/automated-self-review/`.

## Version and scope

Public URL: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/

Downloaded `data.json`: SHA-256 `b0109b0f9662b2b3a3ad9307e45a012db177fd821fd5973fafa223a31cb490ee`, 113,261 bytes. It reports deterministic policy, local JSON memory, missing Exa key, drift fallback, 37 series / 111 rows. Later live pipeline artifacts must not be conflated with this deployed version. Local source was inspected while the parent agent continued final work.

Ran the existing public browser suite independently and a separate stage-device browser audit. Desktop 1440×1100 and 1366×768; mobile 390×844. Public pages were opened without authentication. Tested six tabs, accessible keyboard tab navigation, replay reset/step/play/pause, rejection and empty-search filters, forecast search and instrument filtering, contract and quantile rendering, sponsor panels, source expansion/filtering, displayed downloads. All passed, no JavaScript exceptions, no horizontal page overflow. Screenshots cover every stage tab plus mobile.

## Prioritized findings

1. **High: deployed sponsor proof is stale/incomplete.** The tested website truthfully says OpenAI and past.dev were not run, Exa is blocked, and Modal execution was local. That deployment cannot establish the sponsor requirements. Finish live pipeline, regenerate all public artifacts together, deploy, and recheck the exact downloaded version. Preserve the distinction between original live calls and offline replay. The public repository/video and final receipt must agree. Files: `demo/data.json`, `demo/sponsor_audit.json`, `demo/findings.md`.

2. **High: source-to-method trace overstates citation and loses proposal rationale.** `src/pipeline.py:105` assigns every supplied source to `evidence_urls`, even if the Analyst did not cite or use it. `src/pipeline.py:93` overwrites its `reason` with the Critic verdict reason. `demo/index.html:47` describes these as hypothesis decisions that cite sources, then displays the overwritten reason. Preserve the original proposal rationale separately; label available sources as received context and count actual citations separately. Show the Analyst's own specific source→method explanation, alongside the later Critic verdict. Source retrieval and context inclusion do not establish causal accuracy gains.

3. **High for winning claims: no demonstrated past.dev accuracy/latency/cost win.** Local `results/memory_benchmark.json` currently records 8 paired questions: both arms 25% exact-match accuracy; past.dev mean 1.5712 seconds versus full-context 1.2264 seconds; 72.3884% fewer prompt tokens, but total monetary cost unverified. The benchmark explicitly reports all-three gains false. This is useful honest negative evidence, not a sponsor win. It is memory QA on one frozen corpus, not GPU forecast accuracy. Do not search repeatedly for a favorable subset and present it as the prespecified benchmark.

4. **Medium: “Better forecasts” is stronger than the demonstrated conclusion.** The tested hero (`demo/index.html:7`) leads with this claim while final submission is drift fallback and historical improvement over drift is not established. Replace with a research question or evidence-focused claim. The nearby metric qualifier correctly says CI crosses zero. Coverage 64.6% against an 80% nominal interval is materially undercovered; maintain this visibility.

5. **Medium: researcher description contradicts the newer main-loop design.** `demo/index.html:11` says evidence informs the long-term view separately from scored predictions, while `src/research_loop.py:4` and `src/pipeline.py:100` feed dated evidence to Analyst proposals. Explain that main-loop evidence motivates bounded hypotheses, while long-term scenario analysis is separate and not scored.

6. **Medium: stage composition hides the action.** At 1366×768 the attractive hero/status/stats consume most of the first screen; replay controls are below the fold. Economic view (`demo/index.html:40`) dumps raw arrays and repeated contract metadata across six tall cards. Present a compact H100/A100 scenario table, currency-formatted ranges, and expandable assumptions/contracts. Make the hero demo action scroll/focus to the replay. Maintain downloadable detailed evidence.

7. **Methodological limitation, disclosed rather than hidden:** `src/pipeline.py:53` selects the 37-member cohort at final cutoff, then backtests that fixed cohort. This is retrospective membership/survivorship selection, not point-in-time cohort evaluation. Current findings and visible warning correctly disclose it. “Unseen origins” should always be qualified as temporal holdout within this retrospective cohort. External publication dates do not prove historical page contents were immutable, and contemporary model knowledge can affect historical method discovery. No final November truth or final score is available here.

## Measured stage performance

The separate audit waits until the actual skill metric is rendered, rather than merely HTML load. One fresh browser visit: 1.106 seconds; two subsequent visits are stored in `stage-audit.json` (approximately 0.44 seconds each). These are workspace-to-public-site observations with a warm hosting service, not cold-start guarantees. A cache-disabled CDP network simulation at 150 ms latency and 200,000 bytes/s download became ready in 0.973 seconds. Compression makes this small payload cheap. No inference/API request is needed for normal recorded-demo interactions. The replay is a recorded experiment, accurately labeled. A separate warmed browser supplement measured three further ready times: 0.4403, 0.4342, and 0.4355 seconds (`warm-timings.json`), after a 1.1029-second warmup.

## Verified strengths and rubric judgment

- **Central task / rigor:** actual 37 posted headline targets, declared contracts and three horizons; the 97-series discrepancy is explained rather than fabricating extra targets. Official starter scoring, matured outcome selection (`src/pipeline.py:78`), paired losses and an explicit drift fallback are sound design choices. A full independent reproduction and final deployed hash reconciliation remain final checks, not claims made by this review.
- **Research value:** negative results and undercoverage remain visible. The economic findings distinguish posted offers from realized rent, configuration-specific earnings from universal chip depreciation, and scenario income values from calibrated resale forecasts. This is useful decision framing.
- **Creativity/system behavior:** bounded Analyst proposals, Critic validation, shared memory, and repeated Forecaster selection form an inspectable research loop. The preliminary public instance is policy replay; final live receipts must substantiate the agent and sponsor story.
- **Checkability:** downloadable CSV/findings/data, official metrics, visible sources, source filtering, explicit missing integrations, and no sample-data substitution improve trust. Final repo snapshot, demo video, offline byte identity, and live receipt need consistent publication.
- **Presentation:** cohesive dark financial-research styling, strong hierarchy, responsive layout, and sensible navigation. The first screen looks professional; economic details and tiny stage text need editing for a fast live explanation.

The tested site is mechanically reliable and attractive. It is not yet substantively ready to claim all sponsor requirements or a winning result. The strongest defensible story is an auditable scientist that can reject its own ideas, disclose uncertainty, and preserve a trustworthy baseline. Official Originator score and final competition outcome remain unknown.
