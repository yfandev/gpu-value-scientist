# GPU Value Scientist

**4.323% lower historical forecast error than Pacific’s drift baseline.** The uncertainty includes no gain, and later checks did not confirm improvement. Our central 2029 scenario predicts lower H100 and A100 rents; these are assumption-based future ranges.

**[Open the live demo](https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/)** · **[Watch the narrated, captioned demo](https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/demo.webm)** · **[Selected forecast file](https://github.com/yfandev/gpu-value-scientist/blob/main/forecasts_calibrated.csv)**


## Submission links

- **Live site:** [https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/](https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/)
- **Demo video (1:48):** [Watch or download the narrated walkthrough](https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/demo.webm). Includes spoken AI-generated narration and explanatory on-screen captions.
- **One submission screenshot (16:9):** [Download project-screenshot.png](https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/project-screenshot.png).
- **GitHub:** https://github.com/yfandev/gpu-value-scientist
- **Judge-panel rehearsal:** [Simulated critique and media verification](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/JUDGE_VIDEO_REHEARSAL.md). This is automated self-review, not feedback from the judges.
- **Selected forecasts:** [forecasts_calibrated.csv](https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/forecasts_calibrated.csv)
- **Full form fields and video-upload instructions:** [Submission guide](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/SUBMISSION_DRAFT.md).

The video is publicly hosted on Modal. If the form requires YouTube, Drive or Loom, upload this video there and submit that host's share link; no such link has been created here.

## Submission description

4.323% lower historical forecast error than Pacific’s drift baseline—and a clear 2029 GPU rental outlook.

GPU Value Scientist’s human-guided calibration broadened prediction ranges while keeping middle estimates unchanged. Historical coverage rose from 64.70% to 75.42%. The 4.323% error reduction is promising but not established: its 95% uncertainty interval is −0.82% to +7.02%, and later November checks did not confirm the gain. We preserve those failures rather than claim a proven victory.

Our central 2029 scenario predicts H100 rents falling from $3.55 to $0.98–$2.59 and A100 rents from $1.95 to $0.42–$1.20 per GPU-hour for the specified SXM 80GB rental categories. Newer chips’ greater capability can pressure older-chip rents; lower expected rental profits can also reduce used-equipment values. These are evidence-informed scenarios with explicit assumptions, not tested future prices.

Four AI research roles—Analyst, Forecaster, Critic and Researcher—use OpenAI models, Exa searches inside the research loop, shared past.dev memory, and Modal parallel experiments. Built in the Originator cloud workspace, the system records hypotheses, sources, decisions and rejected ideas. Exa ran in the main loop; three agents wrote to past.dev and two read shared findings; eight experiment jobs ran on Modal. Memory matched local lookup accuracy but was slower, with no established cost savings.

A separate reproducible audit reconstructed 2,837 daily medians from 444,663 observations. One H100 category’s median moved $1.90 → $0.94 → $2.23 while a matching observed record stayed at $0.94—showing why changes in observed listings must be distinguished from changes in a fixed GPU contract’s value.

The public narrated demo exposes results, limitations and economic assumptions. After installing the supplied data pack and dependencies, one command reproduces the saved forecasts offline. Code, frozen protocols, official scores and verification artifacts are public.

## What the price data taught us

A separately frozen audit reconstructed 2,837 daily medians from 444,663 observations. In one H100 marketplace category, the median moved **$1.90 → $0.94 → $2.23** while the matching observed price record remained **$0.94**. Changing observed entries can move an index without that record repricing. This does not prove identical executable offers, a causal market mechanism, or improved forecasting. The full study did not establish a dominant explanation. [Report, scripts, raw evidence and automated verification](https://github.com/yfandev/gpu-value-scientist/blob/main/research/frontier_20261115/REPORT.md).

## What to submit

Use **`forecasts_calibrated.csv`**: 111 predictions covering 37 combinations of GPU model, pricing source and rental type. The predicted dates are **November 7, 9 and 13, 2026**. Input data ends November 6. The original `forecasts.csv` is unchanged.

## What improved—and what did not

These are **historical tests, not results for the November submission**.

| Same saved agent forecasts | Actual prices inside the predicted range | Less forecast error than Pacific’s drift baseline |
|---|---:|---:|
| Before calibration | 64.70% | 0.057% |
| After widening the ranges | **75.42%** | **4.323%** |

Pacific’s **drift** baseline comes from the supplied starter kit. It estimates future prices and ranges from historical price changes. “Less error” means a reduction in the official score, not the percentage of correct answers.

The improvement is uncertain: its 95% interval is **−0.82% to +7.02%**, which includes zero. The ranges are **74.1% wider** and still miss the 80% coverage goal. In a separate matched test using drift as the starting forecast, pooled error improved **4.266%**, but the series-by-series average was **1.63% worse**. The calibration-study average was 1.62% worse; these are two distinct comparisons.

A useful diagnosis: **52.8% of the original ranges had identical lower and upper prices**, leaving no room for a price change. The follow-up widened those ranges without changing the middle predictions.

We selected the calibrated file for its observed overall error and coverage improvements. It is not proven better on future data. The rule was fixed before its test, after we had already seen the original undercoverage. It was first saved in a separate JSON file, then copied unchanged into `config.json`; the timestamps and limitation are preserved.

A further fixed-rule test asked whether separate widening for rental groups beat global widening. **It did not.** It helped hyperscaler spot but hurt neocloud rate cards and neocloud spot on pooled error. The average across series was also worse than global widening. No replacement file was produced. [Read the full comparison](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/GROUP_CALIBRATION_STUDY.md).


**Additional-date check:** on November 1–3 backtests (1- and 3-day horizons), the selected calibration had **1.488% higher error than Pacific drift**. A new learned-median combination looked better on older dates but was **2.610% worse than drift** on this check and was rejected. These are not the final submission outcomes. [Full results and reproducible protocols](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/PRICE_RESET_STUDY.md).

## What the agents actually did

Four OpenAI agents ran a bounded research loop across 14 later test dates. They tested recent-price windows, smaller changes for stable prices, and adjusted uncertainty ranges. The original loop did not establish a reliable improvement over drift. The later calibration studies were prompted by human feedback; we do not present them as autonomous discoveries.

- **Analyst** proposes forecasting ideas and records results.
- **Critic** tests later outcomes and accepts or rejects ideas.
- **Forecaster** reads shared findings and chooses permitted methods.
- **Researcher** searches for dated evidence and shares it with Analyst.

The Economic view leads with the argued 2028–29 outlook. Forecast explorer shows actual posted rental prices through November 6 beside the future predictions; later actual prices are unavailable. The gold dashed line in the learning chart is Pacific’s drift comparison at zero improvement.

The demo’s replay reveals saved results from real completed experiments. It does not run new experiments or play a video.

## Sponsor technology—and the limits

**OpenAI:** real model calls for all four roles; saved requests and responses support offline reproduction.

**Exa:** the verified run includes **13 live calls inside the main loop**, with dated sources in 13 rounds. Sources were supplied to Analyst; the demo distinguishes available sources from explicit citations. This is separate from long-term research notes.

**past.dev writers:** Analyst, Critic and Researcher. **Readers:** Analyst and Forecaster. Agents read records written by other agents. In the structured lookup benchmark, past.dev matched local lookup accuracy (**54/54**) but was slower: **0.8234 seconds versus 0.000426 seconds**. **No cost savings are established.** This tests memory lookup, not GPU forecasting. Actual calls, failures and all three benchmark versions are preserved.

**Modal:** eight real parallel experiment jobs and independent public hosting. We do not claim a speedup from the experiment jobs.

**Originator:** development took place in an ori / hackwithori.com workspace. We do not claim an official judging score or award.

past.dev holds shared hypotheses, verdicts and evidence. Local files hold canonical records, exact API replay caches, data, forecasts and official reports. Local memory is an explicit outage fallback, not proof of a past.dev call.

## Why 37 categories, when the brief says 97?

October 24 has **97 headline series: 80 AWS archive series plus 17 posted-rental series**. November 6 has 37 eligible posted-rental series: those 17 plus 20 more. All 37 have November 6 data.

The AWS series are still forecastable from October 31 observations, but are stale and outside Sunday’s scored posted-rental scope. [`forecasts_extended.csv`](https://github.com/yfandev/gpu-value-scientist/blob/main/forecasts_extended.csv) preserves the original 111 rows and adds 240 AWS predictions: **117 series, 351 rows**. It is not the selected calibrated submission. [Every series, latest date and inclusion reason](https://github.com/yfandev/gpu-value-scientist/blob/main/data/headline_series_audit.csv).

## Reproduce it

Download the unchanged Pacific pack from the [organiser’s Drive folder](https://drive.google.com/drive/folders/14zWi964QlLh3mZeWGrBI85J31-SqfGHN). Extract it to `data/pack/gpu-price-pack-v0.1.1-handover/`.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./reproduce.sh
```

Normal reproduction makes **no API calls**. It rebuilds forecasts, official scores, saved agent decisions, memory comparisons, calibration studies, the series audit and demo data. Original and calibrated forecast bytes reproduce exactly.

To run API-backed research, copy `.env.example` to `.env`, enter `OPENAI_API_KEY`, `EXA_API_KEY` and `PAST_API_KEY`, then run `./reproduce.sh --live`. Existing actual responses may be reused from cache. Never commit `.env`. Modal deployment additionally needs its token ID and secret, `requirements-modal.txt`, and `./deploy_modal.sh`.

## Checks and evidence

- Pacific’s unchanged `starter/scorer.py` supplies every reported loss and skill score.
- The starter rejects history containing a post-cutoff row.
- Network-disabled reproduction preserves forecast bytes and official metrics.
- A second leakage check physically removed future history at every test date; forecasts and eight fresh official reports matched.
- The public site was exercised across desktop/mobile tabs, downloads, replay and stage playback. A narrated, captioned walkthrough lasts 1 minute 48 seconds.
- A fresh agent with no project background reviewed the site for a two-minute judging visit; its clarity findings were fixed before final capture ([review](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/FINAL_IMPATIENT_REVIEW.md)).
- Reviews are **automated self-review by the build agent**, including separately tasked agents in the same system. They are not external certification or official judging.

Details: [findings](https://github.com/yfandev/gpu-value-scientist/blob/main/findings.md), [calibration](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/CALIBRATION_STUDY.md), [falsification audit](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/FALSIFICATION_AUDIT.md), [series audit](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/SERIES_AUDIT.md), [memory benchmarks](https://github.com/yfandev/gpu-value-scientist/blob/main/docs/MEMORY_BENCHMARK_V3.md).

Remaining limits include retrospective target selection, previously inspected test dates, few test origins, dependent prices, uneven gains across series, and unavailable November outcomes. Long-term resale/rental ranges are assumption-based scenarios, not scored forecasts.

Data: Pacific Machines (2026), gpu-price-pack v0.1.1-handover, CC BY 4.0 compilation. Preserve the original pack and [full attribution](https://github.com/yfandev/gpu-value-scientist/blob/main/ATTRIBUTION.md). No endorsement implied.
