"""Parameter scans and representative-case selection."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .classify import CLASS_TO_CODE, classify_dynamics, compute_tail_metrics
from .simulate import simulate_model
from .theory import positive_equilibrium, routh_hurwitz_coefficients


Params = Mapping[str, float]


def scan_k(
    params: Params,
    k_values: Sequence[float],
    alpha_mem: float,
    initial_state: Sequence[float],
    T: float,
    burn_in: float,
    n_points: int,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    rows = []
    for k in k_values:
        run_params = {**params, "k_fear": float(k), "alpha_mem": float(alpha_mem)}
        df = simulate_model("memory", run_params, initial_state, T=T, n_points=n_points)
        metrics = compute_tail_metrics(df, burn_in=burn_in)
        metrics.update({"k_fear": float(k), "alpha_mem": float(alpha_mem), "class": classify_dynamics(metrics)})
        rows.append(metrics)
    result = pd.DataFrame(rows)
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)
    return result


def scan_k_continuation(
    params: Params,
    k_values: Sequence[float],
    alpha_mem: float,
    initial_state: Sequence[float],
    T: float,
    burn_in: float,
    n_points: int,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Scan k while using each run's final state as the next initial state."""
    rows = []
    current_state = np.asarray(initial_state, dtype=float)
    for k in k_values:
        run_params = {**params, "k_fear": float(k), "alpha_mem": float(alpha_mem)}
        df = simulate_model("memory", run_params, current_state, T=T, n_points=n_points)
        metrics = compute_tail_metrics(df, burn_in=burn_in)
        finite_tail = df[["x", "y", "z"]].replace([np.inf, -np.inf], np.nan).dropna()
        if not finite_tail.empty:
            next_state = finite_tail.iloc[-1].to_numpy(dtype=float)
            if np.isfinite(next_state).all():
                current_state = next_state
        metrics.update(
            {
                "k_fear": float(k),
                "alpha_mem": float(alpha_mem),
                "class": classify_dynamics(metrics),
                "continuation": True,
            }
        )
        rows.append(metrics)
    result = pd.DataFrame(rows)
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)
    return result


def _vectorized_step(x, y, z, k_grid, alpha_grid, params):
    r = float(params["r"])
    d1 = float(params.get("d1", 0.0))
    d2 = float(params["d2"])
    p_pred = float(params["p_pred"])
    h_handle = float(params["h_handle"])
    eta = float(params["eta"])
    d3 = float(params["d3"])
    pred = p_pred * x * y / (1.0 + h_handle * x)
    dx = r * x / (1.0 + k_grid * z) - d1 * x - d2 * x * x - pred
    dy = eta * pred - d3 * y
    dz = alpha_grid * (y - z)
    return dx, dy, dz


def _classify_arrays(x_mean, y_mean, x_min, x_max, y_min, y_max, x_amp, y_amp):
    rel_x = x_amp / (np.abs(x_mean) + 1e-12)
    rel_y = y_amp / (np.abs(y_mean) + 1e-12)
    labels = np.full(x_mean.shape, "oscillatory_coexistence", dtype=object)
    labels[(rel_x < 1e-3) & (rel_y < 1e-3) & (x_mean > 1e-6) & (y_mean > 1e-6)] = "stable_coexistence"
    labels[(y_mean < 1e-6) | (y_max < 1e-5)] = "predator_extinct"
    labels[(x_mean < 1e-6) | (x_max < 1e-5)] = "prey_extinct"
    labels[(labels == "oscillatory_coexistence") & ((y_min < 1e-4) | (x_min < 1e-4))] = "low_density_risk"
    finite = np.isfinite(x_mean) & np.isfinite(y_mean) & np.isfinite(x_min) & np.isfinite(y_min)
    labels[(~finite) | (x_min < -1e-7) | (y_min < -1e-7)] = "invalid"
    return labels, rel_x, rel_y


