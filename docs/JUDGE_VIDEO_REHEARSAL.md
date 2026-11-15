# Judge-panel video rehearsal

This is **simulated critique and automated self-review**, produced by a separately tasked agent in the same build system. No judge participated, no endorsement is implied, and these are not predicted official scores. Role-based questions below use only the supplied biographies; they do not assert private preferences or opinions.

Reviewed: README, submission draft, recording and narration scripts, final narration metadata, decoded video frames, and an independent automatic transcription of the actual muxed audio. Review date: November 15, 2026.

## Assessment against the five equally weighted criteria

| Criterion | What the two-minute viewer receives | Remaining limitation |
|---|---|---|
| Rigour | Historical coverage and error gains immediately paired with uncertainty; human-guided calibration disclosed; rejected studies and unchanged submission shown. | Retrospective selection and later failed checks prevent a general superiority claim. The short video cannot explain every protocol limitation. |
| Novelty | A concrete measurement question: a matching observed record can stay unchanged while the category median moves. | This is evidence about index composition, not proof of a new causal pricing model or an executable fixed contract. |
| Results | Coverage improves roughly 65% to 75%; combined historical error falls 4.3%; middle predictions remain unchanged. | Future accuracy is unproven. The 80% coverage target remains unmet. These are historical results, not competition outcomes. |
| Autonomy and self-improvement | Four roles propose, test, record and share bounded ideas; failures remain visible. Human-guided follow-up is explicitly identified. | Reliable autonomous forecasting improvement was not established. Showing a bounded process is stronger than implying open-ended self-improvement. |
| Interpretability and reproducibility | Forecast colours explained; scenarios distinguished from observations; sources, protocols, official scores and offline command available. | Setup requires dependencies and the organiser's data pack. Replaying cached calls does not independently reproduce model behaviour from fresh API calls. |

The most defensible pitch is a falsifiable research workflow plus a useful measurement diagnosis. It is not a proven forecast winner. The revised narration preserves that distinction.

## Role-grounded simulated panel questions

- **Jamie Pinheiro, Jane Street research software / large real-time financial data:** Does the measurement represent a stable instrument or a changing collection of listings? The opening example gives a concrete answer. A careful follow-up should explain that matching observed records are not established executable contracts.
- **Mehdi Djabri, past.dev CEO:** Which agent wrote a finding, which other agent read it, and what changed? The sponsor scene identifies three writers and two readers. The evidence should be opened for an actual cross-agent record if asked. Equal lookup accuracy, worse latency and unestablished cost savings must remain explicit.
- **Jerel Velarde, CopilotKit applied AI:** What does the agent workflow do, and where does a human intervene? The revised 16–38 and 38–52 second segments answer this much more clearly than the first draft.
- **Long Do, OpenAI MTS; Chen Yang, Scale senior research engineer:** What is the baseline, how are leakage and selection handled, and do gains hold on fresh dates? The error/uncertainty narration and frozen protocols support inspection, while later failed checks constrain the claim. Their job titles alone do not justify guessing more specific personal preferences.
- **Miguel Gonzalez, Browserbase technical lead:** Is this an actual working interface, and can the displayed actions be followed? The recording shows real browser tab changes, a selected series and reproduction instructions. It is a saved walkthrough, not evidence of fresh research executing during playback.
- **Nare Janvelyan, Voyager; Michelangelo Valtancoli, Chaotica:** What practical decision can this research support? Separating a category index from a specific GPU rental configuration provides a plausible valuation use case. Scenario estimates are not validated commercial returns, customer evidence or resale-price predictions.
- **Judges with limited biographies:** Use the published equal-weight criteria. Do not invent personalised motivations.

## Revisions requested and incorporated

1. Explicitly identify calibration as human-guided, preserving the autonomy boundary.
2. Say ninety-four cents **per GPU hour**, avoiding an ambiguous money amount.
3. Distinguish bounded agent-loop proposals from later human-guided model studies.
4. Lead and close with the measurement insight while retaining the uncertainty and no-proven-victory caveats.

## Initial media checks (prior version)

Final file reviewed: `artifacts/submission/demo-narrated.webm`.
SHA-256: `eb96430a1306a235c927855107c2922fda892bed1a49211f0e2abb4d8d84f5ce`.

