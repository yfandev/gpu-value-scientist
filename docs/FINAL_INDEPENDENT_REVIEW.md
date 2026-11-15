# Independent final-deployment review

Reviewed anonymously on 2026-11-15 at 18:11 UTC. This is an independent engineering and methodology audit, not an official judging score or a claim of winning. No product files or Git state were changed. Evidence: `artifacts/final-independent/`.

## Exact deployment and browser checks

URL: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/

Downloaded `data.json`: SHA-256 `1995a335c89d3947ca5b63a5c4cb547f1349dd4359e7c88b34b548318862d31d`, 233,169 bytes. This report applies to that version. Local data was being regenerated during review and differed afterward; subsequent deployments need their own version reconciliation.

The existing browser suite passed in a fresh anonymous Chromium context: six tabs, keyboard arrow/Home/End navigation, replay reset/step/play/pause, rejected-hypothesis and empty-search filtering, forecast search/instrument filtering/chart/contracts, four sponsor cards, source expansion/filtering, downloads, and secret-path 404. No page JavaScript exceptions. Mobile 390×844 navigation and desktop 1440×1100 worked without page overflow. Separate 1366×768 stage audit exercised and captured every tab without overflow. Screenshots and machine-readable reports are retained.

Overview correctly says “OpenAI agents ran · replaying saved results” and “past.dev shared memory verified · recorded run”; it does not falsely describe the final recorded run as unexecuted. Sources shows 13 original live Exa calls, 13 source-bearing rounds, writers ANALYST/CRITIC/RESEARCHER, readers ANALYST/FORECASTER, and eight actual Modal jobs. These displayed historical counts agree with the nested matched receipt, rather than the zero-call offline replay fields. I independently recomputed the receipt identity fingerprint and compared the preserved receipt sponsor object with the downloaded nested object: both matched. The receipt establishes recorded service activity, not independently verified provider billing or causal performance improvements. Performance gains are visibly “Not verified.”

Plain-English metrics explain +8.0% lower official error than unchanged-price forecasts, +0.06% relative to the standard forecast as too small to establish reliable improvement, 64.7% coverage against an 80% goal, and 37 series/111 forecasts. The page explains these are historical tests rather than the unavailable final competition result. The hero now says “Tested forecasts”; the earlier unsupported “Better forecasts” headline is resolved. Source text now distinguishes receiving source context from causal improvement.

## Remaining findings

1. **Medium — stage playback remains below the fold.** At 1366×768, the chart starts around y=720 and replay controls around y=1135. The hero playback action starts the timer without scrolling/focusing the chart. A presenter must scroll to show progression. Main metric numbers are readable; dense small captions and research rows are poor projection material.
2. **Medium — Economic view remains too dense for a short demo.** Tall repeated scenario cards expose raw arrays and metadata; a compact currency-formatted H100/A100 comparison with expandable assumptions would make the result easier to understand. This is a presentation issue, not a broken calculation demonstrated by this audit.
3. **Methodology limitation — temporal holdout is within a retrospective cohort.** The hero still says “unseen origin” without immediate qualification. The detailed warning discloses final-cutoff cohort selection and survivorship. Keep that qualification when presenting historical metrics; these are not independent point-in-time cohort results. No final November outcome or official score was verified here.
4. **Evidence boundary — service usage is not a sponsor performance win.** The UI appropriately withholds accuracy/latency/cost gains. Do not reinterpret the receipt's multi-agent-access verification as satisfying every performance criterion.

## Measured presentation performance

Three stage visits became data-ready in 0.594, 0.220, and 0.146 seconds. A cache-disabled CDP network simulation with 150 ms configured latency and 200,000 bytes/s download became ready in 0.577 seconds. These are workspace-to-public-site observations on a warmed hosting service, not cold-start guarantees, audience-network forecasts, or API inference timings. Normal recorded-demo interactions do not require model calls.

## Independent memory v2 code review

Inspected `src/memory_benchmark_v2.py`, shared `Calls`/ground-truth helpers, frozen plan, and methodological documentation while the experiment ran. The same model, temperature, schema and instructions are used across three randomized paired arms. Full context includes every temporally eligible canonical record without truncation; local compact and past.dev compact share exact group/kind/date filtering and projection. Remote context additionally intersects canonical IDs returned by real recall, without local rescue for missing sources. No gold-label injection found: question selectors contain no answers, compact records retain all matches rather than choosing the gold record, and `expected_answer` is invoked after request construction/calls for scoring. Canonical candidate/verdict fields are legitimate task evidence, not separately injected answers.

The local compact control is essential: past.dev versus full raw context bundles filtering/projection with retrieval and cannot isolate the remote service's benefit. The task is deterministic structured lookup and can be solved without a model. Fresh question dates reuse an inspected 48-record corpus; they are not independent unseen data. Eighteen questions repeated twice are not 36 independent problems. The revised prompt was developed after v1 failures; v1's equal 25% accuracy and slower remote arm must remain visible. All of these limitations are appropriately disclosed in the v2 documentation.

Latency sums remote retrieval, measured local preparation, and model round trip, excluding benchmark cache persistence. Replay retains measured live timing. Actual model tokens are not monetary cost; the code explicitly leaves dollar cost null and all-three sponsor gains unverified. Ingestion/recall/subscription charges and model pricing remain unreconciled. No all-three-gains or general forecast-accuracy claim is supported by this task.

Final v2 result reconciliation follows below when the complete run and offline replay are available.

### Final v2 reconciliation

Completed plan hash: `02f953eeb595e7cf0f2be965b19394bfcf850b8347d1687e02c8ed34787d36ef`. Report records 108 model calls and 36 recall calls. Independently ran the five v2 tests: all passed. Read all final summary fields and directly compared cached paired model request payloads.

| Arm | Exact matches | Mean seconds | Prompt tokens |
|---|---:|---:|---:|
| Full raw context | 0/36 | 0.877 | 368,800 |
| Local compact | 25/36 | 0.783 | 11,386 |
| past.dev compact | 26/36 | 1.580 | 11,386 |

All 36 local/past paired OpenAI request payloads are identical as parsed objects. Therefore, the one-answer difference cannot be attributed to better retrieved information; it is repeated model/service variability on identical supplied evidence. Remote recall added latency and saved no model prompt tokens relative to the strong local control. Both compact arms improve over the poor raw-context baseline, but this does not establish a past.dev-specific performance gain. All 57 failures and zero expected-source retrieval misses are reported; no dollar saving is verified. The v2 result does not satisfy an all-three accuracy/latency/cost improvement claim.

A supplemental mobile audit exercised and captured all six tabs at 390×844, with no horizontal page overflow (`mobile-all-tabs.json`).
