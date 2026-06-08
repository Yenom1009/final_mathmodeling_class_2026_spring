"""Simulation utilities with scipy first and RK4 fallback."""

from __future__ import annotations

from typing import Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from .model_catalog import resolve_model_name
from .models import (
    model_delay_fear,
    model_instant_fear,
    model_leslie_gower,
    model_memory_fear,
    model_memory_fear_alt_logistic,
    model_no_fear,
    model_tritrophic,
    step_discrete_fear,
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
    "leslie_gower": model_leslie_gower,
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
    canonical_name = resolve_model_name(model_name)
    rhs = MODEL_REGISTRY[canonical_name]
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


def simulate_delay_model(
    params: Params,
    initial_state: Sequence[float],
    history_state: Sequence[float],
    tau: float,
    T: float,
    n_points: int,
) -> pd.DataFrame:
    """Simple RK4-style method-of-steps solver for the delay extension."""
    y0 = np.asarray(initial_state, dtype=float)
    history = np.asarray(history_state, dtype=float)
    t_eval = np.linspace(0.0, float(T), int(n_points))
    dt = float(t_eval[1] - t_eval[0]) if len(t_eval) > 1 else 0.0
    delay_steps = max(1, int(round(float(tau) / max(dt, 1e-12))))
    values = np.zeros((len(t_eval), len(y0)), dtype=float)
    values[0] = y0

    def delayed(idx: int) -> np.ndarray:
        if idx - delay_steps >= 0:
            return values[idx - delay_steps]
        return history

    for i in range(1, len(t_eval)):
        t = float(t_eval[i - 1])
        y = values[i - 1]
        y_delay = delayed(i - 1)
        k1 = model_delay_fear(t, y, y_delay, params)
        k2 = model_delay_fear(t + 0.5 * dt, y + 0.5 * dt * k1, y_delay, params)
        k3 = model_delay_fear(t + 0.5 * dt, y + 0.5 * dt * k2, y_delay, params)
        k4 = model_delay_fear(t + dt, y + dt * k3, y_delay, params)
        values[i] = y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        values[i] = np.maximum(values[i], 0.0)
        if not np.all(np.isfinite(values[i])):
            values[i:] = np.nan
            break
    return pd.DataFrame({"t": t_eval, "x": values[:, 0], "y": values[:, 1]})


def simulate_discrete_map(
    params: Params,
    initial_state: Sequence[float],
    k_values: Sequence[float],
    n_generations: int,
) -> tuple[dict[str, pd.DataFrame], dict[str, list[float]]]:
    """Generate trajectories and a bifurcation cloud for the discrete extension."""
    x0, y0 = float(initial_state[0]), float(initial_state[1])
    trajectories: dict[str, pd.DataFrame] = {}
    for k_fear in k_values:
        xs = [x0]
        ys = [y0]
        for _ in range(int(n_generations)):
            xn, yn = step_discrete_fear(xs[-1], ys[-1], params, float(k_fear))
            xs.append(xn)
            ys.append(yn)
        trajectories[f"k={float(k_fear):.1f}"] = pd.DataFrame({"t": np.arange(len(xs)), "x": xs, "y": ys})

    bif_k_vals: list[float] = []
    bif_prey: list[float] = []
    bif_pred: list[float] = []
    for k_fear in np.linspace(min(k_values), max(k_values), 200):
        xs = [x0]
        ys = [y0]
        for _ in range(int(n_generations)):
            xn, yn = step_discrete_fear(xs[-1], ys[-1], params, float(k_fear))
            xs.append(xn)
            ys.append(yn)
        tail_x = xs[-(int(n_generations) // 2) :]
        tail_y = ys[-(int(n_generations) // 2) :]
        bif_k_vals.extend([float(k_fear)] * len(tail_x))
        bif_prey.extend(tail_x)
        bif_pred.extend(tail_y)
    bifurcation = {"k_vals": bif_k_vals, "prey": bif_prey, "predator": bif_pred}
    return trajectories, bifurcation


def save_time_series(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
