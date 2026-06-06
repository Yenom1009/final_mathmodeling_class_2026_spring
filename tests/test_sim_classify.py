import pytest
import numpy as np

from params import Params
from models.memory import MemoryModel
from models.baseline import BaselineModel
from core.engine import integrate
from analyze.metrics import compute_tail_metrics
from analyze.classifier import classify_dynamics
from models.fear import FEAR_STRATEGIES


def _with_fear(p, k_val, alpha_val=1.0):
    p.fear_level = k_val
    p.memory_rate = alpha_val
    return p


def _sim_memory(p, k_val, alpha_val):
    _with_fear(p, k_val, alpha_val)
    return integrate(MemoryModel().rhs, p, fear_strategy=FEAR_STRATEGIES["rational"], model_type='ode',
                     initial_state=[p.x0, p.y0, p.z0]).to_dataframe()


def test_tail_metrics_stable():
    p = Params(T=200, n_points=500)
    df = _sim_memory(p, 10.0, 10.0)
    metrics = compute_tail_metrics(df, 100)
    assert 'x_mean' in metrics
    assert 'y_mean' in metrics
    assert 'x_rel_amp' in metrics
    assert metrics['x_rel_amp'] < 0.5


def test_tail_metrics_oscillatory():
    p = Params(T=400, n_points=500)
    df = _sim_memory(p, 0.5, 0.1)
    metrics = compute_tail_metrics(df, 200)
    assert metrics['y_rel_amp'] > 1e-3


def test_classify_stable():
    metrics = {'x_mean': 10, 'y_mean': 5, 'x_rel_amp': 1e-4, 'y_rel_amp': 5e-4,
               'x_min': 9.9, 'y_min': 4.9, 'x_max': 10.1, 'y_max': 5.1}
    cls = classify_dynamics(metrics)
    assert cls == 'stable_coexistence'


def test_classify_oscillatory():
    metrics = {'x_mean': 10, 'y_mean': 5, 'x_rel_amp': 0.5, 'y_rel_amp': 0.8,
               'x_min': 5, 'y_min': 2, 'x_max': 15, 'y_max': 8}
    cls = classify_dynamics(metrics)
    assert cls == 'oscillatory_coexistence'


def test_classify_predator_extinct():
    metrics = {'x_mean': 10, 'y_mean': 1e-7, 'x_rel_amp': 0.1, 'y_rel_amp': 0.1,
               'x_min': 8, 'y_min': 0, 'x_max': 12, 'y_max': 1e-6}
    cls = classify_dynamics(metrics)
    assert cls == 'predator_extinct'


def test_classify_prey_extinct():
    metrics = {'x_mean': 1e-7, 'y_mean': 5, 'x_rel_amp': 0.1, 'y_rel_amp': 0.1,
               'x_min': 0, 'y_min': 4, 'x_max': 1e-6, 'y_max': 6}
    cls = classify_dynamics(metrics)
    assert cls == 'prey_extinct'


def test_classify_low_density():
    metrics = {'x_mean': 10, 'y_mean': 5, 'x_rel_amp': 0.1, 'y_rel_amp': 0.3,
               'x_min': 1e-5, 'y_min': 0.1, 'x_max': 15, 'y_max': 8}
    cls = classify_dynamics(metrics)
    assert cls == 'low_density_risk'


def test_classify_invalid():
    metrics = {'x_mean': float('nan'), 'y_mean': 5, 'x_rel_amp': 0.1, 'y_rel_amp': 0.1,
               'x_min': 0, 'y_min': 4, 'x_max': 10, 'y_max': 6}
    cls = classify_dynamics(metrics)
    assert cls == 'invalid'


def test_no_fear_simulation():
    p = Params(T=100, n_points=500)
    df = integrate(BaselineModel(use_fear=False).rhs, p, model_type='ode',
                   initial_state=[p.prey_0, p.pred_0]).to_dataframe()
    assert len(df) > 100
    assert df['x'].iloc[-1] > 0
    assert df['y'].iloc[-1] > 0


def test_instant_fear_simulation():
    p = Params(T=100, n_points=500)
    _with_fear(p, 1.0)
    df = integrate(BaselineModel(use_fear=True).rhs, p, fear_strategy=FEAR_STRATEGIES["rational"],
                   model_type='ode', initial_state=[p.prey_0, p.pred_0]).to_dataframe()
    assert len(df) > 100


def test_memory_fear_simulation():
    p = Params(T=100, n_points=500)
    df = _sim_memory(p, 1.0, 5.0)
    assert 'z' in df.columns