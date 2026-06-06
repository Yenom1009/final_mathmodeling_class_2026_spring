import numpy as np
from .base import ModelBase


class MemoryModel(ModelBase):
    def __init__(self):
        self.name = "memory"
        self.aliases = ["M2", "memory_fear"]
        self.state_names = ["prey", "predator", "memory"]

    def rhs(self, t, state, params, fear_strategy=None, **extra):
        x, y, z = state
        r = params.prey_birth_rate
        d1 = 0.0
        d2 = params.intra_comp
        p = params.attack_rate
        h = params.handling_time
        eta = params.conversion_eff
        d3 = params.pred_death
        k = params.fear_level
        alpha = params.memory_rate

        fear_val = 1.0
        if fear_strategy is not None:
            fear_val = fear_strategy.compute(k, z)

        predation = p * x * y / (1.0 + h * x)
        dx = fear_val * r * x - d1 * x - d2 * x * x - predation
        dy = eta * predation - d3 * y
        dz = alpha * (y - z)
        return np.array([dx, dy, dz])

    def default_initial(self, params):
        return np.array([params.prey_0, params.pred_0, params.memory_0])