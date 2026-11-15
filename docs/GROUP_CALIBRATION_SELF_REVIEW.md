# Group calibration automated self-review

This is automated self-review by the build agent using a separately tasked reviewer, not an independent human review or external validation.

## Design reviewed before scoring

The reviewer read `results/group_calibration_study/rule.json` before the new implementation and scoring outputs existed. Its SHA-256 was `09215e984505bd5996488e8d0a7a93ac167cdcdf28b3deb48de86bcbd2dfedb1`. The rule fixes one class-by-horizon adjustment, its global-by-horizon control, minimum 20 cells/two prior origins, signed 90th-percentile tail expansions, five later origins, bootstrap, and promotion gate before this run. This is a frozen retrospective follow-up, not a prospective preregistration: those five origin dates had already been evaluated in earlier work.

The grouped and global arms must share identical drift base forecasts, unchanged medians, and a drift-only residual archive. Their contrast can isolate this grouping change within the retrospective replay. The existing-v1 comparator uses a different, mixed-policy archive as well as a different hierarchy, so its contrast cannot isolate grouping alone. Calibration eligibility must require both historical origin and target strictly before the prediction origin. Later evaluation origins may legitimately contribute matured errors to subsequent origins; they are not five independent frozen holdouts.

The promotion gate is appropriately stricter than improving pooled loss or coverage: the paired loss-difference interval's upper endpoint must be strictly negative against both global and existing-v1, and mean-series skill against drift must be nonnegative and at least as high as both comparators. No post-result rule tuning is allowed. Neither existing forecast file may change.

A five-origin paired bootstrap is only descriptive. Resampling entire dates preserves within-date pairing but cannot create independent information or cure serial dependence, correlated series, retrospective design, or small cluster count. A passing gate would remain insufficient proof of future performance or the unavailable November score.

## Prior optimistic claim challenged

The earlier drift-base diagnostic reported +4.2657% pooled skill against drift but -1.6274% mean-series skill. Wider intervals and improved dollar-weighted loss therefore did not establish broad superiority. Any recommendation must show group harms, series concentration, and the new gate outcome rather than select coverage and pooled skill alone.

## Result verification

The implementation matches the frozen design. Both arms call `widen` with the same drift frame as current base and archive. Original `starter/scorer.py` scores written CSVs with no baseline fillers; comparisons and bootstrap consume its emitted losses rather than implementing a new loss function. The existing-v1 arm calls the earlier calibration function unchanged. Four tests passed independently, including truncation and extreme future-truth perturbations for each later origin, sparse fallback, median preservation, explicit archive equivalence, and frozen rule hash. All audit records with a selected pool have maximum target and prior-origin dates strictly below their forecast origin.

All eight official reports share exactly 516 scored cells over five dates and 37 series. Global and grouped written forecasts preserve drift medians exactly. No evidence of tuning was found. A first-run provenance failure was a filename error (`common.py` versus `_common.py`), fixed without changing the rule or result-dependent parameters.

| Method | Pooled skill vs drift | Mean-series skill vs drift | Coverage |
|---|---:|---:|---:|
| Drift | 0% | 0% | 58.14% |
| Global | 5.7142% | 3.1761% | 71.12% |
| Grouped | 5.1169% | 2.8785% | 73.26% |
| Existing v1 | 7.2136% | 2.2322% | 74.81% |

Independently recomputed the frozen paired-origin bootstrap directly from official per-cell losses. Grouped minus global mean loss is **+0.000180586**, 95% interval **[-0.000062115, +0.000468335]**. Grouped minus existing v1 is **+0.000633830**, interval **[-0.00034835, +0.00222758]**. Both upper endpoints fail the required negative bound; grouped also fails mean-series parity with global. **Do not promote a new grouped candidate.** The observed drift improvement has interval [-0.00275536, -0.00065725], but five retrospective dependent dates do not support a strong generalization claim.

## Harms and concentration

Against global, grouping improves 16 series, harms 20, and ties one in official mean loss. Class pooled skill improves for hyperscaler spot (1.31% to 5.49%), but worsens for neocloud rate cards (5.95% to 5.11%) and neocloud spot (10.00% to 8.32%); marketplace ask is unchanged. Seven-day pooled skill worsens from 7.08% to 5.55%. FastGPU and gpurentalprices both worsen in pooled loss. Thus extra coverage does not establish a better forecast distribution.

