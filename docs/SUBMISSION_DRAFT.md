# Final submission form

## Project Title
GPU Value Scientist

## Description
GPU Value Scientist is an AI research team that forecasts GPU rental prices, tests its own ideas, and preserves the evidence—including failures.

Four roles—Analyst, Forecaster, Critic and Researcher—use OpenAI models, Exa searches inside the research loop, shared past.dev memory, and Modal parallel experiments. Built in the Originator cloud workspace, the public demo shows predictions, sources, decisions and rejected hypotheses.

Our strongest research finding challenges what a GPU price index measures. A reproducible audit reconstructed 2,837 daily medians from 444,663 observations. In one H100 marketplace category, the median moved $1.90 → $0.94 → $2.23 while a matching observed price record stayed at $0.94. Changes in the observed listings can move the index without that matching record changing price—a distinction that matters when valuing a specific GPU configuration.

A human-guided calibration step broadened prediction ranges without changing their middle estimates. Historical coverage rose from 64.70% to 75.42%, with 4.323% lower combined forecast error than Pacific’s drift baseline. However, the confidence interval includes no improvement, and later checks did not confirm the gain. We rejected two subsequent forecasting approaches that failed their adoption tests and preserved the frozen submission.

The demo also presents evidence-informed, assumption-based 2028–2029 scenarios for H100 and A100 rentals and equipment values. Exa ran inside the research loop; multiple agents wrote to and read from past.dev; eight experiment jobs ran on Modal. Memory retrieval matched local lookup on accuracy but was slower, with no established cost savings.

After installing the supplied data pack and dependencies, one command reproduces the saved forecasts offline. Code, experiment protocols, official scores, sources and verification artifacts are public.

## Track
Recursive Self-Improvement by Pacific — Direction A: self-improving forecasts

## Challenges
- Exa: select. Thirteen actual Exa requests ran inside the recorded research loop; source-bearing decisions can be inspected in Sources & sponsors.
- Modal: select. Eight experiment jobs ran on Modal; Modal also hosts the persistent public site.
- past.dev: used and disclosed in the description, but the form’s stricter requirement to demonstrate better accuracy, latency and cost is not met. Both past.dev and local lookup returned 54/54 correct answers; past.dev was slower, and cost savings are not established. Do not claim those gains.
- Originator: separate challenge; work occurred in Ori. Entry and official judging status have not been independently verified.

## Project Screenshot
Use the final 1920×1080 `project-screenshot.png`, captured only after the complete nontechnical copy review passed.
Public file: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/project-screenshot.png

## GitHub URL
https://github.com/yfandev/gpu-value-scientist

Default branch: `main`. Published as `yfandev`.

## Demo video
Public download: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/demo.webm

This is a 1 minute 52 second (112.28 seconds), 1920×1080 browser recording with spoken AI-generated narration and captions. The judging brief names YouTube, Drive or Loom; the direct WebM link is not one of those hosts. No connected uploader is available in this workspace.

To get a compliant Drive link:
1. Open the public video, right-click the video and choose **Save video as…**; save `demo.webm`.
2. Open https://drive.google.com and click **New → File upload**; choose the saved video.
3. After upload, right-click the file and choose **Share → Share**.
4. Under **General access**, change **Restricted** to **Anyone with the link**; keep **Viewer**, click **Copy link**, then **Done**.
5. Open that copied link in a private/incognito browser window and verify playback without signing in. Paste that Drive link into the submission form.

## Selected forecast
`forecasts_calibrated.csv`, 111 rows across 37 advertised-rental categories, input cutoff November 6, 2026; target dates November 7, 9 and 13. The original `forecasts.csv` remains unchanged. `forecasts_extended.csv` adds AWS history-based forecasts outside the competition’s scored target set and is not the selected submission.