- Full FFmpeg decode completed without errors. Video: 1920×1080, VP9, 25 fps. Audio: Opus, mono, 48 kHz. Video duration 112.280 seconds; container/audio duration approximately 112.288 seconds, safely under two minutes.
- Independent Whisper transcription of the audio extracted from the final video recovers the complete narrative, including human-guided calibration, uncertainty, the slower memory comparison, unavailable future observations, scenario qualification and the final no-proven-victory sentence. Evidence: `artifacts/submission/judge-transcription.json`. This is automatic speech recognition, not a claim of human listening; its word timestamps are approximate and can extend beyond actual audio duration.
- Sampled frames at 16, 38, 65, 81 and 96 seconds show the learning chart, rejected research log, H100 explorer, economics and reproduction scenes corresponding to the narration. A broader contact sheet also shows the measurement and sponsor scenes in order.
- Large burned-in explanatory overlays are visible. They summarise the scenes; they are **not verbatim speech subtitles**, and the file has no separate subtitle stream. Describe the deliverable as a narrated walkthrough with explanatory on-screen captions.
- One-second sampling found the initial loading frame white and no subsequent white or black frames. This is a short startup polish issue, not missing middle content. An older saved `video-frame-20.png` is blank; fresh decoding of the current video at that timestamp shows the chart, so that stale image is not evidence of a current 20-second blank.
- Speech recognition rendered Exa as “Exer” and past.dev as “pass.dev”. Proper-name recognition is imperfect; sponsor names are spelled correctly on screen. No substantive quantitative claim was lost in transcription.

No blocking media or factual issue found after the revisions. Small UI body text requires full-screen viewing; the narration and larger overlays carry the essential story. This review did not alter forecasts, model files, app code or the recording scripts.

## Highlight revision review

The subsequent user-requested revision promotes **4.323% lower historical error** and the **2029 rental outlook** across the hero and submission description. This supersedes the earlier measurement-first editorial emphasis; the media hash above identifies the earlier recording only.

Independently opened the deployed public site at 1920×1080, 1366×768 and 390×844. At all three sizes, both highlights appear on the first screen with readable adjacent qualifications. No document horizontal overflow or headline clipping was detected. The 95% interval, lack of confirmation on later November checks, human-guided calibration label and assumption-based 2029 label remain visible. The README and submission description use the same qualified claims. Approved for recapture.

Reviewed revised narration source: exact 4.323% opens the video, the calibration scene retains unchanged middle predictions and failed later checks, and the economics scene speaks the H100 $0.98–$2.59 and A100 $0.42–$1.20 hourly ranges. Recommended keeping “After setup” in the closing reproduction line. This paragraph is a source/UI review; the revised rendered recording needs its own final media check before publication.

## Highlight recording approval (prior version)

The highlight revision was independently checked after rendering. Final reviewed file: `artifacts/submission/demo-narrated.webm`; SHA-256 `5924d7869b3183b67bbd94e459159c1d43b79ca85988ef3d46abd003c2bc82c1`. Video duration **108.12 seconds**. Full video/audio decoding succeeded without errors.

A new automatic transcription extracted from this actual muxed file replaces the earlier `artifacts/submission/judge-transcription.json`. It confirms the opening **4.323%** figure, immediate uncertainty caveat, human-guided calibration, unchanged middle estimates, failure of later November checks, and spoken **2029 H100 $0.98–$2.59 / A100 $0.42–$1.20 per GPU-hour** ranges. It also recovers the assumption-based qualification, “After setup” and the final no-proven-victory sentence. ASR still imperfectly renders the past.dev name, which is correctly spelled on screen.

Frames sampled two seconds into the opening, calibration, economics and reproduction segments show matching content and explanatory overlays. The opening presents both requested highlights; the economics overlay repeats the spoken ranges and their limitation. The corresponding scene starts are approximately 0, 20.95, 74.21 and 88.26 seconds. This is sampled visual alignment plus full automatic speech transcription, not a claim of human listening or frame-by-frame manual review.

**Approved: no blocking factual, duration, audio or sampled synchronization issue found.** Earlier 112-second media metadata in this document is historical and does not describe this final revision. No forecasts or application files were changed by the reviewer.

## Upright headline layout check

After the final cosmetic request, the deployed headline was checked again at 1920×1080, 1366×768 and 390×844. At the two desktop sizes its height equals one computed line height (50.39/50.4 pixels and 42.61/42.62 pixels respectively). The headline contains no forced break or emphasis element; computed style is upright sans-serif. At 390 pixels it wraps naturally to two lines without horizontal overflow. Both highlighted results and their qualifications remain in the first screen. Approved for the final screenshot and opening-frame replacement; this check does not itself verify the subsequently encoded media.

## Opening-only replacement verification (prior version)

