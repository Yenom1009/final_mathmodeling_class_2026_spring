import unittest

import numpy as np
import pandas as pd

from src.classify import classify_dynamics, compute_tail_metrics
from src.simulate import simulate_model


class SimulationClassificationChecks(unittest.TestCase):
    def test_tail_metrics_classify_stable_series(self):
        df = pd.DataFrame(
            {
                "t": np.linspace(0.0, 10.0, 11),
                "x": np.ones(11) * 2.0,
                "y": np.ones(11) * 0.5,
                "z": np.ones(11) * 0.5,
            }
        )
        metrics = compute_tail_metrics(df, burn_in=5.0)
        self.assertEqual(classify_dynamics(metrics), "stable_coexistence")
        self.assertLess(metrics["relative_amp_x"], 1e-9)

    def test_tail_metrics_classify_oscillatory_series(self):
        t = np.linspace(0.0, 10.0, 101)
        df = pd.DataFrame({"t": t, "x": 2.0 + np.sin(t), "y": 1.0 + 0.2 * np.cos(t), "z": np.nan})
        metrics = compute_tail_metrics(df, burn_in=5.0)
        self.assertEqual(classify_dynamics(metrics), "oscillatory_coexistence")

    def test_simulate_model_returns_expected_columns(self):
        params = {
            "r": 0.5,
            "d1": 0.0,
            "d2": 0.005,
            "p_pred": 0.8,
            "h_handle": 10.0,
            "eta": 0.5,
            "d3": 0.3,
            "k_fear": 1.0,
            "alpha_mem": 1.0,
        }
        df = simulate_model("memory", params, [30.0, 10.0, 10.0], T=20.0, n_points=401, solver="rk4")
        self.assertEqual(list(df.columns), ["t", "x", "y", "z"])
        self.assertEqual(len(df), 401)
        self.assertTrue(np.isfinite(df[["x", "y", "z"]].to_numpy()).all())
        self.assertGreaterEqual(df[["x", "y", "z"]].to_numpy().min(), 0.0)


if __name__ == "__main__":
    unittest.main()
