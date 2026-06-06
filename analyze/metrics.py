from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional


def compute_tail_metrics(df: pd.DataFrame, burn_in: float = 300.0) -> dict:
    tail = df[df["t"] >= burn_in].copy()
    if len(tail) == 0:
        tail = df.tail(100)
    metrics = {}
    for var in ["x", "y", "z"]:
        if var in tail.columns:
            vals = tail[var].values
            metrics[f"{var}_mean"] = np.mean(vals)
            metrics[f"{var}_min"] = np.min(vals)
            metrics[f"{var}_max"] = np.max(vals)
            metrics[f"{var}_amplitude"] = np.max(vals) - np.min(vals)
            metrics[f"{var}_rel_amp"] = metrics[f"{var}_amplitude"] / (np.mean(vals) + 1e-15)
    return metrics


__all__ = ["compute_tail_metrics"]