import matplotlib.pyplot as plt

from .config import COLORS, _save
from .time_series import _model_label


def plot_tritrophic(series_dict, title='Tritrophic Dynamics', filename='fig08_tritrophic'):
    n = len(series_dict)
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 5), squeeze=False)
    axes = axes[0]
    fig.suptitle(title, fontsize=14, fontweight='bold')
    colors_t = [COLORS[0], COLORS[1], COLORS[2], COLORS[3]]
    for idx, (name, df) in enumerate(series_dict.items()):
        ax = axes[idx]
        df_cols = {c.lower(): c for c in df.columns}
        if 'x' in df_cols:
            ax.plot(df['t'], df[df_cols['x']], color=colors_t[0], linewidth=1.2, label='Basal (X)')
        if 'y' in df_cols:
            ax.plot(df['t'], df[df_cols['y']], color=colors_t[1], linewidth=1.2, label='Mid (Y)')
        if 'z' in df_cols:
            ax.plot(df['t'], df[df_cols['z']], color=colors_t[2], linewidth=1.2, label='Top (Z)')
        ax.set_xlabel('Time')
        ax.set_ylabel('Density')
        ax.set_title(name)
        if len(ax.lines) > 0:
            ax.legend()
    plt.tight_layout()
    _save(fig, filename)
    return fig


def plot_delay_model(series_dict, title='Delay Model Dynamics', filename='fig11_delay_model'):
    n_plots = len(series_dict)
    fig, axes = plt.subplots(1, n_plots, figsize=(7 * n_plots, 5), squeeze=False)
    axes = axes[0]
    fig.suptitle(title, fontsize=14, fontweight='bold')
    for idx, (name, df) in enumerate(series_dict.items()):
        ax = axes[idx]
        if 'x' in df.columns:
            ax.plot(df['t'], df['x'], color=COLORS[0], linewidth=1.2, label='Prey')
        elif 'prey' in df.columns:
            ax.plot(df['t'], df['prey'], color=COLORS[0], linewidth=1.2, label='Prey')
        if 'y' in df.columns:
            ax.plot(df['t'], df['y'], color=COLORS[1], linewidth=1.2, label='Predator')
        elif 'predator' in df.columns:
            ax.plot(df['t'], df['predator'], color=COLORS[1], linewidth=1.2, label='Predator')
        ax.set_xlabel('Time')
        ax.set_ylabel('Density')
        ax.set_title(name)
        ax.legend(fontsize=8)
    plt.tight_layout()
    _save(fig, filename)
    return fig


def plot_discrete_model(trajectory_dict, bif_data=None, title='Discrete Map Dynamics', filename='fig12_discrete'):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold')
    ax = axes[0]
    for idx, (label, df) in enumerate(trajectory_dict.items()):
        c = COLORS[idx % len(COLORS)]
        col_x = 'x' if 'x' in df.columns else ('prey' if 'prey' in df.columns else df.columns[1])
        ax.plot(df['t'], df[col_x], color=c, linewidth=0.8, alpha=0.7, label=label)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Prey density')
    ax.set_title('Prey time series (fear effect)')
    ax.legend(fontsize=8)

    ax = axes[1]
    if isinstance(bif_data, dict) and 'k_vals' in bif_data:
        k_vals = bif_data['k_vals']
        prey_key = 'prey' if 'prey' in bif_data else ('x' if 'x' in bif_data else None)
        pred_key = 'predator' if 'predator' in bif_data else ('y' if 'y' in bif_data else None)
        if prey_key:
            ax.scatter(k_vals, bif_data[prey_key], c='steelblue', s=0.5, alpha=0.15, label='Prey (x)')
        if pred_key:
            ax.scatter(k_vals, bif_data[pred_key], c='coral', s=0.5, alpha=0.15, label='Predator (y)')
    elif bif_data:
        for k_val, (tail_x, tail_y) in bif_data.items():
            ax.scatter([k_val] * len(tail_x), tail_y, c='coral', s=0.5, alpha=0.15)
            ax.scatter([k_val] * len(tail_x), tail_x, c='steelblue', s=0.5, alpha=0.15)
    ax.set_xlabel('Fear level k')
    ax.set_ylabel('Steady-state density')
    ax.set_title('Steady states vs k')
    ax.legend(fontsize=8)
    plt.tight_layout()
    _save(fig, filename)
    return fig


def plot_leslie_gower(series_dict, title='Leslie-Gower Dynamics', filename='fig13_leslie_gower'):
    n_plots = len(series_dict)
    fig, axes = plt.subplots(1, n_plots, figsize=(7 * n_plots, 5), squeeze=False)
    axes = axes[0]
    fig.suptitle(title, fontsize=14, fontweight='bold')
    for idx, (name, df) in enumerate(series_dict.items()):
        ax = axes[idx]
        if 'x' in df.columns:
            ax.plot(df['t'], df['x'], color=COLORS[0], linewidth=1.2, label='Prey (x)')
        elif 'w' in df.columns:
            ax.plot(df['t'], df['w'], color=COLORS[0], linewidth=1.2, label='Prey (w)')
        if 'y' in df.columns:
            ax.plot(df['t'], df['y'], color=COLORS[1], linewidth=1.2, label='Predator (y)')
        elif 'v' in df.columns:
            ax.plot(df['t'], df['v'], color=COLORS[1], linewidth=1.2, label='Predator (v)')
        ax.set_xlabel('Time')
        ax.set_ylabel('Density')
        ax.set_title(name)
        ax.legend(fontsize=8)
    plt.tight_layout()
    _save(fig, filename)
    return fig