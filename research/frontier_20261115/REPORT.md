# When a GPU rental-price index moves, what changed?

**Research result: the same index can move because comparable observed cells change price, because the observed basket changes, or because rows receive different aggregation weight. These mechanisms are empirically distinguishable in this pack. The evidence does not establish that either basket change or matched-cell repricing dominates overall.**

One particularly clear example: the gpurentalprices H100 marketplace median fell from **$1.90 to $0.94 per GPU-hour on October 27**, then rose to **$2.23 on October 28**. The one cell observed across both transitions stayed at **$0.94**. The observed basket changed from five cells to one to four. Calling these −50.5% and +137.2% moves changes in the price of a comparable GPU rental offer would be misleading. They remain real changes in the specified basket statistic. The missing offers might reflect availability, collection, or other changes; this dataset does not identify why they disappeared.

The frozen primary result is **41.63% membership/aggregation share of absolute bridge components**, with a descriptive 95% block-bootstrap interval of **21.94–56.17%**. This is **not** “41.63% of market price changes are artifacts,” nor a causal fraction of net movement explained. The interval supports neither prespecified dominance criterion. No forecast or competition score was changed, estimated to improve, or promoted.

## Why this question, rather than another forecasting feature?

The repository's earlier experiments primarily asked how to predict aggregate posted-price series: recent windows, shrinkage, volatility, empirical increments, and uncertainty calibration. Original-loop hypotheses were largely rejected; one empirical method was temporarily accepted. Calibration improved some historical pooled metrics but not all series summaries. A subsequent price-reset model and its median/tail combination were rejected by their frozen promotion gates, including deterioration on the later November diagnostic.

Those experiments leave a prior measurement question open: **what process is the aggregate price actually measuring?** A model can accurately forecast the median of whatever happens to be observed while remaining unsuitable for underwriting a specific machine or contract. Conversely, a comparable-offer index might be commercially meaningful while scoring worse against a changing-basket competition target. The pack documentation itself warns about multiple daily snapshots, different instruments, and changing provider coverage; it does not quantify a matched-cell decomposition for this target cohort. A repository search found no prior implementation of that decomposition. This is an empirical audit of a known index-number problem, not a claim to have invented a new economic theory.

## Frozen design and competing explanations

The question and tests were fixed in `protocol.json` before computing a transition, decomposition, or result. SHA-256: `04943247ee6a28716761a4b0d1dec67ebcc2664f6a7c59cbb3d9a0053702e0db`. Before freezing, we read the prior research/results, upstream data construction and eligibility notes, schema, target source counts, and two non-price example records per collector. All analysis is retrospective on a cohort selected at the November 6 cutoff; this is not an untouched holdout.

The competing explanations were:

- **Predominantly comparable-cell movement:** membership/aggregation absolute-component share at most 20%; support requires the entire 95% interval below 20%.
- **Predominantly basket/aggregation movement:** share at least 50%; support requires the entire interval above 50%.
- **Mixed or inconclusive:** neither criterion passes, or results depend materially on matching or source.

The final outcome is the third. The interval is inconsistent with a very small share under this particular descriptive bootstrap, but does not establish majority basket/aggregation dominance.

Inputs are the unmodified Pacific pack and the existing 37-target catalog. The analysis uses **444,663 original observations**, **2,837 target-days**, and **2,731 exactly adjacent target-day pairs**. Inputs begin July 9, after the pack's documented early-July re-emission, and end November 6. Missing days are never filled. The target cohort uses three of the pack's five collectors; neither tanod nor the cheapest-price collector belongs to these 37 targets.

| Collector | Targets | Raw observations | Adjacent pairs | Membership/aggregation component share |
|---|---:|---:|---:|---:|
| afhubbard | 4 | 429,262 | 472 | 18.52% |
| FastGPU daily | 20 | 7,777 | 1,180 | 46.28% |
| gpurentalprices | 13 | 7,624 | 1,079 | 42.47% |
| All targets | 37 | 444,663 | 2,731 | **41.63%** |

