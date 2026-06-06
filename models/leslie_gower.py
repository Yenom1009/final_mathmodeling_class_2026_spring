import numpy as np
from .base import ModelBase


class LeslieGowerModel(ModelBase):
    def __init__(self):
        self.name = "leslie_gower"
        self.aliases = []
        self.state_names = ["prey", "predator"]

    def rhs(self, t, state, params, fear_strategy=None, **extra):
        w, v = state
        r = params.r
        K = params.K
        a = params.a
        s = params.s
        tau_pred = params.tau_pred

        fear = 1.0 / (1.0 + params.theta * v)
        holling3 = a * w * w * v / (w * w + s * v * v)

        dw = fear * r * w * (1.0 - w / K) - holling3
        dv = tau_pred * v * (1.0 - v / w) if w > 1e-10 else -tau_pred * v

        return np.array([dw, dv])

    def default_initial(self, params):
        return np.array([params.x0, params.y0])