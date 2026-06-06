import matplotlib.pyplot as plt
from pathlib import Path

FIG_DIR = Path(__file__).resolve().parent.parent / 'output' / 'figures'

COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4']

COLOR_MAP = {
    'stable_coexistence': '#2E86AB',
    'oscillatory_coexistence': '#F18F01',
    'predator_extinct': '#C73E1D',
    'prey_extinct': '#A23B72',
    'low_density_risk': '#44BBA4',
    'invalid': '#D3D3D3',
}


def _save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f'{name}.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)