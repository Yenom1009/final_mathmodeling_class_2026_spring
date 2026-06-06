from __future__ import annotations

import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Optional

from params import Params
from models.memory import MemoryModel
from models.fear import FEAR_STRATEGIES
from core.engine import integrate
from analyze.metrics import compute_tail_metrics
from analyze.classifier import classify_dynamics, CLASS_TO_CODE


def scan_k(
    p,
    k_values: np.ndarray,
    alpha_mem: float = 10.0,
    T: Optional[float] = None,
    burn_in: Optional[float] = None,
    n_points: Optional[int] = None,
    desc: str = "k-scan",
) -> pd.DataFrame:
    T = T or p.T
    burn_in = burn_in or p.burn_in
    n_points = n_points or p.n_points
    rows = []
    for k in tqdm(k_values, desc=desc):
        p.fear_level = k
        p.memory_rate = alpha_mem
        result = integrate(MemoryModel().rhs, p, fear_strategy=FEAR_STRATEGIES["rational"],
                           initial_state=[p.prey_0, p.pred_0, p.memory_0])
        df = result.to_dataframe()
        metrics = compute_tail_metrics(df, burn_in)
        classification = classify_dynamics(metrics)
        row = {"k": k, "class": classification, "class_code": CLASS_TO_CODE.get(classification, -1)}
        row.update(metrics)
        rows.append(row)
    return pd.DataFrame(rows)