This is a panel of posted statistics, not transaction rents or realized utilization. Rows are never pooled across collectors into a new price index.

## An exact accounting bridge

A matched cell is defined by published source, instrument, GPU model, pricing tier, provider, memory, GPU count, SKU, region, country, price basis, and available configuration/contract fields. Prices, observation IDs, dates, fetch times and collector versions are excluded from the key. Missing attributes are explicit missing categories, not proof of identical hidden quality. A cell's daily price is the median of its observed rows.

For each old/new pair:

- **A** is the median of all raw rows, the unrounded precursor to the official target.
- **E** is the equally weighted median of the daily cell prices.
- **M** is the equally weighted median restricted to cells observed on both days.

The log change satisfies the identity:

```text
D = log(A_new / A_old)
S = log(A_new / E_new) − log(A_old / E_old)       aggregation/row-weight bridge
C = log(E_new / M_new) + log(M_old / E_old)       membership/overlap bridge
R = log(M_new / M_old)                          matched-cell median movement
D = S + C + R
F = Σ(|S| + |C|) / Σ(|S| + |C| + |R|)
```

All pairs retain at least one common cell. Maximum numerical identity error is **3.1 × 10⁻¹⁶**. Raw daily medians reproduce the supplied daily-statistics values within their **$0.00005** rounding bound, and every raw observation count matches.

The sum of absolute log components is 0.391861 for S, 9.551165 for C, and 13.941082 for R. Of the total absolute components, 4.48% cancels when forming net changes, because components can offset. Taking absolute components avoids unstable division by a near-zero net change, but means F is not an explained-variance statistic or share of net movement. This overlap bridge is one accounting convention; it is not a unique causal decomposition.

The bootstrap resamples **18 fixed seven-calendar-day blocks**, preserving all series inside each block: 2,000 draws, seed 20261115. It retains within-week and cross-series dependence, but cannot guarantee independence between blocks or transport to future conditions. All draws and block sums are saved.

## What the controls and diagnostics show

**The broad result is mixed, not a winning new model.** The prespecified coarser matching key gives 46.35%; replacing normalized provider IDs with raw provider IDs leaves 41.63% unchanged. Leaving out each source in turn gives 39.14–43.93%. The conclusion is not reversed by removing one collector, although individual series differ substantially.

**Poor overlap matters.** Requiring at least three common cells and at least 80% overlap on both sides retains 2,648 pairs and lowers the share to **23.52%**. The other 83 pairs—3.0% of pairs—contain 25.3% of total absolute raw movement. These are prespecified overlap diagnostics, not a replacement primary endpoint or an independent significance test.

**An unchanged matched median is weaker than unchanged matched cells.** Among 914 changes in the *unrounded* raw median, 100 have an unchanged matched median, but only 47 have no changing common cell. A median can hide offsetting or noncentral price changes. For the prespecified material-move subset, 346 pairs move at least log(1.01) in absolute value; 62 have unchanged matched medians, and **39 have no change in any common cell**. There are also 18 sign reversals between the unrounded raw and matched-median changes, including 12 material moves. These counts refer to the unrounded reconstruction, not necessarily the rounded official target's reset count.

**A rate-card example goes beyond the thin marketplace example.** FastGPU A100 40GB on October 11–12 falls from **$1.6815 to $1.42**, or **15.55%**. The four surviving cells' median instead rises from $1.6815 to $1.695, or **0.80%**. Northflank enters the observed basket at $1.42; Verda rises from $1.373 to $1.40; the other three published cell prices stay fixed. This is a concrete sign reversal. These are FastGPU daily provider/GPU minima, however, not identified individual executable offers.

| FastGPU A100 40GB cell | October 11 | October 12 |
|---|---:|---:|
| Jarvislabs | $0.890 | $0.890 |
| Lambda | $1.990 | $1.990 |
| Modal | $2.099 | $2.099 |
| Verda | $1.373 | $1.400 |
| Northflank | absent | $1.420 |
| All-cell median | **$1.6815** | **$1.4200** |
| Common-cell median | **$1.6815** | **$1.6950** |

