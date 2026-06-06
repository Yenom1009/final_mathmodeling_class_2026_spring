import numpy as np
from .base import ModelBase


class DelayModel(ModelBase):
    def __init__(self):
        self.name = "delay"
        self.aliases = ["delay_fear"]
        self.state_names = ["prey", "predator"]

    def rhs(self, t, state, params, fear_strategy=None, **extra):
        x, y_curr = state
        r = params.prey_birth_rate
        d2 = params.intra_comp
        p = params.attack_rate
        h = params.handling_time
        eta = params.conversion_eff
        d3 = params.pred_death
        k = getattr(params, 'fear_level', 0.0)
        fear_val = 1.0
        if fear_strategy is not None:
            fear_val = fear_strategy.compute(k, y_curr)
        predation = p * x * y_curr / (1.0 + h * x)
        dx = fear_val * r * x - d2 * x * x - predation
        dy = eta * predation - d3 * y_curr
        return np.array([dx, dy])

    def rhs_func(self, params, fear_strategy=None):
        def f(t, y, y_delayed, *args):
            x, y_curr = y
            x_del, y_del = y_delayed
            r = params.prey_birth_rate
            d2 = params.intra_comp
            p = params.attack_rate
            h = params.handling_time
            eta = params.conversion_eff
            d3 = params.pred_death
            k = params.fear_level

            fear_val = 1.0
            if fear_strategy is not None:
                fear_val = fear_strategy.compute(k, y_del)

            predation = p * x * y_curr / (1.0 + h * x)
            dx = fear_val * r * x - d2 * x * x - predation
            dy = eta * predation - d3 * y_curr
            return np.array([dx, dy])
        return f

    def default_initial(self, params):
        return np.array([params.prey_0, params.pred_0])

    def history_func(self, params):
        def hf(t):
            return np.array([params.history_x, params.history_y])
        return hf