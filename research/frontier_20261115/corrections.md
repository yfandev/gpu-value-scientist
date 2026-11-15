# Preserved implementation corrections

2026-11-15 21:06 UTC: initial mechanism controls passed 10 of 11. Independent Python reconstruction of a key found that DuckDB represented an explicitly null JSON attribute as the string `null`, while a missing attribute became SQL NULL. This needlessly distinguished two kinds of unavailable contract metadata. Normalize both to null before key serialization, consistent with missing attributes being an explicit missing category. No field or estimand was added or removed. The first execution, initial script, all raw-derived outputs and failed test log are preserved under `initial_null_encoding/`; protocol unchanged. Re-execute the identical frozen protocol with corrected serialization, then compare all numeric results. This is an implementation correction, not an adaptive new experiment.

Correction result: every numeric summary for all three matching variants and bootstrap output is exactly unchanged. All 11 controls pass after normalization.

Final independent checker rerun after canonical-null correction: FRONTIER_INDEPENDENT_VERIFICATION_PASS. It independently reconstructs 2,837 daily medians,11 selected cases and all2,000 bootstrap draws;536 input fingerprints and3 protected forecast fingerprints match. See independent_verification.json.
