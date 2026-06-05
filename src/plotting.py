"""Figure generation for the fear predator-prey project."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".mplconfig"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

from .classify import CLASS_ORDER


FIG_DPI = 220


def save_both(fig: plt.Figure, png_path: str | Path) -> None:
    png = Path(png_path)
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=FIG_DPI, bbox_inches="tight")
    fig.savefig(png.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_mechanism_diagram(path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.axis("off")
    boxes = {
        "Predator density\ny(t)": (0.08, 0.63),
        "Perceived risk\nz(t)": (0.34, 0.63),
        "Fear multiplier\n1/(1+kz)": (0.60, 0.63),
        "Lower prey\nbirth rate": (0.82, 0.63),
        "Prey density\nx(t)": (0.34, 0.20),
        "Holling II predation\npxy/(1+hx)": (0.60, 0.20),
        "Predator-prey\ndynamics": (0.82, 0.20),
    }
    for text, (x, y) in boxes.items():
        ax.text(x, y, text, ha="center", va="center", fontsize=11, bbox=dict(boxstyle="round,pad=0.45", fc="#f6f8fa", ec="#3a506b"))
    arrows = [
        ("Predator density\ny(t)", "Perceived risk\nz(t)"),
        ("Perceived risk\nz(t)", "Fear multiplier\n1/(1+kz)"),
        ("Fear multiplier\n1/(1+kz)", "Lower prey\nbirth rate"),
        ("Lower prey\nbirth rate", "Predator-prey\ndynamics"),
        ("Prey density\nx(t)", "Holling II predation\npxy/(1+hx)"),
        ("Predator density\ny(t)", "Holling II predation\npxy/(1+hx)"),
        ("Holling II predation\npxy/(1+hx)", "Predator-prey\ndynamics"),
    ]
    for src, dst in arrows:
        x1, y1 = boxes[src]
        x2, y2 = boxes[dst]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=1.8, color="#1f2937"))
    ax.set_title("Mechanism: direct predation and non-consumptive fear feedback", fontsize=14)
    save_both(fig, path)


def plot_model_layers(path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.axis("off")
    layers = [
        ("M0", "No fear baseline", "x,y"),
        ("M1", "Instant fear", "z=y"),
        ("M2", "Memory fear", "z'=alpha(y-z)"),
        ("M3", "Tritrophic extension", "X,Y,Z with two fear links"),
    ]
    xs = np.linspace(0.12, 0.88, len(layers))
    for i, (code, title, detail) in enumerate(layers):
        ax.text(xs[i], 0.55, code, ha="center", va="center", fontsize=18, weight="bold", bbox=dict(boxstyle="circle,pad=0.55", fc="#e8f1ff", ec="#315c99"))
        ax.text(xs[i], 0.31, f"{title}\n{detail}", ha="center", va="center", fontsize=11)
        if i < len(layers) - 1:
            ax.annotate("", xy=(xs[i + 1] - 0.075, 0.55), xytext=(xs[i] + 0.075, 0.55), arrowprops=dict(arrowstyle="->", lw=1.8))
    ax.set_title("Model layers used in the project", fontsize=14)
    save_both(fig, path)


def plot_time_series_cases(case_series: Mapping[str, pd.DataFrame], path: str | Path) -> None:
    fig, axes = plt.subplots(len(case_series), 1, figsize=(10, 2.2 * len(case_series)), sharex=False)
    if len(case_series) == 1:
        axes = [axes]
    for ax, (name, df) in zip(axes, case_series.items()):
        ax.plot(df["t"], df["x"], label="prey x", lw=1.2)
        ax.plot(df["t"], df["y"], label="predator y", lw=1.2)
        if "z" in df and df["z"].notna().any():
            ax.plot(df["t"], df["z"], label="risk z", lw=1.0, alpha=0.8)
        ax.set_title(name, fontsize=10)
        ax.set_ylabel("density")
        ax.grid(alpha=0.25)
    axes[-1].set_xlabel("time")
    axes[0].legend(ncol=3, fontsize=9, loc="upper right")
    save_both(fig, path)


def plot_phase_portraits(case_series: Mapping[str, pd.DataFrame], path: str | Path) -> None:
    fig, axes = plt.subplots(1, min(4, len(case_series)), figsize=(12, 3.2))
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    for ax, (name, df) in zip(axes, list(case_series.items())[: len(axes)]):
        tail = df[df["t"] >= 0.4 * df["t"].max()]
        ax.plot(tail["x"], tail["y"], lw=1.2)
        ax.scatter(tail["x"].iloc[0], tail["y"].iloc[0], s=18, label="tail start")
        ax.set_title(name, fontsize=9)
        ax.set_xlabel("prey x")
        ax.set_ylabel("predator y")
        ax.grid(alpha=0.25)
    save_both(fig, path)


def plot_bifurcation_k(scan_k_df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.8), sharex=True)
    axes[0].plot(scan_k_df["k_fear"], scan_k_df["x_max"], color="#1f77b4", label="x max")
    axes[0].plot(scan_k_df["k_fear"], scan_k_df["x_min"], color="#1f77b4", ls="--", label="x min")
    axes[1].plot(scan_k_df["k_fear"], scan_k_df["y_max"], color="#d62728", label="y max")
    axes[1].plot(scan_k_df["k_fear"], scan_k_df["y_min"], color="#d62728", ls="--", label="y min")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=9)
        ax.set_ylabel("tail extrema")
    axes[1].set_xlabel("fear intensity k")
    axes[0].set_title("Bifurcation-style extrema over k")
    save_both(fig, path)


def plot_mean_amplitude(scan_k_df: pd.DataFrame, path: str | Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.8), sharex=True)
    axes[0].plot(scan_k_df["k_fear"], scan_k_df["x_mean"], label="mean x")
    axes[0].plot(scan_k_df["k_fear"], scan_k_df["y_mean"], label="mean y")
    axes[1].plot(scan_k_df["k_fear"], scan_k_df["x_amp"], label="amp x")
    axes[1].plot(scan_k_df["k_fear"], scan_k_df["y_amp"], label="amp y")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=9)
    axes[1].set_xlabel("fear intensity k")
    axes[0].set_ylabel("tail mean")
    axes[1].set_ylabel("tail amplitude")
    axes[0].set_title("Mean density and oscillation amplitude vs k")
    save_both(fig, path)


def _pivot(df: pd.DataFrame, value: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k = np.sort(df["k_fear"].unique())
    alpha = np.sort(df["alpha_mem"].unique())
    mat = df.pivot(index="alpha_mem", columns="k_fear", values=value).loc[alpha, k].to_numpy()
    return k, alpha, mat


def plot_classification_heatmap(scan_df: pd.DataFrame, path: str | Path) -> None:
    k, alpha, mat = _pivot(scan_df, "class_code")
    cmap = ListedColormap(["#2ca02c", "#ffbf00", "#9467bd", "#7f7f7f", "#d62728", "#111111"])
    norm = BoundaryNorm(np.arange(-0.5, len(CLASS_ORDER) + 0.5, 1), cmap.N)
    fig, ax = plt.subplots(figsize=(9, 5.6))
    mesh = ax.pcolormesh(k, alpha, mat, cmap=cmap, norm=norm, shading="nearest")
    cbar = fig.colorbar(mesh, ax=ax, ticks=range(len(CLASS_ORDER)))
    cbar.ax.set_yticklabels(CLASS_ORDER)
    ax.set_yscale("log")
    ax.set_xlabel("fear intensity k")
    ax.set_ylabel("memory update rate alpha")
    ax.set_title("k-alpha classification heatmap")
    save_both(fig, path)


def plot_amplitude_heatmap(scan_df: pd.DataFrame, path: str | Path) -> None:
    df = scan_df.copy()
    df["amp_score"] = np.log10(df["x_amp"].clip(lower=0) + df["y_amp"].clip(lower=0) + 1e-9)
    k, alpha, mat = _pivot(df, "amp_score")
    fig, ax = plt.subplots(figsize=(9, 5.6))
    mesh = ax.pcolormesh(k, alpha, mat, cmap="viridis", shading="nearest")
    fig.colorbar(mesh, ax=ax, label="log10(Ax + Ay + eps)")
    ax.set_yscale("log")
    ax.set_xlabel("fear intensity k")
    ax.set_ylabel("memory update rate alpha")
    ax.set_title("Continuous amplitude heatmap")
    save_both(fig, path)


def plot_theory_boundary(scan_df: pd.DataFrame, theory_df: pd.DataFrame, path: str | Path) -> None:
    k, alpha, mat = _pivot(scan_df, "class_code")
    _, _, margin = _pivot(theory_df, "rh_margin")
    fig, ax = plt.subplots(figsize=(9, 5.6))
    cmap = ListedColormap(["#2ca02c", "#ffbf00", "#9467bd", "#7f7f7f", "#d62728", "#111111"])
    norm = BoundaryNorm(np.arange(-0.5, len(CLASS_ORDER) + 0.5, 1), cmap.N)
    mesh = ax.pcolormesh(k, alpha, mat, cmap=cmap, norm=norm, shading="nearest", alpha=0.86)
    fig.colorbar(mesh, ax=ax, ticks=range(len(CLASS_ORDER))).ax.set_yticklabels(CLASS_ORDER)
    try:
        ax.contour(k, alpha, margin, levels=[0.0], colors="black", linewidths=2.0)
    except ValueError:
        pass
    ax.set_yscale("log")
    ax.set_xlabel("fear intensity k")
    ax.set_ylabel("memory update rate alpha")
    ax.set_title("Routh-Hurwitz boundary over numerical classification")
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
