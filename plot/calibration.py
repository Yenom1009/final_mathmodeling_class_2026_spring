import numpy as np
import matplotlib.pyplot as plt

from .config import COLORS, _save


def plot_empirical_calibration(title='Empirical Calibration', filename='fig10_calibration'):
    fig, ax = plt.subplots(figsize=(8, 6))
    k_vals = np.linspace(0, 10, 100)
    reduction_target = 0.4
    for r in [0.3, 0.5, 0.8, 1.0]:
        y_vals = np.linspace(0.1, 20, 100)
        fear_vals = 1.0 / (1.0 + np.outer(k_vals, y_vals))
        reduction = 1 - fear_vals.mean(axis=1)
        ax.plot(k_vals, reduction, linewidth=1.5, label=f'r={r}')
    ax.axhline(y=reduction_target, color='gray', ls='--', linewidth=1.5)
    ax.set_xlabel('Fear level k')
    ax.set_ylabel('Mean birth reduction')
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    _save(fig, filename)
    return fig