# Narrated demo

The public `demo.webm` is the final 112.28-second browser capture with captions and an AI-generated OpenAI `gpt-4o-mini-tts` / `coral` voice. The opening explicitly discloses the synthetic voice. No judge endorsed this presentation.

`narration-script.json` records the spoken text and scene timestamps. `narrate_demo.py` generates and caches speech, fits each segment to its existing scene, and muxes Opus audio without re-encoding the video. `audio-validation.json` checks an audible audio stream in every scene. The cached WAV files are local, excluded from Git; rebuilding speech makes API calls and may sound different.

To rebuild after capturing the silent walkthrough:

```bash
.venv/bin/pip install -r requirements-video.txt
.venv/bin/python -B artifacts/submission/narrate_demo.py
.venv/bin/python -B artifacts/submission/check_narrated_demo.py
```

Requires the project's existing OpenAI dependency and `OPENAI_API_KEY`. This affects presentation assets only, never competition forecasts. `demo-silent.webm` is the preserved input capture; remove it before narrating a newly recorded capture. The output is `artifacts/submission/demo-narrated.webm`; only publish after review.
