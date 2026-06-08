# Current Validation Status

## Scope checked

The consolidated final version was rechecked after merging the strongest ideas from `hsr` and `zcq`.

Validated components:

- main ODE models `M0`, `M1`, `M2`
- tritrophic extension `M3`
- delay extension
- Leslie-Gower comparison
- discrete-time comparison
- theory utilities and classification logic

## What was corrected

1. The quadratic fear form was fixed so that `k=0` exactly matches the no-fear baseline.
2. The main `k-alpha` scan range was restricted to `alpha in [10^-2, 5]` to avoid stiffness-driven numerical invalid regions in the vectorized phase map.
3. Delay outputs were regenerated with a parameter set where changing `tau` produces visible dynamical differences.
4. The stale tritrophic invalid corner at `k1=k2=0` was recomputed and corrected in `results/tritrophic_scan.csv`.
5. Obsolete delay output `results/delay_tau_1p0.csv` was removed.

## Current numerical status

- unit tests passed: `13 / 13`
- main `k` scan:
  one oscillatory no-fear baseline point and stable coexistence for the remaining scanned `k` values
- main `k-alpha` scan:
  stable coexistence, oscillatory coexistence, and low-density-risk regions only
- theory overlay:
  local Routh-Hurwitz boundary is broadly consistent with simulation, with the main mismatch concentrated in very slow-memory regimes
- robustness scan:
  all fear functions now share the same `k=0` baseline
- tritrophic scan:
  no stale invalid row remains in the saved result table

## Remaining interpretation limits

These are not code bugs, but they should be stated honestly in the final paper:

- the theory boundary is local, while the heatmap is a finite-time numerical classification
- mismatch is therefore expected in some slow-memory regions
- the tritrophic, delay, Leslie-Gower, and discrete models are extensions, not the theorem-bearing core
- `report/report.md` and `overleaf_report/main.tex` are historical drafts and must be updated before final submission

## Recommended canonical sources

Use these files as the current ground truth:

- `results/*.csv`
- `figures/*.png`
- `docs/final_modeling_analysis.md`
- `docs/objective_quality_review.md`
- `docs/course_requirements_checklist.md`
- `docs/final_report_blueprint.md`
