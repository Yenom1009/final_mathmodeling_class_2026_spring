from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional

from models.baseline import BaselineModel
from models.memory import MemoryModel
from models.fear import FEAR_STRATEGIES
from core.engine import integrate
from analyze.metrics import compute_tail_metrics
from analyze.classifier import classify_dynamics


def find_representative_cases(scan_df: pd.DataFrame, scan_k_df: pd.DataFrame, params):
    cases = {}
    no_fear = scan_k_df[scan_k_df["k"] < 0.1]
    if len(no_fear) > 0:
        nf_metrics = no_fear.iloc[0]
        nf_osc = nf_metrics.get("y_rel_amp", 0) > 1e-3
    else:
        result = integrate(BaselineModel(use_fear=False).rhs, params,
                           initial_state=[params.prey_0, params.pred_0])
        df_nf = result.to_dataframe()
        metrics = compute_tail_metrics(df_nf, params.burn_in)
        nf_osc = metrics.get("y_rel_amp", 0) > 1e-3
    if nf_osc:
        k_stable_idx = scan_k_df[scan_k_df["class"] == "stable_coexistence"]["k"]
        if len(k_stable_idx) > 0:
            cases["A"] = {"k": float(k_stable_idx.iloc[0]), "alpha": 10.0, "label": "Fear stabilizes oscillation", "type": "stabilize"}
    oscillatory = scan_df[scan_df["class"] == "oscillatory_coexistence"]
    if len(oscillatory) > 0:
        fast_memory = oscillatory[oscillatory["alpha"] > 1.0]
        if len(fast_memory) > 0:
            low_k = fast_memory.loc[fast_memory["k"].idxmin()]
            cases["B"] = {"k": low_k["k"], "alpha": low_k["alpha"], "label": f"Fast memory (alpha={low_k['alpha']:.2f})", "type": "fast_memory"}
        slow_memory = oscillatory[oscillatory["alpha"] < 0.1]
        if len(slow_memory) > 0:
            high_k = slow_memory.loc[slow_memory["k"].idxmax()]
            cases["C"] = {"k": high_k["k"], "alpha": high_k["alpha"], "label": f"Slow memory (alpha={high_k['alpha']:.2f})", "type": "slow_memory"}
    if "A" not in cases:
        cases["A"] = {"k": 1.0, "alpha": 5.012, "label": "Stable coexistence", "type": "stabilize"}
    if "B" not in cases:
        cases["B"] = {"k": 4.8, "alpha": 0.01, "label": "Slow memory, low k", "type": "fast_memory"}
    if "C" not in cases:
        cases["C"] = {"k": 5.2, "alpha": 0.01, "label": "Slow memory, high k", "type": "slow_memory"}
    return cases


__all__ = ["find_representative_cases"]