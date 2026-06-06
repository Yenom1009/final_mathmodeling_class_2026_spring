import pandas as pd
import matplotlib.pyplot as plt

from .config import COLORS, _save


def plot_bifurcation(scan_k_df, title='Bifurcation: Extrema vs k', filename='fig03_bifurcation'):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold')
    k_vals = scan_k_df['k'].values
    for i, (var, color, label) in enumerate([('x', COLORS[0], 'Prey'), ('y', COLORS[1], 'Predator')]):
        ax = axes[i]
        max_col = f'{var}_max'
        min_col = f'{var}_min'
        if max_col not in scan_k_df.columns:
            max_col = f'prey_max' if var == 'x' else f'predator_max'
            min_col = f'prey_min' if var == 'x' else f'predator_min'
            if max_col not in scan_k_df.columns:
                continue
        ax.plot(k_vals, scan_k_df[max_col].values, color=color, linewidth=1.5, label=f'{label} max')
        ax.plot(k_vals, scan_k_df[min_col].values, color=color, linewidth=1.5, ls='--', label=f'{label} min')
        ax.set_xlabel('Fear level k')
        ax.set_ylabel('Density')
        ax.set_title(f'{label} extrema')
        ax.legend()
    plt.tight_layout()
    _save(fig, filename)
    return fig


def plot_mean_amplitude(scan_k_df, title='Mean Density & Amplitude vs k', filename='fig04_mean_amplitude'):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold')
    k_vals = scan_k_df['k'].values
    ax = axes[0]
    ax.plot(k_vals, scan_k_df['x_mean'].values, color=COLORS[0], linewidth=2, label='Prey')
    ax.plot(k_vals, scan_k_df['y_mean'].values, color=COLORS[1], linewidth=2, label='Predator')
    ax.set_xlabel('Fear level k')
    ax.set_ylabel('Mean density')
    ax.set_title('Mean density')
    ax.legend()
    ax = axes[1]
    ax.plot(k_vals, scan_k_df.get('x_rel_amp', scan_k_df.get('x_amplitude', 0)), color=COLORS[0], linewidth=2, label='Prey')
    ax.plot(k_vals, scan_k_df.get('y_rel_amp', scan_k_df.get('y_amplitude', 0)), color=COLORS[1], linewidth=2, label='Predator')
    ax.set_xlabel('Fear level k')
    ax.set_ylabel('Relative amplitude')
    ax.set_title('Oscillation amplitude')
    ax.legend()
    plt.tight_layout()
    _save(fig, filename)
    return fig