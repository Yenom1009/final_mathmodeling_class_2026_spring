import math
import unittest

import numpy as np

from src.models import model_instant_fear, model_memory_fear
from src.theory import (
    finite_difference_jacobian,
    is_stable_by_routh_hurwitz,
    jacobian_instant_fear,
    jacobian_memory_fear,
    positive_equilibrium,
    routh_hurwitz_coefficients,
)


BASE_PARAMS = {
    "r": 0.5,
    "d1": 0.0,
    "d2": 0.005,
    "p_pred": 0.08,
    "h_handle": 0.1,
    "eta": 0.5,
    "d3": 0.3,
}


class TheoryChecks(unittest.TestCase):
    def test_positive_equilibrium_residual_is_small_for_instant_model(self):
        eq = positive_equilibrium(BASE_PARAMS, k_fear=1.0)
        self.assertIsNotNone(eq)
        residual = model_instant_fear(0.0, np.array([eq.x, eq.y]), {**BASE_PARAMS, "k_fear": 1.0})
        self.assertLess(float(np.linalg.norm(residual)), 1e-8)

    def test_positive_equilibrium_residual_is_small_for_memory_model(self):
        eq = positive_equilibrium(BASE_PARAMS, k_fear=1.0)
        self.assertIsNotNone(eq)
        residual = model_memory_fear(
            0.0,
            np.array([eq.x, eq.y, eq.z]),
            {**BASE_PARAMS, "k_fear": 1.0, "alpha_mem": 0.5},
        )
        self.assertLess(float(np.linalg.norm(residual)), 1e-8)

    def test_instant_jacobian_matches_finite_difference(self):
        eq = positive_equilibrium(BASE_PARAMS, k_fear=0.7)
        analytic = jacobian_instant_fear(BASE_PARAMS, k_fear=0.7)
        numeric = finite_difference_jacobian(
            lambda state: model_instant_fear(0.0, state, {**BASE_PARAMS, "k_fear": 0.7}),
            np.array([eq.x, eq.y]),
        )
        self.assertLess(float(np.max(np.abs(analytic - numeric))), 1e-5)

    def test_memory_jacobian_matches_finite_difference(self):
        eq = positive_equilibrium(BASE_PARAMS, k_fear=0.7)
        analytic = jacobian_memory_fear(BASE_PARAMS, k_fear=0.7, alpha_mem=0.2)
        numeric = finite_difference_jacobian(
            lambda state: model_memory_fear(
                0.0, state, {**BASE_PARAMS, "k_fear": 0.7, "alpha_mem": 0.2}
            ),
            np.array([eq.x, eq.y, eq.z]),
        )
        self.assertLess(float(np.max(np.abs(analytic - numeric))), 1e-5)

    def test_routh_hurwitz_coefficients_match_characteristic_polynomial(self):
        J = jacobian_memory_fear(BASE_PARAMS, k_fear=1.0, alpha_mem=0.8)
        coeffs = np.poly(J)
        A1, A2, A3 = routh_hurwitz_coefficients(BASE_PARAMS, k_fear=1.0, alpha_mem=0.8)
        self.assertTrue(math.isclose(coeffs[1], A1, rel_tol=1e-8, abs_tol=1e-8))
        self.assertTrue(math.isclose(coeffs[2], A2, rel_tol=1e-8, abs_tol=1e-8))
        self.assertTrue(math.isclose(coeffs[3], A3, rel_tol=1e-8, abs_tol=1e-8))
        self.assertIsInstance(is_stable_by_routh_hurwitz(BASE_PARAMS, 1.0, 0.8), bool)


if __name__ == "__main__":
    unittest.main()
