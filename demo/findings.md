# GPU Value Scientist

Question: can bounded experiments and an auditable memory improve posted GPU rental quantiles over drift?

## Measured result

Final submission: **drift fallback**, 111 rows across 37 posted-rental series, origin 2026-11-06, horizons 1, 3, 7.

Historical prequential results (14 unseen origins; NOT the withheld November scoring window): pooled skill against last value **0.080144**; against drift **0.000567**; interval coverage **0.647001**. Mean series skill 0.119973, median 0.097439, geometric-mean skill 0.133529. Scored cells: 1017. All scores come from the unmodified starter scorer.py, with complete reports in results/.

Paired mean loss difference against drift: -1.2174539823008747e-05; exploratory origin-cluster bootstrap 95% CI [-2.4329069252961188e-05, 0.0] across 14 origin clusters. Repeated tests and small cluster counts limit inferential strength. Zero difference is not improvement.

## Evaluation and targets

config.json was saved and hashed before any score was run. Fifteen weekly origins run July 15–October 21 inclusive, the starter's interpretation of July 15–October 24. October 24 is a separate quickstart cutoff. Each forecast slices history at its own origin. Calibration uses only matured residuals. Each proposed hypothesis is frozen before its validation forecast origins, with at least three later origins required by the critic. Predictions for round t are committed before their error is evaluated. The 14-round curve evaluates July 22–October 21. Results from the same round never enter its own choices.

Important brief discrepancy: the starter's October 24 headline catalog has 97 series, of which 80 are AWS archive spot and only 17 are posted rentals. At November 6 the official builder yields **37 posted-rental headline series**. We forecast that actual set, not 97 invented posted targets. The original 97-series quickstart remains in results/quickstart. data/targets.csv declares every instrument and full benchmark contract. Posted hyperscaler_spot is a collector's daily statistic, distinct from the unscored AWS archive. Source-specific medians are never chained. No index date alignment or interpolation across the AWS hole is used. The fixed final-cutoff cohort creates retrospective selection/survivorship bias in earlier backtests; this is not a real-time cohort backtest.

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
