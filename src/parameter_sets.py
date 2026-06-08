"""Named parameter presets for the final project.

This keeps parameter choices explicit and auditable, which matters for a course
project where each experiment should have a clear origin and interpretation.
"""

from __future__ import annotations


def main_reference_params() -> dict[str, float]:
    return {
        "r": 0.5,
        "d1": 0.0,
        "d2": 0.005,
        "p_pred": 0.08,
        "h_handle": 0.1,
        "eta": 0.5,
        "d3": 0.3,
    }


def liu2021_style_params() -> dict[str, float]:
    return {
        "r": 0.1,
        "d1": 0.01,
        "d2": 0.01,
        "p_pred": 0.5,
        "h_handle": 0.6,
        "eta": 0.4,
        "d3": 0.22,
    }


def tritrophic_params() -> dict[str, float]:
    return {
        "r": 0.8,
        "dX": 0.05,
        "aX": 0.01,
        "p1": 0.6,
        "h1": 0.08,
        "eta1": 0.45,
        "dY": 0.12,
        "p2": 0.45,
        "h2": 0.1,
        "eta2": 0.35,
        "dZ": 0.08,
        "k1": 0.4,
        "k2": 0.3,
    }


def leslie_gower_params() -> dict[str, float]:
    return {
        "lg_r": 0.8,
        "lg_K": 1.0,
        "lg_theta": 2.0,
        "lg_a": 0.5,
        "lg_s": 0.5,
        "lg_tau_pred": 0.3,
    }


def discrete_map_params() -> dict[str, float]:
    return {
        "disc_a_growth": 2.0,
        "disc_d_death": 0.1,
        "disc_b_comp": 0.05,
        "disc_c_pred": 0.03,
        "disc_mu_conv": 0.5,
        "disc_e_death": 0.2,
    }
