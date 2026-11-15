# Two-minute stage flow

Open the public page before taking the stage. Confirm it names `forecasts_calibrated.csv`, shows75.42% coverage and4.323% historical error reduction, and displays the uncertainty caveat. The site keeps one Modal web container warm; interactions replay saved results and do not wait for model calls.

- **0:00–0:20 — Problem and result.** “GPU rentals are hard to price. We built an AI research team that tests ideas and keeps failures visible. Our selected wider ranges cover75.42% of historical outcomes, up from64.70%. The error reduction is uncertain and some rental categories get worse.”
- **0:20–0:45 — Actual research loop.** Click “Replay saved research results.” Say explicitly this is the original agent experiment before calibration. Explain the three ideas listed above the chart. The button reveals saved results; it does not run a new experiment or play a video.
- **0:45–1:10 — Evidence and collaboration.** Open “Sources & sponsors.” Show13 verified Exa calls and actual past.dev writers/readers. Say memory matched local lookup54/54 but was slower, with no cost savings established.
- **1:10–1:30 — Reject a tempting idea.** Return to the rejected experiments or explain the group-specific follow-up. “Separate rules for rental groups sounded better, but lost to global widening and failed our promotion rule. We kept the selected file unchanged.” Calibration follow-ups came from human feedback; do not call them autonomous discoveries.
- **1:30–1:50 — Concrete output.** Open “Forecast explorer.” Show an H100 category and its November7,9,13 estimates. The explorer displays the selected calibrated CSV. Thirty-seven categories times three dates gives111 predictions.
- **1:50–2:00 — Reproduction.** Show `./reproduce.sh`. “Every result comes from Pacific’s scorer. The repo includes saved decisions, sources, failed experiments and offline reproduction.”

Do not describe historical results as November judging scores. If a live page fails, use the downloaded captioned video and CSV; label that fallback as a recording. Do not claim novelty of standard quantile calibration or claim an official award.