**Aggregation effects are not the primary driver of the pooled statistic.** S is zero for both single-row-per-cell sources and nonzero only in afhubbard's multiple-snapshot series. It can include genuine intraday price movement interacting with the aggregation rule. Calling all of S “sampling error” would therefore be wrong.

## Identification limits and commercial meaning

The strongest defensible discovery is a failure of equivalence: **an aggregate posted-price reset need not be a price reset for any surviving observed cell, and can point in the opposite direction from the common-cell median.** The examples establish this directly; the primary test does not establish that composition dominates the panel overall.

There are important boundaries. All FastGPU target rows lack SKU, GPU count and region, and are already daily minima. Of 7,624 gpurentalprices rows, 6,560 lack SKU, all lack GPU count, and 7,416 lack region. Null-aware matching is reproducible but cannot make unrecorded service quality, commitment, node size or availability constant. No primary key has conflicting simultaneous prices in this sample, which is reassuring but does not recover absent attributes. Observed-cell movement R is consequently not certified same-contract economic repricing. C does not distinguish genuine entry/exit, availability changes, collector outages, or changed hidden products; prices for absent cells are unidentified.

For a lender or lessor, the result motivates reporting a comparable-configuration panel and overlap alongside the broad basket median before using index moves as evidence of collateral or earnings deterioration. For a capacity buyer, composition itself may convey real option availability, so removing it can discard economically relevant information. For a forecast competition whose target is the changing basket, these movements remain part of the target to predict. The decomposition uses tomorrow's observed membership **after the fact** and is not an admissible forward feature without additional design and testing.

This study does not measure transaction discounts, utilization, resale value, causal hardware depreciation, or forecast skill. It cannot explain why earlier models failed without another frozen study. No November 7–13 observations, prohibited external source, Kalshi prices or market-performance claims were used.

## Validation, corrections and reproducibility

Eleven mechanism/invariant controls pass: synthetic pure membership, uniform repricing, pure multiplicity, cancellation, no overlap, order invariance, exact identity/stable baskets, gaps/cutoff, price/time-independent keys, median/count reconciliation, and input/protected-file hashes. A deliberately corrupted bridge fails the identity check; its failed run is retained.

The first validation run also found a genuine implementation detail: DuckDB serialized JSON `null` differently from absent fields. Both now normalize to the same missing category. **Every numeric result in all three matching variants and every bootstrap result is exactly unchanged.** The first script, output, failed test log and correction are preserved in `initial_null_encoding/` and `corrections.md`. No hypothesis, threshold, key dimension or endpoint changed.

A separately tasked automated reviewer independently rebuilt the 11 deterministically selected cases from **1,020 original parquet rows**, all 2,837 raw daily medians, summary arithmetic and all bootstrap draws. It used independent tuple keys and standard-library median calculations, not the study bridge function. See `independent_review.md` and `independent_verification.json` for its final scope and caveats. This is automated independent implementation review within the same system, not external certification.

Reproduce from the repository root, with the existing environment:

```bash
.venv/bin/python -B research/frontier_20261115/study.py
.venv/bin/python -B research/frontier_20261115/test_study.py
.venv/bin/python -B research/frontier_20261115/verify_independent.py
```

The script checks the frozen protocol hash, all input hashes, and the three protected forecast hashes. Writes stay inside this research directory. It performs no network calls, model training, official scoring, publication, commit or push. The Pacific pack, code outside this directory, and selected forecasts are unchanged.

Data attribution: Pacific Machines (2026), *gpu-price-pack v0.1.1-handover*, CC BY 4.0 compilation; Alex Hubbard, *GPU Price Tracker*, CC BY 4.0; FastGPU GPU cloud pricing dataset, CC BY 4.0; GPU rental price data by gpurentalprices.com, CC BY 4.0. Original source URLs and licenses remain in extracted rows. Full upstream notices remain in the unchanged pack and repository `ATTRIBUTION.md`. No endorsement implied.
