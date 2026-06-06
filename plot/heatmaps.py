import numpy as np
import matplotlib.pyplot as plt

from .config import COLORS, COLOR_MAP, _save


def plot_2d_classification(scan_2d_df, title='k-α Classification', filename='fig05_2d_classification'):
    fig, ax = plt.subplots(figsize=(10, 7))
    pivot = scan_2d_df.pivot_table(index='alpha', columns='k', values='class_code', aggfunc='first')
    k_vals = pivot.columns.values
    alpha_vals = pivot.index.values
    data = pivot.values
    cmap = plt.matplotlib.colors.ListedColormap([COLOR_MAP[c] for c in [
        'stable_coexistence', 'oscillatory_coexistence', 'predator_extinct',
        'prey_extinct', 'low_density_risk', 'invalid']])
    bound = np.arange(-0.5, 6.5, 1)
    norm = plt.matplotlib.colors.BoundaryNorm(bound, cmap.N)
    im = ax.pcolormesh(k_vals, alpha_vals, data, cmap=cmap, norm=norm, shading='auto')
    ax.set_xlabel('Fear level k')
    ax.set_ylabel('Memory rate α')
    ax.set_yscale('log')
    ax.set_title(title)
    cbar = plt.colorbar(im, ax=ax, ticks=np.arange(6))
    cbar.set_ticklabels(['Stable', 'Oscillation', 'Pred Ext', 'Prey Ext', 'Low Density', 'Invalid'])
    plt.tight_layout()
    _save(fig, filename)
    return fig


def plot_amplitude_heatmap(scan_2d_df, title='Log Amplitude Heatmap', filename='fig05b_amplitude_heatmap'):
    fig, ax = plt.subplots(figsize=(10, 7))
    pivot = scan_2d_df.pivot_table(index='alpha', columns='k', values='amplitude', aggfunc='first')
    k_vals = pivot.columns.values
    alpha_vals = pivot.index.values
    data = np.log10(np.maximum(pivot.values, 1e-15))
    im = ax.pcolormesh(k_vals, alpha_vals, data, cmap='viridis', shading='auto')
    ax.set_xlabel('Fear level k')
    ax.set_ylabel('Memory rate α')
    ax.set_yscale('log')
    ax.set_title(title)
    plt.colorbar(im, ax=ax, label='log₁₀(Amplitude)')
    plt.tight_layout()
    _save(fig, filename)
    return fig