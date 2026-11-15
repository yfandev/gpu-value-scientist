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
