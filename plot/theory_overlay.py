import numpy as np
import matplotlib.pyplot as plt

from .config import COLOR_MAP, _save


def plot_theory_boundary(scan_2d_df, stable_grid, k_grid, alpha_grid,
                         title='Theory vs Simulation', filename='fig06_theory_boundary'):
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
    ax.pcolormesh(k_vals, alpha_vals, data, cmap=cmap, norm=norm, shading='auto', alpha=0.7)
    K, A = np.meshgrid(k_grid, alpha_grid)
    ax.contour(K, A, stable_grid.T, levels=[0.5], colors='white', linewidths=2.5, linestyles='--')
    ax.set_xlabel('Fear level k')
    ax.set_ylabel('Memory rate α')
    ax.set_yscale('log')
    ax.set_title(title)
    plt.tight_layout()
    _save(fig, filename)
    return fig