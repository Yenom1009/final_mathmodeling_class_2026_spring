import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .config import COLORS, _save


def _get_col(df, names):
    for n in names:
        if n in df.columns:
            return df[n]
    return df[names[0]]


def _model_label(name):
    labels = {
        'no_fear': 'M0: No Fear',
        'instant': 'M1: Instant Fear',
        'memory': 'M2: Memory Fear',
        'tritrophic': 'M3: Tritrophic',
        'adaptive': 'M-AD: Adaptive Defense',
        'leslie_gower': 'M-LG: Leslie-Gower',
        'delay': 'M-D: Time Delay',
    }
    return labels.get(name, name)


def plot_time_series(series_dict, title='Time Series', filename='fig01_timeseries'):
    n_plots = len(series_dict)
    n_cols = min(2, n_plots)
    n_rows = (n_plots + 1) // 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4 * n_rows), squeeze=False)
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    for idx, (name, df) in enumerate(series_dict.items()):
        ax = axes[idx // n_cols][idx % n_cols]
        if 'x' in df.columns:
            ax.plot(df['t'], df['x'], color=COLORS[0], linewidth=1.2, label='Prey (x)')
        elif 'prey' in df.columns:
            ax.plot(df['t'], df['prey'], color=COLORS[0], linewidth=1.2, label='Prey')
        if 'y' in df.columns:
            ax.plot(df['t'], df['y'], color=COLORS[1], linewidth=1.2, label='Predator (y)')
        elif 'predator' in df.columns:
            ax.plot(df['t'], df['predator'], color=COLORS[1], linewidth=1.2, label='Predator')
        if 'z' in df.columns:
            ax.plot(df['t'], df['z'], color=COLORS[2], linewidth=1.0, alpha=0.7, label='Memory (z)')
        elif 'memory' in df.columns:
            ax.plot(df['t'], df['memory'], color=COLORS[2], linewidth=1.0, alpha=0.7, label='Memory')
        if 'w' in df.columns or 'X' in df.columns:
            label = 'Top Pred (w)' if 'w' in df.columns else 'Basal (X)'
            col = 'w' if 'w' in df.columns else 'X'
            ax.plot(df['t'], df[col], color=COLORS[3], linewidth=1.2, label=label)
        if 'Y' in df.columns:
            ax.plot(df['t'], df['Y'], color=COLORS[4], linewidth=1.2, label='Mid Pred (Y)')
        if 'Z' in df.columns:
            ax.plot(df['t'], df['Z'], color=COLORS[5], linewidth=1.2, label='Top Pred (Z)')
        ax.set_xlabel('Time')
        ax.set_ylabel('Density')
        ax.set_title(_model_label(name))
        ax.legend(fontsize=8)
        ax.set_xlim(0, df['t'].max())
    for idx in range(n_plots, n_rows * n_cols):
        axes[idx // n_cols][idx % n_cols].set_visible(False)
    plt.tight_layout()
    _save(fig, filename)
    return fig


def plot_representative_cases(cases, params, title='Representative Cases', filename='fig09_representative'):
    n_cases = len(cases)
    fig, axes = plt.subplots(1, n_cases, figsize=(6 * n_cases, 4), squeeze=False)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    from models.memory import MemoryModel
    from models.fear import FEAR_STRATEGIES
    from core.engine import integrate
    for idx, (key, case) in enumerate(cases.items()):
        ax = axes[0][idx]
        params.fear_level = case['k']
        params.memory_rate = case['alpha']
        result = integrate(MemoryModel().rhs, params,
                           fear_strategy=FEAR_STRATEGIES["rational"],
                           initial_state=[params.prey_0, params.pred_0, params.memory_0])
        df = result.to_dataframe()
        burn = int(params.burn_in)
        tail = df[df['t'] >= burn]
        full = df
        ax.plot(full['t'], full['x'], color=COLORS[0], linewidth=1.2, label='Prey')
        ax.plot(full['t'], full['y'], color=COLORS[1], linewidth=1.2, label='Predator')
        ax.axvline(x=params.burn_in, color='gray', ls=':', alpha=0.5)
        ax.set_xlabel('Time')
        ax.set_ylabel('Density')
        ax.set_title(f'Case {key}: k={case["k"]}, α={case["alpha"]:.3f}')
        ax.legend(fontsize=8)
    plt.tight_layout()
    _save(fig, filename)
    return fig