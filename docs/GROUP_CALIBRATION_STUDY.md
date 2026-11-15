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
