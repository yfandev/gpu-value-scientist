# Frozen measurement investigation, November 15, 2026

Start with [REPORT.md](REPORT.md). **Result: mixed/inconclusive dominance test; concrete observed-basket versus matched-cell divergences. No forecast change or claimed score improvement.**

- `protocol.json` / `protocol.sha256`: design fixed before decomposition results.
- `study.py`: extraction, exact log-median bridge, diagnostics and block bootstrap.
- `test_study.py`, `tests.log`, `negative_control.log`: synthetic controls and invariants; corrupted bridge must fail.
- `verify_independent.py`, `independent_verification.json`, `independent_review.md`: separate implementation review.
- `summary.json`, `transitions_*.csv`, `by_series_*.csv`: complete results, including null/inconclusive cases.
- `raw_selected.parquet`: 444,663 original selected rows with provenance and derived matching keys.
- `cells_*.parquet`, `raw_daily.csv`, `median_reconciliation.csv`: intermediate derived tables.
- `bootstrap_blocks.csv`, `bootstrap_draws.csv`: all uncertainty inputs and draws.
- `case_studies.csv`, `case_*_raw.csv`: deterministically selected examples and their original input rows.
- `input_hashes.json`: read-only source fingerprints; protected forecast fingerprints also in summary.
- `corrections.md`, `initial_null_encoding/`: preserved initial run, failed key-serialization test and corrected implementation. Numeric results unchanged.
- `discovery_chain.json`: audit trail from existing research to frozen question and conclusion.

Reproduction commands are in the report. All outputs remain here. No new dependency is required. Existing `.venv` supplies Python, DuckDB, NumPy and pandas.
