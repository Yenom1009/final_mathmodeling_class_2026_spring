"""One-command reproduction pipeline."""

from __future__ import annotations

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path.cwd() / ".cache"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from .classify import compute_tail_metrics
from .data_sources import (
    write_configs,
    write_literature_files,
    write_readme,
    write_references_bib,
    write_report,
    write_requirements,
    write_simple_report_pdf,
)
from .plotting import (
    plot_amplitude_heatmap,
    plot_bifurcation_k,
    plot_classification_heatmap,
    plot_empirical_calibration,
    plot_fear_function_robustness,
    plot_mean_amplitude,
    plot_mechanism_diagram,
    plot_model_layers,
    plot_phase_portraits,
    plot_theory_boundary,
    plot_time_series_cases,
    plot_tritrophic_extension,
)
from .scan import compute_theory_boundary, find_representative_cases, scan_k, scan_k_alpha
from .simulate import simulate_model


def ensure_dirs(root: Path) -> None:
    for dirname in [
        "configs",
        "literature",
        "results",
        "results/time_series_cases",
        "figures",
        "report",
    ]:
        (root / dirname).mkdir(parents=True, exist_ok=True)


def user_literature_params() -> dict[str, float]:
    return {
        "r": 0.5,
        "d1": 0.0,
        "d2": 0.005,
        "p_pred": 0.08,
        "h_handle": 0.1,
        "eta": 0.5,
        "d3": 0.3,
    }


def literature_liu_params() -> dict[str, float]:
    return {
        "r": 0.1,
        "d1": 0.01,
        "d2": 0.01,
        "p_pred": 0.5,
        "h_handle": 0.6,
        "eta": 0.4,
        "d3": 0.22,
    }


def make_time_series(root: Path, params: dict[str, float], reps: pd.DataFrame) -> dict[str, pd.DataFrame]:
    out = root / "results" / "time_series_cases"
    cases: dict[str, pd.DataFrame] = {}
    T = 800.0
    n_points = 3201
    cases["M0 no fear"] = simulate_model("no_fear", params, [30.0, 10.0], T=T, n_points=n_points)
    cases["M1 instant fear k=1"] = simulate_model("instant", {**params, "k_fear": 1.0}, [30.0, 10.0], T=T, n_points=n_points)
    cases["M2 memory k=1 alpha=10"] = simulate_model(
        "memory", {**params, "k_fear": 1.0, "alpha_mem": 10.0}, [30.0, 10.0, 10.0], T=T, n_points=n_points
    )
    cases["M2 memory k=1 alpha=0.1"] = simulate_model(
        "memory", {**params, "k_fear": 1.0, "alpha_mem": 0.1}, [30.0, 10.0, 10.0], T=T, n_points=n_points
    )
    for _, row in reps.iterrows():
        if row["case_id"] in {"Case A", "Case C"}:
            name = f"{row['case_id']} k={row.k_fear:.2g} alpha={row.alpha_mem:.2g}"
            cases[name] = simulate_model(
                "memory",
                {**params, "k_fear": float(row.k_fear), "alpha_mem": float(row.alpha_mem)},
                [30.0, 10.0, 10.0],
                T=T,
                n_points=n_points,
            )
    for name, df in cases.items():
        safe = name.replace(" ", "_").replace("=", "").replace(".", "p")
        df.to_csv(out / f"{safe}.csv", index=False)
    return cases


def make_robustness(root: Path, params: dict[str, float]) -> pd.DataFrame:
    rows = []
    for form in ["rational", "exponential", "quadratic"]:
        for k in np.linspace(0.0, 4.0, 25):
            df = simulate_model(
                "memory",
                {**params, "fear_form": form, "k_fear": float(k), "alpha_mem": 10.0},
                [30.0, 10.0, 10.0],
                T=500.0,
                n_points=1601,
            )
            metrics = compute_tail_metrics(df, burn_in=300.0)
            rows.append({"fear_form": form, "k_fear": float(k), **metrics})
    result = pd.DataFrame(rows)
    result.to_csv(root / "results" / "fear_function_robustness.csv", index=False)
    return result


