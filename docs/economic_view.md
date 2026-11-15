## The 2028–2029 view: argued scenarios, not scored forecasts

The useful conclusion is conditional: **underwrite the earnings of a specific GPU configuration and contract, not an aggregate “GPU price.”** A posted rental rate does not establish the realized rent, utilization, resale transaction price, or lender recovery. Our short-horizon evaluation cannot calibrate a two- or three-year prediction interval. The ranges below are transparent sensitivities, not q10/q90 forecasts.

### Evidence and economic mechanism

- **2024-03-18 — [NVIDIA Blackwell Platform Arrives to Power a New Era of Computing](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing).** A newer competing architecture creates a plausible channel for older-chip price pressure. The vendor's workload-specific performance claims are not used as a universal depreciation multiplier.
- **2023-11-13 — [NVIDIA Supercharges Hopper, the World’s Leading AI Computing Platform](https://nvidianews.nvidia.com/news/nvidia-supercharges-hopper-the-worlds-leading-ai-computing-platform).** H200 was announced with 141 GB memory and 4.8 TB/s bandwidth, with shipping expected in Q2 2024. Memory fit and bandwidth can matter more than nominal arithmetic throughput for a particular buyer.
- **2024-12-20 — [DOE Releases New Report Evaluating Increase in Electricity Demand from Data Centers](https://www.energy.gov/articles/doe-releases-new-report-evaluating-increase-electricity-demand-data-centers).** DOE reports data centers consumed about 4.4% of U.S. electricity in 2023 and projects approximately 6.7–12% in 2028. Capacity and power constraints can delay substitution and support older-chip earnings. This is a demand projection, not an electricity-price forecast; we have not treated it as the BLS electricity PPI or invented a PPI observation.

These three citations were fetched directly and their displayed publication dates checked. They are labeled separately from Exa results. Four live Exa narrative searches have now completed with an exclusive end-publication filter at 2026-11-07T00:00:00Z. Undated/later results, restricted source domains, and secondary snippets referencing excluded price publishers are rejected. Cached requests and accepted excerpts are in data/evidence.json and data/evidence_search_cache.json. Separate per-origin Exa searches run inside the historical research loop, before hypothesis selection; these narrative notes do not enter those earlier decisions.

The pack’s capability ladder supplies a complementary observation: the precision-matched cross-benchmark inference median is **2.464960 H100/A100**, on SXM 80GB parts in MLPerf Inference v3.0/v3.1. It is a derived composite, not an official verified MLPerf score or a universal conversion between rental prices. Workload, precision, software maturity, interconnect, and memory fit limit transport to today's production jobs. The pack’s broader headline rounds this comparison to 2.46.

The hardware table records **$33,600 for H100 SXM5 80GB**, explicitly an analyst's $269k eight-GPU server quote divided by eight, with no official MSRP. It records **$15,000 for A100 SXM4 40GB**, while A100 SXM4 80GB has no release price. Those are different configurations and price bases; we do not use the 40GB release figure to manufacture an 80GB residual percentage, or treat an allocated H100 server quote as a standalone-GPU transaction.

The four-year AWS archive is a useful counterexample to an inevitable smooth decline. The starter’s fixed-member A100 40GB `aws_spot.p4d.24xlarge.az_median` spans 2022-06-01 through 2026-10-31. Its median daily closes by calendar year are $1.45255625 (partial 2022), $1.228975 (2023), $1.293396875 (2024), $1.24396875 (2025), and $2.1154875 (partial 2026), per GPU-hour. The 2026 figure excludes the March–June archive hole, so it is not a comparable full-year estimate. H100 `aws_spot.p5.48xlarge.az_median` begins only on 2024-12-19, not in 2022. These administered spot prices are never spliced into posted rate-card targets; no rows or returns are interpolated across the hole. The comparison motivates a capacity-constrained scenario and cautions against fitting universal depreciation from chip age alone.


### Additional evidence found through live Exa searches

- **2023-11-13 — [NVIDIA Supercharges Hopper, the World’s Leading AI Computing Platform | NVIDIA Newsroom](https://nvidianews.nvidia.com/news/nvidia-supercharges-hopper-the-worlds-leading-ai-computing-platform)**. Establishes the sequence of competing GPU generations; it does not estimate a depreciation coefficient. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.
- **2026-09-29 — [AI Data Center Boom: Can We Build It If They Come? | Bain & Company](https://www.bain.com/insights/ai-data-center-boom-can-we-build-it-if-they-come-technology-report-2026/)**. Supports testing a capacity-constrained scenario; the scenario ranges remain explicit assumptions. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.
- **2021-05-04 — [Trends in electricity prices during the transition away from ...](https://www.bls.gov/opub/btn/volume-10/trends-in-electricity-prices-during-the-transition-away-from-coal.htm)**. Explains why generation and distribution PPIs must be distinguished; no missing BLS observation is fabricated. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.
- **2026-10-01 — [Productive, Durable, Fungible: How NVIDIA AI Factories ...](https://blogs.nvidia.com/blog/productive-durable-fungible-ai-factories/)**. Provides context for useful-life and resale assumptions, without treating accounting depreciation or vendor commentary as a resale transaction dataset. Publication metadata comes from Exa; a publication date is not proof of an immutable historical page.

### Conditional rental ranges

Anchor each chip to its own observed contract on **2026-11-06**: `gpurentalprices.neocloud_rate_card.H100_SXM_80GB.on_demand.median` at **$3.5539/GPU-hour**, and the corresponding `A100_SXM_80GB` series at **$1.95/GPU-hour**. Instrument: neocloud rate card, median of shipped posted on-demand offers from that collector, all regions pooled, no commitment. Neither is a transaction price; changing provider composition can move the median.

Choose explicit annual rental changes, then compound `price(t) = price(2026-11-06) × (1 + annual_change)^t`. No probability is assigned to these scenarios.

| Chip | Scenario | Assumed annual change | Nov 2028 rent, $/GPU-h | Nov 2029 rent, $/GPU-h |
|---|---|---:|---:|---:|
| H100 SXM 80GB | Stress | −50% to −35% | 0.89–1.50 | 0.44–0.98 |
| H100 SXM 80GB | Central sensitivity | −35% to −10% | 1.50–2.88 | 0.98–2.59 |
| H100 SXM 80GB | Capacity constrained | −10% to 0% | 2.88–3.55 | 2.59–3.55 |
| A100 SXM 80GB | Stress | −55% to −40% | 0.39–0.70 | 0.18–0.42 |
| A100 SXM 80GB | Central sensitivity | −40% to −15% | 0.70–1.41 | 0.42–1.20 |
| A100 SXM 80GB | Capacity constrained | −15% to 0% | 1.41–1.95 | 1.20–1.95 |

A100's more adverse chosen sensitivity reflects its older generation and lower measured capability, not an estimated causal depreciation coefficient. Demand shocks could move outside every range, including upward. The central label is a scenario name, not an estimated median or an assertion that it is most likely.

### Resale: income-value sensitivities, with a missing transaction anchor

`resale_pointers.csv` is pointer-only. American Compute residual bands, CCIR hardware records, Compute Exchange ranges, and Silicon Data analysis are useful places to seek a permitted appraisal; we copied no values from them. There is no open transaction-level resale history here, so a calibrated resale forecast is not identifiable.

Instead we compute an **illustrative GPU-attributed income value at the future resale date**. This is an argued proxy for what an operating buyer might justify, not a statement of market clearing price. Assume two further operating years, 35–65% paid utilization, $0.15–$0.50 operating cost per calendar GPU-hour, a 15–30% discount rate, 50–80% of positive net system earnings allocated to the GPU, $200–$1,000 sale/refurbishment cost, and zero terminal value. All are analyst-selected assumptions, not estimated facts. The same annual rental decline continues for those two years. Operating costs exclude the purchase price; the allocation accounts for other system assets and is especially uncertain.

`value = max(0, allocation × Σ[j=1,2] {8760 × max(0, utilization × future_rent × (1+annual_change)^j − cost) / (1+discount)^j} − sale_cost)`.

For the **central rental sensitivities**, the resulting 2028 income-value ranges are **H100 $0–$16,385** and **A100 $0–$6,341** per GPU; for 2029, **H100 $0–$14,555** and **A100 $0–$5,103**. The floor is a zero operating-income value, not a prediction of zero salvage proceeds. In the capacity-constrained scenario the favorable upper values are much higher: the width exposes sensitivity to utilization, realized rent, and non-GPU capital allocation, rather than establishing collateral value. `data/economic.json` includes every scenario and assumption, recomputed by code from the pack's anchors.

A lessor should test debt coverage under the adverse utilization and rent path and avoid relying on the favorable residual. A lender needs a current, configuration-matched appraisal and liquidation-cost evidence before sizing collateral advances. A capacity buyer should compare a reserved contract's total committed spend to the same SKU/region/service-level scenario, rather than assuming a posted median is executable. A stronger successor GPU raises substitution pressure, but power availability and usable-work compatibility can preserve niches for the older chip.

### Attribution and reproducibility

Pacific Machines (2026), *gpu-price-pack v0.1.1-handover*, cutoff 2026-11-06 23:59:59 UTC, CC BY 4.0 on the compilation. GPU rental price data by gpurentalprices.com (https://gpurentalprices.com), licensed under CC BY 4.0. “AWS Spot Price History”, Eric Pauley (University of Wisconsin-Madison), Zenodo, https://doi.org/10.5281/zenodo.14198917, version https://doi.org/10.5281/zenodo.23853281, CC BY 4.0. Epoch AI, “Data on machine learning hardware”, https://epoch.ai/data/machine-learning-hardware, CC BY 4.0. MLCommons Association, MLPerf Inference v3.0/v3.1 results, github.com/mlcommons/inference_results_v3.0 and inference_results_v3.1, Apache License 2.0. Derived ladder ratio: **Result not verified by MLCommons Association**. The MLPerf name and logo are registered and unregistered trademarks of MLCommons Association in the United States and other countries. All rights reserved. Unauthorized use strictly prohibited. See www.mlcommons.org for more information.

All transformed data retains source attribution in the pack and exported catalog. The economic calculations are sensitivities built from the two named anchors; the original pack is unchanged. Run `.venv/bin/python src/evidence.py` to replay cached evidence and rebuild economic JSON without API calls; add `--live` to attempt Exa.
