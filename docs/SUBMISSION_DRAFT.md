# Final submission form

## Project Title
GPU Value Scientist

## Description
GPU Value Scientist tests GPU rental-price forecasts—and investigates what the price data actually measures.

Built with OpenAI agents, Exa searches inside the research loop, shared past.dev memory, and Modal parallel experiments and public hosting, the system preserves hypotheses, tests, sources and rejected ideas. Development took place in the Ori cloud workspace.

A separately frozen data audit reconstructed 2,837 daily medians from 444,663 observations. In one H100 marketplace category, the median moved $1.90 → $0.94 → $2.23 while the matching observed price record stayed at $0.94. Changing observed entries can move an index without that record changing price; this does not prove that all market movements are artificial.

Earlier forecast-range widening improved historical coverage from 64.70% to 75.42%, with 4.323% lower combined error than Pacific’s drift method. The uncertainty interval includes no improvement, and additional November checks did not confirm the gain. A new price-reset model and a follow-up combination failed their promotion rules, so the frozen submission was preserved.

The demo exposes the evidence, official scoring, decisions and failures, plus assumption-based 2028–2029 H100/A100 rental and equipment-value scenarios. After installing the supplied pack and dependencies, one command reproduces the saved forecasts offline; the separate measurement study has reproducible scripts and automated verification.

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

This is a 1 minute 52 second (112.28 seconds), 1920×1080 captioned browser recording, without audio. The judging brief names YouTube, Drive or Loom; the direct WebM link is not one of those hosts. No connected uploader is available in this workspace.

To get a compliant Drive link:
1. Open the public video, right-click the video and choose **Save video as…**; save `demo.webm`.
2. Open https://drive.google.com and click **New → File upload**; choose the saved video.
3. After upload, right-click the file and choose **Share → Share**.
4. Under **General access**, change **Restricted** to **Anyone with the link**; keep **Viewer**, click **Copy link**, then **Done**.
5. Open that copied link in a private/incognito browser window and verify playback without signing in. Paste that Drive link into the submission form.

## Selected forecast
`forecasts_calibrated.csv`, 111 rows across 37 advertised-rental categories, input cutoff November 6, 2026; target dates November 7, 9 and 13. The original `forecasts.csv` remains unchanged. `forecasts_extended.csv` adds AWS history-based forecasts outside the competition’s scored target set and is not the selected submission.
