# Independent economic evidence review

The economic argument meets the quoted Track 2 requirement to argue resale and the two-to-three-year view from public evidence, state assumptions, and give ranges. Its numerical ranges are sensitivities chosen by the analyst, not a demonstrated long-term forecasting advantage. Keep that distinction in the prominent copy.

## What was actually inspected

Reviewed `docs/economic_view.md`, the economic section of `findings.md`, `data/economic.json`, `data/evidence.json`, the live-page source `demo/index.html`, and the supplied pack's DATA.md, capability methodology and ladder, and resale pointers. No new forecast experiment or post-cutoff economic evidence was introduced.

The supplied [Drive folder](https://drive.google.com/drive/folders/14zWi964QlLh3mZeWGrBI85J31-SqfGHN) is reachable. It contains the pack zip, `READ ME FIRST.txt`, and `ZIP.sha256`. The [readme](https://drive.google.com/file/d/1cDbhiKZeRemzxZEx3cdN1d5k3iIfOqZ2/view) was downloaded and read; it says the full brief is separately linked on the event resources page. The full original brief was therefore **not independently retrieved**. Assessment of its resale requirement relies on the user's supplied quotation: “These cannot be scored by Sunday. Argue them from public evidence (the resale pointers, the capability ladder, launch prices, the four-year spot history) ... State assumptions and give ranges.”

## Pacific is the compiler and forecast reference, not the benchmark laboratory

There is no requirement in the quoted instruction to find evidence outside the Pacific pack to beat its reference forecast. DATA.md explicitly permits external public data equally accessible to all teams at no cost and dated before each forecast origin; permission is not a requirement. The supplied pack already contains external evidence. Forecast improvement must be established by an appropriate comparison of forecast errors, not by whether a citation was discovered independently.

The 2.46 comparison originates in public **MLCommons MLPerf Inference v3.0/v3.1 closed-division submission results**. Pacific compiled those results and calculated the derived ladder. The exact row in `capability/capability_ladder.csv` is:

- `ladder_type`: `measured_median_of_benchmark_medians_ship_only_sxm_precision_matched`
- A100 → H100; `suite=inference_datacenter`; `benchmark_key=ALL`; `scenario=ALL`
- `ratio_median=2.464959884055451`; 24 benchmark/scenario medians; SXM 80GB configurations; matching declared precision
- Individual benchmark/scenario medians span approximately 1.654–5.213. The aggregate is not a universal throughput multiplier, a price ratio, or a measured depreciation rate.

Upstream repositories: [Inference v3.0](https://github.com/mlcommons/inference_results_v3.0/tree/94bdf4d349b4ae55916a3a38a74dfef7bde80e5a) and [Inference v3.1](https://github.com/mlcommons/inference_results_v3.1/tree/f7b504d40dfb65180fe59438d4b4d6f9f8598647), Apache 2.0. The compilation is Pacific Machines' CC BY 4.0 pack. Preserve the pack's notice: **“Result not verified by MLCommons Association”**, and its MLPerf trademark legend. The supplied compilation was assembled after the observation cutoff; do not describe its compilation timestamp as an original benchmark publication date.

Recommended exact third sentence for the nontechnical page:

> Public MLCommons tests compiled by Pacific show H100 handling about 2.46 times as much work as A100 on selected AI tasks, suggesting why newer chips can pressure older chips’ rental prices.

Nearby source detail should identify “selected inference benchmarks, SXM 80GB, matching precision; derived median, not an official verified MLPerf score.” Avoid “Pacific's benchmark tests” and the unrestricted “AI-processing work per GPU-hour.”

## What supports the argument, and what remains a gap

The argument correctly combines substitution pressure with constraints on replacement. The dated [Blackwell announcement](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing) (2024-03-18) and [H200 announcement](https://nvidianews.nvidia.com/news/nvidia-supercharges-hopper-the-worlds-leading-ai-computing-platform) (2023-11-13) establish competing generations and different memory capabilities. The [DOE report announcement](https://www.energy.gov/articles/doe-releases-new-report-evaluating-increase-electricity-demand-data-centers) (2024-12-20) motivates an infrastructure constraint scenario; it is not an electricity-price forecast. Existing cached Exa sources add context, but none identifies the chosen annual decline coefficients.

The pack's four-year A100 AWS history supports rejecting automatic smooth depreciation. Its 40GB spot configuration, partial years and archive gap prevent treating its growth rate as a forecast for 80GB neocloud posted rentals. The document already makes those distinctions. The $33,600 H100 hardware figure is an allocation from an eight-GPU server quote, while the $15,000 A100 figure is for 40GB; the document correctly avoids deriving comparable 80GB residual percentages from them.

The genuine remaining gap is a configuration-matched, reusable resale observation or appraisal. `resale_pointers.csv` supplies discovery leads and reuse restrictions, not transaction data. The existing income-value model is a defensible illustrative proxy, with explicit utilization, operating cost, discount, allocation and disposal assumptions. It cannot establish liquidation proceeds, market resale ranges, or lender recovery. The evidence supports the direction and the competing mechanisms; it does not statistically support the numerical bounds or make the middle scenario most likely.

A small wording improvement to the first sentence is warranted: replace “our central scenario predicts” with **“under our middle assumptions”**. Keep the numerical 2029 ranges and identify the annual declines in the calculation details. This gives a clear outlook without promoting selected sensitivities to a validated prediction.

No new experiment, wider research project, or replacement of the existing economic model is needed for this correction. The useful change is accurate provenance and a clear boundary between evidence, assumptions, and measured forecasting performance.
