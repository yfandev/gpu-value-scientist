# Independent implementation review

Review by a separately tasked agent in the same automated system, 2026-11-15. This is not external certification. Scope is validation of the already frozen investigation, with no additional experiment or forecast change.

**The persisted numerical result reproduces. Neither of the two prespecified dominance hypotheses is supported.** The primary absolute bridge-component share is 0.4163030043, with the prespecified descriptive block-bootstrap interval [0.2193586354, 0.5616814948]. The interval is neither wholly above 0.50 nor wholly below 0.20.

## What was checked independently

`verify_independent.py` does not import `study.py` or call its decomposition function. It:

- Reads original pack parquet files and uses pandas to reconstruct all 2,837 selected daily raw medians and their observation counts from 444,663 observations.
- Reads the original source/day partitions for every one of the 11 deterministically selected example transitions (1,020 original rows in total, including repeated dates across examples). Python `statistics.median`, separately constructed observable-attribute tuple keys, and separately written log arithmetic reproduce their full- and matched-cell prices, overlap counts, price-change counts and all three bridge components.
- Recomputes the three variants' pooled shares and source-level shares from persisted transitions; validates their exact bridge identities, same-day sequence exclusions and stable-basket membership zeros.
- Reconstructs all 18 calendar blocks and all 2,000 saved bootstrap draws from the primary transitions and the frozen random seed. The interval reproduces.
- Verifies the protocol hash, all recorded input hashes and all three protected forecast hashes.

The checker passed. Its `--negative-control` deliberately offsets the claimed share by 0.01; that invocation failed with an assertion as intended before the successful run. The checker only prints its success token after all assertions pass. Details are in `independent_verification.json`.

## Findings and limits that must accompany the result

1. **The identity is not causal attribution.** The term called sampling S includes changes caused by median-of-cell versus raw-row aggregation; genuine within-cell temporal repricing can contribute to it. Membership C is an overlap-bridge residual. For newly appearing or disappearing offers, counterfactual prices are not observed. Call F the *membership/aggregation absolute bridge-component share*, not the fraction of economic price change caused by collection errors or the fraction of forecast error explained.
2. **The result does not prove matched contracts are identical executable offers.** Missing configuration attributes, daily minima from FastGPU, changing within-day observations and shared providers across collectors limit interpretation. Neither 47 unchanged-matched-cell events nor 100 unchanged-matched-median events establishes absence of any economic price change outside the matched cells.
3. **The formal result is mixed/inconclusive.** The bootstrap uses a small, changing panel across 18 fixed weekly blocks, only three collectors and retrospective targets. It is a descriptive uncertainty interval under that resampling scheme, not a causal or out-of-sample confidence guarantee. Thresholds 0.20 and 0.50 are declared research definitions, not externally established economic laws.
4. **Unrounded medians differ from the official target.** The 914 changed-index count uses unrounded raw medians and the declared 1e-9 log tolerance. Some tiny raw changes disappear after official four-decimal rounding. For example, case_02 has a $0.00000025 raw change. Label these as unrounded index movements; the frozen 1%-movement diagnostic is more interpretable for material changes. The raw/official medians reconcile within the expected $0.00005 rounding tolerance.
5. **Weighting and matching affect interpretation.** Primary F is 41.63%; coarse-key F is 46.35%; the high-overlap primary subset is 23.52%. Those values are different populations/estimands and cannot be silently substituted for the primary result. The pooled log-movement metric weights larger movements and series with longer available histories more heavily; it is not an equal-source or equal-series average.
6. **No forecast-performance conclusion follows.** This investigation validates a measurement diagnosis; it does not train a replacement model, test predictive improvement, establish November scores or justify changing the frozen submission.

## Implementation correction reviewed

The initial DuckDB key representation distinguished an absent extra-JSON field from an explicitly null field. The study author identified this in a synthetic control and proposed canonicalizing both to one missing-value representation. The reviewer checked the original primary key universe: 2,201 unique encoded keys remain 2,201 unique keys after canonicalizing these nulls, with zero merged groups. Thus this correction cannot alter primary cell grouping or membership for the observed data. It is a defensible implementation cleanup, not a new key dimension or scientific hypothesis. Initial results should remain preserved and the final corrected implementation should be revalidated; this review records the initial verification and the correction rationale.

Reproduce verification from the repository root:

```bash
.venv/bin/python -B research/frontier_20261115/verify_independent.py
```
