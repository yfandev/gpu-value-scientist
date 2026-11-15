# GPU Value Scientist

Question: can bounded experiments and an auditable memory improve posted GPU rental quantiles over drift?

## Selected submission

The user selected **forecasts_calibrated.csv**: 111 predictions across 37 rental-price categories for November 7, 9 and 13, 2026. Inputs stop November 6. `forecasts.csv` remains unchanged as the before-calibration reference.

The historical original-agent calibration study gives **75.42% coverage** and **4.323% lower pooled forecast error than Pacific’s starter drift baseline**. Its 95% uncertainty interval **[-0.82%, 7.02%] includes zero**, and ranges are **74.1% wider**. The matched drift-only comparison gives **4.266%** pooled improvement but a **1.63% worse series-by-series average**; the original-agent calibration study’s mean-series figure is 1.62% worse. These are distinct comparisons, not November submission scores.

A separately frozen group-specific follow-up failed its promotion gates on five later, previously inspected dates. It was worse than global widening on pooled error and mean-series skill. No new forecast file was promoted; the selected calibrated file is unchanged. Details and group-level harms appear below.

## Original agent-loop result

Original forecast file (preserved): **drift fallback**, 111 rows across 37 posted-rental series, origin 2026-11-06, horizons 1, 3, 7.

Historical prequential results (14 unseen origins; NOT the withheld November scoring window): pooled skill against last value **0.080144**; against drift **0.000567**; interval coverage **0.647001**. Mean series skill 0.119973, median 0.097439, geometric-mean skill 0.133529. Scored cells: 1017. All scores come from the unmodified starter scorer.py, with complete reports in results/.

Paired mean loss difference against drift: -1.2174539823008747e-05; exploratory origin-cluster bootstrap 95% CI [-2.4329069252961188e-05, 0.0] across 14 origin clusters. Repeated tests and small cluster counts limit inferential strength. Zero difference is not improvement.

## Evaluation and targets

config.json was saved and hashed before any score was run. Fifteen weekly origins run July 15–October 21 inclusive, the starter's interpretation of July 15–October 24. October 24 is a separate quickstart cutoff. Each forecast slices history at its own origin. Calibration uses only matured residuals. Each proposed hypothesis is frozen before its validation forecast origins, with at least three later origins required by the critic. Predictions for round t are committed before their error is evaluated. The 14-round curve evaluates July 22–October 21. Results from the same round never enter its own choices.

Important brief discrepancy: the starter's October 24 headline catalog has 97 series, of which 80 are AWS archive spot and only 17 are posted rentals. Our November 6 posted-only build yields **37 headline posted-rental series**. The 80 AWS archive series from the October catalog remain legitimately forecastable from older observations, but are excluded from the posted-rental submission and Sunday scoring. A separate full-catalog audit and extended forecast file document that distinction. The original 97-series quickstart remains in results/quickstart. data/targets.csv declares every instrument and full benchmark contract. Posted hyperscaler_spot is a collector's daily statistic, distinct from the unscored AWS archive. Source-specific medians are never chained. No index date alignment or interpolation across the AWS hole is used. The fixed final-cutoff cohort creates retrospective selection/survivorship bias in earlier backtests; this is not a real-time cohort backtest.

## Methods and research loop

JSON parameter sets select fixed library code: starter drift, last_value_empirical, 28/56/90-day empirical increments, recent-volatility-scaled intervals, step-aware shrinkage, and prequential residual quantile calibration. Recent methods fall back to full-history increments when samples are sparse. Step shrinkage is a hypothesis about price stickiness, not a structural economic model. Calibration is conformal-style, not an exchangeability guarantee for dependent time series.

Agents may select bounded method IDs only and cannot execute generated code. Analyst freezes hypotheses and records mature results; Critic tests later-origin paired official losses and writes verdicts; Forecaster reads shared records and picks only drift or critic-approved candidates; Researcher searches Exa inside each round using that origin’s publication cutoff, writes cited notes to memory, and Analyst reads those notes before proposing bounded experiments. Search-publication dates do not prove page immutability; externally informed live runs are method-discovery experiments with that limitation. Every decision and rejection is in logs/agent_log.jsonl. Cached calls are keyed by model, temperature, schema, role, and input content. Offline mode never makes an API call.

Runtime: **openai_recorded**. Shared memory: **local_json**. Exa: **exa_complete**. Deterministic fallback roles are software policies, not evidence that OpenAI agents ran. Local-memory success is not a claim of past.dev integration success.

## Experiments (development diagnostics, not all unseen)

|Method|Pooled skill vs last value|Coverage|
|---|---:|---:|
|drift|0.079123|0.651118|
|last_value_empirical|0.087093|0.652089|
|recent_28|0.080058|0.712342|
|recent_56|0.077294|0.672498|
|recent_90|0.07768|0.656948|
|volatility|0.083846|0.670554|
|step_shrink|0.073376|0.631681|
|calibrated|0.059082|0.758989|

## Hypotheses and learning

- h01 / hyperscaler_spot / recent_28: **rejected** — The statistical gate requires rejection based on the paired origin-cluster bootstrap 95% confidence interval and mean loss difference. Although the mean loss difference is positive, indicating some improvement, the confidence interval does not support acceptance under the given criteria. Therefore, the hypothesis cannot be accepted. CI [2.865486305555699e-05, 0.003450739255555565].
- h02 / marketplace_ask / step_shrink: **rejected** — The statistical gate indicates rejection, and the bootstrap evidence shows a mean loss difference of 0.0 with a confidence interval of [0.0, 0.0], providing no support for improvement. Therefore, the hypothesis cannot be accepted despite the contextual reasoning. CI [0.0, 0.0].
- h03 / neocloud_rate_card / calibrated: **rejected** — The statistical gate indicates rejection, and the 95% confidence interval includes zero with a mean loss difference very close to zero, providing no significant evidence to accept the hypothesis. Therefore, the hypothesis should be rejected based on the supplied paired bootstrap evidence. CI [-0.0002571455938888859, 0.0].
- h05 / hyperscaler_spot / recent_56: **rejected** — The 95% confidence interval for the mean loss difference includes zero (-3.6868e-05 to 0.000492), indicating no statistically significant improvement. Additionally, the statistical gate explicitly requires rejection. Therefore, the evidence does not support accepting the recent_56 method. CI [-3.6868449166664596e-05, 0.0004920854549999994].
- h06 / marketplace_ask / last_value_empirical: **accepted** — The bootstrap confidence interval for the mean loss difference is entirely below zero, indicating a statistically significant improvement of the candidate method over the baseline. The statistical gate allows acceptance. The hypothesis rationale is sound given the market volatility and prior rejections of more complex methods, supporting the choice of the last_value_empirical method as a reasonable approach. CI [-0.0066818481111111175, -0.0009269826111111141].
- h07 / neocloud_rate_card / volatility: **rejected** — The bootstrap confidence interval [-8.25e-06, 1.89e-05] includes zero, indicating no statistically significant improvement in mean loss difference. The statistical gate requires rejection due to lack of significant evidence supporting the candidate hypothesis 'volatility' over the baseline. Therefore, the hypothesis cannot be accepted at this time. CI [-8.245881352659438e-06, 1.8887056521745198e-05].
- h04 / neocloud_spot / calibrated: **rejected** — The statistical gate indicates rejection based on the paired origin-cluster bootstrap analysis with a 95% confidence interval of [0.0, 0.0] and a mean loss difference of 0.0, suggesting no improvement or calibration benefit. Therefore, despite the detailed academic framework and calibration approach, the evidence does not support accepting the hypothesis at this time. CI [0.0, 0.0].
- h08 / neocloud_spot / volatility: **rejected** — The bootstrap confidence interval includes zero and the mean loss difference is zero, indicating no significant improvement. The statistical gate requires rejection under these conditions, so the hypothesis cannot be accepted despite the theoretical promise of the volatility method. CI [0.0, 0.0].
- h09 / hyperscaler_spot / last_value_empirical: **rejected** — The bootstrap confidence interval [-1.6879602592592458e-05, 7.694063888888998e-06] includes zero, indicating no statistically significant improvement. The statistical gate requires significance to accept, so the hypothesis must be rejected. CI [-1.6879602592592458e-05, 7.694063888888998e-06].
- h10 / marketplace_ask / last_value_empirical: **rejected** — The bootstrap confidence interval includes zero, indicating no statistically significant improvement. The statistical gate requires significance to accept, so the hypothesis must be rejected despite the negative mean loss difference. CI [-0.0012804499999999792, 0.0].
- h11 / neocloud_rate_card / last_value_empirical: **rejected** — The 95% confidence interval for the mean loss difference includes zero ([-0.0002266, 0.0000733]), indicating no statistically significant improvement of the candidate method over the baseline. The statistical gate requires significance to accept, so the hypothesis must be rejected. CI [-0.00022659706695905572, 7.333119009661452e-05].
- h12 / neocloud_spot / last_value_empirical: **pending** — Not enough subsequent origins before replay ends; cannot promote. CI [-4.7108075396825715e-05, 0.0006468278841269867].
- h13 / hyperscaler_spot / last_value_empirical: **pending** — Not enough subsequent origins before replay ends; cannot promote. CI [-0.00023928520092592618, -0.00023928520092592618].
- h14 / marketplace_ask / last_value_empirical: **pending** — Not enough subsequent origins before replay ends; cannot promote. CI [None, None].

