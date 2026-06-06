from dataclasses import dataclass
from typing import Optional


@dataclass
class Params:
    prey_birth_rate: float = 0.5
    intra_comp: float = 0.005
    attack_rate: float = 0.08
    handling_time: float = 0.1
    conversion_eff: float = 0.5
    pred_death: float = 0.3

    prey_0: float = 5.0
    pred_0: float = 2.0
    z0: float = 10.0
    memory_0: float = 10.0

    T: float = 800.0
    burn_in: float = 300.0
    n_points: int = 5000

    k: float = 1.0
    alpha: float = 1.0
    fear_level: float = 1.0
    memory_rate: float = 1.0

    model_type: str = "ode"
    model_name: str = "no_fear"

    k_scan_range: tuple = (0, 20, 101)
    k_2d_range: tuple = (0, 20, 91)
    alpha_2d_range: tuple = (-2, 2, 91)
    k_robust_range: tuple = (0, 4, 50)

    @property
    def r(self): return self.prey_birth_rate
    @property
    def d1(self): return 0.0
    @property
    def d2(self): return self.intra_comp
    @property
    def p(self): return self.attack_rate
    @property
    def h(self): return self.handling_time
    @property
    def eta(self): return self.conversion_eff
    @property
    def d3(self): return self.pred_death
    @property
    def x0(self): return self.prey_0
    @property
    def y0(self): return self.pred_0


@dataclass
class TritrophicParams:
    r_X: float = 0.8
    d_X: float = 0.01
    a_X: float = 0.01
    p1: float = 0.6
    h1: float = 0.08
    eta1: float = 0.45
    d_Y: float = 0.15
    p2: float = 0.45
    h2: float = 0.1
    eta2: float = 0.35
    d_Z: float = 0.08
    k1: float = 1.0
    k2: float = 0.5
    X0: float = 30.0
    Y0: float = 10.0
    Z0: float = 5.0
    T: float = 1000.0
    n_points: int = 6000
    model_type: str = "ode"
    model_name: str = "tritrophic"


@dataclass
class LeslieGowerParams:
    r: float = 0.8
    K: float = 1.0
    theta: float = 2.0
    a: float = 0.5
    s: float = 0.5
    tau_pred: float = 0.3
    x0: float = 0.8
    y0: float = 0.3
    T: float = 500.0
    n_points: int = 3000
    model_type: str = "ode"
    model_name: str = "leslie_gower"


@dataclass
class DiscreteParams:
    a_growth: float = 2.0
    d_death: float = 0.1
    b_comp: float = 0.05
    c_pred: float = 0.03
    mu_conv: float = 0.5
    e_death: float = 0.2
    x0: float = 5.0
    y0: float = 2.0
    n_generations: int = 500
    model_type: str = "discrete"
    model_name: str = "discrete"


