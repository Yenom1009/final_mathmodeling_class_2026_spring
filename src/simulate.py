"""Simulation utilities with scipy first and RK4 fallback."""

from __future__ import annotations

from typing import Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from .models import (
    model_instant_fear,
    model_memory_fear,
    model_memory_fear_alt_logistic,
    model_no_fear,
    model_tritrophic,
)


Params = Mapping[str, float]


MODEL_REGISTRY: dict[str, Callable[[float, np.ndarray, Params], np.ndarray]] = {
    "no_fear": model_no_fear,
    "M0": model_no_fear,
    "instant": model_instant_fear,
    "instant_fear": model_instant_fear,
    "M1": model_instant_fear,
    "memory": model_memory_fear,
    "memory_fear": model_memory_fear,
    "M2": model_memory_fear,
    "alt_logistic": model_memory_fear_alt_logistic,
    "tritrophic": model_tritrophic,
    "M3": model_tritrophic,
}


def _rk4(
    rhs: Callable[[float, np.ndarray, Params], np.ndarray],
    params: Params,
    initial_state: np.ndarray,
    t_eval: np.ndarray,
) -> np.ndarray:
    values = np.zeros((len(t_eval), len(initial_state)), dtype=float)
    values[0] = initial_state
    for i in range(1, len(t_eval)):
        t = float(t_eval[i - 1])
        dt = float(t_eval[i] - t_eval[i - 1])
        y = values[i - 1]
        k1 = rhs(t, y, params)
        k2 = rhs(t + 0.5 * dt, y + 0.5 * dt * k1, params)
        k3 = rhs(t + 0.5 * dt, y + 0.5 * dt * k2, params)
        k4 = rhs(t + dt, y + dt * k3, params)
        values[i] = y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        if not np.all(np.isfinite(values[i])):
            values[i:] = np.nan
            break
    return values


def simulate_model(
    model_name: str,
    params: Params,
    initial_state: Sequence[float],
    T: float,
    n_points: int,
    solver: str = "auto",
) -> pd.DataFrame:
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"unknown model_name: {model_name}")
    rhs = MODEL_REGISTRY[model_name]
    y0 = np.asarray(initial_state, dtype=float)
    t_eval = np.linspace(0.0, float(T), int(n_points))
    values: np.ndarray
    if solver != "rk4":
        try:
            from scipy.integrate import solve_ivp

            method = "Radau" if solver == "radau" else "DOP853"
            sol = solve_ivp(
                lambda t, state: rhs(t, state, params),
                (0.0, float(T)),
                y0,
                t_eval=t_eval,
                method=method,
                rtol=1e-9,
                atol=1e-11,
            )
            if not sol.success:
                raise RuntimeError(sol.message)
            values = sol.y.T
        except Exception:
            values = _rk4(rhs, params, y0, t_eval)
    else:
        values = _rk4(rhs, params, y0, t_eval)
    if values.shape[1] == 2:
        return pd.DataFrame({"t": t_eval, "x": values[:, 0], "y": values[:, 1], "z": np.nan})
    return pd.DataFrame({"t": t_eval, "x": values[:, 0], "y": values[:, 1], "z": values[:, 2]})


def save_time_series(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