Final promotion requires positive online skill and an upper paired-loss CI below zero. Keeping drift when alternatives fail is a negative result, not a successful improvement claim. The full-library table is exploratory development feedback; only the online curve represents the specified decision process on subsequent origins.


Source provenance: each hypothesis preserves its original Analyst rationale separately from the Critic verdict. Available evidence is not automatically a citation. References to structural forecasting papers motivate experiments; our residual calibration does not implement those papers’ models.

# Shared-memory comparison protocol

This benchmark compares two ordinary ways to give a research agent its history: complete local context and past.dev retrieval. It tests memory-question answering, not GPU forecast skill. Successful API integration alone does not establish a sponsor challenge win.

`src/memory_benchmark.py --prepare` freezes an immutable copy of the canonical memory in `results/memory_benchmark_snapshot.json`, then saves eight questions, their ground truth, model configuration, snapshot hash, and randomized paired execution order in `results/memory_benchmark_plan.json`. It makes no API calls. The plan must exist before any benchmark answer is obtained.

There are two questions for each of four instrument groups: identify its latest hypothesis and its latest critic verdict as of the frozen snapshot date. Ground truth comes mechanically from canonical records sorted by origin, round, and source ID. Questions with no matching record have an explicit `none` answer. Both arms receive the same question, system instructions, strict JSON output schema, model, temperature zero, and temporal eligibility rule.

- **Complete context:** supply every eligible canonical record, without truncation, lossy summarization, or a weakened baseline prompt.
- **past.dev:** query the existing project using the experiment's Forecaster identity, `queryTimestamp` and `occurredTo`; accept only returned `sources[].sourceId` values in the exact same eligible canonical corpus. Supply those canonical records to the model. No extra sources or generated memory summaries become facts.

The benchmark performs no past.dev writes. It uses the already ingested corpus and namespace. Eight questions × two arms gives 16 model requests and eight recall requests. The default is one measurement per pair; `--prepare --repetitions 3` predeclares three. A seed of 42 randomizes question order and which arm runs first within each pair. Repeating selected bad outcomes after looking would invalidate the comparison.

Run the authorized benchmark and the completed research memory snapshot:

```sh
.venv/bin/python -B src/memory_benchmark.py --prepare
.venv/bin/python -B src/memory_benchmark.py --live
.venv/bin/python -B src/memory_benchmark.py  # recorded replay; no network
```

Credentials load through the existing `.env` loader and are never printed. Every request and response uses a separate hash-keyed cache, `data/memory_benchmark_cache.json`. Repetition and declared-plan IDs are in keys, so new repetitions make new calls while offline replay reuses the original answers and timings. No benchmark operation writes the main agent cache, canonical memory, agent log, or forecast results. Missing offline responses and failed APIs halt explicitly instead of manufacturing an answer.

The report includes exact-match accuracy for all three required fields, source-record identification accuracy, measured model API round-trip latency, retrieval latency, and their sum as the API-path end-to-end latency. This sum excludes JSON serialization and cache-file persistence; it is not browser response time. Complete-context filtering is locally measured. Cached replay uses the recorded timings, never the speed of reading cache files. Individual trial observations and randomized order remain available.

Actual OpenAI `prompt_tokens`, `completion_tokens`, `total_tokens`, and any detailed usage fields are preserved. past.dev's `usedEvidenceTokens` is an estimate of returned memory text, not the model's billed usage. **Tokens saved are not dollars saved.** No monetary-savings claim is made without reconciling both services' charges, cached model input discounts, original corpus ingestion, subscription allocation and local compute.

