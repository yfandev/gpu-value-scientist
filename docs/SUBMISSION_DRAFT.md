# Submission form draft

Project Title
GPU Value Scientist

Description
GPU Value Scientist is an auditable AI research loop for GPU rental prices. Four OpenAI agents propose bounded forecasting hypotheses, search Exa for dated evidence inside the main loop, share findings and critiques through past.dev, and test ideas on later forecast origins before adopting them. Every source, decision, rejected hypothesis, and uncertainty estimate is inspectable in the demo.

Built for Pacific's GPU Value challenge, it produces positive, ordered q10/q50/q90 forecasts at 1-, 3-, and 7-day horizons from the November 6 cutoff. The unmodified Pacific scorer supplies all official metrics. A strict cutoff-refusal test and offline, byte-identical reproduction make the results checkable. The system keeps drift when improvement is not established, and separates argued 2028–2029 rental/resale scenarios from scored short-horizon forecasts.

Sponsor technology: OpenAI for four strict-JSON research roles; Exa for origin-filtered source discovery that informs hypotheses; past.dev for real cross-agent shared memory; Modal for eight parallel experiment jobs and a public, independently hosted demo. Development and validation were performed in an Originator/ori cloud workspace. No accuracy, latency, or cost benefit from memory is claimed without a matched comparison.

Track
Recursive Self-Improvement by Pacific — Direction A: self-improving GPU price forecasts.

Challenges
- Exa: actual main-loop calls and source-to-hypothesis trail verified; public repository available at https://github.com/yfandev/gpu-value-scientist.
- Modal: eight actual remote experiment jobs and public demo deployment verified.
- past.dev: multiple live writers/readers and cross-agent use verified. The detailed brief says gains are not required; the form says to prove accuracy/latency/cost gains. Those gains are NOT established. Do not claim them.

Project Screenshot
Download the 16:9 screenshot: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/project-screenshot.png

GitHub URL
https://github.com/yfandev/gpu-value-scientist

Public website
https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/

Demo Link (YouTube/Loom)
Recorded captioned walkthrough: https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/demo.webm . This is a direct video, not a YouTube or Loom upload.

Optional calibrated submission improves historical coverage to75.42% and measured pooled skill vs drift to4.323%, but uncertainty includes no improvement and some groups worsen. Original forecasts stay unchanged. See docs/CALIBRATION_STUDY.md; no final November performance claim.
