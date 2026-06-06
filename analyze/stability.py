from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional

from params import Params as ModelParams


@dataclass
class Equilibrium:
    x: float
    y: float
    z: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def is_positive(self) -> bool:
        return self.x > 0 and self.y > 0 and self.z >= 0


def positive_equilibrium(params: ModelParams, k_fear: float = 0.0, model_type: str = "memory") -> Optional[Equilibrium]:
    r, d1, d2, p, h, eta, d3 = params.r, params.d1, params.d2, params.p, params.h, params.eta, params.d3
    denom = eta * p - d3 * h
    if denom <= 0:
        return None
    x_star = d3 / denom
    if x_star <= 0:
        return None
    B = p / (1.0 + h * x_star)
    H = d1 + d2 * x_star
    if r <= H or B <= 0:
        return None
    if abs(k_fear) < 1e-14:
        y_star = (r - H) / B
    else:
        disc = (B + k_fear * H) ** 2 + 4.0 * B * k_fear * (r - H)
        y_star = (-(B + k_fear * H) + np.sqrt(disc)) / (2.0 * B * k_fear)
    if x_star <= 0 or y_star <= 0:
        return None
    z_star = y_star if model_type in ("memory", "M2") else 0.0
    return Equilibrium(x_star, y_star, z_star)


def jacobian_memory_fear(params: ModelParams, eq: Equilibrium, k_fear: float = 1.0, alpha: float = 1.0) -> np.ndarray:
    r, d1, d2, p, h, eta, d3 = params.r, params.d1, params.d2, params.p, params.h, params.eta, params.d3
    x, y, z = eq.x, eq.y, eq.z
    f = 1.0 / (1.0 + k_fear * z)
    df_dz = -k_fear / ((1.0 + k_fear * z) ** 2)
    pred = p * x / (1.0 + h * x)
    dpred_dx = p / ((1.0 + h * x) ** 2)
    J11 = f * r - d1 - 2 * d2 * x - y * dpred_dx
    J12 = -pred
    J13 = r * x * df_dz
    J21 = eta * y * dpred_dx
    J22 = eta * pred - d3
    J23 = 0.0
    J31 = 0.0
    J32 = alpha
    J33 = -alpha
    return np.array([[J11, J12, J13], [J21, J22, J23], [J31, J32, J33]])


def routh_hurwitz_coefficients(jac: np.ndarray) -> tuple[float, float, float, float]:
    n = jac.shape[0]
    if n == 2:
        A1 = -np.trace(jac)
        A2 = np.linalg.det(jac)
        return A1, A2, 0.0, 0.0
    elif n == 3:
        A1 = -np.trace(jac)
        A2 = sum(jac[i, i] * jac[j, j] - jac[i, j] * jac[j, i]
                 for i in range(3) for j in range(i + 1, 3))
        A3 = -np.linalg.det(jac)
        return A1, A2, A3, A1 * A2 - A3


def is_stable_by_eigenvalues(jac: np.ndarray) -> bool:
    eigvals = np.linalg.eigvals(jac)
    return np.all(np.real(eigvals) < -1e-12)


def is_stable_by_routh_hurwitz(jac: np.ndarray) -> bool:
    n = jac.shape[0]
    if n == 2:
        A1, A2, _, _ = routh_hurwitz_coefficients(jac)
        return A1 > 1e-12 and A2 > 1e-12
    elif n == 3:
        A1, A2, A3, A1A2_minus_A3 = routh_hurwitz_coefficients(jac)
        return A1 > 1e-12 and A2 > 1e-12 and A3 > 1e-12 and A1A2_minus_A3 > 1e-12
    return False


def finite_difference_jacobian(func, y0, args, eps=1e-6):
    n = len(y0)
    f0 = np.array(func(0, y0, *args))
    jac = np.zeros((n, n))
    for i in range(n):
        y_plus = y0.copy()
        y_plus[i] += eps
        f_plus = np.array(func(0, y_plus, *args))
        jac[:, i] = (f_plus - f0) / eps
    return jac


def theory_grid(params: ModelParams, k_grid: np.ndarray, alpha_grid: np.ndarray) -> np.ndarray:
    stable = np.zeros((len(k_grid), len(alpha_grid)), dtype=bool)
    for i, k in enumerate(k_grid):
        eq = positive_equilibrium(params, k, "memory")
        if eq is None or not eq.is_positive():
            continue
        for j, alpha in enumerate(alpha_grid):
            jac = jacobian_memory_fear(params, eq, k, alpha)
            stable[i, j] = is_stable_by_routh_hurwitz(jac)
    return stable


__all__ = [
    "theory_grid", "positive_equilibrium", "jacobian_memory_fear",
    "routh_hurwitz_coefficients",
    "is_stable_by_routh_hurwitz", "finite_difference_jacobian",
    "Equilibrium",
]