import tempfile
import unittest
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(__file__).resolve().parents[1] / ".cache"))

import matplotlib.image as mpimg
import numpy as np
import pandas as pd

from src.plotting import (
    _tail_is_effectively_stationary,
    plot_mechanism_diagram,
    plot_model_layers,
    plot_representative_cases_overview,
    plot_results_dashboard,
)
from src.scan import scan_k_continuation


PARAMS = {
    "r": 0.5,
    "d1": 0.0,
    "d2": 0.005,
    "p_pred": 0.08,
    "h_handle": 0.1,
    "eta": 0.5,
    "d3": 0.3,
}


class PresentationOutputChecks(unittest.TestCase):
    def test_tail_stationarity_detects_fixed_points_but_not_cycles(self):
        t = np.linspace(0.0, 10.0, 101)
        fixed = pd.DataFrame({"t": t, "x": 30.0 + 1e-11 * t, "y": 1.7 + 1e-12 * t})
        cycle = pd.DataFrame({"t": t, "x": 30.0 + np.sin(t), "y": 1.7 + 0.2 * np.cos(t)})

        self.assertTrue(_tail_is_effectively_stationary(fixed))
        self.assertFalse(_tail_is_effectively_stationary(cycle))

    def test_scan_k_continuation_returns_expected_columns(self):
        result = scan_k_continuation(
            PARAMS,
            k_values=[0.0, 0.2],
            alpha_mem=10.0,
            initial_state=[30.0, 10.0, 10.0],
            T=40.0,
            burn_in=20.0,
            n_points=401,
        )
        self.assertEqual(len(result), 2)
        self.assertIn("continuation", result.columns)
        self.assertTrue(result["continuation"].all())
        self.assertTrue({"k_fear", "x_mean", "y_mean", "x_amp", "y_amp", "class"}.issubset(result.columns))

    def test_presentation_figures_are_written(self):
        t = np.linspace(0.0, 10.0, 101)
        case_series = {
            "Case A": pd.DataFrame({"t": t, "x": 30.0 + 0 * t, "y": 1.7 + 0 * t, "z": 1.7 + 0 * t}),
            "Case B": pd.DataFrame({"t": t, "x": 30.0 + np.sin(t), "y": 0.4 + 0.1 * np.cos(t), "z": 0.4 + 0.05 * np.sin(t)}),
            "Case C": pd.DataFrame({"t": t, "x": 30.0 + 2.0 * np.sin(t), "y": 0.5 + 0.2 * np.cos(t), "z": 0.5 + 0.1 * np.sin(t)}),
        }
        scan_k_df = pd.DataFrame(
            {
                "k_fear": [0.0, 1.0],
                "x_mean": [58.0, 30.0],
                "y_mean": [9.5, 1.7],
                "x_amp": [95.0, 0.0],
                "y_amp": [25.0, 0.0],
            }
        )
        scan_df = pd.DataFrame(
            {
                "class": ["stable_coexistence", "oscillatory_coexistence"],
                "class_code": [0, 1],
                "k_fear": [0.0, 1.0],
                "alpha_mem": [1.0, 0.1],
                "x_amp": [0.0, 1.0],
                "y_amp": [0.0, 0.5],
            }
        )
        reps = pd.DataFrame(
            {
                "case_id": ["Case A", "Case B", "Case C"],
                "k_fear": [1.0, 4.8, 5.2],
                "alpha_mem": [5.012, 0.01, 0.01],
                "y_mean": [1.7, 0.42, 0.43],
                "y_amp": [0.0, 0.52, 1.50],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            overview = tmpdir / "overview.png"
            dashboard = tmpdir / "dashboard.png"
            plot_representative_cases_overview(case_series, reps, overview)
            plot_results_dashboard(scan_k_df, scan_df, reps, dashboard)
            self.assertGreater(overview.stat().st_size, 1000)
            self.assertGreater(dashboard.stat().st_size, 1000)

    def test_introductory_diagrams_use_compact_wide_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            mechanism = tmpdir / "mechanism.png"
            layers = tmpdir / "layers.png"
            plot_mechanism_diagram(mechanism)
            plot_model_layers(layers)

            for path in [mechanism, layers]:
                image = mpimg.imread(path)
                height, width = image.shape[:2]
                self.assertGreater(width / height, 1.7)
                self.assertGreater(path.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
