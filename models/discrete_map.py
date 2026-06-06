import numpy as np
from .base import ModelBase


class DiscreteMapModel(ModelBase):
    def __init__(self):
        self.name = "discrete"
        self.aliases = ["discrete_map"]
        self.state_names = ["prey", "predator"]

    def rhs(self, t, state, params, fear_strategy=None, **extra):
        raise NotImplementedError("DiscreteMapModel is a discrete map; use step() instead")

    def step(self, x, y, params, k=0.0):
        a_growth = params.a_growth
        d_death = params.d_death
        b_comp = params.b_comp
        c_pred = params.c_pred
        mu_conv = params.mu_conv
        e_death = params.e_death

        fear = 1.0 / (1.0 + k * y)
        x_next = x * np.exp(fear * a_growth - d_death - b_comp * x - c_pred * y)
        y_next = y * np.exp(mu_conv * c_pred * x - e_death)
        return x_next, y_next

    def default_initial(self, params):
        return np.array([params.x0, params.y0])