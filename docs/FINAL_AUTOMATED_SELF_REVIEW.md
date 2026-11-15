# Independent final-deployment review

Reviewed anonymously on 2026-11-15 at 18:11 UTC. This is an independent engineering and methodology audit, not an official judging score or a claim of winning. No product files or Git state were changed. Evidence: `artifacts/final-automated-self-review/`.

## Exact deployment and browser checks

URL: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/

Downloaded `data.json`: SHA-256 `1995a335c89d3947ca5b63a5c4cb547f1349dd4359e7c88b34b548318862d31d`, 233,169 bytes. This report applies to that version. Local data was being regenerated during review and differed afterward; subsequent deployments need their own version reconciliation.

The existing browser suite passed in a fresh anonymous Chromium context: six tabs, keyboard arrow/Home/End navigation, replay reset/step/play/pause, rejected-hypothesis and empty-search filtering, forecast search/instrument filtering/chart/contracts, four sponsor cards, source expansion/filtering, downloads, and secret-path 404. No page JavaScript exceptions. Mobile 390×844 navigation and desktop 1440×1100 worked without page overflow. Separate 1366×768 stage audit exercised and captured every tab without overflow. Screenshots and machine-readable reports are retained.

Overview correctly says “OpenAI agents ran · replaying saved results” and “past.dev shared memory verified · recorded run”; it does not falsely describe the final recorded run as unexecuted. Sources shows 13 original live Exa calls, 13 source-bearing rounds, writers ANALYST/CRITIC/RESEARCHER, readers ANALYST/FORECASTER, and eight actual Modal jobs. These displayed historical counts agree with the nested matched receipt, rather than the zero-call offline replay fields. I independently recomputed the receipt identity fingerprint and compared the preserved receipt sponsor object with the downloaded nested object: both matched. The receipt establishes recorded service activity, not independently verified provider billing or causal performance improvements. Performance gains are visibly “Not verified.”

Plain-English metrics explain +8.0% lower official error than unchanged-price forecasts, +0.06% relative to the standard forecast as too small to establish reliable improvement, 64.7% coverage against an 80% goal, and 37 series/111 forecasts. The page explains these are historical tests rather than the unavailable final competition result. The hero now says “Tested forecasts”; the earlier unsupported “Better forecasts” headline is resolved. Source text now distinguishes receiving source context from causal improvement.

## Remaining findings

1. **Resolved on latest deployment — stage playback was below the fold.** At 1366×768, the chart starts around y=720 and replay controls around y=1135. The hero playback action starts the timer without scrolling/focusing the chart. A presenter must scroll to show progression. Main metric numbers are readable; dense small captions and research rows are poor projection material.
2. **Resolved on latest deployment — Economic view was too dense for a short demo.** Tall repeated scenario cards expose raw arrays and metadata; a compact currency-formatted H100/A100 comparison with expandable assumptions would make the result easier to understand. This is a presentation issue, not a broken calculation demonstrated by this audit.
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

## V3 automated self-review by the build agent (18:17 UTC)

Inspected `src/memory_benchmark_v3.py`, its frozen plan, final report, and documentation. Four v3 tests pass independently. The new resolver makes no model call and only resolves matching canonical records whose IDs are actually returned by past.dev, with temporal checks and no rescue for missing recall. Gold answers are used for evaluation rather than request construction. This is a legitimate deterministic implementation of the exact structured task, but the helper has access to the full local canonical corpus, so it is a retrieval-gated local resolver rather than a standalone remote memory store evaluation.

V3 openly reuses the 18 already evaluated questions, repeats three times, and randomizes contemporaneous arm ordering. It is operational replication, not independent holdout. The full raw prompt model is a weak comparator for a task completely specified by exact selectors; the local deterministic arm is the meaningful implementation control.

| Arm | Exact matches | Mean seconds | Prompt tokens |
|---|---:|---:|---:|
| Full raw model context | 0/54 | 0.691 | 553,200 |
| Local deterministic | 54/54 | 0.000426 | 0 |
| past.dev deterministic | 54/54 | 0.823 | 0 |

Remote deterministic lookup is correct on this corpus and eliminates unnecessary model tokens. It is slower than the newly measured raw model comparator and far slower than equally accurate local resolution. No all-three accuracy/latency/cost gain is established. Request IDs and provider credits/list prices can support a clearly labeled cost estimate; they are not invoice-level actual expenditure or proof of total savings. Ingestion amortization, subscriptions, credit conversion and pricing assumptions must remain explicit.

At the 18:16 UTC deployment recheck, the public page still served the original header/playback/economic rendering and the original data hash; requested presentation fixes were not yet visible in fresh anonymous browser checks. This finding will be superseded only after the changed public assets are observed.

V3 cost-estimate audit: all 54 unique recorded recall request IDs exactly match the cost artifact's 54 ledger IDs, totaling 54 credits. Recalculation using stated model list rates and reported cached/uncached/output token counts agrees with $0.0734432 for the raw-model comparator. Recall list cost is $0.0162; estimated one-corpus ingestion adds $0.0828, making $0.099 for this 54-query experiment, higher than the raw-model estimate. Longer-use amortization changes that comparison, but no amortization horizon was demonstrated. The artifact correctly labels estimates rather than invoice charges and leaves actual savings unverified. Local deterministic resolution requires neither recall nor model API charges.


## Latest public presentation fixes verified

A subsequent fresh anonymous visit observed the deployed fixes. Public index SHA-256: `e0c98fa0af74eff4a77ed50b3ede1b435accbb4259824d2c970698f52ff13afc`. At 1366×768, clicking the hero playback action scrolls to y=581: the chart occupies viewport y=73–318 and controls y=361, clearly visible. Economic view now presents six currency-formatted H100/A100 scenario rows with expandable assumptions and a visible illustrative-value caveat. Both earlier medium presentation findings are resolved. Evidence: `fixed-stage-play.png`, `fixed-stage-economics.png`, and `fixes.json`. Earlier 18:16 observations document propagation delay and are superseded by this check.

The complete anonymous browser regression suite was rerun against the newly deployed presentation and passed again: six tabs, replay, keyboard, filters, downloads, mobile checks and no JavaScript errors. Latest regression evidence is under `artifacts/final-automated-self-review/latest/`.
