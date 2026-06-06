import matplotlib.pyplot as plt

from .config import COLORS, _save


def plot_robustness(scan_k_dict, title='Fear Function Robustness', filename='fig07_robustness'):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold')
    colors_r = [COLORS[0], COLORS[1], COLORS[2]]
    for idx, (label, df) in enumerate(scan_k_dict.items()):
        k_vals = df['k'].values
        axes[0].plot(k_vals, df['x_mean'].values, color=colors_r[idx], linewidth=2, label=label)
        axes[1].plot(k_vals, df.get('y_rel_amp', df.get('y_amplitude', 0)), color=colors_r[idx], linewidth=2, label=label)
    axes[0].set_xlabel('Fear level k')
    axes[0].set_ylabel('Mean prey density')
    axes[0].set_title('Mean prey density')
    axes[0].legend()
    axes[1].set_xlabel('Fear level k')
    axes[1].set_ylabel('Predator rel. amplitude')
    axes[1].set_title('Predator oscillation')
    axes[1].legend()
    plt.tight_layout()
    _save(fig, filename)
    return fig