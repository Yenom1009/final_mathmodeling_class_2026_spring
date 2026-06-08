"""Equilibria, Jacobians, and stability checks for the main ODE models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

import numpy as np

from .models import get_param


Params = Mapping[str, float]


@dataclass(frozen=True)
class Equilibrium:
    x: float
    y: float
    z: float


def positive_equilibrium(params: Params, k_fear: float) -> Equilibrium | None:
    r = get_param(params, "r")
    d1 = get_param(params, "d1", 0.0)
    d2 = get_param(params, "d2")
    p_pred = get_param(params, "p_pred")
    h_handle = get_param(params, "h_handle")
    eta = get_param(params, "eta")
    d3 = get_param(params, "d3")
    denom = eta * p_pred - d3 * h_handle
    if denom <= 0:
        return None
    x_star = d3 / denom
    B = p_pred / (1.0 + h_handle * x_star)
    H = d1 + d2 * x_star
    if r <= H or B <= 0:
        return None
    if abs(k_fear) < 1e-14:
        y_star = (r - H) / B
    else:
        disc = (B + k_fear * H) ** 2 + 4.0 * B * k_fear * (r - H)
        y_star = (-(B + k_fear * H) + float(np.sqrt(disc))) / (2.0 * B * k_fear)
    if x_star <= 0 or y_star <= 0:
        return None
    return Equilibrium(x=x_star, y=y_star, z=y_star)


def jacobian_instant_fear(params: Params, k_fear: float) -> np.ndarray:
    eq = positive_equilibrium(params, k_fear)
    if eq is None:
        raise ValueError("positive equilibrium does not exist")
    x, y = eq.x, eq.y
    r = get_param(params, "r")
    d1 = get_param(params, "d1", 0.0)
    d2 = get_param(params, "d2")
    p_pred = get_param(params, "p_pred")
    h_handle = get_param(params, "h_handle")
    eta = get_param(params, "eta")
    d3 = get_param(params, "d3")
    denom_x = 1.0 + h_handle * x
    denom_fear = 1.0 + k_fear * y
    F_x = r / denom_fear - d1 - 2.0 * d2 * x - p_pred * y / (denom_x * denom_x)
    F_y = -r * k_fear * x / (denom_fear * denom_fear) - p_pred * x / denom_x
    G_x = eta * p_pred * y / (denom_x * denom_x)
    G_y = eta * p_pred * x / denom_x - d3
    return np.array([[F_x, F_y], [G_x, G_y]], dtype=float)


def jacobian_memory_fear(params: Params, k_fear: float, alpha_mem: float) -> np.ndarray:
    eq = positive_equilibrium(params, k_fear)
    if eq is None:
        raise ValueError("positive equilibrium does not exist")
    x, y, z = eq.x, eq.y, eq.z
    r = get_param(params, "r")
    d1 = get_param(params, "d1", 0.0)
    d2 = get_param(params, "d2")
    p_pred = get_param(params, "p_pred")
    h_handle = get_param(params, "h_handle")
    eta = get_param(params, "eta")
    denom_x = 1.0 + h_handle * x
    denom_fear = 1.0 + k_fear * z
    A = r / denom_fear - d1 - 2.0 * d2 * x - p_pred * y / (denom_x * denom_x)
    B = -p_pred * x / denom_x
    C = -r * k_fear * x / (denom_fear * denom_fear)
    D = eta * p_pred * y / (denom_x * denom_x)
    return np.array([[A, B, C], [D, 0.0, 0.0], [0.0, alpha_mem, -alpha_mem]], dtype=float)


def routh_hurwitz_coefficients(params: Params, k_fear: float, alpha_mem: float) -> tuple[float, float, float]:
    J = jacobian_memory_fear(params, k_fear, alpha_mem)
    A = J[0, 0]
    B = J[0, 1]
    C = J[0, 2]
    D = J[1, 0]
    A1 = alpha_mem - A
    A2 = -A * alpha_mem - B * D
    A3 = -alpha_mem * D * (B + C)
    return float(A1), float(A2), float(A3)


def is_stable_by_eigenvalues(J: np.ndarray) -> bool:
    eig = np.linalg.eigvals(J)
    return bool(np.all(np.real(eig) < -1e-9))


def is_stable_by_routh_hurwitz(params: Params, k_fear: float, alpha_mem: float) -> bool:
    try:
        A1, A2, A3 = routh_hurwitz_coefficients(params, k_fear, alpha_mem)
    except ValueError:
        return False
    return bool(A1 > 0 and A2 > 0 and A3 > 0 and A1 * A2 > A3)


def finite_difference_jacobian(func: Callable[[np.ndarray], np.ndarray], state: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    state = np.asarray(state, dtype=float)
    f0 = np.asarray(func(state), dtype=float)
    J = np.zeros((len(f0), len(state)), dtype=float)
    for i in range(len(state)):
        step = np.zeros_like(state)
        step[i] = eps
        fp = np.asarray(func(state + step), dtype=float)
        fm = np.asarray(func(state - step), dtype=float)
        J[:, i] = (fp - fm) / (2.0 * eps)
    return J


def theory_grid(params: Params, k_values: np.ndarray, alpha_values: np.ndarray) -> np.ndarray:
    stable = np.zeros((len(alpha_values), len(k_values)), dtype=bool)
    for i, alpha in enumerate(alpha_values):
        for j, k in enumerate(k_values):
            stable[i, j] = is_stable_by_routh_hurwitz(params, float(k), float(alpha))
    return stable