Final encoded deliverable reviewed: `artifacts/submission/demo-final.webm`, SHA-256 `79691880d4a84511d968783ef5adfe1d85197517a0fe9cdf01f273c5a1ca6022`. Full decode succeeds; video remains **108.12 seconds**. Decoded signed-16-bit PCM audio is byte-identical to the previously transcribed narration, SHA-256 `5ba018f7759d5983b953f093249235edbb1f60f1f3c5d98df23e1ded21857677`; no new speech-recognition call was necessary.

The two-second frame shows the updated upright, single-line headline and the 2029 outlook. The 15-second frame correctly shows the measurement scene and matching explanatory overlay. Only the opening through approximately 12.923 seconds was replaced: subsequent footage retains the earlier typography, including its italic, two-line hero when visible. This is consistent with the opening-only edit scope, not a claim that every frame has the new typography. No blocking decode, audio, duration or sampled transition issue found.


## Current final deliverable verification

The opening screenshot was extended through approximately **20.945 seconds**, including the measurement explanation, before replay begins. Current `artifacts/submission/demo-final.webm` SHA-256: `7201d69b7f35333cd1a3f1b0b7420a29ac0f2901813c02e2303e308dcdc9af16`. All earlier media hashes in this report identify prior versions.

Full decode succeeds at **108.12 seconds**. Decoded audio retains the identical PCM hash `5ba018f7759d5983b953f093249235edbb1f60f1f3c5d98df23e1ded21857677`. The 15-second frame now shows the upright single-line headline, 2029 outlook and complete matching-record comparison table. The earlier typography reappearance in that scene is resolved. The replaced segment uses the page screenshot rather than the old explanatory overlay; the page itself supplies the claims and caveats. **Approved, with no blocking issue found.**

## Final concise-narration revision

Current reviewed final file SHA-256: `3104a3c949f039cbd7e986bfef9aee47e2346022e5f91fc8c2d92967ad61f9a0`. This supersedes the media versions above. Full decode passes at **108.12 seconds**.

New automatic transcription of the actual final muxed audio replaces `artifacts/submission/judge-transcription.json`. Both user-requested spoken phrases—“The gain is uncertain” and “The uncertainty includes no improvement”—are absent. The complete narration remains recoverable without an apparent cut-off, including exact 4.323%, human-guided calibration, unchanged middle estimates, later November checks not confirming the gain, the 2029 ranges and scenario qualification, and the closing no-proven-victory sentence.

The actual opening frame retains the adjacent on-screen uncertainty interval, failed-November qualification and assumption-based 2029 label. Only the requested spoken repetitions were removed; the visible qualifications remain. **Approved: no blocking media or factual issue identified.** Speech verification is automatic transcription, not human listening.

## Footer qualification revision

Reviewed the subsequent user-requested move of the exact hero qualification paragraph into a 12px global page footer, linked by a superscript 1 from the headline. The historical-result / human-guided-calibration label remains above the headline. This supersedes earlier descriptions of an immediately adjacent uncertainty paragraph.

On the deployed site, the headline remains one line at 1920×1080 and 1366×768. At 390×844 it wraps naturally to three lines with the footnote link; no horizontal overflow is present. After initial page rendering settles, clicking the accessible “Read forecast result qualifications” link changes the fragment to `#forecast-caveat` and displays the entire caveat at all three sizes (vertical bounds approximately 955–974, 624–662 and 663–739 pixels respectively). Exact wording and numeric interval are retained.

Minor edge case: clicking immediately when the first metric populates can land short of the footer because later asynchronous layout expands the page. Waiting for the initial layout to settle produces the correct anchor position. This finding was reported to the build agent. Settled-page layout and anchor approved for screenshot capture; no application files were edited by this reviewer. This remains automated self-review, not actual judge feedback.

## Final footer-version media verification

Current final video SHA-256: `24c2188b8e981188cba88249157bf2f6cad2567ae5a3277ea5f9c78469cce221`. This supersedes previous final-media hashes above. Full decode passes at **108.12 seconds**. Decoded PCM audio is identical to the already transcribed concise narration: SHA-256 `191e0c3b08f46895c3e88b1fd9f3e88f5e25ab57d6a5ca5f46c10966d06af464` in both current final and narrated source files.

The actual two-second video frame shows the upright single-line headline with superscript 1, the 2029 scenario card and the discovery table. The moved caveat paragraph is absent from the hero as requested; its full wording remains linked in the live site's footer, as separately verified above. The screenshot-based opening does not itself make that link interactive. No new numeric claim or audio change was introduced in this revision. **Media verification approved.**
