import logging
import numpy as np
import pandas as pd
from pathlib import Path

from params import Params
from core.engine import integrate
from models.fear import FEAR_STRATEGIES
from models.baseline import BaselineModel
from models.memory import MemoryModel
from models.food_chain import FoodChainModel
from models.delay_model import DelayModel
from models.discrete_map import DiscreteMapModel
from models.leslie_gower import LeslieGowerModel
from analyze.sweeper import scan_k, scan_k_alpha, compute_theory_boundary
from analyze.representative import find_representative_cases
from analyze.metrics import compute_tail_metrics
from plot.time_series import plot_time_series, plot_representative_cases
from plot.phase import plot_phase_portraits
from plot.bifurcation import plot_bifurcation, plot_mean_amplitude
from plot.heatmaps import plot_2d_classification, plot_amplitude_heatmap
from plot.theory_overlay import plot_theory_boundary as plot_theory_boundary_fig
from plot.robustness import plot_robustness
from plot.calibration import plot_empirical_calibration
from plot.extended_models import plot_delay_model, plot_discrete_model, plot_tritrophic

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / 'output' / 'figures'
RESULTS_DIR = ROOT / 'output' / 'results'


def run_step_baseline(params):
    log.info('[1/9] Baseline model comparison (M0, M1, M2)...')
    series = {}
    p = params
    p.fear_level = 0.0
    m0 = BaselineModel(use_fear=False)
    series['M0 (no fear)'] = integrate(m0.rhs, p).to_dataframe()
    p.fear_level = 1.0
    m1 = BaselineModel(use_fear=True)
    series['M1 (instant, k=1)'] = integrate(m1.rhs, p, fear_strategy=FEAR_STRATEGIES["rational"]).to_dataframe()
    p.fear_level = 1.0
    p.memory_rate = 5.0
    mem = MemoryModel()
    series['M2 (fast memory, a=5)'] = integrate(mem.rhs, p, fear_strategy=FEAR_STRATEGIES["rational"], initial_state=[p.prey_0, p.pred_0, p.memory_0]).to_dataframe()
    p.memory_rate = 0.1
    series['M2 (slow memory, a=0.1)'] = integrate(mem.rhs, p, fear_strategy=FEAR_STRATEGIES["rational"], initial_state=[p.prey_0, p.pred_0, p.memory_0]).to_dataframe()
    plot_time_series(series, 'Baseline Model Comparison')
    plot_phase_portraits(series, 'Phase Portraits')
    return series


def run_step_k_scan(params):
    log.info('[2/9] k bifurcation scan...')
    p = params
    k_range = np.linspace(0, 20, 101)
    scan_k_df = scan_k(p, k_range, alpha_mem=10.0)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    scan_k_df.to_csv(RESULTS_DIR / 'scan_k.csv', index=False)
    plot_bifurcation(scan_k_df)
    plot_mean_amplitude(scan_k_df)
    return scan_k_df


def run_step_2d_scan(params):
    log.info('[3/9] k-alpha 2D scan...')
    p = params
    k_grid = np.linspace(0, 20, 91)
    alpha_grid = np.logspace(-2, 2, 91)
    scan_2d = scan_k_alpha(p, k_grid, alpha_grid)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    scan_2d.to_csv(RESULTS_DIR / 'scan_k_alpha.csv', index=False)
    plot_2d_classification(scan_2d)
    plot_amplitude_heatmap(scan_2d)
    return scan_2d, k_grid, alpha_grid


def run_step_theory(params, k_grid, alpha_grid, scan_2d):
    log.info('[4/9] Computing theory boundary...')
    p = params
    stable = compute_theory_boundary(p, k_grid, alpha_grid)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    np.save(RESULTS_DIR / 'theory_boundary.npy', stable)
    np.save(RESULTS_DIR / 'k_grid.npy', k_grid)
    np.save(RESULTS_DIR / 'alpha_grid.npy', alpha_grid)
    boundary_df = pd.DataFrame({
        'k': np.repeat(k_grid, len(alpha_grid)),
        'alpha': np.tile(alpha_grid, len(k_grid)),
        'stable': stable.flatten(),
    })
    boundary_df.to_csv(RESULTS_DIR / 'theory_boundary.csv', index=False)
    plot_theory_boundary_fig(scan_2d, stable, k_grid, alpha_grid)
    return stable


def run_step_robustness(params):
    log.info('[5/9] Fear function robustness...')
    p = params
    k_range = np.linspace(0, 4, 50)
    scan_dict = {}
    for fear_type in ['rational', 'exponential', 'quadratic']:
        rows = []
        for k_val in k_range:
            p.fear_level = k_val
            p.memory_rate = 10.0
            df = integrate(MemoryModel().rhs, p, fear_strategy=FEAR_STRATEGIES[fear_type], initial_state=[p.prey_0, p.pred_0, p.memory_0]).to_dataframe()
            metrics = compute_tail_metrics(df, int(p.burn_in / p.T * p.n_points))
            metrics['k'] = k_val
            rows.append(metrics)
        scan_dict[fear_type] = pd.DataFrame(rows)
    plot_robustness(scan_dict)
    return scan_dict