def scan_k_alpha(
    params,
    k_grid: np.ndarray,
    alpha_grid: np.ndarray,
    T: float = 800.0,
    burn_in: float = 300.0,
    dt: float = 0.1,
    desc: str = "2D scan",
) -> pd.DataFrame:
    nk, na = len(k_grid), len(alpha_grid)
    x0, y0, z0 = params.x0, params.y0, params.z0
    n_steps = int(T / dt)
    n_burn = int(burn_in / dt)

    x = np.full((nk, na), x0, dtype=np.float64)
    y = np.full((nk, na), y0, dtype=np.float64)
    z = np.full((nk, na), z0, dtype=np.float64)

    K, A = np.meshgrid(k_grid, alpha_grid, indexing='ij')

    x_sum = np.zeros((nk, na), dtype=np.float64)
    y_sum = np.zeros((nk, na), dtype=np.float64)
    x_min = np.full((nk, na), np.inf, dtype=np.float64)
    x_max = np.full((nk, na), -np.inf, dtype=np.float64)
    y_min = np.full((nk, na), np.inf, dtype=np.float64)
    y_max = np.full((nk, na), -np.inf, dtype=np.float64)
    tail_count = np.zeros((nk, na), dtype=np.int64)

    r, d1, d2, p, h, eta, d3 = params.r, params.d1, params.d2, params.p, params.h, params.eta, params.d3

    with tqdm(total=n_steps, desc=desc) as pbar:
        for step in range(n_steps):
            f = 1.0 / (1.0 + K * z)
            pred = p * x / (1.0 + h * x)

            k1_x = dt * (f * r * x - d1 * x - d2 * x * x - pred * y)
            k1_y = dt * (eta * pred * y - d3 * y)
            k1_z = dt * A * (y - z)

            x2 = np.maximum(x + 0.5 * k1_x, 0)
            y2 = np.maximum(y + 0.5 * k1_y, 0)
            z2 = np.maximum(z + 0.5 * k1_z, 0)
            f2 = 1.0 / (1.0 + K * z2)
            pred2 = p * x2 / (1.0 + h * x2)
            k2_x = dt * (f2 * r * x2 - d1 * x2 - d2 * x2 * x2 - pred2 * y2)
            k2_y = dt * (eta * pred2 * y2 - d3 * y2)
            k2_z = dt * A * (y2 - z2)

            x3 = np.maximum(x + 0.5 * k2_x, 0)
            y3 = np.maximum(y + 0.5 * k2_y, 0)
            z3 = np.maximum(z + 0.5 * k2_z, 0)
            f3 = 1.0 / (1.0 + K * z3)
            pred3 = p * x3 / (1.0 + h * x3)
            k3_x = dt * (f3 * r * x3 - d1 * x3 - d2 * x3 * x3 - pred3 * y3)
            k3_y = dt * (eta * pred3 * y3 - d3 * y3)
            k3_z = dt * A * (y3 - z3)

            x4 = np.maximum(x + k3_x, 0)
            y4 = np.maximum(y + k3_y, 0)
            z4 = np.maximum(z + k3_z, 0)
            f4 = 1.0 / (1.0 + K * z4)
            pred4 = p * x4 / (1.0 + h * x4)
            k4_x = dt * (f4 * r * x4 - d1 * x4 - d2 * x4 * x4 - pred4 * y4)
            k4_y = dt * (eta * pred4 * y4 - d3 * y4)
            k4_z = dt * A * (y4 - z4)

            x += (k1_x + 2 * k2_x + 2 * k3_x + k4_x) / 6
            y += (k1_y + 2 * k2_y + 2 * k3_y + k4_y) / 6
            z += (k1_z + 2 * k2_z + 2 * k3_z + k4_z) / 6
            x = np.maximum(x, 0)
            y = np.maximum(y, 0)
            z = np.maximum(z, 0)

            invalid = ~(np.isfinite(x) & np.isfinite(y))
            x[invalid] = x0
            y[invalid] = 0.0
            z[invalid] = 0.0

            if step >= n_burn:
                x_sum += x
                y_sum += y
                np.minimum(x_min, x, out=x_min)
                np.maximum(x_max, x, out=x_max)
                np.minimum(y_min, y, out=y_min)
                np.maximum(y_max, y, out=y_max)
                tail_count += 1

            if step % 100 == 0:
                pbar.update(100)

        remaining = n_steps % 100
        if remaining:
            pbar.update(remaining)

    tail_count = np.maximum(tail_count, 1)
    x_mean = x_sum / tail_count
    y_mean = y_sum / tail_count

    class_grid = np.full((nk, na), "stable_coexistence", dtype=object)

    invalid_mask = ~(np.isfinite(x_mean) & np.isfinite(y_mean) & (x_mean >= 0) & (y_mean >= 0))
    class_grid[invalid_mask] = "invalid"

    pred_ext = (y_mean < 1e-6) | (y_max < 1e-5)
    class_grid[pred_ext] = "predator_extinct"

    prey_ext = (x_mean < 1e-6) | (x_max < 1e-5)
    class_grid[prey_ext] = "prey_extinct"

    still_alive = ~pred_ext & ~prey_ext & ~invalid_mask
    low_dens = (x_min < 1e-4) | (y_min < 1e-4)
    class_grid[still_alive & low_dens] = "low_density_risk"

    x_amp = x_max - x_min
    y_amp = y_max - y_min
    x_rel = x_amp / (x_mean + 1e-15)
    y_rel = y_amp / (y_mean + 1e-15)
    rel_amp = np.maximum(x_rel, y_rel)

    osc_mask = rel_amp >= 1e-3
    osc_eligible = still_alive & ~low_dens
    class_grid[osc_eligible & osc_mask] = "oscillatory_coexistence"

    return _build_2d_df(k_grid, alpha_grid, class_grid, rel_amp, x_mean, y_mean)


def _build_2d_df(k_grid, alpha_grid, class_grid, amp_grid, x_mean_grid, y_mean_grid):
    rows = []
    for i, k in enumerate(k_grid):
        for j, alpha in enumerate(alpha_grid):
            rows.append({
                "k": k,
                "alpha": alpha,
                "class": class_grid[i, j],
                "class_code": CLASS_TO_CODE.get(class_grid[i, j], -1),
                "amplitude": amp_grid[i, j],
                "x_mean": x_mean_grid[i, j],
                "y_mean": y_mean_grid[i, j],
            })
    return pd.DataFrame(rows)


def compute_theory_boundary(params, k_grid: np.ndarray, alpha_grid: np.ndarray):
    from analyze.stability import theory_grid
    return theory_grid(params, k_grid, alpha_grid)


__all__ = ["scan_k", "scan_k_alpha", "compute_theory_boundary"]