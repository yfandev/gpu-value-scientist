# Final impatient-judge review

Date: 2026-11-15. **Automated self-review by a separately tasked build-system agent, not external independent validation or official judging.** Perspective: an impatient, nontechnical visitor with no project background. No research experiments were run; no application files were changed by this reviewer.

Reviewed `demo/index.html`, `artifacts/submission/record_demo.py`, and the deployed site at https://y-fan-development--gpu-value-scientist-demo-site.us-east.modal.run/ using Chromium through the repository's `.venv` Playwright. Confirmed deployed legend: “Green: predictions after broadening the price ranges.” Inspected rendered desktop replay and mobile landing screenshots in memory; these were not saved as deliverables.

## Verdict

No blocking site defect found. The central story is understandable: AI agents tried GPU rental-price forecasting ideas, their original ranges were too narrow, and a human-guided follow-up broadened them. More historical prices fit inside those ranges, but reliable forecast improvement remains unproven. This is honest and comprehensible. The main presentation weakness is the amount of text before and around the chart; the recorded captions provide a useful guided path.

The recording timing issue found in the initial script has been fixed: the replay now holds for 21 seconds, enough for 14 rounds at 1.4-second intervals to reach the endpoint and stop. I re-read the updated script. The parent also identified and fixed a smaller-stage scroll issue; I verified the deployed fix at 1366×768: replay scrolls to the chart itself, with chart and controls visible together. No remaining blocker was found.

## Measured evidence

- Public navigation reached network idle in 1.493 seconds in one fresh browser context from this workspace. Browser navigation timings: DOM content loaded 450 ms, load complete 476 ms. A separate initial request populated the main metric within 1.322 seconds. These are individual observations, not a cold-start SLA or a consumer-network benchmark.
- Zero JavaScript page errors and zero HTTP responses at status 400 or above during the full navigation/interaction pass.
- All six tabs activated their matching panel at 1440×900, 390×844 and 320×740. Document scroll width exactly equaled viewport width in all 18 combinations. Wide tables and the mobile tab bar use local horizontal scrolling; absence of document overflow does not mean every table column fits on screen.
- Overview panel height: 2867 px at desktop, 6013 px at 390 px, and 7010 px at 320 px. This quantitatively supports the density concern.
- Research log's “Not adopted” filter returned 10 rows. A nonsense search produced a clear empty-state message.
- Forecast explorer's H100 search returned six categories. Selecting the advertised H100 SXM 80GB category displayed all three forecast dates (November 7, 9 and 13) and ordered lower/middle/upper values.
- Opening the first source round exposed its query, dated sources and linked Analyst/Critic notes, with a warning that original AI notes may contain mistakes.
- Replay controls worked: reset displayed “READY TO REPLAY · 14 RECORDED TESTS”; stepping displayed test 1; replay progressed to test 3 after 2.5 seconds from that state.

## Six-tab reading

| Tab | Nontechnical interpretation and finding |
| --- | --- |
| Overview | Clear opening definition of a GPU and practical budgeting audience. Coverage improvement is distinguished from better prediction. The new $0.94 matching-record example gives a concrete explanation of why an index may move when observed entries change. Several competing numerical summaries make impatient reading harder. |
| Research log | Plain-language idea names and “not adopted” verdicts are understandable. Rejected ideas remain inspectable. Technical original notes are behind disclosure controls. |
| Forecast explorer | The cost of one GPU-hour is explained. Recorded prices and future estimates share one time axis; November 6 cutoff and overlapping middle estimates are explicitly explained. Lower/middle/upper goals are described without claiming guarantees. |
| Economic view | The 2028–29 numbers are prominently identified as assumptions. Equipment values are income-based scenarios rather than observed resale prices. The 80%-coverage interpretation is explicitly disclaimed for these scenario ranges. |
| Reproduce | Offline versus live modes and credential requirements are clear. One-command replay is qualified by dependency setup. The 80% coverage goal is honestly marked not achieved. I inspected the interface, not reran this research or independently verified its saved checks. |
| Sources & sponsors | Service use is distinguished from service benefit. Exa has 13 recorded requests; past.dev's 54/54 retrieval comparison is explicitly separated from forecast accuracy, with slower retrieval and no established cost savings. Modal shows eight completed jobs. These are interface disclosures, not independent audit findings. |

## Claim honesty and presentation

The page discloses the −0.82% to +7.02% uncertainty range, retrospective development of the widening rule, later November backtests that failed to confirm the gain, missing actual outcomes for final submission dates, and the difference between the autonomous loop and human-guided correction. It does not advertise 75.42% as “prediction accuracy.” Gold is explained as equal forecast error, not equal predicted price. The green/blue before-and-after explanation is clear.

The headline's long-term “we expect” language is balanced immediately by “based on assumptions,” and Economic view explains what those assumptions mean. No material contradiction was found in the inspected public copy. This review does not independently verify the statistical calculations, source provenance, or live-service receipts.

The opening mobile screenshot was readable with no clipped text; buttons and the six-tab strip were usable. Chart labels and supporting details are small on a 1920-pixel recording and may become hard to read when a video is played in a small embedded player. Captions carry the essential message, but the viewer should not be expected to read every chart note.

## Stage flow and captions

The inspected updated recording sequence is coherent: uncertainty correction → concrete measurement example → before/after replay → rejected ideas → recorded sponsor evidence → a named H100 forecast → conditional economics → reproduction. Captions avoid claiming a live run, proven future improvement, or measured resale prices. The measurement caption says a matching record stayed unchanged, without claiming a continuously executable offer.

The script uses 24px captions at 1920×1080 with a dark background and pointer-events disabled, so captions should remain readable without intercepting clicks. The script records silent video; this review does not claim to have watched the final encoded file or checked its final runtime. The updated 21-second replay hold is sufficient by inspection.

### Final stage verification

On the deployed page at 1366×768, the tour handler directly calls `learning-chart.scrollIntoView`. Two seconds after clicking replay, the chart occupied y≈0–307 px and the transport occupied y=448–508 px. Pause, Next test and Start over all occupied y=463–494 px, fully inside the viewport. This verifies the stage scroll fix. The final metric color-only change requested afterward does not change these findings; it was not separately evaluated here.
