# Structured temporal memory benchmark v2

V1 remains intact: both arms achieved 25% exact-match accuracy; past.dev used fewer model tokens but was slower. Its expected records were present: wrong group and kind selection, rather than retrieval absence, caused the observed errors.

V2 compares the same `gpt-4.1-mini`, temperature zero, strict three-field answer schema and revised explicit group/kind instructions in three arms:

- `full_context`: every temporally eligible raw canonical record, with no truncation.
- `local_compact`: locally filter exact group/kind/date and project id, origin, round, group, kind, candidate and verdict. Supply all matching records, not the gold answer.
- `past_dev_compact`: real past.dev recall, canonical `sources[].sourceId` intersection, then the same filtering and projection. Generated memory text is never used as evidence. Missing retrieval records receive no local rescue.

The comparison against full context bundles projection, filtering and retrieval; it cannot isolate a past.dev benefit. The strong local compact arm isolates the value of remote recall given the same projection. This structured lookup can also be answered deterministically without a model; a model-powered memory advantage must not be inferred from this task alone.

The predeclared plan contains 18 fresh questions: every group and both kinds as of August 19 and September 16, plus two July 21 no-history questions. Two repetitions use seed 20261115 to randomize question order and all three arms within each pair: 108 model calls and 36 recall calls. The old October 14 questions are development cases. These are held-out question cutoffs on an already inspected 48-record corpus, not an independent unseen dataset. Repeated trials are related, not 36 independent problems.

Plan SHA-256: `02f953eeb595e7cf0f2be965b19394bfcf850b8347d1687e02c8ed34787d36ef`. The frozen snapshot, selectors, schedule, prompt and unchanged v1 deterministic ground-truth function existed before v2 calls. The separate convenience `gold.json` was generated just after initial calls began because the first system-Python invocation lacked `requests`; it is mechanically derived and was never sent to either service. No results were used to tune selectors or answers.

Latency includes the remote recall round trip, canonical validation/filtering/projection and prompt serialization, plus model round trip. Benchmark disk persistence is excluded. Offline replay retains original timings; it never presents replay speed as inference speed. Provider usage tokens are reported separately from money. past.dev evidence tokens are not model billing tokens. No total dollar savings are verified: ingestion, recall, subscriptions, model cached-token prices and actual account charges must be reconciled. Failures and raw trial rows remain recorded rather than selectively rerun.

Commands:

```sh
.venv/bin/python -B src/memory_benchmark_v2.py --prepare
.venv/bin/python -B src/memory_benchmark_v2.py --live
.venv/bin/python -B src/memory_benchmark_v2.py # network-free recorded replay
.venv/bin/python -m unittest discover -s tests -p test_memory_benchmark_v2.py
```

Plan preparation refuses to overwrite a declared experiment. Frozen inputs and results are in `results/memory_benchmark_v2/`; the separate request/response cache is `data/memory_benchmark_v2_cache.json`. The original main loop, production memory and v1 artifacts are untouched. Five offline tests cover strict group/kind/time filtering, source intersection, rejected future-source metadata, randomized repeated plans, complete raw context, absence of gold in requests, cache-miss refusal and exact replay of answers, tokens and timing components.

A separately labeled post-plan deterministic diagnostic uses the same local compact records and takes the last sorted matching record, without a model. It answers 18/18 questions correctly with zero model tokens and zero remote calls (`deterministic_diagnostic.json`). It is not a predeclared fourth experimental arm, but demonstrates that this structured task itself does not require semantic retrieval or an LLM. The reusable `compact_records` and `deterministic_answer` helpers are not wired into the recorded research loop.

## Completed live result — November 15, 2026

All 108 model requests and 36 past.dev recalls completed. Offline replay reproduced byte-identical trial rows with `requests.post` patched to raise on any network call. Twelve v1/v2 tests passed (five v2 tests, including the deterministic tie-break and absent-history case).

| Measure | Full raw context | Local compact | past.dev compact |
|---|---:|---:|---:|
| Exact matches / 36 | 0 | 25 | 26 |
| Accuracy | 0% | 69.44% | 72.22% |
| Mean total seconds | 0.8768 | 0.7833 | 1.5800 |
| Median total seconds | 0.8883 | 0.7675 | 1.5600 |
| Model prompt tokens | 368,800 | 11,386 | 11,386 |
| Model completion tokens | 822 | 1,296 | 1,298 |
| Missing expected sources | 0 | 0 | 0 |

Compact past.dev context improved observed accuracy versus raw full context and reduced prompt tokens by 96.91%, but added 0.7032 seconds mean latency. Against the stronger local compact baseline it used **exactly the same prompt tokens**, was 0.7967 seconds slower, and answered just one additional trial correctly. Identical compact inputs can yield different model outputs even at temperature zero; this one-answer difference is not evidence of a retrieval accuracy advantage. No expected source was absent in either compact arm. This experiment does **not** establish all three sponsor gains or even a reliable past.dev-specific gain.

All 57 incorrect trial answers are retained in `report.json` under `summary.failures` and in full `trials.json`. The full-context model sometimes returned the question ID as source ID or selected the wrong record. Compact arms still made answer-format/field errors, especially empty-history responses. No incorrect answer was repaired after the model call. No runtime API failures occurred. The separate gold-file preparation import failure is disclosed above. Complete raw context had all expected records, so its 0% result must not be attributed to unavailable information. Better prompting, different models and larger independent corpora remain untested; v1-v2 cross-run differences are not a paired causal comparison.
