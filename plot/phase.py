import matplotlib.pyplot as plt

from .config import COLORS, _save
from .time_series import _model_label


def plot_phase_portraits(series_dict, title='Phase Portraits', filename='fig02_phase'):
    n_plots = len(series_dict)
    n_cols = min(2, n_plots)
    n_rows = (n_plots + 1) // 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4 * n_rows), squeeze=False)
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    for idx, (name, df) in enumerate(series_dict.items()):
        ax = axes[idx // n_cols][idx % n_cols]
        burn = len(df) // 3
        tail = df.iloc[burn:]
        if 'x' in df.columns and 'y' in df.columns:
            ax.plot(tail['x'], tail['y'], color=COLORS[idx % len(COLORS)], linewidth=0.8, alpha=0.8)
        elif 'prey' in df.columns and 'predator' in df.columns:
            ax.plot(tail['prey'], tail['predator'], color=COLORS[idx % len(COLORS)], linewidth=0.8, alpha=0.8)
        if 'X' in df.columns and 'Y' in df.columns:
            ax.plot(tail['X'], tail['Y'], color=COLORS[(idx + 1) % len(COLORS)], linewidth=0.8, alpha=0.8)
        ax.set_xlabel('Prey')
        ax.set_ylabel('Predator')
        ax.set_title(_model_label(name))
    for idx in range(n_plots, n_rows * n_cols):
        axes[idx // n_cols][idx % n_cols].set_visible(False)
    plt.tight_layout()
    _save(fig, filename)
    return fig