The public [past.dev pricing document](https://past.dev/pricing.md), read November 15, 2026, states one credit per 350 bytes of ingested payload rounded up per data point, one credit per recall on Pay as you go and above fair use on applicable plans, with subscription and prepaid-credit pricing. Those costs cannot be treated as zero because the corpus already exists or event credits are available. Account-specific marginal and amortized totals remain **unverified** in this experiment.

Eight related questions on one small research corpus are a demonstration, not a representative general benchmark. Equal accuracy is a tie, worse accuracy is a negative result, and faster/slower measurements may reflect network noise. A successful memory QA test does not prove lower forecasting pinball loss. The report never claims all three sponsor gains unless accuracy, latency and total monetary savings are independently established; monetary cost is currently unverified, so that claim is false.

## Recorded live result — November 15, 2026

The predeclared plan was frozen at 17:53:32 UTC from **48 canonical records captured during the ongoing main research run**, with an as-of date of October 14. This was not represented as the completed final corpus. Plan SHA-256: `96a5946751810ec124766f26c3a0ac3980717841ae40086b71ecdd24e3bd6888`.

The benchmark made 16 actual OpenAI requests and eight actual past.dev recalls. The original API responses, reported usage and measured round-trip durations are cached. Offline replay subsequently reproduced those answers and measurements without new API calls.

| Measure | Complete context | past.dev retrieval |
|---|---:|---:|
| Exact-match accuracy | 2/8 (25%) | 2/8 (25%) |
| Mean API-path latency | 1.2264 seconds | 1.5712 seconds |
| Median API-path latency | 1.1498 seconds | 1.5445 seconds |
| Total prompt tokens | 179,928 | 49,681 |
| Total completion tokens | 376 | 374 |
| Total model tokens | 180,304 | 50,055 |

past.dev reduced prompt tokens by **72.39%**, tied accuracy, and added **0.3448 seconds** to mean API-path latency in this small run. Total monetary cost remains **unverified**. These measurements do **not** establish the three improvements required by the sponsor challenge.

Inspection of the wrong answers found that both arms commonly returned the globally latest record of the requested kind instead of the latest record for the requested instrument group. The full-context baseline had all eligible records and received the same explicit group selector and instructions as the retrieval arm. The negative result remains intact; prompts and expected answers were not retuned after observing it. Any revised prompt should use a separately declared experiment and fresh questions rather than present these questions as unseen again.

Measured results: `results/memory_benchmark.json`; individual trials: `results/memory_benchmark_trials.json`; frozen plan and corpus: `results/memory_benchmark_plan.json` and `results/memory_benchmark_snapshot.json`. The report's `mode: recorded` denotes offline presentation of original live measurements, not simulated API usage.


# Structured temporal memory benchmark v2

V1 remains intact: both arms achieved 25% exact-match accuracy; past.dev used fewer model tokens but was slower. Its expected records were present: wrong group and kind selection, rather than retrieval absence, caused the observed errors.

V2 compares the same `gpt-4.1-mini`, temperature zero, strict three-field answer schema and revised explicit group/kind instructions in three arms:

- `full_context`: every temporally eligible raw canonical record, with no truncation.
- `local_compact`: locally filter exact group/kind/date and project id, origin, round, group, kind, candidate and verdict. Supply all matching records, not the gold answer.
- `past_dev_compact`: real past.dev recall, canonical `sources[].sourceId` intersection, then the same filtering and projection. Generated memory text is never used as evidence. Missing retrieval records receive no local rescue.

The comparison against full context bundles projection, filtering and retrieval; it cannot isolate a past.dev benefit. The strong local compact arm isolates the value of remote recall given the same projection. This structured lookup can also be answered deterministically without a model; a model-powered memory advantage must not be inferred from this task alone.

The predeclared plan contains 18 fresh questions: every group and both kinds as of August 19 and September 16, plus two July 21 no-history questions. Two repetitions use seed 20261115 to randomize question order and all three arms within each pair: 108 model calls and 36 recall calls. The old October 14 questions are development cases. These are held-out question cutoffs on an already inspected 48-record corpus, not an independent unseen dataset. Repeated trials are related, not 36 independent problems.

Plan SHA-256: `02f953eeb595e7cf0f2be965b19394bfcf850b8347d1687e02c8ed34787d36ef`. The frozen snapshot, selectors, schedule, prompt and unchanged v1 deterministic ground-truth function existed before v2 calls. The separate convenience `gold.json` was generated just after initial calls began because the first system-Python invocation lacked `requests`; it is mechanically derived and was never sent to either service. No results were used to tune selectors or answers.

Latency includes the remote recall round trip, canonical validation/filtering/projection and prompt serialization, plus model round trip. Benchmark disk persistence is excluded. Offline replay retains original timings; it never presents replay speed as inference speed. Provider usage tokens are reported separately from money. past.dev evidence tokens are not model billing tokens. No total dollar savings are verified: ingestion, recall, subscriptions, model cached-token prices and actual account charges must be reconciled. Failures and raw trial rows remain recorded rather than selectively rerun.

Commands:

```sh
.venv/bin/python -B src/memory_benchmark_v2.py --prepare
.venv/bin/python -B src/memory_benchmark_v2.py --live
.venv/bin/python -B src/memory_benchmark_v2.py # network-free recorded replay
.venv/bin/python -m unittest discover -s tests -p test_memory_benchmark_v2.py
```

Plan preparation refuses to overwrite a declared experiment. Frozen inputs and results are in `results/memory_benchmark_v2/`; the separate request/response cache is `data/memory_benchmark_v2_cache.json`. The original main loop, production memory and v1 artifacts are untouched. Five offline tests cover strict group/kind/time filtering, source intersection, rejected future-source metadata, randomized repeated plans, complete raw context, absence of gold in requests, cache-miss refusal and exact replay of answers, tokens and timing components.

A separately labeled post-plan deterministic diagnostic uses the same local compact records and takes the last sorted matching record, without a model. It answers 18/18 questions correctly with zero model tokens and zero remote calls (`deterministic_diagnostic.json`). It is not a predeclared fourth experimental arm, but demonstrates that this structured task itself does not require semantic retrieval or an LLM. The reusable `compact_records` and `deterministic_answer` helpers are not wired into the recorded research loop.

## Completed live result — November 15, 2026

All 108 model requests and 36 past.dev recalls completed. Offline replay reproduced byte-identical trial rows with `requests.post` patched to raise on any network call. Twelve v1/v2 tests passed (five v2 tests, including the deterministic tie-break and absent-history case).

| Measure | Full raw context | Local compact | past.dev compact |
|---|---:|---:|---:|
| Exact matches / 36 | 0 | 25 | 26 |
| Accuracy | 0% | 69.44% | 72.22% |
| Mean total seconds | 0.8768 | 0.7833 | 1.5800 |
| Median total seconds | 0.8883 | 0.7675 | 1.5600 |
| Model prompt tokens | 368,800 | 11,386 | 11,386 |
| Model completion tokens | 822 | 1,296 | 1,298 |
| Missing expected sources | 0 | 0 | 0 |

Compact past.dev context improved observed accuracy versus raw full context and reduced prompt tokens by 96.91%, but added 0.7032 seconds mean latency. Against the stronger local compact baseline it used **exactly the same prompt tokens**, was 0.7967 seconds slower, and answered just one additional trial correctly. Identical compact inputs can yield different model outputs even at temperature zero; this one-answer difference is not evidence of a retrieval accuracy advantage. No expected source was absent in either compact arm. This experiment does **not** establish all three sponsor gains or even a reliable past.dev-specific gain.

All 57 incorrect trial answers are retained in `report.json` under `summary.failures` and in full `trials.json`. The full-context model sometimes returned the question ID as source ID or selected the wrong record. Compact arms still made answer-format/field errors, especially empty-history responses. No incorrect answer was repaired after the model call. No runtime API failures occurred. The separate gold-file preparation import failure is disclosed above. Complete raw context had all expected records, so its 0% result must not be attributed to unavailable information. Better prompting, different models and larger independent corpora remain untested; v1-v2 cross-run differences are not a paired causal comparison.


# Model-free structured recall benchmark v3

V3 removes the model from exact structured memory lookup. `resolve_recalled(entries, question, response)` reads only past.dev's canonical `sources[].sourceId`, validates provided occurrence timestamps, intersects with the trusted corpus, filters exact group/kind and as-of date, and deterministically selects the latest `(origin, round, id)`. It returns the answer and canonical provenance IDs. Missing remote evidence is never repaired from local records. This API is a reusable helper, not a change to the recorded forecasting loop.

This task is an exact lookup over structured metadata. Removing an unnecessary model can avoid its selection errors and tokens. It does not demonstrate improved forecasting, arbitrary semantic memory QA, or a general past.dev advantage: an entirely local deterministic lookup is a necessary strong comparator.

Before calls, `--prepare` froze corpus, gold answers, selectors, prompt, schedule and three arms under plan hash `e86b85d8849ae30a57dda6869ce64840a01949860f702ccbeca4c2a46de242d5`:

- **Full context:** contemporaneous complete raw eligible corpus, same v2 explicit prompt, gpt-4.1-mini, temperature zero and strict answer schema.
- **Local deterministic:** exact local predicate lookup and deterministic latest-record selection; no remote API or model.
- **past.dev deterministic:** real remote recall and the validated deterministic resolver; no model.

All 18 previously evaluated v2 questions are repeated three times, with seed 20261116 randomizing question order and arm order within each pair. These are now-known questions in an operational replication, **not new held-out data**. This makes 54 live recall calls, 54 model requests and 162 trials. All outcomes are retained. Accuracy is exact match of source ID, candidate and verdict. The latency sums full remote round trips and measured local request preparation/canonical processing, excluding benchmark cache disk persistence. Replays use recorded measurements. No repeat is a hidden cache hit: repetition, arm, question and plan IDs are part of request keys.

The documented recall `level=low` is used. The saved OpenAPI `RecallRequest` schema specifies low as the default 8,000-token evidence budget, medium as 16,000, and caps both to 8,000 on Pay as you go/Flex. Consequently switching level need not change the actual budget or improve speed. This experiment cannot attribute a speed change to level alone, especially since it also removes the model call. Source: `artifacts/automated-self-review/past-openapi.json` (`https://past.dev/openapi.json`).

Every v3 API response records UTC request start, request ID when provided, actual elapsed time and raw response. Recall IDs support subsequent billing reconciliation. Zero model tokens does **not** mean zero total cost: recall credits, ingestion amortization and subscription allocation remain relevant. No actual monetary-savings claim is made without account billing evidence. V2 timings are historical only; the full-context comparison here is newly measured and paired.

```sh
.venv/bin/python -B src/memory_benchmark_v3.py --prepare
.venv/bin/python -B src/memory_benchmark_v3.py --live
.venv/bin/python -B src/memory_benchmark_v3.py
.venv/bin/python -m unittest discover -s tests -p 'test_memory_benchmark*.py'
```

Artifacts live in `results/memory_benchmark_v3/` and `data/memory_benchmark_v3_cache.json`; v1/v2 and main-loop artifacts remain untouched. Four new tests cover forged/unreturned IDs, future source metadata, deterministic no-network local lookup, absence of remote model calls, request-ID recording, exact offline replay and missing-cache refusal. The first test run exposed a malformed fixture that put a verdict field on a hypothesis; the fixture was corrected to canonical corpus semantics, with no benchmark algorithm change.

## Completed live result — November 15, 2026

All 54 recall and 54 model requests completed without API failures. A network-blocked replay reproduced byte-identical trial rows, and all 16 v1/v2/v3 tests passed.

| Measure | Full raw context + model | Local deterministic | past.dev deterministic |
|---|---:|---:|---:|
| Exact answers / 54 | 0 | 54 | 54 |
| Accuracy | 0% | 100% | 100% |
| Mean total seconds | 0.690853 | 0.000426 | 0.823395 |
| Median total seconds | 0.638885 | 0.000355 | 0.797488 |
| Model prompt tokens | 553,200 | 0 | 0 |
| Model completion tokens | 1,274 | 0 | 0 |
| Missing expected sources | 0 | 0 | 0 |

Removing the model fixed all observed answer errors and eliminated model tokens, but **past.dev remained 0.132541 seconds slower than the contemporaneous raw baseline** (19.18% higher mean latency). It tied local deterministic accuracy and was approximately 0.823 seconds slower than local lookup. The faster historical v2-to-v3 past.dev result is not a paired comparison and does not establish a latency win over current full context. This run therefore does **not** satisfy all three sponsor criteria. All 54 raw-context failures are preserved; its full corpus contained the necessary records. No incorrect response was repaired.

## Credits and conditional list-price estimate

`cost_estimate.json` matches **all 54 recall response request IDs** to the account's read-only request ledger: **54 actual credits consumed**. This is direct per-request credit evidence, not a timestamp-only inference. The reconciliation utility is `src/memory_benchmark_v3_costs.py` (it makes read-only account requests and saves only selected noncredential fields).

Official OpenAI documentation fetched on November 15 lists GPT-4.1 mini at **$0.40/M uncached input, $0.10/M cached input and $1.60/M output**: https://developers.openai.com/api/docs/models/gpt-4.1-mini . Saved source text: `artifacts/automated-self-review/openai-gpt41mini-pricing.txt`. The full-context responses reported 553,200 prompt tokens, including **499,584 cached tokens**, and 1,274 completion tokens. Applying those rates gives **$0.0734432** model list cost, correctly accounting for cached input.

At the published conservative PAYG pack rate of **$0.0003/credit**, the 54 recalls have **$0.0162** list cost. Corpus ingestion is estimated separately as 276 credits, **$0.0828**, from each canonical source's UTF-8 content bytes rounded up per 350 bytes. Original ingestion receipts were not reconciled, so this is an estimate, not observed ingestion billing.

| Corpus ingestion amortized across | past.dev cost allocated to these 54 queries | Full-context model list estimate |
|---|---:|---:|
| 54 queries (all ingestion charged here) | $0.099000 | $0.0734432 |
| 100 queries | $0.060912 | $0.0734432 |
| 1,000 queries | $0.0206712 | $0.0734432 |
| 10,000 queries | $0.01664712 | $0.0734432 |

The monetary comparison changes with ingestion allocation: charging all ingestion to this small run makes past.dev more expensive. Reusing the corpus across 1,000 queries gives a conditional 71.85% list-cost reduction for the 54 queries. Actual cash savings remain unverified: credit grants, discounts, subscription allocation, taxes and local compute are excluded rather than silently treated as known zero. Local deterministic lookup has zero provider API charges but unmeasured local compute cost. Even under favorable amortization, the failed latency criterion remains unchanged.

The resolver depends on retaining the complete trusted canonical corpus locally to validate and hydrate returned source IDs. This is not a demonstration that remote retrieval replaces local storage, and it does not measure operating without that corpus. Because exact selectors and local canonical data already suffice, the local deterministic comparator is the preferred path for this particular lookup.



## past.dev challenge: measured result

**Writers:** Analyst writes hypotheses and results; Critic writes verdicts; Researcher writes dated evidence. **Readers:** Analyst and Forecaster read shared records, including records written by other agents. The recorded live run verifies these past.dev API calls.

In the structured lookup benchmark, past.dev matched the local lookup’s accuracy (**54/54**) but was slower: **0.8234 seconds** per query versus **0.000426 seconds** locally. **No cost savings are established.** Token reductions and list-price scenarios are not proof of lower total cost. This benchmark measures memory lookup, not GPU forecast accuracy.

Reviews in this project are **automated self-review by the build agent**, including delegated agents in the same system. They are not external certification or official judging scores.


# History-only interval calibration follow-up

The fixed follow-up improves historical coverage from **64.70% to 75.42%**, still below the nominal 80%, and pooled skill versus drift from **0.057% to 4.323%**. This is a retrospective follow-up designed after seeing the original undercoverage, not an untouched external holdout or a November result. The original agent's historical choices were preserved. At each replay origin the adjustment uses only targets dated strictly before that origin. The official scorer reproduces 64.7001%, rather than the approximate 64.6% in the request, for both original baseline reports.

## Fixed rule and chronology

`results/calibration_study/rule.json` was written before the first calibrated run. Its exact unchanged contents were subsequently copied into `config.json`; the config chronology note makes that ordering explicit. There was one rule and no search or retuning after viewing calibrated results. The executable checks config equality against the predeclared JSON.

Use original prequential forecast errors, never errors of previously recalibrated forecasts. For each horizon calculate signed relative lower residual `(q10-y)/max(abs(q50),1e-9)` and upper residual `(y-q90)/max(abs(q50),1e-9)`. Eligible records require both prior origin and target date strictly earlier than the current origin. Choose the first pool with at least **20 cells from at least 2 prior origins**: source × instrument class × horizon; instrument class × horizon; then horizon. Take order statistic `min(n,ceil(.9*(n+1)))` in each signed tail. Clip the resulting adjustment at zero, subtract the lower expansion from q10 (floor zero), and add the upper expansion to q90, scaling by the current absolute q50. Keep q50 unchanged. If no pool qualifies, leave the interval unchanged. Actual outputs remain strictly positive: minimum historical q10 0.0657612, final q10 0.0732508; the zero floor was not reached.

This is a conservative empirical widening rule, not a finite-sample coverage guarantee: grouped time-series residuals are dependent and not exchangeable. Pooling normalized errors prevents the dollar scale alone deciding cross-series corrections. Fallback avoids estimating tails from tiny individual series samples, but can transfer an inappropriate error distribution. The first three origins are unchanged; on August 12 only 34 of 51 forecasts have enough matured history. `audit.csv` records every selected pool, sample count, prior-origin count and maximum target date.

## Fair official comparison

All loss and skill calculations use the **unmodified official `starter/scorer.py`**, including its imported aggregation routine for breakdowns and bootstrap. The four independently scored reports have identical **1,017 cells**, 37 series, 14 origins July 22–October 21, no baseline-filled predictions and no missing forecast cells. There are 504 grid cells without truth and 33 without an eligible baseline; these are excluded consistently. The forecast file itself has 1,056 rows. Missing values are not imputed for calibration or scoring. Scorer and input hashes are in `summary.json`.

| Metric | Original | Calibrated |
|---|---:|---:|
| Pinball loss | 0.021470 | 0.020554 |
| Pooled skill vs last value | 8.0144% | 11.9406% |
| Pooled skill vs drift | 0.0567% | 4.3226% |
| Mean series skill vs drift | 0.0084% | -1.6189% |
| Median series skill vs drift | 0% | 1.9899% |
| Geometric-mean skill vs drift | 0.0084% | 0.6100% |
| Mean series skill vs last value | 11.9973% | 9.7409% |
| Median series skill vs last value | 9.7439% | 14.8514% |
| Geometric-mean skill vs last value | 13.3529% | 13.8741% |
| Inclusive q10–q90 coverage | 64.7001% | 75.4179% |
| Below q10 | 10.4228% | 8.3579% |
| Above q90 | 24.8771% | 16.2242% |
| Mean interval width, USD/GPU-hour | 0.062730 | 0.109200 |

Width increases **74.1%**. The unchanged q50 means the gain comes from tails, not improved central forecasts. Pooled results reward the dollar-scale reductions on expensive series; mean series skill worsens, so this is not a broad or uniform dominance claim.

A descriptive 2,000-draw paired whole-origin bootstrap (seed 42) gives 95% percentile intervals: calibrated pooled drift skill **[-0.82%, 7.02%]**; pinball change **[-0.001926, +0.000143]**; coverage gain **[6.28, 14.80] percentage points**. The skill interval crosses zero. Fourteen origins, serial dependence, correlated series and retrospective rule selection prevent treating this as strong significance evidence.

## Where coverage failed and what changed

Original upper misses were **253 cells**, versus **106 lower misses**. The original upper tail is the dominant shortfall. **52.8%** of original scored intervals have zero width: repeated unchanged daily prices yield zero empirical return quantiles, so later price steps escape the bands. This is consistent with price-step/nonstationarity and insufficient tail adaptation; it is a diagnosis from the observed residual pattern, not proof of a particular market cause. Longer-horizon errors are markedly worse.

| Group | Cells | Original coverage | Calibrated coverage | Original lower / upper misses | Calibrated lower / upper misses |
|---|---:|---:|---:|---:|---:|
| Hyperscaler spot | 210 | 67.14% | 77.14% | 20.48% / 12.38% | 13.81% / 9.05% |
| Marketplace ask | 33 | 69.70% | 69.70% | 12.12% / 18.18% | 12.12% / 18.18% |
| Neocloud rate card | 627 | 61.08% | 72.25% | 9.25% / 29.67% | 8.13% / 19.62% |
| Neocloud spot | 147 | 75.51% | 87.76% | 0.68% / 23.81% | 0.68% / 11.56% |
| 1 day | 352 | 73.58% | 81.53% | 6.82% / 19.60% | 6.25% / 12.22% |
| 3 days | 326 | 67.79% | 76.69% | 8.59% / 23.62% | 7.67% / 15.64% |
| 7 days | 339 | 52.51% | 67.85% | 15.93% / 31.56% | 11.21% / 20.94% |

Rate cards constitute 61.7% of scored cells and carry most undercoverage. Their original zero-width share is 58.9%; neocloud spot is 61.9%. Worst individual original coverage includes FastGPU RTX 6000 Ada rate card (23.81%, upper misses 71.43%), gpurentalprices B300 rate card (30.30%, upper misses 54.55%) and FastGPU A100 40GB rate card (33.33%, upper misses 52.38%). Hyperscaler spot has the reverse tail imbalance, with lower misses dominating. Pool/horizon distinctions are therefore necessary; a uniform symmetric widening would ignore this evidence.

Calibration still undercovers 7-day and rate-card cells. It overcovers neocloud spot. One-day pinball worsens: calibrated skill vs drift **-2.599%**; 3-day skill is **+2.851%**, 7-day **+6.7649%**. By source the tradeoff is similarly mixed: afhubbard **-7.1268%**, FastGPU **+9.0591%**, gpurentalprices **+0.7462%** pooled drift skill. Full source, class, source×class, class×horizon, horizon, GPU, pricing tier, origin and individual-series diagnostics are in `group_diagnostics.csv`; official reports contain all per-series and per-horizon scores.

## Secondary check matching the final drift base

After the main results, a requested diagnostic applied the **identical fixed rule** to current-origin drift forecasts on the same 14 origins and 1,017 cells. The residual archive remains the original selected-policy forecasts, exactly as for the final candidate. There was no parameter change. This isolates the change from the final base more directly, while retaining the retrospective and residual-distribution caveats.

| Metric | Drift base | Same base + calibration |
|---|---:|---:|
| Pinball | 0.021483 | 0.020566 |
| Pooled skill vs drift | 0% | 4.2657% |
| Pooled skill vs last value | 7.9622% | 11.8882% |
| Mean series skill vs drift | 0% | -1.6274% |
| Median series skill vs drift | 0% | 1.9899% |
| Geometric-mean skill vs drift | 0% | 0.6015% |
| Coverage | 64.7001% | 75.4179% |
| Below q10 / above q90 | 10.4228% / 24.8771% | 8.3579% / 16.2242% |
| Mean width | 0.062730 | 0.109201 |

See `drift_base_summary.json` and the four `drift_base*.json` official reports. The main bootstrap intervals concern the original selected-policy comparison, not this secondary diagnostic. For the stated historical pooled-loss and coverage objectives, the optional calibrated candidate is the better observed choice. It is not a demonstrated future winner: average per-series skill declines, the main skill interval crosses zero, and final November truth is unavailable.

## Optional November candidate and validation

Because historical coverage moved closer to 80% and pooled drift skill improved, `forecasts_calibrated.csv` contains the optional November 6 candidate in the original column format, with **111 rows**. **`forecasts.csv` remains byte-for-byte unchanged**; hashes are in `final_provenance.json`. The same frozen rule uses only original historical prequential errors with target dates before November 6. Its calibration population follows the historical selected-policy forecasts, whereas the original final forecast uses drift fallback; this distribution mismatch is a limitation. It does not refit or alter the original point forecasts.

The official frozen-cutoff scorer reports zero validation problems and no refusals, with **zero scored cells because all 111 November targets are unavailable**. No final-window skill is claimed. Historical final-audit dates remain strictly earlier than the cutoff.

Run `.venv/bin/python src/calibration_study.py` to reproduce the study and conditionally regenerate the optional candidate. Run `.venv/bin/python -m unittest tests.test_calibration_study -v` for the five checks: widening/median preservation; strict maturity and minimum-pool fallback; truth dated **on or after every one of the 14 origins** changed to extreme values without affecting forecasts through that origin; future-forecast perturbation invariance; and preservation of the explicit original residual archive when the current base changes. All passed. These tests verify the calibration layer; they do not certify that every historical base forecast or fixed target catalog was free of earlier design-time selection effects.

Data attribution remains as specified in `ATTRIBUTION.md` and the pack's `DATA.md`; no external data or providers were added.


# Headline catalog and archived AWS forecast audit

The actual catalog snapshots have **117 distinct headline series in their union**, not a fixed 97-series final target set. All 117 can be forecast using valid history dated on or before November 6. Absence of a November 6 observation does not prohibit an AWS forecast.

| Actual artifact | Catalog as-of | All catalog series | Headline posted | Headline AWS | Total headline |
|---|---|---:|---:|---:|---:|
| `results/quickstart/series_catalog.csv` | 2026-10-24 | 725 | 17 | 80 | 97 |
| `data/series_catalog.csv` | 2026-11-06 | 592 | 37 | omitted | 37 |
| `results/series_audit/series_catalog.csv` (full starter rebuild) | 2026-11-06 | 725 | 37 | 0 | 37 |

The 17 October posted headline series remain headline in November; another 20 posted series qualify. The union is therefore 80 AWS plus 37 posted series. The starter README's older 728-series prose is not the count in these actual handover-derived catalogs. The existing November catalog is a **posted-only project build**, not evidence that the AWS targets do not exist and not a separately verified official competition target list.

`data/headline_series_audit.csv` enumerates **every one of the 117 series**, with snapshot membership, tiers, exact November 6 observation availability, latest usable date, history row count, full November tier reason, original inclusion, exclusion reason, posted-scope eligibility, forecast eligibility and truth availability. It is the authoritative per-series list for this audit.

- All 37 posted series have an observation exactly on November 6 and are in the project's posted headline submission.
- All 80 October headline AWS series have a usable archive close on October 31, six days before the origin. Each fails only `stale>3d_at_as_of` in the full November catalog. Each is a legitimate extended forecast target.
- Those 80 AWS series are excluded from the posted-only scored scope by instrument/source scope and unavailable November archive truth. They are not inherently unforecastable. The starter permits extended-tier forecasts and scoring wherever matching truth exists.
- No November 7–13 truth is present in the shipped pack, including for the posted targets. Consequently neither file has a claimed November score. AWS November scoring additionally requires an authorised live collection or the November archive, described by the pack as due December 1. We did not obtain either.

## Forecast extension and semantics

`forecasts_extended.csv` contains **351 rows: the original 111 rows unchanged, followed by 240 rows for the 80 AWS series at horizons 1, 3 and 7**. Original forecast bytes are preserved as the leading rows. The origin is November 6 and target dates are November 7, 9 and 13. `forecasts.csv` remains untouched; its SHA-256 is `62ea5d18a77f4fd509ac96d9518c1d448ee777fa5839e380a0689d074a5eae31`.

The extension is an additional forecast ledger, not a claim that all 117 series belong in the posted Sunday score. Added rows use the unchanged starter `baselines.py --method drift --frozen` with all available history through the cutoff and its default 20-change minimum. The starter anchors at the last observed value, then applies empirical h-day log-change quantiles. **For stale AWS history this is exactly the starter h-day convention, not a separately fitted six-plus-h-day uncertainty model.** `results/series_audit/aws_starter_drift.csv` retains its `method_note`, explicitly recording `last_value_date=2026-10-31;stale_days=6` and change counts.

The unchanged full `build_series.py` reads the original archive and builds end-of-day closes. It carries within contiguous archive segments only: no prices are invented for the March–June archive hole or November 1–6. Composite membership is reused from the October quickstart catalog via `--members-from`, retaining the same instrument definition. Quickstart `series_daily.csv` already extends through November 6 for posted data and October 31 for AWS; its catalog's October 24 **as-of** is a tier-evaluation date, not proof that its full series file stops on that date.

## Reproduce and verify

```bash
.venv/bin/python src/series_audit.py
```

This rebuilds full cutoff history from the unchanged pack, regenerates the 117-row audit and the extended forecasts, and validates the exact 117×3 grid, origin/target dates, positive finite ordered quantiles, original row bytes and hash, unchanged starter source hashes, no future history, absence of archive-gap rows, and numerical equality of the new forecasts to the starter drift implementation. Results and command output are in `results/series_audit/audit_report.json`; the full starter build report is beside it. No pack files are modified.


# Later-origin group calibration challenge

**Instrument-class widening does not beat one global pool on the frozen later-origin comparison. No new November forecast was promoted. `forecasts.csv` and `forecasts_calibrated.csv` are unchanged.** Grouping improves coverage and the hyperscaler class but worsens pooled loss and mean-series skill relative to global widening. The prior pooled gain is not evidence that grouping uniformly helps.

## Predeclaration and population

`results/group_calibration_study/rule.json` was saved and its SHA256 communicated before any new scoring: `09215e984505bd5996488e8d0a7a93ac167cdcdf28b3deb48de86bcbd2dfedb1`. No search or result-driven tuning followed. The five evaluation origins were fixed as September 23, September 30, October 7, October 14 and October 21, 2026. These dates had already been viewed in the original study: this is a **retrospective later-origin test, not an independent heldout validation**.

Earlier available origins provide warmup. Both controlled arms use identical drift base forecasts and the same **drift-only** residual archive; each later origin may also use matured residuals from earlier evaluation origins. For each horizon, signed tails are `(q10-y)/max(abs(q50),1e-9)` and `(y-q90)/max(abs(q50),1e-9)`. Eligibility requires both prior origin and target date strictly before the forecast origin. A pool needs 20 cells and 2 distinct prior origins. The tail order statistic is `min(n,ceil(.9*(n+1)))`, one-indexed; negative expansions are clipped to zero, q10 is floored at zero, and q50 stays unchanged.

Global widening pools all instrument classes within a horizon. Grouped widening first uses instrument class × horizon, falling back to global only when that class pool is sparse. Neither uses a source-specific pool. The current-v1 reference instead uses its existing source/class/global hierarchy and original mixed-policy residual archive on the same drift base. Consequently grouped versus global isolates grouping, whereas grouped versus current-v1 changes both archive and pooling. Pure drift is the fourth reference.

The unmodified official scorer scored every arm against both drift and last-value baselines. All eight runs have identical **516 exact cells across 37 series and 5 origins**, zero missing forecasts and zero baseline fillers. There are 39 unavailable truth cells. All loss values come from official per-cell files; breakdowns use official aggregation and series statistics. No alternative loss was implemented. Full reports include pooled, mean-series, median-series and geometric-mean skill against both baselines.

## Later-origin results

Skills below are percentages versus drift; width is USD/GPU-hour.

| Method | Pinball | Pooled skill | Mean-series | Median-series | Geomean | Coverage | Mean width |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pure drift | 0.030230 | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 58.14% | 0.091529 |
| Global widening | 0.028502 | 5.7142% | 3.1761% | 5.1051% | 4.5234% | 71.12% | 0.138165 |
| Class widening | 0.028683 | 5.1169% | 2.8785% | 5.5630% | 4.6973% | 73.26% | 0.137057 |
| Current v1 | 0.028049 | 7.2136% | 2.2322% | 5.7855% | 4.1476% | 74.81% | 0.157987 |

Class widening has 7.75% lower misses and 18.99% upper misses, compared with global's 9.69% and 19.19%. Better coverage does not imply lower pinball loss or better mean-series skill. Class widening's mean-series skill is 0.2976 percentage points below global, but 0.6463 points above current v1.

## Helps and hurts

| Instrument class | Cells | Global pooled skill vs drift | Class pooled skill vs drift | Global → class coverage | Global → class mean-series skill |
|---|---:|---:|---:|---:|---:|
| Hyperscaler spot | 90 | 1.3095% | 5.4870% | 71.11% → 83.33% | -1.8305% → -0.0456% |
| Marketplace ask | 12 | -2.2999% | -2.2999% | 100% → 100% | -2.2999% → -2.2999% |
| Neocloud rate card | 309 | 5.9512% | 5.1143% | 66.02% → 66.02% | 7.6423% → 8.3522% |
| Neocloud spot | 105 | 9.9966% | 8.3222% | 82.86% → 82.86% | -6.4250% → -11.8603% |

Grouping helps hyperscaler pooled loss and coverage, hurts rate-card pooled loss despite better mean-series skill, and hurts neocloud spot on both loss summaries with unchanged coverage. Marketplace uses the sparse global fallback. Class widening still has negative mean-series skill in three of four classes. `group_diagnostics.csv` contains source, class, horizon, class × horizon, origin and individual-series breakdowns for both baselines.

`series_concentration.csv` reports each series' additive contribution to pooled mean-loss change and mean-series skill change, and recomputes outcomes leaving each series out. For grouped versus global, the largest pooled harms are FastGPU B300 rate card (+0.000084), gpurentalprices B300 rate card (+0.000066) and gpurentalprices H200 rate card (+0.000039); the largest benefit is FastGPU hyperscaler A100 80GB (-0.000058). Removing any one series still leaves grouped worse than global: pooled loss changes range +0.000100 to +0.000245. Against current v1 they remain positive, +0.000203 to +0.000756. Thus neither comparison is reversed by removing just one series.

Against pure drift, the largest three pooled improvements account for **34.9% of the net improvement**; removing any one series preserves improvement (loss changes -0.001612 to -0.001354). Mean-series gains hide a substantial loss for FastGPU neocloud-spot A100 80GB: its contribution alone is -3.5991 percentage points of the overall mean-series change versus drift. These checks describe concentration; they do not eliminate broader dependence or selection effects.

## Uncertainty and promotion decision

The frozen descriptive bootstrap resamples whole origins in pairs, 2,000 draws with seed 42. Class-minus-comparator mean pinball changes and 95% percentile intervals are:

| Comparator | Change | 95% interval |
|---|---:|---:|
| Global widening | +0.000181 | [-0.000062, +0.000468] |
| Current v1 | +0.000634 | [-0.000348, +0.002228] |
| Pure drift | -0.001547 | [-0.002755, -0.000657] |

There are only **five origin clusters**, with dependent series and time and a retrospectively selected rule. The drift interval is descriptive evidence of later-period improvement, not proof of generalization or an independent significance test. Both comparator intervals cross zero and the observed grouped loss is worse. The frozen promotion rule required BOTH comparator interval upper endpoints below zero, plus grouped mean-series skill at least each comparator's and nonnegative versus drift. Three checks fail (both intervals and mean-series versus global); two pass (mean-series versus current v1 and versus drift). **No `forecasts_group_calibrated.csv` was created.** This does not promote global widening either: global is a comparator, not a searched replacement.

## Reproduction and verification

Run `.venv/bin/python -B src/group_calibration_study.py`; all outputs remain in `results/group_calibration_study/`. `summary.json` includes protected CSV hashes before/after, official scorer and `_common.py` hashes, frozen rule hash, comparison population and promotion checks. Per-row audits record source counts, distinct prior origins, maximum target/source-origin dates and the frozen rule hash. `origin_audit.csv` summarizes those source dates and sample coverage for every method and origin.

Run `.venv/bin/python -B -m unittest tests.test_group_calibration_study -v`. Four tests pass, including actual-history truncation and extreme future-truth perturbation at every later origin for both arms, strict maturity and sparse-only fallback, widening with unchanged medians, explicit archive invariance and frozen rule integrity. The official scorer was exercised end to end on persisted forecasts. Initial reporting-only errors (a provenance filename and numpy boolean serialization) were corrected and the unchanged frozen study rerun; no rule or gate was altered. No pack file was changed. Existing data attribution continues to apply.

## The 2028–2029 view: argued scenarios, not scored forecasts

The useful conclusion is conditional: **underwrite the earnings of a specific GPU configuration and contract, not an aggregate “GPU price.”** A posted rental rate does not establish the realized rent, utilization, resale transaction price, or lender recovery. Our short-horizon evaluation cannot calibrate a two- or three-year prediction interval. The ranges below are transparent sensitivities, not q10/q90 forecasts.

### Evidence and economic mechanism

- **2024-03-18 — [NVIDIA Blackwell Platform Arrives to Power a New Era of Computing](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing).** A newer competing architecture creates a plausible channel for older-chip price pressure. The vendor's workload-specific performance claims are not used as a universal depreciation multiplier.
- **2023-11-13 — [NVIDIA Supercharges Hopper, the World’s Leading AI Computing Platform](https://nvidianews.nvidia.com/news/nvidia-supercharges-hopper-the-worlds-leading-ai-computing-platform).** H200 was announced with 141 GB memory and 4.8 TB/s bandwidth, with shipping expected in Q2 2024. Memory fit and bandwidth can matter more than nominal arithmetic throughput for a particular buyer.
- **2024-12-20 — [DOE Releases New Report Evaluating Increase in Electricity Demand from Data Centers](https://www.energy.gov/articles/doe-releases-new-report-evaluating-increase-electricity-demand-data-centers).** DOE reports data centers consumed about 4.4% of U.S. electricity in 2023 and projects approximately 6.7–12% in 2028. Capacity and power constraints can delay substitution and support older-chip earnings. This is a demand projection, not an electricity-price forecast; we have not treated it as the BLS electricity PPI or invented a PPI observation.

These three citations were fetched directly and their displayed publication dates checked. They are labeled separately from Exa results. Four live Exa narrative searches have now completed with an exclusive end-publication filter at 2026-11-07T00:00:00Z. Undated/later results, restricted source domains, and secondary snippets referencing excluded price publishers are rejected. Cached requests and accepted excerpts are in data/evidence.json and data/evidence_search_cache.json. Separate per-origin Exa searches run inside the historical research loop, before hypothesis selection; these narrative notes do not enter those earlier decisions.

The pack’s capability ladder supplies a complementary observation: the precision-matched cross-benchmark inference median is **2.464960 H100/A100**, on SXM 80GB parts in MLPerf Inference v3.0/v3.1. It is a derived composite, not an official verified MLPerf score or a universal conversion between rental prices. Workload, precision, software maturity, interconnect, and memory fit limit transport to today's production jobs. The pack’s broader headline rounds this comparison to 2.46.

The hardware table records **$33,600 for H100 SXM5 80GB**, explicitly an analyst's $269k eight-GPU server quote divided by eight, with no official MSRP. It records **$15,000 for A100 SXM4 40GB**, while A100 SXM4 80GB has no release price. Those are different configurations and price bases; we do not use the 40GB release figure to manufacture an 80GB residual percentage, or treat an allocated H100 server quote as a standalone-GPU transaction.

The four-year AWS archive is a useful counterexample to an inevitable smooth decline. The starter’s fixed-member A100 40GB `aws_spot.p4d.24xlarge.az_median` spans 2022-06-01 through 2026-10-31. Its median daily closes by calendar year are $1.45255625 (partial 2022), $1.228975 (2023), $1.293396875 (2024), $1.24396875 (2025), and $2.1154875 (partial 2026), per GPU-hour. The 2026 figure excludes the March–June archive hole, so it is not a comparable full-year estimate. H100 `aws_spot.p5.48xlarge.az_median` begins only on 2024-12-19, not in 2022. These administered spot prices are never spliced into posted rate-card targets; no rows or returns are interpolated across the hole. The comparison motivates a capacity-constrained scenario and cautions against fitting universal depreciation from chip age alone.


### Additional evidence found through live Exa searches

- **2023-11-13 — [NVIDIA Supercharges Hopper, the World’s Leading AI Computing Platform | NVIDIA Newsroom](https://nvidianews.nvidia.com/news/nvidia-supercharges-hopper-the-worlds-leading-ai-computing-platform)**. Establishes the sequence of competing GPU generations; it does not estimate a depreciation coefficient. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.
- **2026-09-29 — [AI Data Center Boom: Can We Build It If They Come? | Bain & Company](https://www.bain.com/insights/ai-data-center-boom-can-we-build-it-if-they-come-technology-report-2026/)**. Supports testing a capacity-constrained scenario; the scenario ranges remain explicit assumptions. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.
- **2021-05-04 — [Trends in electricity prices during the transition away from ...](https://www.bls.gov/opub/btn/volume-10/trends-in-electricity-prices-during-the-transition-away-from-coal.htm)**. Explains why generation and distribution PPIs must be distinguished; no missing BLS observation is fabricated. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.
- **2026-10-01 — [Productive, Durable, Fungible: How NVIDIA AI Factories ...](https://blogs.nvidia.com/blog/productive-durable-fungible-ai-factories/)**. Provides context for useful-life and resale assumptions, without treating accounting depreciation or vendor commentary as a resale transaction dataset. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.

### Conditional rental ranges

Anchor each chip to its own observed contract on **2026-11-06**: `gpurentalprices.neocloud_rate_card.H100_SXM_80GB.on_demand.median` at **$3.5539/GPU-hour**, and the corresponding `A100_SXM_80GB` series at **$1.95/GPU-hour**. Instrument: neocloud rate card, median of shipped posted on-demand offers from that collector, all regions pooled, no commitment. Neither is a transaction price; changing provider composition can move the median.

Choose explicit annual rental changes, then compound `price(t) = price(2026-11-06) × (1 + annual_change)^t`. No probability is assigned to these scenarios.

| Chip | Scenario | Assumed annual change | Nov 2028 rent, $/GPU-h | Nov 2029 rent, $/GPU-h |
|---|---|---:|---:|---:|
| H100 SXM 80GB | Stress | −50% to −35% | 0.89–1.50 | 0.44–0.98 |
| H100 SXM 80GB | Central sensitivity | −35% to −10% | 1.50–2.88 | 0.98–2.59 |
| H100 SXM 80GB | Capacity constrained | −10% to 0% | 2.88–3.55 | 2.59–3.55 |
| A100 SXM 80GB | Stress | −55% to −40% | 0.39–0.70 | 0.18–0.42 |
| A100 SXM 80GB | Central sensitivity | −40% to −15% | 0.70–1.41 | 0.42–1.20 |
| A100 SXM 80GB | Capacity constrained | −15% to 0% | 1.41–1.95 | 1.20–1.95 |

A100's more adverse chosen sensitivity reflects its older generation and lower measured capability, not an estimated causal depreciation coefficient. Demand shocks could move outside every range, including upward. The central label is a scenario name, not an estimated median or an assertion that it is most likely.

### Resale: income-value sensitivities, with a missing transaction anchor

`resale_pointers.csv` is pointer-only. American Compute residual bands, CCIR hardware records, Compute Exchange ranges, and Silicon Data analysis are useful places to seek a permitted appraisal; we copied no values from them. There is no open transaction-level resale history here, so a calibrated resale forecast is not identifiable.

Instead we compute an **illustrative GPU-attributed income value at the future resale date**. This is an argued proxy for what an operating buyer might justify, not a statement of market clearing price. Assume two further operating years, 35–65% paid utilization, $0.15–$0.50 operating cost per calendar GPU-hour, a 15–30% discount rate, 50–80% of positive net system earnings allocated to the GPU, $200–$1,000 sale/refurbishment cost, and zero terminal value. All are analyst-selected assumptions, not estimated facts. The same annual rental decline continues for those two years. Operating costs exclude the purchase price; the allocation accounts for other system assets and is especially uncertain.

`value = max(0, allocation × Σ[j=1,2] {8760 × max(0, utilization × future_rent × (1+annual_change)^j − cost) / (1+discount)^j} − sale_cost)`.

For the **central rental sensitivities**, the resulting 2028 income-value ranges are **H100 $0–$16,385** and **A100 $0–$6,341** per GPU; for 2029, **H100 $0–$14,555** and **A100 $0–$5,103**. The floor is a zero operating-income value, not a prediction of zero salvage proceeds. In the capacity-constrained scenario the favorable upper values are much higher: the width exposes sensitivity to utilization, realized rent, and non-GPU capital allocation, rather than establishing collateral value. `data/economic.json` includes every scenario and assumption, recomputed by code from the pack's anchors.

A lessor should test debt coverage under the adverse utilization and rent path and avoid relying on the favorable residual. A lender needs a current, configuration-matched appraisal and liquidation-cost evidence before sizing collateral advances. A capacity buyer should compare a reserved contract's total committed spend to the same SKU/region/service-level scenario, rather than assuming a posted median is executable. A stronger successor GPU raises substitution pressure, but power availability and usable-work compatibility can preserve niches for the older chip.

### Attribution and reproducibility

Pacific Machines (2026), *gpu-price-pack v0.1.1-handover*, cutoff 2026-11-06 23:59:59 UTC, CC BY 4.0 on the compilation. GPU rental price data by gpurentalprices.com (https://gpurentalprices.com), licensed under CC BY 4.0. “AWS Spot Price History”, Eric Pauley (University of Wisconsin-Madison), Zenodo, https://doi.org/10.5281/zenodo.14198917, version https://doi.org/10.5281/zenodo.23853281, CC BY 4.0. Epoch AI, “Data on machine learning hardware”, https://epoch.ai/data/machine-learning-hardware, CC BY 4.0. MLCommons Association, MLPerf Inference v3.0/v3.1 results, github.com/mlcommons/inference_results_v3.0 and inference_results_v3.1, Apache License 2.0. Derived ladder ratio: **Result not verified by MLCommons Association**. The MLPerf name and logo are registered and unregistered trademarks of MLCommons Association in the United States and other countries. All rights reserved. Unauthorized use strictly prohibited. See www.mlcommons.org for more information.

All transformed data retains source attribution in the pack and exported catalog. The economic calculations are sensitivities built from the two named anchors; the original pack is unchanged. Run `.venv/bin/python src/evidence.py` to replay cached evidence and rebuild economic JSON without API calls; add `--live` to attempt Exa.

## Limitations

- 37 posted headline targets at Nov 6; the brief’s 97 at Oct 24 include 80 AWS archive series.
- Historical cohort selected at final cutoff: retrospective cohort/survivorship limitation; forecast values and decisions remain time-filtered.
- Final Nov 6 scoring truth is withheld: no final-submission performance claim.
- Paired bootstrap is exploratory with few origin clusters and repeated tests; no multiplicity-controlled guarantee.
- Past.dev current backend: local_json; recorded source: past.dev. Actual live access is audited separately.

## Reproduction and attribution

Run `./reproduce.sh` after installing requirements in a local virtual environment. `./reproduce.sh --live` requires configured API keys and rebuilds live decisions. The pack is read-only, verified with MANIFEST.sha256, and never bundled with generated submission files.

Pacific Machines (2026), gpu-price-pack v0.1.1-handover, CC BY 4.0. Full unchanged upstream attribution accompanies this work in ATTRIBUTION.md; original notices remain in the pack. Derived changes: target extraction, history-only forecasts, official score reports, and research decisions. No endorsement implied.