def make_tritrophic(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    params = {
        "r": 0.8,
        "dX": 0.05,
        "aX": 0.01,
        "p1": 0.6,
        "h1": 0.08,
        "eta1": 0.45,
        "dY": 0.12,
        "p2": 0.45,
        "h2": 0.1,
        "eta2": 0.35,
        "dZ": 0.08,
        "k1": 0.4,
        "k2": 0.3,
    }
    ts = simulate_model("tritrophic", params, [20.0, 4.0, 1.5], T=500.0, n_points=2001)
    ts.to_csv(root / "results" / "tritrophic_time_series.csv", index=False)
    rows = []
    for k1 in np.linspace(0.0, 2.0, 21):
        for k2 in np.linspace(0.0, 2.0, 21):
            run_params = {**params, "k1": float(k1), "k2": float(k2)}
            df = simulate_model("tritrophic", run_params, [20.0, 4.0, 1.5], T=250.0, n_points=1001, solver="rk4")
            metrics = compute_tail_metrics(df, burn_in=150.0)
            rows.append({"k1": float(k1), "k2": float(k2), **metrics})
    scan = pd.DataFrame(rows)
    scan.to_csv(root / "results" / "tritrophic_scan.csv", index=False)
    return ts, scan


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    ensure_dirs(root)
    write_requirements(root)
    write_readme(root)
    write_configs(root)
    write_references_bib(root)
    write_literature_files(root)

    params = user_literature_params()
    k_values = np.linspace(0.0, 20.0, 101)
    alpha_values = np.logspace(-2, 2, 81)
    initial = [30.0, 10.0, 10.0]
    scan_k_df = scan_k(
        params,
        k_values=k_values,
        alpha_mem=10.0,
        initial_state=initial,
        T=1000.0,
        burn_in=650.0,
        n_points=2501,
        output_path=root / "results" / "scan_k.csv",
    )
    scan_df = scan_k_alpha(
        params,
        k_grid=k_values,
        alpha_grid=alpha_values,
        initial_state=initial,
        T=2000.0,
        burn_in=1200.0,
        n_steps=4001,
        output_path=root / "results" / "scan_k_alpha.csv",
    )
    theory_df = compute_theory_boundary(params, k_values, alpha_values, output_path=root / "results" / "theory_boundary.csv")
    reps = find_representative_cases(scan_df, scan_k_df, params, output_path=root / "results" / "representative_cases.csv")

    liu_scan = scan_k(
        literature_liu_params(),
        k_values=np.linspace(0.0, 10.0, 51),
        alpha_mem=10.0,
        initial_state=[4.0, 0.5, 0.5],
        T=800.0,
        burn_in=500.0,
        n_points=2001,
        output_path=root / "results" / "scan_k_liu2021_params.csv",
    )
    del liu_scan

    case_series = make_time_series(root, params, reps)
    robust_df = make_robustness(root, params)
    tri_ts, tri_scan = make_tritrophic(root)

    figures = root / "figures"
    plot_mechanism_diagram(figures / "fig01_mechanism_diagram.png")
    plot_model_layers(figures / "fig02_model_layers.png")
    plot_time_series_cases(case_series, figures / "fig03_time_series_cases.png")
    plot_phase_portraits(case_series, figures / "fig04_phase_portraits.png")
    plot_bifurcation_k(scan_k_df, figures / "fig05_bifurcation_k_extrema.png")
    plot_mean_amplitude(scan_k_df, figures / "fig06_mean_amplitude_vs_k.png")
    plot_classification_heatmap(scan_df, figures / "fig07_k_alpha_classification_heatmap.png")
    plot_amplitude_heatmap(scan_df, figures / "fig08_k_alpha_amplitude_heatmap.png")
    plot_theory_boundary(scan_df, theory_df, figures / "fig09_theory_boundary_vs_simulation.png")
    plot_fear_function_robustness(robust_df, figures / "fig10_fear_function_robustness.png")
    plot_empirical_calibration(figures / "fig11_dataset_or_empirical_calibration.png")
    plot_tritrophic_extension(tri_ts, tri_scan, figures / "fig12_tritrophic_extension.png")

    class_counts = scan_df["class"].value_counts()
    write_report(root, scan_k_df, reps, class_counts)
    write_simple_report_pdf(root)
    print("Generated fear predator-prey project outputs.")
    print(f"Root: {root}")
    print(f"Classes: {class_counts.to_dict()}")
    print(f"Representative cases: {reps[['case_id', 'k_fear', 'alpha_mem', 'class']].to_dict(orient='records')}")


if __name__ == "__main__":
    main()
