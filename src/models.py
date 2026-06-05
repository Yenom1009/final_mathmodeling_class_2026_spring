"""ODE right-hand sides for the fear predator-prey project."""

from __future__ import annotations

import math
from typing import Mapping

import numpy as np


Params = Mapping[str, float]


def get_param(params: Params, name: str, default: float | None = None) -> float:
    aliases = {
        "p_pred": ("p_pred", "p", "c"),
        "h_handle": ("h_handle", "h", "a"),
        "k_fear": ("k_fear", "k"),
        "alpha_mem": ("alpha_mem", "alpha"),
        "d3": ("d3", "d"),
    }
    for key in aliases.get(name, (name,)):
        if key in params:
            return float(params[key])
    if default is not None:
        return float(default)
    raise KeyError(f"missing parameter {name}")


def fear_multiplier(k_fear: float, risk: np.ndarray | float, params: Params) -> np.ndarray | float:
    """Return the reproduction multiplier used by fear models."""
    form = str(params.get("fear_form", "rational"))
    if form == "rational":
        return 1.0 / (1.0 + k_fear * risk)
    if form == "exponential":
        return np.exp(-k_fear * risk)
    if form == "quadratic":
        k2 = float(params.get("k2_fear", 0.05 * max(k_fear, 1.0)))
        return 1.0 / (1.0 + k_fear * risk + k2 * risk * risk)
    raise ValueError(f"unknown fear_form: {form}")


def model_no_fear(t: float, state: np.ndarray, params: Params) -> np.ndarray:
    del t
    x, y = state
    r = get_param(params, "r")
    d1 = get_param(params, "d1", 0.0)
    d2 = get_param(params, "d2")
    p_pred = get_param(params, "p_pred")
    h_handle = get_param(params, "h_handle")
    eta = get_param(params, "eta")
    d3 = get_param(params, "d3")
    pred = p_pred * x * y / (1.0 + h_handle * x)
    dx = r * x - d1 * x - d2 * x * x - pred
    dy = eta * pred - d3 * y
    return np.array([dx, dy], dtype=float)


def model_instant_fear(t: float, state: np.ndarray, params: Params) -> np.ndarray:
    del t
    x, y = state
    r = get_param(params, "r")
    d1 = get_param(params, "d1", 0.0)
    d2 = get_param(params, "d2")
    p_pred = get_param(params, "p_pred")
    h_handle = get_param(params, "h_handle")
    eta = get_param(params, "eta")
    d3 = get_param(params, "d3")
    k_fear = get_param(params, "k_fear", 0.0)
    pred = p_pred * x * y / (1.0 + h_handle * x)
    dx = r * x * fear_multiplier(k_fear, y, params) - d1 * x - d2 * x * x - pred
    dy = eta * pred - d3 * y
    return np.array([dx, dy], dtype=float)


def model_memory_fear(t: float, state: np.ndarray, params: Params) -> np.ndarray:
    del t
    x, y, z = state
    r = get_param(params, "r")
    d1 = get_param(params, "d1", 0.0)
    d2 = get_param(params, "d2")
    p_pred = get_param(params, "p_pred")
    h_handle = get_param(params, "h_handle")
    eta = get_param(params, "eta")
    d3 = get_param(params, "d3")
    k_fear = get_param(params, "k_fear", 0.0)
    alpha_mem = get_param(params, "alpha_mem", 1.0)
    pred = p_pred * x * y / (1.0 + h_handle * x)
    dx = r * x * fear_multiplier(k_fear, z, params) - d1 * x - d2 * x * x - pred
    dy = eta * pred - d3 * y
    dz = alpha_mem * (y - z)
    return np.array([dx, dy, dz], dtype=float)


def model_memory_fear_alt_logistic(t: float, state: np.ndarray, params: Params) -> np.ndarray:
    """Rosenzweig-MacArthur style compatibility model.

    This uses c*x*y/(a+x) and r*x/(1+kz) - (r/K)x^2, matching the user's
    earlier parameter convention.
    """
    del t
    x, y, z = state
    r = get_param(params, "r")
    K = float(params.get("K", 100.0))
    c_attack = float(params.get("c", params.get("p", params.get("p_pred", 0.8))))
    half_sat = float(params.get("a", params.get("h", params.get("h_handle", 10.0))))
    eta = get_param(params, "eta")
    d3 = get_param(params, "d3")
    k_fear = get_param(params, "k_fear", 0.0)
    alpha_mem = get_param(params, "alpha_mem", 1.0)
    pred = c_attack * x * y / (half_sat + x)
    dx = r * x * fear_multiplier(k_fear, z, params) - (r / K) * x * x - pred
    dy = eta * pred - d3 * y
    dz = alpha_mem * (y - z)
    return np.array([dx, dy, dz], dtype=float)


def model_tritrophic(t: float, state: np.ndarray, params: Params) -> np.ndarray:
    del t
    X, Y, Z = state
    r = float(params.get("r", 0.8))
    dX = float(params.get("dX", 0.05))
    aX = float(params.get("aX", 0.01))
    p1 = float(params.get("p1", 0.6))
    h1 = float(params.get("h1", 0.08))
    eta1 = float(params.get("eta1", 0.45))
    dY = float(params.get("dY", 0.12))
    p2 = float(params.get("p2", 0.45))
    h2 = float(params.get("h2", 0.1))
    eta2 = float(params.get("eta2", 0.35))
    dZ = float(params.get("dZ", 0.08))
    k1 = float(params.get("k1", 0.0))
    k2 = float(params.get("k2", 0.0))
    pred1 = p1 * X * Y / (1.0 + h1 * X)
    pred2 = p2 * Y * Z / (1.0 + h2 * Y)
    dXdt = r * X / (1.0 + k1 * Y) - dX * X - aX * X * X - pred1
    dYdt = eta1 * pred1 / (1.0 + k2 * Z) - dY * Y - pred2
    dZdt = eta2 * pred2 - dZ * Z
    return np.array([dXdt, dYdt, dZdt], dtype=float)


def convert_alt_to_literature_params(params: Params) -> dict[str, float]:
    """Map c*x*y/(a+x) parameters to p*x*y/(1+h*x)."""
    half_sat = float(params.get("a", params.get("h", 10.0)))
    c_attack = float(params.get("c", params.get("p", params.get("p_pred", 0.8))))
    return {
        "r": float(params["r"]),
        "d1": float(params.get("d1", 0.0)),
        "d2": float(params.get("d2", params["r"] / float(params.get("K", 100.0)))),
        "p_pred": c_attack / half_sat,
        "h_handle": 1.0 / half_sat,
        "eta": float(params["eta"]),
        "d3": float(params.get("d3", params.get("d"))),
    }

