import unittest
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models import model_delay_fear, step_discrete_fear
from src.model_catalog import resolve_model_name
from src.simulate import simulate_delay_model, simulate_model


BASE_PARAMS = {
    "r": 0.5,
    "d1": 0.0,
    "d2": 0.005,
    "p_pred": 0.08,
    "h_handle": 0.1,
    "eta": 0.5,
    "d3": 0.3,
    "k_fear": 1.0,
}


class ExtensionChecks(unittest.TestCase):
    def test_delay_rhs_shape(self):
        deriv = model_delay_fear(
            0.0,
            np.array([30.0, 10.0]),
            np.array([30.0, 9.5]),
            BASE_PARAMS,
        )
        self.assertEqual(deriv.shape, (2,))
        self.assertTrue(np.isfinite(deriv).all())

    def test_delay_simulation_columns(self):
        df = simulate_delay_model(
            BASE_PARAMS,
            initial_state=[30.0, 10.0],
            history_state=[30.0, 10.0],
            tau=1.0,
            T=20.0,
            n_points=201,
        )
        self.assertEqual(list(df.columns), ["t", "x", "y"])
        self.assertEqual(len(df), 201)
        self.assertTrue(np.isfinite(df[["x", "y"]].to_numpy()).all())

    def test_leslie_gower_simulation_columns(self):
        df = simulate_model(
            "leslie_gower",
            {"lg_r": 0.8, "lg_K": 1.0, "lg_theta": 2.0, "lg_a": 0.5, "lg_s": 0.5, "lg_tau_pred": 0.3},
            [0.8, 0.3],
            T=10.0,
            n_points=101,
            solver="rk4",
        )
        self.assertEqual(list(df.columns), ["t", "x", "y", "z"])
        self.assertEqual(len(df), 101)

    def test_discrete_step_nonnegative(self):
        x_next, y_next = step_discrete_fear(
            5.0,
            2.0,
            {
                "disc_a_growth": 2.0,
                "disc_d_death": 0.1,
                "disc_b_comp": 0.05,
                "disc_c_pred": 0.03,
                "disc_mu_conv": 0.5,
                "disc_e_death": 0.2,
            },
            5.0,
        )
        self.assertGreaterEqual(x_next, 0.0)
        self.assertGreaterEqual(y_next, 0.0)

    def test_model_alias_resolution(self):
        self.assertEqual(resolve_model_name("M0"), "no_fear")
        self.assertEqual(resolve_model_name("M2"), "memory")
        self.assertEqual(resolve_model_name("food_chain"), "tritrophic")


if __name__ == "__main__":
    unittest.main()
