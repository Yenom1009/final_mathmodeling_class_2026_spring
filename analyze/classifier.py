from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional

CLASS_ORDER = [
    "stable_coexistence",
    "oscillatory_coexistence",
    "predator_extinct",
    "prey_extinct",
    "low_density_risk",
    "invalid",
]

CLASS_TO_CODE = {name: i for i, name in enumerate(CLASS_ORDER)}
CODE_TO_CLASS = {i: name for i, name in enumerate(CLASS_ORDER)}


def classify_dynamics(metrics: dict) -> str:
    x_mean = metrics.get("x_mean", 0)
    y_mean = metrics.get("y_mean", 0)
    x_rel_amp = metrics.get("x_rel_amp", 0)
    y_rel_amp = metrics.get("y_rel_amp", 0)
    x_min = metrics.get("x_min", 0)
    y_min = metrics.get("y_min", 0)
    x_max = metrics.get("x_max", 0)
    y_max = metrics.get("y_max", 0)
    if not np.isfinite(x_mean) or not np.isfinite(y_mean):
        return "invalid"
    if x_mean < 0 or y_mean < 0:
        return "invalid"
    if y_mean < 1e-6 or y_max < 1e-5:
        return "predator_extinct"
    if x_mean < 1e-6 or x_max < 1e-5:
        return "prey_extinct"
    if x_min < 1e-4 or y_min < 1e-4:
        return "low_density_risk"
    rel_amp = max(x_rel_amp, y_rel_amp)
    if rel_amp < 1e-3:
        return "stable_coexistence"
    return "oscillatory_coexistence"


__all__ = ["classify_dynamics", "CLASS_ORDER", "CLASS_TO_CODE", "CODE_TO_CLASS"]