def scan_k_alpha(
    params: Params,
    k_grid: Sequence[float],
    alpha_grid: Sequence[float],
    initial_state: Sequence[float],
    T: float,
    burn_in: float,
    n_steps: int,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    k_values = np.asarray(k_grid, dtype=float)
    alpha_values = np.asarray(alpha_grid, dtype=float)
    K, A = np.meshgrid(k_values, alpha_values)
    x = np.full_like(K, float(initial_state[0]), dtype=float)
    y = np.full_like(K, float(initial_state[1]), dtype=float)
    z = np.full_like(K, float(initial_state[2]), dtype=float)
    dt = float(T) / float(n_steps - 1)
    burn_step = int(round(float(burn_in) / dt))
    count = 0
    x_sum = np.zeros_like(K, dtype=float)
    y_sum = np.zeros_like(K, dtype=float)
    z_sum = np.zeros_like(K, dtype=float)
    x_min = np.full_like(K, np.inf, dtype=float)
    y_min = np.full_like(K, np.inf, dtype=float)
    z_min = np.full_like(K, np.inf, dtype=float)
    x_max = np.full_like(K, -np.inf, dtype=float)
    y_max = np.full_like(K, -np.inf, dtype=float)
    z_max = np.full_like(K, -np.inf, dtype=float)
    invalid = np.zeros_like(K, dtype=bool)

    for step in range(n_steps):
        if step >= burn_step:
            finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
            count += 1
            x_sum += np.where(finite, x, 0.0)
            y_sum += np.where(finite, y, 0.0)
            z_sum += np.where(finite, z, 0.0)
            x_min = np.where(finite, np.minimum(x_min, x), x_min)
            y_min = np.where(finite, np.minimum(y_min, y), y_min)
            z_min = np.where(finite, np.minimum(z_min, z), z_min)
            x_max = np.where(finite, np.maximum(x_max, x), x_max)
            y_max = np.where(finite, np.maximum(y_max, y), y_max)
            z_max = np.where(finite, np.maximum(z_max, z), z_max)
        if step == n_steps - 1:
            break
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            k1 = _vectorized_step(x, y, z, K, A, params)
            k2 = _vectorized_step(x + 0.5 * dt * k1[0], y + 0.5 * dt * k1[1], z + 0.5 * dt * k1[2], K, A, params)
            k3 = _vectorized_step(x + 0.5 * dt * k2[0], y + 0.5 * dt * k2[1], z + 0.5 * dt * k2[2], K, A, params)
            k4 = _vectorized_step(x + dt * k3[0], y + dt * k3[1], z + dt * k3[2], K, A, params)
            x = x + (dt / 6.0) * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0])
            y = y + (dt / 6.0) * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1])
            z = z + (dt / 6.0) * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2])
        invalid |= (~np.isfinite(x)) | (~np.isfinite(y)) | (~np.isfinite(z)) | (np.abs(x) > 1e9) | (np.abs(y) > 1e9)
        x = np.where(invalid, np.nan, x)
        y = np.where(invalid, np.nan, y)
        z = np.where(invalid, np.nan, z)

    x_mean = x_sum / max(count, 1)
    y_mean = y_sum / max(count, 1)
    z_mean = z_sum / max(count, 1)
    x_amp = x_max - x_min
    y_amp = y_max - y_min
    z_amp = z_max - z_min
    labels, rel_x, rel_y = _classify_arrays(x_mean, y_mean, x_min, x_max, y_min, y_max, x_amp, y_amp)
    labels[invalid] = "invalid"

    rows = []
    for i, alpha in enumerate(alpha_values):
        for j, k in enumerate(k_values):
            rows.append(
                {
                    "k_fear": float(k),
                    "alpha_mem": float(alpha),
                    "x_mean": float(x_mean[i, j]),
                    "y_mean": float(y_mean[i, j]),
                    "z_mean": float(z_mean[i, j]),
                    "x_min": float(x_min[i, j]),
                    "x_max": float(x_max[i, j]),
                    "y_min": float(y_min[i, j]),
                    "y_max": float(y_max[i, j]),
                    "z_min": float(z_min[i, j]),
                    "z_max": float(z_max[i, j]),
                    "x_amp": float(x_amp[i, j]),
                    "y_amp": float(y_amp[i, j]),
                    "z_amp": float(z_amp[i, j]),
                    "relative_amp_x": float(rel_x[i, j]),
                    "relative_amp_y": float(rel_y[i, j]),
                    "class": str(labels[i, j]),
                    "class_code": CLASS_TO_CODE[str(labels[i, j])],
                }
            )
    result = pd.DataFrame(rows)
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)
    return result


def compute_theory_boundary(params: Params, k_grid: Sequence[float], alpha_grid: Sequence[float], output_path=None) -> pd.DataFrame:
    rows = []
    for alpha in alpha_grid:
        for k in k_grid:
            eq = positive_equilibrium(params, float(k))
            if eq is None:
                rows.append({"k_fear": float(k), "alpha_mem": float(alpha), "stable_theory": False, "rh_margin": np.nan})
                continue
            A1, A2, A3 = routh_hurwitz_coefficients(params, float(k), float(alpha))
            stable = A1 > 0 and A2 > 0 and A3 > 0 and A1 * A2 > A3
            rows.append(
                {
                    "k_fear": float(k),
                    "alpha_mem": float(alpha),
                    "stable_theory": bool(stable),
                    "A1": A1,
                    "A2": A2,
                    "A3": A3,
                    "rh_margin": A1 * A2 - A3,
                }
            )
    df = pd.DataFrame(rows)
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
    return df


