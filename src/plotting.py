"""Figure generation for the fear predator-prey project."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

from .classify import CLASS_ORDER


FIG_DPI = 220
PREY_COLOR = "#2563eb"
PREDATOR_COLOR = "#e76f51"
RISK_COLOR = "#2a9d8f"
NEUTRAL = "#475569"
CLASS_COLORS = {
    "stable_coexistence": "#2a9d8f",
    "oscillatory_coexistence": "#f4a261",
    "predator_extinct": "#8b5cf6",
    "prey_extinct": "#94a3b8",
    "low_density_risk": "#e63946",
    "invalid": "#e5e7eb",
}
CLASS_LABELS = {
    "stable_coexistence": "stable",
    "oscillatory_coexistence": "oscillatory",
    "predator_extinct": "predator extinct",
    "prey_extinct": "prey extinct",
    "low_density_risk": "low-density risk",
    "invalid": "outside / invalid",
}


plt.rcParams.update(
    {
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def save_both(fig: plt.Figure, png_path: str | Path) -> None:
    png = Path(png_path)
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=FIG_DPI, bbox_inches="tight")
    fig.savefig(png.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _soft_grid(ax: plt.Axes) -> None:
    ax.grid(True, color="#cbd5e1", alpha=0.45, linewidth=0.8)
    ax.tick_params(colors="#334155", labelsize=9)
    ax.xaxis.label.set_color("#334155")
    ax.yaxis.label.set_color("#334155")


def _class_cmap() -> tuple[ListedColormap, BoundaryNorm]:
    cmap = ListedColormap([CLASS_COLORS[name] for name in CLASS_ORDER])
    norm = BoundaryNorm(np.arange(-0.5, len(CLASS_ORDER) + 0.5, 1), cmap.N)
    return cmap, norm


def _add_class_colorbar(fig: plt.Figure, ax: plt.Axes, mesh) -> None:
    cbar = fig.colorbar(mesh, ax=ax, ticks=range(len(CLASS_ORDER)), shrink=0.88, pad=0.025)
    cbar.ax.set_yticklabels([CLASS_LABELS[name] for name in CLASS_ORDER])
    cbar.ax.tick_params(labelsize=8)


def _tail_is_effectively_stationary(tail: pd.DataFrame, rel_tol: float = 5e-3, abs_tol: float = 1e-4) -> bool:
    finite = tail[["x", "y"]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(finite) < 3:
        return True
    x = finite["x"].to_numpy(dtype=float)
    y = finite["y"].to_numpy(dtype=float)
    x_span = float(np.nanmax(x) - np.nanmin(x))
    y_span = float(np.nanmax(y) - np.nanmin(y))
    scale = max(abs(float(np.nanmean(x))), abs(float(np.nanmean(y))), 1.0)
    return max(x_span, y_span) < abs_tol or max(x_span, y_span) / scale < rel_tol


def _plot_phase_tail(ax: plt.Axes, tail: pd.DataFrame, color: str = PREY_COLOR) -> None:
    finite = tail[["x", "y"]].replace([np.inf, -np.inf], np.nan).dropna()
    if finite.empty:
        ax.text(0.5, 0.5, "no finite tail", ha="center", va="center", transform=ax.transAxes, color=NEUTRAL)
        return

    if _tail_is_effectively_stationary(finite):
        x_mean = float(finite["x"].mean())
        y_mean = float(finite["y"].mean())
        ax.scatter([x_mean], [y_mean], marker="D", s=52, color=RISK_COLOR, zorder=5, label="tail fixed point")
        ax.text(0.05, 0.92, "tail converges\nto fixed point", transform=ax.transAxes, va="top", fontsize=8, color=NEUTRAL)
        x_pad = max(0.06, abs(x_mean) * 0.003)
        y_pad = max(0.04, abs(y_mean) * 0.05)
        ax.set_xlim(x_mean - x_pad, x_mean + x_pad)
        ax.set_ylim(max(0.0, y_mean - y_pad), y_mean + y_pad)
        return

    ax.plot(finite["x"], finite["y"], lw=1.4, color=color, alpha=0.9)
    ax.scatter(finite["x"].iloc[0], finite["y"].iloc[0], s=30, color=RISK_COLOR, zorder=5, label="tail start")
    ax.scatter(finite["x"].iloc[-1], finite["y"].iloc[-1], s=30, color=PREDATOR_COLOR, zorder=5, label="tail end")


def _save_generated_asset(asset_name: str, png_path: str | Path) -> None:
    png = Path(png_path)
    source = Path(__file__).resolve().parents[1] / "assets" / "generated" / asset_name
    if not source.exists():
        raise FileNotFoundError(f"Missing generated figure asset: {source}")
    png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, png)

    image = plt.imread(source)
    height, width = image.shape[:2]
    fig_width = 11.5
    fig_height = fig_width * height / width
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.imshow(image)
    ax.axis("off")
    fig.savefig(png.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def plot_mechanism_diagram(path: str | Path) -> None:
    _save_generated_asset("fig01_mechanism_diagram_generated.png", path)


def plot_model_layers(path: str | Path) -> None:
    _save_generated_asset("fig02_model_layers_generated.png", path)


def plot_time_series_cases(case_series: Mapping[str, pd.DataFrame], path: str | Path) -> None:
    n = len(case_series)
    ncols = 2 if n > 3 else 1
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(11.5, 2.75 * nrows), squeeze=False, constrained_layout=True)
    for ax, (name, df) in zip(axes.flat, case_series.items()):
        ax.plot(df["t"], df["x"], label="prey x", lw=1.7, color=PREY_COLOR)
        ax.plot(df["t"], df["y"], label="predator y", lw=1.7, color=PREDATOR_COLOR)
        if "z" in df and df["z"].notna().any():
            ax.plot(df["t"], df["z"], label="risk z", lw=1.3, color=RISK_COLOR, alpha=0.9)
        ax.set_title(name, weight="bold", pad=6)
        ax.set_xlabel("time")
        ax.set_ylabel("density")
        ax.set_ylim(bottom=-0.02 * max(1.0, float(df[["x", "y"]].max().max())))
        _soft_grid(ax)
    for ax in axes.flat[n:]:
        ax.axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.02), fontsize=9)
    fig.suptitle("Model comparison and representative dynamics", fontsize=14, weight="bold", y=1.06)
    save_both(fig, path)


def plot_phase_portraits(case_series: Mapping[str, pd.DataFrame], path: str | Path) -> None:
    shown = list(case_series.items())[:6]
    ncols = 3 if len(shown) > 4 else min(4, len(shown))
    nrows = int(np.ceil(len(shown) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 3.45 * nrows), squeeze=False, constrained_layout=True)
    for ax, (name, df) in zip(axes.flat, shown):
        tail = df[df["t"] >= 0.4 * df["t"].max()]
        _plot_phase_tail(ax, tail, color=PREY_COLOR)
        ax.ticklabel_format(useOffset=False, style="plain")
        ax.set_title(name, fontsize=9, weight="bold", pad=6)
        ax.set_xlabel("prey x")
        ax.set_ylabel("predator y")
        _soft_grid(ax)
    for ax in axes.flat[len(shown) :]:
        ax.axis("off")
    axes.flat[0].legend(fontsize=8, loc="best")
    fig.suptitle("Phase portraits after burn-in", fontsize=14, weight="bold")
    save_both(fig, path)


def plot_bifurcation_k(scan_k_df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharex=True, constrained_layout=True)
    axes[0].scatter(scan_k_df["k_fear"], scan_k_df["x_max"], color=PREY_COLOR, s=14, label="x max")
    axes[0].scatter(scan_k_df["k_fear"], scan_k_df["x_min"], color=PREY_COLOR, s=14, alpha=0.55, label="x min")
    axes[1].scatter(scan_k_df["k_fear"], scan_k_df["y_max"], color=PREDATOR_COLOR, s=14, label="y max")
    axes[1].scatter(scan_k_df["k_fear"], scan_k_df["y_min"], color=PREDATOR_COLOR, s=14, alpha=0.55, label="y min")
    axes[0].set_title("Prey tail extrema", weight="bold")
    axes[1].set_title("Predator tail extrema", weight="bold")
    for ax in axes:
        _soft_grid(ax)
        ax.legend(fontsize=9)
        ax.set_xlabel("fear intensity k")
        ax.set_ylabel("tail extrema")
        ax.set_ylim(bottom=0)
    fig.suptitle("Bifurcation-style extrema over fear intensity", fontsize=14, weight="bold")
    save_both(fig, path)


def plot_mean_amplitude(scan_k_df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharex=True, constrained_layout=True)
    axes[0].plot(scan_k_df["k_fear"], scan_k_df["x_mean"], label="mean x", color=PREY_COLOR, lw=2)
    axes[0].plot(scan_k_df["k_fear"], scan_k_df["y_mean"], label="mean y", color=PREDATOR_COLOR, lw=2)
    axes[1].plot(scan_k_df["k_fear"], scan_k_df["x_amp"], label="amp x", color=PREY_COLOR, lw=2)
    axes[1].plot(scan_k_df["k_fear"], scan_k_df["y_amp"], label="amp y", color=PREDATOR_COLOR, lw=2)
    axes[0].set_title("Tail means", weight="bold")
    axes[1].set_title("Tail amplitudes", weight="bold")
    for ax in axes:
        _soft_grid(ax)
        ax.legend(fontsize=9)
        ax.set_xlabel("fear intensity k")
        ax.set_ylim(bottom=0)
    axes[0].set_ylabel("mean density")
    axes[1].set_ylabel("tail amplitude")
    fig.suptitle("Mean density and oscillation amplitude vs k", fontsize=14, weight="bold")
    save_both(fig, path)


def _pivot(df: pd.DataFrame, value: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k = np.sort(df["k_fear"].unique())
    alpha = np.sort(df["alpha_mem"].unique())
    mat = df.pivot(index="alpha_mem", columns="k_fear", values=value).loc[alpha, k].to_numpy()
    return k, alpha, mat


def plot_classification_heatmap(scan_df: pd.DataFrame, path: str | Path) -> None:
    k, alpha, mat = _pivot(scan_df, "class_code")
    cmap, norm = _class_cmap()
    fig, ax = plt.subplots(figsize=(9.5, 5.8), constrained_layout=True)
    mesh = ax.pcolormesh(k, alpha, mat, cmap=cmap, norm=norm, shading="nearest")
    _add_class_colorbar(fig, ax, mesh)
    ax.set_yscale("log")
    ax.set_xlabel("fear intensity k")
    ax.set_ylabel("memory update rate alpha")
    ax.set_title("k-alpha classification heatmap", weight="bold")
    save_both(fig, path)


def plot_amplitude_heatmap(scan_df: pd.DataFrame, path: str | Path) -> None:
    df = scan_df.copy()
    df["amp_score"] = np.log10(df["x_amp"].clip(lower=0) + df["y_amp"].clip(lower=0) + 1e-9)
    k, alpha, mat = _pivot(df, "amp_score")
    fig, ax = plt.subplots(figsize=(9.5, 5.8), constrained_layout=True)
    mesh = ax.pcolormesh(k, alpha, mat, cmap="mako" if "mako" in plt.colormaps() else "viridis", shading="nearest")
    fig.colorbar(mesh, ax=ax, label="log10(Ax + Ay + eps)")
    ax.set_yscale("log")
    ax.set_xlabel("fear intensity k")
    ax.set_ylabel("memory update rate alpha")
    ax.set_title("Continuous amplitude heatmap", weight="bold")
    save_both(fig, path)


def plot_theory_boundary(scan_df: pd.DataFrame, theory_df: pd.DataFrame, path: str | Path) -> None:
    k, alpha, mat = _pivot(scan_df, "class_code")
    _, _, margin = _pivot(theory_df, "rh_margin")
    fig, ax = plt.subplots(figsize=(9.5, 5.8), constrained_layout=True)
    cmap, norm = _class_cmap()
    mesh = ax.pcolormesh(k, alpha, mat, cmap=cmap, norm=norm, shading="nearest", alpha=0.86)
    _add_class_colorbar(fig, ax, mesh)
    try:
        ax.contour(k, alpha, margin, levels=[0.0], colors="#111827", linewidths=2.2)
        boundary_handle = plt.Line2D([0], [0], color="#111827", lw=2.2, label="Routh-Hurwitz boundary")
        ax.legend(handles=[boundary_handle], loc="lower right", fontsize=8)
    except ValueError:
        pass
    ax.set_yscale("log")
    ax.set_xlabel("fear intensity k")
    ax.set_ylabel("memory update rate alpha")
    ax.set_title("Routh-Hurwitz boundary over numerical classification", weight="bold")
    save_both(fig, path)


def plot_fear_function_robustness(robust_df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.8), sharex=True)
    for form, group in robust_df.groupby("fear_form"):
        group = group.sort_values("k_fear")
        axes[0].plot(group["k_fear"], group["y_mean"], label=form)
        axes[1].plot(group["k_fear"], group["y_amp"], label=form)
    axes[0].set_ylabel("mean predator y")
    axes[1].set_ylabel("predator amplitude")
    axes[1].set_xlabel("fear intensity k")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=9)
    axes[0].set_title("Robustness to alternative fear functions")
    save_both(fig, path)


def plot_empirical_calibration(path: str | Path) -> None:
    z = np.linspace(0.0, 2.0, 300)
    k = 2.0 / 3.0
    f = 1.0 / (1.0 + k * z)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.plot(z, f, lw=2.0, label="1/(1+kz), k=0.667")
    ax.scatter([1.0], [0.6], color="#d62728", zorder=5, label="Zanette 40% reduction")
    ax.axhline(0.6, color="#d62728", ls="--", lw=1.0)
    ax.axvline(1.0, color="#d62728", ls="--", lw=1.0)
    ax.set_xlabel("normalized perceived risk z")
    ax.set_ylabel("birth-rate multiplier")
    ax.set_ylim(0.0, 1.05)
    ax.set_title("Empirical scale calibration from perceived predation risk")
    ax.grid(alpha=0.25)
    ax.legend()
    save_both(fig, path)


def plot_tritrophic_extension(ts_df: pd.DataFrame, scan_df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(ts_df["t"], ts_df["x"], label="basal prey X")
    axes[0].plot(ts_df["t"], ts_df["y"], label="middle predator Y")
    axes[0].plot(ts_df["t"], ts_df["z"], label="top predator Z")
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("density")
    axes[0].set_title("Tritrophic time series")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.25)
    k1 = np.sort(scan_df["k1"].unique())
    k2 = np.sort(scan_df["k2"].unique())
    mat = scan_df.pivot(index="k2", columns="k1", values="y_amp").loc[k2, k1].to_numpy()
    mesh = axes[1].pcolormesh(k1, k2, np.log10(mat + 1e-9), shading="nearest", cmap="magma")
    fig.colorbar(mesh, ax=axes[1], label="log10 middle predator amplitude")
    axes[1].set_xlabel("basal fear k1")
    axes[1].set_ylabel("middle-predator fear k2")
    axes[1].set_title("Tritrophic fear scan")
    save_both(fig, path)


def plot_representative_cases_overview(case_series: Mapping[str, pd.DataFrame], reps: pd.DataFrame, path: str | Path) -> None:
    """Presentation figure for the three representative mechanisms."""
    selected: list[tuple[str, pd.DataFrame]] = []
    for case_id in ["Case A", "Case B", "Case C"]:
        match = [(name, df) for name, df in case_series.items() if name.startswith(case_id)]
        if match:
            selected.append(match[0])
    if not selected:
        selected = list(case_series.items())[-3:]

    fig, axes = plt.subplots(len(selected), 2, figsize=(12, 3.2 * len(selected)), constrained_layout=True)
    if len(selected) == 1:
        axes = np.array([axes])
    descriptions = {
        "Case A": "fear stabilizes oscillation",
        "Case B": "predator peak falls, oscillation remains",
        "Case C": "long memory amplifies oscillation",
    }
    for row_idx, (name, df) in enumerate(selected):
        case_id = name.split()[0] + (" " + name.split()[1] if len(name.split()) > 1 and name.split()[0] == "Case" else "")
        if not case_id.startswith("Case"):
            case_id = f"Case {chr(ord('A') + row_idx)}"
        rep = reps[reps["case_id"].eq(case_id)]
        subtitle = descriptions.get(case_id, "representative behavior")
        if not rep.empty:
            item = rep.iloc[0]
            subtitle = f"{subtitle}: k={item.k_fear:.3g}, alpha={item.alpha_mem:.3g}"
        ax_ts, ax_phase = axes[row_idx]
        ax_ts.plot(df["t"], df["x"], color=PREY_COLOR, lw=1.5, label="prey x")
        ax_ts.plot(df["t"], df["y"], color=PREDATOR_COLOR, lw=1.5, label="predator y")
        if "z" in df and df["z"].notna().any():
            ax_ts.plot(df["t"], df["z"], color=RISK_COLOR, lw=1.2, label="risk z")
        ax_ts.set_title(f"{case_id}: {subtitle}", weight="bold", fontsize=10)
        ax_ts.set_xlabel("time")
        ax_ts.set_ylabel("density")
        ax_ts.set_ylim(bottom=0)
        _soft_grid(ax_ts)

        tail = df[df["t"] >= 0.55 * df["t"].max()]
        _plot_phase_tail(ax_phase, tail, color=NEUTRAL)
        ax_phase.ticklabel_format(useOffset=False, style="plain")
        ax_phase.set_xlabel("prey x")
        ax_phase.set_ylabel("predator y")
        ax_phase.set_title("tail phase portrait", fontsize=10)
        _soft_grid(ax_phase)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.02), fontsize=9)
    fig.suptitle("Three representative dynamics found by parameter search", fontsize=14, weight="bold", y=1.055)
    save_both(fig, path)


def plot_bifurcation_k_continuation(fixed_df: pd.DataFrame, continuation_df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), constrained_layout=True)
    series = [("fixed initial state", fixed_df, "o", 0.55), ("continuation", continuation_df, "x", 0.9)]
    for _label, df, marker, alpha in series:
        axes[0].scatter(df["k_fear"], df["x_max"], s=16, color=PREY_COLOR, marker=marker, alpha=alpha)
        axes[0].scatter(df["k_fear"], df["x_min"], s=16, color=PREY_COLOR, marker=marker, alpha=alpha * 0.55)
        axes[1].scatter(df["k_fear"], df["y_max"], s=16, color=PREDATOR_COLOR, marker=marker, alpha=alpha)
        axes[1].scatter(df["k_fear"], df["y_min"], s=16, color=PREDATOR_COLOR, marker=marker, alpha=alpha * 0.55)
    axes[0].set_title("Prey extrema", weight="bold")
    axes[1].set_title("Predator extrema", weight="bold")
    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=NEUTRAL, markeredgecolor=NEUTRAL, markersize=6, label="fixed initial state"),
        plt.Line2D([0], [0], marker="x", color=NEUTRAL, markersize=7, linestyle="none", label="continuation"),
        plt.Line2D([0], [0], color=NEUTRAL, lw=2, alpha=0.9, label="darker: max"),
        plt.Line2D([0], [0], color=NEUTRAL, lw=2, alpha=0.35, label="lighter: min"),
    ]
    for ax in axes:
        _soft_grid(ax)
        ax.set_xlabel("fear intensity k")
        ax.set_ylabel("tail extrema")
        ax.set_ylim(bottom=0)
        ax.legend(handles=legend_handles, fontsize=8, loc="upper right")
    fig.suptitle("Fixed-initial scan vs continuation scan", fontsize=14, weight="bold")
    save_both(fig, path)


def plot_results_dashboard(scan_k_df: pd.DataFrame, scan_df: pd.DataFrame, reps: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    ax = axes[0, 0]
    ax.plot(scan_k_df["k_fear"], scan_k_df["y_mean"], color=PREDATOR_COLOR, lw=2.2, label="mean predator")
    ax.plot(scan_k_df["k_fear"], scan_k_df["y_amp"], color=NEUTRAL, lw=2.0, label="predator amplitude")
    ax.set_title("Predator response to fear", weight="bold")
    ax.set_xlabel("fear intensity k")
    ax.set_ylabel("density / amplitude")
    ax.set_ylim(bottom=0)
    _soft_grid(ax)
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    counts = scan_df["class"].value_counts().reindex(CLASS_ORDER).dropna()
    colors = [CLASS_COLORS[name] for name in counts.index]
    ax.barh([CLASS_LABELS[name] for name in counts.index], counts.values, color=colors)
    ax.set_title("k-alpha scan coverage", weight="bold")
    ax.set_xlabel("grid points")
    _soft_grid(ax)

    ax = axes[1, 0]
    width = 0.36
    x = np.arange(len(reps))
    ax.bar(x - width / 2, reps["y_mean"], width=width, color=PREDATOR_COLOR, label="mean predator")
    ax.bar(x + width / 2, reps["y_amp"], width=width, color=NEUTRAL, label="predator amplitude")
    ax.set_xticks(x)
    ax.set_xticklabels(reps["case_id"])
    ax.set_title("Representative cases", weight="bold")
    ax.set_ylabel("tail metric")
    ax.set_ylim(bottom=0)
    _soft_grid(ax)
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    if {"k_fear", "alpha_mem", "class_code"}.issubset(scan_df.columns) and scan_df["k_fear"].nunique() > 2:
        k, alpha, mat = _pivot(scan_df, "class_code")
        cmap, norm = _class_cmap()
        ax.pcolormesh(k, alpha, mat, cmap=cmap, norm=norm, shading="nearest")
        ax.set_yscale("log")
        ax.set_xlabel("k")
        ax.set_ylabel("alpha")
    else:
        for _, row in scan_df.iterrows():
            ax.scatter(row["k_fear"], row["alpha_mem"], color=CLASS_COLORS[CLASS_ORDER[int(row["class_code"])]], s=80)
        ax.set_xlabel("k")
        ax.set_ylabel("alpha")
    ax.set_title("Parameter-plane summary", weight="bold")
    _soft_grid(ax)
    fig.suptitle("Fear-effect modeling results at a glance", fontsize=15, weight="bold")
    save_both(fig, path)


def plot_delay_extension(series_dict: Mapping[str, pd.DataFrame], path: str | Path) -> None:
    fig, axes = plt.subplots(1, len(series_dict), figsize=(4.4 * len(series_dict), 3.8), squeeze=False)
    axes = axes[0]
    for ax, (name, df) in zip(axes, series_dict.items()):
        ax.plot(df["t"], df["x"], label="prey x", lw=1.2)
        ax.plot(df["t"], df["y"], label="predator y", lw=1.2)
        ax.set_title(name, fontsize=10)
        ax.set_xlabel("time")
        ax.set_ylabel("density")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    fig.suptitle("Delay extension: fear responds to delayed predator risk", fontsize=13)
    save_both(fig, path)


def plot_discrete_extension(
    trajectory_dict: Mapping[str, pd.DataFrame],
    bifurcation: Mapping[str, list[float]],
    path: str | Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for label, df in trajectory_dict.items():
        axes[0].plot(df["t"], df["x"], lw=0.9, alpha=0.8, label=label)
    axes[0].set_xlabel("generation")
    axes[0].set_ylabel("prey density")
    axes[0].set_title("Discrete trajectories")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=7, ncol=2)

    axes[1].scatter(bifurcation["k_vals"], bifurcation["prey"], s=0.4, alpha=0.18, label="prey")
    axes[1].scatter(bifurcation["k_vals"], bifurcation["predator"], s=0.4, alpha=0.18, label="predator")
    axes[1].set_xlabel("fear intensity k")
    axes[1].set_ylabel("tail values")
    axes[1].set_title("Discrete bifurcation cloud")
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=8)
    save_both(fig, path)


def plot_leslie_gower_extension(df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].plot(df["t"], df["x"], label="prey", lw=1.3)
    axes[0].plot(df["t"], df["y"], label="predator", lw=1.3)
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("density")
    axes[0].set_title("Leslie-Gower time series")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=8)

    tail = df[df["t"] >= 0.35 * df["t"].max()]
    axes[1].plot(tail["x"], tail["y"], lw=1.2)
    axes[1].set_xlabel("prey")
    axes[1].set_ylabel("predator")
    axes[1].set_title("Leslie-Gower phase portrait")
    axes[1].grid(alpha=0.25)
    save_both(fig, path)