def run_step_representative(params, scan_2d, scan_k_df):
    log.info('[6/9] Finding representative cases...')
    p = params
    cases = find_representative_cases(scan_2d, scan_k_df, p)
    log.info(f'  Cases: { {k: f"k={v["k"]}, a={v["alpha"]:.3f}" for k, v in cases.items()} }')
    plot_representative_cases(cases, p)
    return cases


def run_step_tritrophic(params):
    log.info('[7/9] Tritrophic extension...')
    from params import TritrophicParams as TP
    tp_default = TP()
    series = {}
    for name, k1, k2 in [
        ('No fear', 0.0, 0.0),
        ('Both fear', tp_default.k1, tp_default.k2),
        ('Only basal fear', tp_default.k1, 0.0),
        ('Only mid fear', 0.0, tp_default.k2),
    ]:
        tp = TP()
        tp.k1 = k1
        tp.k2 = k2
        result = integrate(FoodChainModel().rhs, tp, initial_state=[tp.X0, tp.Y0, tp.Z0])
        series[name] = result.to_dataframe()
    plot_tritrophic(series)
    return series


def run_step_calibration(params):
    log.info('[8/9] Empirical calibration...')
    plot_empirical_calibration()


def run_step_extensions(params):
    log.info('[9/9] Extended models (delay, Leslie-Gower, discrete)...')
    from models.delay_model import DelayModel
    from models.leslie_gower import LeslieGowerModel
    from models.discrete_map import DiscreteMapModel
    from params import LeslieGowerParams, DiscreteParams
    from plot.extended_models import plot_leslie_gower

    delay_series = {}
    dm = DelayModel()
    for tau in [0.5, 1.0, 2.0]:
        result = integrate(dm.rhs_func(params), params, model_type="dde", tau=tau,
                           initial_state=[params.prey_0, params.pred_0])
        delay_series[f'tau={tau}'] = result.to_dataframe()
    plot_delay_model(delay_series, 'Delay Model (fear with time lag)')

    lg = LeslieGowerParams()
    result = integrate(LeslieGowerModel().rhs, lg, initial_state=[lg.x0, lg.y0], T=lg.T, n_points=lg.n_points)
    df_lg = result.to_dataframe()
    plot_leslie_gower({'Leslie-Gower': df_lg}, 'Leslie-Gower + Holling Type III')

    dp = DiscreteParams()
    dmm = DiscreteMapModel()
    trajectory_series = {}
    for k_val in [0.0, 5.0, 10.0, 15.0, 20.0]:
        xs, ys = [dp.x0], [dp.y0]
        for i in range(dp.n_generations):
            xn, yn = dmm.step(xs[-1], ys[-1], dp, k=k_val)
            xs.append(xn)
            ys.append(yn)
        trajectory_series[f'k={k_val:.1f}'] = pd.DataFrame({'t': np.arange(len(xs)), 'x': xs, 'y': ys})

    bif_k_vals = []
    bif_prey = []
    bif_pred = []
    for k_val in np.linspace(0, 20, 200):
        xs, ys = [dp.x0], [dp.y0]
        for i in range(dp.n_generations):
            xn, yn = dmm.step(xs[-1], ys[-1], dp, k=k_val)
            xs.append(xn)
            ys.append(yn)
        tail_x = xs[-(dp.n_generations // 2):]
        tail_y = ys[-(dp.n_generations // 2):]
        bif_k_vals.extend([k_val] * len(tail_x))
        bif_prey.extend(tail_x)
        bif_pred.extend(tail_y)
    bifurcation_data = {'k_vals': bif_k_vals, 'prey': bif_prey, 'predator': bif_pred}
    plot_discrete_model(trajectory_series, bifurcation_data)

    log.info('All extended models plotted.')
    return delay_series, df_lg, trajectory_series, bifurcation_data


def run_pipeline(params=None):
    if params is None:
        params = Params()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    log.info('=' * 60)
    log.info('Predator-Prey Fear Model - Full Pipeline')
    log.info('=' * 60)

    series = run_step_baseline(params)
    scan_k_df = run_step_k_scan(params)
    scan_2d, k_grid, alpha_grid = run_step_2d_scan(params)
    run_step_theory(params, k_grid, alpha_grid, scan_2d)
    run_step_robustness(params)
    run_step_representative(params, scan_2d, scan_k_df)
    run_step_tritrophic(params)
    run_step_calibration(params)
    run_step_extensions(params)

    log.info('=' * 60)
    log.info('All steps complete. Figures saved to output/figures/')
    log.info('=' * 60)