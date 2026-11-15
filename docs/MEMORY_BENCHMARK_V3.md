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
