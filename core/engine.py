from dataclasses import dataclass, field
from typing import Callable, Optional
import numpy as np
import pandas as pd


@dataclass
class SimulationResult:
    t: np.ndarray
    state: np.ndarray
    names: list[str] = field(default_factory=lambda: ["x", "y"])
    params: Optional[dict] = None

    def to_dataframe(self) -> pd.DataFrame:
        data = {"t": self.t}
        for i, name in enumerate(self.names):
            data[name] = self.state[i]
        return pd.DataFrame(data)


def integrate(
    model,
    params,
    fear_strategy=None,
    model_type: str = "ode",
    initial_state: Optional[list] = None,
    **kwargs,
) -> SimulationResult:
    if callable(model):
        func = model
    elif isinstance(model, str):
        func = resolve_model(model)
    else:
        raise TypeError(f"model must be callable or str, got {type(model)}")

    if model_type == "ode":
        return _integrate_ode(func, params, fear_strategy, initial_state, **kwargs)
    elif model_type == "dde":
        return _integrate_dde(func, params, fear_strategy, initial_state, **kwargs)
    elif model_type == "discrete":
        return _integrate_discrete(func, params, fear_strategy, initial_state, **kwargs)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")


def _integrate_ode(func, params, fear_strategy, initial_state, **kwargs):
    T = kwargs.get("T", getattr(params, "T", 800.0))
    n_points = kwargs.get("n_points", getattr(params, "n_points", 5000))
    dt = T / n_points
    t = np.linspace(0.0, T, n_points)

    if initial_state is None:
        x0 = getattr(params, "x0", 30.0)
        y0 = getattr(params, "y0", 10.0)
        initial_state = [x0, y0]
    n_vars = len(initial_state)
    y = np.zeros((n_vars, n_points))
    y[:, 0] = initial_state

    args_list = [params]
    if fear_strategy is not None:
        args_list.append(fear_strategy)

    for i in range(n_points - 1):
        k1 = np.array(func(t[i], y[:, i], *args_list)) * dt
        k2 = np.array(func(t[i] + dt / 2, y[:, i] + k1 / 2, *args_list)) * dt
        k3 = np.array(func(t[i] + dt / 2, y[:, i] + k2 / 2, *args_list)) * dt
        k4 = np.array(func(t[i] + dt, y[:, i] + k3, *args_list)) * dt
        y[:, i + 1] = y[:, i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if np.any(np.isnan(y[:, i + 1])) or np.any(y[:, i + 1] < -1e-10):
            y[:, i + 1] = y[:, i]
            if np.any(y[:, i + 1] < 0):
                y[:, i + 1] = np.maximum(y[:, i + 1], 0)

    names = ["x", "y", "z", "w"][:n_vars]
    return SimulationResult(t=t, state=y, names=names)


def _integrate_dde(func, params, fear_strategy, initial_state, **kwargs):
    T = kwargs.get("T", getattr(params, "T", 800.0))
    n_points = kwargs.get("n_points", getattr(params, "n_points", 5000))
    tau = kwargs.get("tau", getattr(params, "tau", 1.0))
    dt = T / n_points
    t = np.linspace(0.0, T, n_points)

    if initial_state is None:
        x0 = kwargs.get("x0", getattr(params, "x0", 30.0))
        y0 = kwargs.get("y0", getattr(params, "y0", 10.0))
    else:
        x0, y0 = initial_state[0], initial_state[1]

    def history_func(t):
        return np.array([x0, y0])

    y_history = np.zeros((2, n_points))
    y_history[:, 0] = history_func(0)
    delay_steps = int(tau / dt)

    args_list = [params]
    if fear_strategy is not None:
        args_list.append(fear_strategy)

    for i in range(1, n_points):
        t_current = t[i]
        if i > delay_steps:
            y_delayed = y_history[:, i - delay_steps]
        else:
            y_delayed = history_func(t_current - tau)

        k1 = dt * np.array(func(t_current, y_history[:, i - 1], y_delayed, *args_list))

        if i > delay_steps:
            y_delayed_k2 = y_history[:, max(0, i - 1 - delay_steps)]
        else:
            y_delayed_k2 = history_func(t_current - tau + dt / 2)
        k2 = dt * np.array(func(t_current + dt / 2, y_history[:, i - 1] + k1 / 2, y_delayed_k2, *args_list))

        if i > delay_steps:
            y_delayed_k3 = y_history[:, max(0, i - 1 - delay_steps)]
        else:
            y_delayed_k3 = history_func(t_current - tau + dt / 2)
        k3 = dt * np.array(func(t_current + dt / 2, y_history[:, i - 1] + k2 / 2, y_delayed_k3, *args_list))

        if i > delay_steps:
            y_delayed_k4 = y_history[:, max(0, i - 1 - delay_steps)]
        else:
            y_delayed_k4 = history_func(t_current - tau)
        k4 = dt * np.array(func(t_current + dt, y_history[:, i - 1] + k3, y_delayed_k4, *args_list))

        y_history[:, i] = y_history[:, i - 1] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if np.any(np.isnan(y_history[:, i])) or np.any(y_history[:, i] < 0):
            y_history[:, i] = y_history[:, i - 1]

    return SimulationResult(t=t, state=y_history, names=["x", "y"])


def _integrate_discrete(func, params, fear_strategy, initial_state, **kwargs):
    n_generations = kwargs.get("n_generations", getattr(params, "n_generations", 500))
    if initial_state is not None:
        x, y = initial_state[0], initial_state[1]
    else:
        x = kwargs.get("x0", getattr(params, "x0", 5.0))
        y = kwargs.get("y0", getattr(params, "y0", 2.0))

    xs, ys = [x], [y]
    extra_args = [params]
    if fear_strategy is not None:
        extra_args.append(fear_strategy)

    for _ in range(n_generations):
        xn, yn = func(xs[-1], ys[-1], *extra_args)
        xs.append(xn)
        ys.append(yn)

    t = np.arange(len(xs))
    state = np.array([xs, ys])
    return SimulationResult(t=t, state=state, names=["x", "y"])