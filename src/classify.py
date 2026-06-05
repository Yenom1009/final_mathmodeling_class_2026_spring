"""Tail metrics and qualitative labels for numerical trajectories."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_tail_metrics(df: pd.DataFrame, burn_in: float, eps: float = 1e-12) -> dict[str, float]:
    tail = df[df["t"] >= burn_in].copy()
    if tail.empty:
        tail = df.tail(max(2, len(df) // 5)).copy()
    metrics: dict[str, float] = {}
    for col in ("x", "y", "z"):
        if col not in tail:
            continue
        values = tail[col].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        if finite.size == 0:
            metrics[f"{col}_mean"] = float("nan")
            metrics[f"{col}_min"] = float("nan")
            metrics[f"{col}_max"] = float("nan")
            metrics[f"{col}_amp"] = float("nan")
            metrics[f"relative_amp_{col}"] = float("nan")
            continue
        metrics[f"{col}_mean"] = float(np.mean(finite))
        metrics[f"{col}_min"] = float(np.min(finite))
        metrics[f"{col}_max"] = float(np.max(finite))
        metrics[f"{col}_amp"] = float(np.max(finite) - np.min(finite))
        metrics[f"relative_amp_{col}"] = float(metrics[f"{col}_amp"] / (abs(metrics[f"{col}_mean"]) + eps))
    return metrics


def classify_dynamics(metrics: dict[str, float], eps: float = 1e-6) -> str:
    required = ("x_mean", "y_mean", "x_max", "y_max")
    if any(not np.isfinite(metrics.get(key, np.nan)) for key in required):
        return "invalid"
    if metrics["x_min"] < -1e-7 or metrics["y_min"] < -1e-7:
        return "invalid"
    if metrics["y_mean"] < eps or metrics["y_max"] < 1e-5:
        return "predator_extinct"
    if metrics["x_mean"] < eps or metrics["x_max"] < 1e-5:
        return "prey_extinct"
    if metrics["y_min"] < 1e-4 or metrics["x_min"] < 1e-4:
        return "low_density_risk"
    rel_x = metrics.get("relative_amp_x", float("inf"))
    rel_y = metrics.get("relative_amp_y", float("inf"))
    if rel_x < 1e-3 and rel_y < 1e-3:
        return "stable_coexistence"
    return "oscillatory_coexistence"


CLASS_ORDER = [
    "stable_coexistence",
    "oscillatory_coexistence",
    "predator_extinct",
    "prey_extinct",
    "low_density_risk",
    "invalid",
]


CLASS_TO_CODE = {name: idx for idx, name in enumerate(CLASS_ORDER)}

