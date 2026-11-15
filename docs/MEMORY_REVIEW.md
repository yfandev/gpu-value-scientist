# Automated self-review by the build agent: memory benchmark

Reviewed 2026-11-15. This document records v1 diagnosis and constraints for v2; it does not claim v2 has passed.

## V1 diagnosis

All 16 model trials had the expected canonical record in their supplied context. Both arms nevertheless scored 2/8 exact matches. Failures repeatedly chose the wrong instrument group or record kind: q05/q07 returned the latest hyperscaler hypothesis instead of their requested groups; q02 returned a marketplace verdict (past.dev) or a hypothesis (full context); q08 past.dev returned a hypothesis instead of the requested verdict. Thus v1 did not demonstrate a retrieval-recall deficit. The actual cached prompts include group/kind selectors and exclude expected answers. Better prompt clarity and compact canonical projection are defensible optimizations if applied equally.

Measured v1 mean latency was 1.5712 seconds past.dev versus 1.2264 seconds full context, with 72.3884% fewer model prompt tokens. Token reduction is not monetary savings. V1 counts network request time plus local retrieval, not every serialization/filtering step; v2 should measure complete elapsed answer time and separately break down retrieval/model work.

## V2 gates

- Preserve v1 plan, responses, and negative result. Freeze v2 plan and held-out question IDs/answers before its requests. Changes learned from v1 are development; rerunning the same questions is not held-out validation.
- Compare the identical eligible corpus and temporal cutoff. Never transmit expected answers, expected record IDs, or answer-dependent selectors to any arm.
- Include full context and a strong local predicate/keyword retrieval baseline. The question explicitly names kind, group and date, so filtering these is fair and necessary. Include deterministic local answer selection as a reference: this structured task can be solved without an LLM. A win against a weak full-context prompt is not superiority over existing approaches.
- Apply canonical field projection and clearer selector instructions equally to model arms. Keep model, temperature, answer schema and question identical. Report expected-record recall and answer accuracy separately.
- Randomize paired execution order, use repeated trials, report all trials and failures, and disclose the small single-corpus scope. Count total elapsed time, retries, source joining and serialization; report cold/warm/cache state. Replay may reproduce measured timings but is not a new latency sample.
- If sponsor wording requires improvement on accuracy, latency AND cost, all three must be demonstrated against the named comparator. Accuracy ties or unknown costs do not satisfy it. Memory QA gains do not establish GPU pinball-score gains.

## Monetary evidence actually available

Fetched public https://past.dev/pricing.md and https://past.dev/docs/memory-api/debugging/llms.txt on 2026-11-15; copies are under `artifacts/automated-self-review/`. Published ingestion is ceil(UTF-8 bytes/350) credits per data point. PAYG recall is one credit per call; Flex includes recall within fair use but costs $99/month. Purchased credit tiers range from $0.0003/credit at 100,000 credits/$30 to $0.00013/credit at 10 million/$1,300. Free grants, subscription allocation, purchased-credit tiers and expiry mean list price is not proof of actual cash paid.

Authorized read-only `GET /api/v1/usage` succeeded using the existing configured project credential without printing the credential. At 18:08:40 UTC it reported metered=true, 1,385 project credits, 347 ingestions and 186 recalls. Aggregate sanitized evidence is `past-usage.json`; it includes other project activity and cannot price the benchmark alone.

`GET /api/v1/requests` also succeeded. It exposes request ID, receipt time, duration and actual consumed credits. Sample recall rows consumed one credit each. The v1 time window contained 11 recalls versus 8 benchmark recalls; time matching alone therefore cannot isolate benchmark cost. Sanitized rows are in `past-v1-window-credits.json`. Do not publish API key metadata from request responses.

For v2, record each response's X-Request-Id and reconcile it to request-log credit consumption. Sum canonical ingestion costs separately and specify whether they are sunk, one-time or amortized over N queries. Report model API prompt/completion/cached-token usage using documented model price assumptions. This can establish actual credits consumed plus a clearly labeled list-price cost estimate. Without invoice/paid-tier confirmation it cannot establish the user's actual dollar bill. Include local compute treatment consistently rather than silently setting one arm's costs to zero.

Current defensible claim: past.dev reduced v1 prompt tokens, with tied answer accuracy and slower end-to-end requests; total monetary savings remain unverified. Updated v2 evidence must be judged on its own frozen protocol.
