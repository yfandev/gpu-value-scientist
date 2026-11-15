# Headline catalog and archived AWS forecast audit

The actual catalog snapshots have **117 distinct headline series in their union**, not a fixed 97-series final target set. All 117 can be forecast using valid history dated on or before November 6. Absence of a November 6 observation does not prohibit an AWS forecast.

| Actual artifact | Catalog as-of | All catalog series | Headline posted | Headline AWS | Total headline |
|---|---|---:|---:|---:|---:|
| `results/quickstart/series_catalog.csv` | 2026-10-24 | 725 | 17 | 80 | 97 |
| `data/series_catalog.csv` | 2026-11-06 | 592 | 37 | omitted | 37 |
| `results/series_audit/series_catalog.csv` (full starter rebuild) | 2026-11-06 | 725 | 37 | 0 | 37 |

The 17 October posted headline series remain headline in November; another 20 posted series qualify. The union is therefore 80 AWS plus 37 posted series. The starter README's older 728-series prose is not the count in these actual handover-derived catalogs. The existing November catalog is a **posted-only project build**, not evidence that the AWS targets do not exist and not a separately verified official competition target list.

`data/headline_series_audit.csv` enumerates **every one of the 117 series**, with snapshot membership, tiers, exact November 6 observation availability, latest usable date, history row count, full November tier reason, original inclusion, exclusion reason, posted-scope eligibility, forecast eligibility and truth availability. It is the authoritative per-series list for this audit.

- All 37 posted series have an observation exactly on November 6 and are in the project's posted headline submission.
- All 80 October headline AWS series have a usable archive close on October 31, six days before the origin. Each fails only `stale>3d_at_as_of` in the full November catalog. Each is a legitimate extended forecast target.
- Those 80 AWS series are excluded from the posted-only scored scope by instrument/source scope and unavailable November archive truth. They are not inherently unforecastable. The starter permits extended-tier forecasts and scoring wherever matching truth exists.
- No November 7–13 truth is present in the shipped pack, including for the posted targets. Consequently neither file has a claimed November score. AWS November scoring additionally requires an authorised live collection or the November archive, described by the pack as due December 1. We did not obtain either.

## Forecast extension and semantics

`forecasts_extended.csv` contains **351 rows: the original 111 rows unchanged, followed by 240 rows for the 80 AWS series at horizons 1, 3 and 7**. Original forecast bytes are preserved as the leading rows. The origin is November 6 and target dates are November 7, 9 and 13. `forecasts.csv` remains untouched; its SHA-256 is `62ea5d18a77f4fd509ac96d9518c1d448ee777fa5839e380a0689d074a5eae31`.

The extension is an additional forecast ledger, not a claim that all 117 series belong in the posted Sunday score. Added rows use the unchanged starter `baselines.py --method drift --frozen` with all available history through the cutoff and its default 20-change minimum. The starter anchors at the last observed value, then applies empirical h-day log-change quantiles. **For stale AWS history this is exactly the starter h-day convention, not a separately fitted six-plus-h-day uncertainty model.** `results/series_audit/aws_starter_drift.csv` retains its `method_note`, explicitly recording `last_value_date=2026-10-31;stale_days=6` and change counts.

The unchanged full `build_series.py` reads the original archive and builds end-of-day closes. It carries within contiguous archive segments only: no prices are invented for the March–June archive hole or November 1–6. Composite membership is reused from the October quickstart catalog via `--members-from`, retaining the same instrument definition. Quickstart `series_daily.csv` already extends through November 6 for posted data and October 31 for AWS; its catalog's October 24 **as-of** is a tier-evaluation date, not proof that its full series file stops on that date.

## Reproduce and verify

```bash
.venv/bin/python src/series_audit.py
```

This rebuilds full cutoff history from the unchanged pack, regenerates the 117-row audit and the extended forecasts, and validates the exact 117×3 grid, origin/target dates, positive finite ordered quantiles, original row bytes and hash, unchanged starter source hashes, no future history, absence of archive-gap rows, and numerical equality of the new forecasts to the starter drift implementation. Results and command output are in `results/series_audit/audit_report.json`; the full starter build report is beside it. No pack files are modified.