def random_parameter_search(
    n_samples: int,
    seed: int = 20260604,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_samples):
        params = {
            "r": rng.uniform(0.05, 2.0),
            "d1": rng.uniform(0.0, 0.5),
            "d2": rng.uniform(0.001, 0.2),
            "p_pred": rng.uniform(0.05, 2.0),
            "h_handle": rng.uniform(0.0, 1.0),
            "eta": rng.uniform(0.05, 1.0),
            "d3": rng.uniform(0.01, 1.0),
        }
        k = rng.uniform(0.0, 20.0)
        alpha = 10 ** rng.uniform(-2, 2)
        eq = positive_equilibrium(params, k)
        if eq is None:
            continue
        run_params = {**params, "k_fear": k, "alpha_mem": alpha}
        df = simulate_model("memory", run_params, [eq.x * 1.2, max(eq.y * 0.8, 0.05), max(eq.z, 0.05)], T=300.0, n_points=1201)
        metrics = compute_tail_metrics(df, burn_in=180.0)
        rows.append({**params, "k_fear": k, "alpha_mem": alpha, **metrics, "class": classify_dynamics(metrics)})
    result = pd.DataFrame(rows)
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)
    return result


def find_representative_cases(scan_df: pd.DataFrame, scan_k_df: pd.DataFrame, params: Params, output_path=None) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for alpha in sorted(scan_df["alpha_mem"].unique(), key=lambda v: abs(np.log10(v) - 1.0)):
        alpha_slice = scan_df[np.isclose(scan_df["alpha_mem"], alpha)]
        k0 = alpha_slice.loc[alpha_slice["k_fear"].idxmin()]
        stable_high = alpha_slice[(alpha_slice["k_fear"] >= 1.0) & (alpha_slice["class"] == "stable_coexistence")]
        if k0["class"] == "oscillatory_coexistence" and not stable_high.empty:
            chosen = stable_high.sort_values("k_fear").iloc[0]
            rows.append(
                {
                    "case_id": "Case A",
                    "description": "No fear oscillates, stronger fear stabilizes coexistence.",
                    "k_fear": chosen["k_fear"],
                    "alpha_mem": chosen["alpha_mem"],
                    "model": "M2 memory fear",
                    "class": chosen["class"],
                    "x_mean": chosen["x_mean"],
                    "y_mean": chosen["y_mean"],
                    "x_amp": chosen["x_amp"],
                    "y_amp": chosen["y_amp"],
                }
            )
            break

    for alpha in sorted(scan_df["alpha_mem"].unique()):
        alpha_slice = scan_df[np.isclose(scan_df["alpha_mem"], alpha)].sort_values("k_fear")
        oscill = alpha_slice[alpha_slice["class"] == "oscillatory_coexistence"]
        if len(oscill) < 2:
            continue
        base = oscill.iloc[0]
        lower = oscill[(oscill["k_fear"] > base["k_fear"]) & (oscill["y_max"] < 0.8 * base["y_max"])]
        if lower.empty:
            continue
        chosen = lower.sort_values(["y_max", "k_fear"]).iloc[0]
        rows.append(
            {
                "case_id": "Case B",
                "description": "Fear lowers predator peak while oscillation remains under slow memory.",
                "k_fear": chosen["k_fear"],
                "alpha_mem": chosen["alpha_mem"],
                "model": "M2 memory fear",
                "class": chosen["class"],
                "x_mean": chosen["x_mean"],
                "y_mean": chosen["y_mean"],
                "x_amp": chosen["x_amp"],
                "y_amp": chosen["y_amp"],
            }
        )
        break

    best_c = None
    for k in sorted(scan_df["k_fear"].unique()):
        k_slice = scan_df[np.isclose(scan_df["k_fear"], k)].sort_values("alpha_mem")
        low_osc = k_slice[(k_slice["alpha_mem"] <= 0.03) & (k_slice["class"] == "oscillatory_coexistence")]
        high_stable = k_slice[(k_slice["alpha_mem"] >= 1.0) & (k_slice["class"] == "stable_coexistence")]
        if low_osc.empty or high_stable.empty:
            continue
        cand = low_osc.sort_values("y_amp", ascending=False).iloc[0]
        if best_c is None or cand["y_amp"] > best_c["y_amp"]:
            best_c = cand
    if best_c is not None:
        rows.append(
            {
                "case_id": "Case C",
                "description": "Long memory induces or amplifies oscillation while fast memory is stable.",
                "k_fear": best_c["k_fear"],
                "alpha_mem": best_c["alpha_mem"],
                "model": "M2 memory fear",
                "class": best_c["class"],
                "x_mean": best_c["x_mean"],
                "y_mean": best_c["y_mean"],
                "x_amp": best_c["x_amp"],
                "y_amp": best_c["y_amp"],
            }
        )

    while len(rows) < 3:
        fallback = scan_df.sort_values("relative_amp_x", ascending=False).iloc[min(len(rows), len(scan_df) - 1)]
        rows.append(
            {
                "case_id": f"Fallback {len(rows) + 1}",
                "description": "Representative high-amplitude point from the scan.",
                "k_fear": fallback["k_fear"],
                "alpha_mem": fallback["alpha_mem"],
                "model": "M2 memory fear",
                "class": fallback["class"],
                "x_mean": fallback["x_mean"],
                "y_mean": fallback["y_mean"],
                "x_amp": fallback["x_amp"],
                "y_amp": fallback["y_amp"],
            }
        )
    result = pd.DataFrame(rows)
    for key, value in params.items():
        result[key] = value
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)
    return result
