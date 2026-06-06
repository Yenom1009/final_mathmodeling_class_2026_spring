import numpy as np
from .base import ModelBase


class BaselineModel(ModelBase):
    def __init__(self, use_fear=True):
        self.use_fear = use_fear
        self.name = "baseline"
        self.aliases = ["M0", "M1", "no_fear", "instant", "instant_fear"]
        self.state_names = ["prey", "predator"]

    def rhs(self, t, state, params, fear_strategy=None, **extra):
        x, y = state
        r = params.prey_birth_rate
        d1 = 0.0
        d2 = params.intra_comp
        p = params.attack_rate
        h = params.handling_time
        eta = params.conversion_eff
        d3 = params.pred_death
        k = params.fear_level

        fear = 1.0
        if self.use_fear and fear_strategy is not None:
            fear = fear_strategy.compute(k, y)

        predation = p * x * y / (1.0 + h * x)
        dx = fear * r * x - d1 * x - d2 * x * x - predation
        dy = eta * predation - d3 * y
        return np.array([dx, dy])

    def default_initial(self, params):
        return np.array([params.prey_0, params.pred_0])