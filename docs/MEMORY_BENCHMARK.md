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
