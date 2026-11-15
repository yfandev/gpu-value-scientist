# A promising prediction change failed its additional-date check

The selected competition file remains `forecasts_calibrated.csv`; no new candidate was promoted. Both investigations below were frozen before their own results, used Pacific’s unchanged scorer, and preserve all negative results. The follow-up was designed after seeing the first study, so it is a sequential, retrospective research process—not independent confirmation.

## Question and model

Can the age of a posted price and changes in related GPU prices predict a price reset? The model learns an empirical distribution of future price changes, including an exact probability mass for no change. It uses only observations and matured outcomes before each forecast date. Its settings, peer definition, sparse-data fallback, dates, and adoption gates are frozen in `results/price_reset_study/protocol.json` (SHA256 `577025ea38996e03eda04038a2ebba71b6074b5afea493be049a651d60b73c46`). This is new to this project; no claim is made that nearest-neighbor or hurdle distributions are novel statistical inventions.

One predeclared ablation removes the peer features. Peer information improved the full-distribution error score but slightly worsened the middle-price error versus the ablation; do not attribute the middle-price gain specifically to peers.

## What happened

On five predeclared later dates, 516 identical scored predictions:

- Reset model: **6.334% less combined error than Pacific drift**, paired origin-bootstrap 95% interval **4.755% to 10.782%**.
- Existing selected calibration: **7.254% less error than drift** on those same dates.
- Reset model therefore had **0.992% more error than selected calibration**, and coverage was **68.99% versus 74.81%**. It failed adoption.
- Middle-price error improved against both controls, with positive bootstrap improvement intervals. Mean-category drift skill was **+6.244%**, versus **+2.266%** for selected calibration.

On all 14 historical dates, reset skill was **4.986%**, versus selected calibration’s **4.323%**. This secondary result cannot override the predeclared later-date failure. These dates had already been inspected in earlier project work; the intervals do not establish independent future performance.

## Evidence-driven follow-up and falsification

The single follow-up kept the existing calibrated lower/upper bounds and replaced only the middle estimate with the learned reset-model median, expanding a bound only if needed to keep the quantiles ordered. Its protocol is `results/reset_median_followup/protocol.json` (SHA256 `baa340570fab8c722698ff536808142af1e5a60687b516e0c77bc2304920f4aa`).

It looked better on the old primary dates: **8.403% less error than drift**, **1.238% less than selected calibration**. But additional, previously unscored November 1–3 forecast origins at horizons 1 and 3 days reversed the result across 222 scored predictions:

| November backtest | Combined error versus Pacific drift |
|---|---:|
| Existing selected calibration | **1.488% higher** |
| Learned median plus calibrated ranges | **2.610% higher** |

The follow-up was **1.106% worse than selected calibration**, failed its declared gate, and was rejected. No `forecasts_reset_median.csv` was created. These November prices already existed in the pack and November 6 prices had been used as economic anchors; this is newly scored data, not a truly untouched dataset. The three origins overlap some outcomes, so no statistical significance claim is made from this small check. These are not the final November 7, 9 and 13 submission outcomes.

## Verification and reproduction

A separately tasked automated reviewer reproduced the pooled scores and origin-bootstrap intervals, checked identical scored cells, confirmed the original residual archive was used for November calibration, and ran future truncation/perturbation, missing-day, filled-row, peer-membership and quantile-ordering checks. This is automated self-review by the build agent, not external certification.

After installing the project dependencies and supplied data pack:

```bash
.venv/bin/python -B src/price_reset_study.py
.venv/bin/python -B src/reset_median_followup.py
```

Raw forecasts, official reports, scored cells, protocols, guard results and audits are retained in the two study directories. Candidate code reads the unchanged pack and writes outside it. The existing three competition forecast files remain byte-identical.

The lesson is not that a different-looking price line wins. Better middle estimates on inspected dates did not guarantee better uncertainty ranges or continued gains on additional dates. The research process prevented that apparent improvement from silently replacing the frozen submission.