Against drift, grouped improves 29 series and harms eight. Marketplace ask has -2.30% pooled skill, and afhubbard -1.36%. Neocloud spot illustrates the pooled-versus-average problem particularly clearly: +8.32% pooled skill but **-11.86% mean-series skill**; FastGPU A100 80GB spot has -133.17% series skill versus drift, despite a small absolute loss contribution. One-day mean-series skill is -3.06%. Grouped rate-card coverage remains only 66.02%, while marketplace coverage was already 100% before widening.

The two largest grouped-versus-global harm contributions are FastGPU B300 rate card (+0.000084) and gpurentalprices B300 rate card (+0.000066), together about 83% of the net pooled loss increase. Against existing v1, FastGPU B300 and B200 rate cards contribute roughly +0.000437 and +0.000393; other series offset part of that harm. Dropping any single series leaves grouped worse than global (loss differences +0.000100 to +0.000245) and existing v1 (+0.000203 to +0.000756). The rejection is not reversed by one influential series. Against drift the two largest gains contribute about 28% of the net reduction, and all leave-one-series-out comparisons still improve pooled loss. These facts support a mixed historical gain against drift, not grouped dominance over available calibration alternatives.

## Protected artifacts

Rechecked unchanged SHA-256 values after scoring:

- `forecasts.csv`: `62ea5d18a77f4fd509ac96d9518c1d448ee777fa5839e380a0689d074a5eae31`.
- `forecasts_calibrated.csv`: `226f58a63771488290a8073579853ec9e64189ac2e7a4c99d706db6c370fe59d`.
- Frozen rule: `09215e984505bd5996488e8d0a7a93ac167cdcdf28b3deb48de86bcbd2dfedb1`.

Recommendation: retain both existing files unchanged and publish this negative group-comparison result. Do not call the five later dates a fresh holdout, claim all groups benefit, or treat improved coverage as sufficient for promotion.

Final `summary.json` reconciled with the independent checks: both CI gates and mean-series parity with global are false; mean-series parity with existing v1 and nonnegative skill are true; `promoted` is false. Protected before/after hashes match, and no `forecasts_group_calibrated.csv` was created.

## Selected-submission public UI appendix

Automated self-review of the selected-submission deployment at `https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/`. Direct public downloads byte-match `deliverables/deploy_demo` for index, data, README and selected CSV. Public index SHA-256: `4e2ccabd80dbce9bd2dcc00f385817d292c390da23963fd5d45272e6f58a2d73`; data: `19e4d9e6601b29c865c2f9470994f4a2d1373f705e2e8ff88f6dc026812d1277`. Selected CSV retains `226f58a63771488290a8073579853ec9e64189ac2e7a4c99d706db6c370fe59d`.

A fresh Chromium visit rendered 75.42% coverage, +4.323% historical drift skill, and `forecasts_calibrated.csv — wider price ranges`. Every one of the 111 explorer data rows matches the selected CSV, including all three quantiles. Download choice and explorer therefore agree. The original uncalibrated file remains available and clearly marked before calibration.

The visible warning and comparison distinguish the original-agent calibration study from the drift-only diagnostic (+4.266%, mean-series 1.63% worse). They disclose the [-0.82%, +7.02%] uncertainty range, 74.1% widening, and unavailable November outcomes. README additionally states the main study's mean-series result is 1.62% worse, avoiding conflation. Headline metrics agree with saved official reports; they are not represented as measured November submission outcomes. The comparison table rounds to one decimal, while headline and caveat retain their stated precision.

Research rows display plain method names and plain rejection explanations; raw recorded reasons and confidence intervals are inside closed Details. Playback explicitly reveals saved experiments and neither runs a new experiment nor plays video. Exa's visible statement reports 13 actual main-loop calls and 13 source-bearing rounds. Shared-memory wording reports 54/54 accuracy tied with local lookup, slower operation, and no established cost savings. Public source contains the automated-self-review disclosure, and README explicitly distinguishes human-prompted calibration follow-ups from autonomous discoveries. The grouped follow-up remains described as rejected and retrospective.

One navigation finding remains in this reviewed snapshot: README links `docs/GROUP_CALIBRATION_STUDY.md`, `docs/CALIBRATION_STUDY.md`, and `data/headline_series_audit.csv` return HTTP 404 when followed from the public README. They are repository-relative documentation links, but those paths are not in the public deployment. Reported to the root agent for correction; this does not affect selected forecast downloads or their values. Full cross-tab/mobile regression is being performed separately by the root agent and is not claimed by this targeted review.
