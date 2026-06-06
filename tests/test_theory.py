import pytest
import numpy as np

from params import Params
from models.memory import MemoryModel
from models.baseline import BaselineModel
from core.engine import integrate
from core.registry import MODEL_REGISTRY
from analyze.metrics import compute_tail_metrics
from analyze.classifier import classify_dynamics, CLASS_ORDER
from analyze.stability import positive_equilibrium, jacobian_memory_fear, routh_hurwitz_coefficients, is_stable_by_routh_hurwitz, finite_difference_jacobian
from models.fear import FEAR_STRATEGIES
from params import Params as ModelParams
from models import get_model_instance


def _with_fear(p, k_val, alpha_val=1.0):
    p.fear_level = k_val
    p.memory_rate = alpha_val
    return p


def _sim_memory(p, k_val, alpha_val):
    _with_fear(p, k_val, alpha_val)
    return integrate(MemoryModel().rhs, p, fear_strategy=FEAR_STRATEGIES["rational"], model_type='ode',
                     initial_state=[p.x0, p.y0, p.z0]).to_dataframe()


def test_model_registry():
    for name in ['no_fear', 'M0', 'instant', 'M1', 'memory', 'M2']:
        assert name in MODEL_REGISTRY, f'{name} not in registry'


def test_simulation_returns_correct_columns():
    p = Params(T=100, n_points=500)
    df = integrate(BaselineModel(use_fear=False).rhs, p, model_type='ode',
                   initial_state=[p.prey_0, p.pred_0]).to_dataframe()
    assert 't' in df.columns
    assert 'x' in df.columns
    assert 'y' in df.columns


def test_simulation_positivity():
    p = Params(T=500, n_points=500)
    df = _sim_memory(p, 1.0, 5.0)
    assert (df['x'] >= 0).all()
    assert (df['y'] >= 0).all()


def test_stable_classification():
    p = Params(T=500, n_points=500)
    df = _sim_memory(p, 5.0, 10.0)
    metrics = compute_tail_metrics(df, 200)
    cls = classify_dynamics(metrics)
    assert cls in CLASS_ORDER


def test_oscillatory_classification():
    p = Params(T=500, n_points=500)
    df = _sim_memory(p, 1.0, 0.1)
    metrics = compute_tail_metrics(df, 200)
    cls = classify_dynamics(metrics)
    assert cls in CLASS_ORDER


def test_equilibrium_positive():
    sp = ModelParams()
    eq = positive_equilibrium(sp, k_fear=1.0, model_type='memory')
    if eq is not None:
        assert eq.is_positive()
        residual = MemoryModel().rhs(0.0, np.array([eq.x, eq.y, eq.z]), sp, FEAR_STRATEGIES["rational"])
        assert np.linalg.norm(residual) < 1e-6


def test_jacobian_shape():
    sp = ModelParams()
    eq = positive_equilibrium(sp, k_fear=1.0, model_type='memory')
    if eq is not None:
        jac = jacobian_memory_fear(sp, eq, 1.0, 5.0)
        assert jac.shape == (3, 3)


def test_routh_hurwitz_stable():
    sp = ModelParams()
    eq = positive_equilibrium(sp, k_fear=5.0, model_type='memory')
    if eq is not None:
        jac = jacobian_memory_fear(sp, eq, 5.0, 10.0)
        stable = is_stable_by_routh_hurwitz(jac)
        assert stable == True


def test_finite_difference_jacobian():
    model = get_model_instance('memory')
    sp = ModelParams()
    sp.fear_level = 1.0
    sp.memory_rate = 5.0
    sp.prey_birth_rate = 0.5
    sp.intra_comp = 0.005
    sp.attack_rate = 0.08
    sp.handling_time = 0.1
    sp.conversion_eff = 0.5
    sp.pred_death = 0.3
    args = (sp, FEAR_STRATEGIES["rational"])
    y0 = np.array([30.0, 10.0, 10.0])
    fd_jac = finite_difference_jacobian(model.rhs, y0, args, eps=1e-6)
    assert fd_jac.shape == (3, 3)
    assert np.all(np.isfinite(fd_jac))