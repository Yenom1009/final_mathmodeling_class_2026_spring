# Predator-Prey Fear Effect Final

This directory is the consolidated final working version for the course project on predator-prey dynamics under fear effects.

It keeps the strongest parts of the existing work and merges them into one codebase:

- `hsr` strengths kept: closed loop from theory to scans to figures to report assets.
- `zcq` strengths absorbed: extension models, more explicit pipeline stages, and broader comparison scope.
- `predator_prey_fear` role: historical prototype only, not the final base.

## Modeling scope

Main model hierarchy:

- `M0`: no-fear Holling-II predator-prey baseline.
- `M1`: instant fear, where current predator density reduces prey effective birth.
- `M2`: memory fear, where perceived risk follows `z' = alpha (y - z)`.
- `M3`: tritrophic extension with fear at two trophic links.

Comparison extensions:

- delay extension: fear responds to delayed predator risk.
- Leslie-Gower / Holling-III comparison model.
- discrete-time fear map for dynamical comparison.

## Directory layout

- `src/`: simulation, theory, scans, plots, and pipeline code.
- `configs/`: baseline and scan-range parameter files.
- `results/`: generated CSV outputs.
- `figures/`: generated PNG and PDF figures.
- `literature/`: structured literature notes and summary table.
- `docs/`: analysis notes for the final write-up.
- `report/`: existing report assets kept for reference, not the canonical design document.

## Recommended use

For modeling and code work, use this directory as the main project.

For report writing, start from:

- `docs/final_modeling_analysis.md`
- `docs/objective_quality_review.md`
- `docs/course_requirements_checklist.md`
- `docs/final_report_blueprint.md`
- `literature/literature_table.md`

## Running the pipeline

```bash
pip install -r requirements.txt
python -m src.run_all
```

The pipeline generates:

- baseline comparisons
- `k` scans
- `k-alpha` two-parameter scans
- Routh-Hurwitz theory boundary overlays
- robustness comparisons across fear functions
- representative cases
- tritrophic extension outputs
- delay / Leslie-Gower / discrete comparison outputs

Current validated output set:

- figures `fig01` to `fig15`
- main CSV tables in `results/`
- time-series case exports in `results/time_series_cases/`

Important numerical note:

- the main `k-alpha` phase map is intentionally restricted to `alpha in [10^-2, 5]`
- this avoids stiffness-driven numerical invalid regions that appear for extremely fast memory and would otherwise pollute the qualitative heatmap

## Current positioning

This version is designed to be the strongest engineering and modeling base for the final submission. It is aimed at mechanism analysis and qualitative dynamics, not precise ecological forecasting.
