import numpy as np
from .base import ModelBase


class FoodChainModel(ModelBase):
    def __init__(self):
        self.name = "food_chain"
        self.aliases = ["M3", "tritrophic"]
        self.state_names = ["X", "Y", "Z"]

    def rhs(self, t, state, params, fear_strategy=None, **extra):
        X, Y, Z = state
        r_X = params.r_X
        d_X = params.d_X
        a_X = params.a_X
        p1 = params.p1
        h1 = params.h1
        eta1 = params.eta1
        d_Y = params.d_Y
        p2 = params.p2
        h2 = params.h2
        eta2 = params.eta2
        d_Z = params.d_Z
        k1 = params.k1
        k2 = params.k2

        f_basal = 1.0 / (1.0 + k1 * Y)
        f_mid = 1.0 / (1.0 + k2 * Z)
        pred1 = p1 * X * Y / (1.0 + h1 * X)
        pred2 = p2 * Y * Z / (1.0 + h2 * Y)

        dX = f_basal * r_X * X - d_X * X - a_X * X * X - pred1
        dY = f_mid * eta1 * pred1 - d_Y * Y - pred2
        dZ = eta2 * pred2 - d_Z * Z
        return np.array([dX, dY, dZ])

    def default_initial(self, params):
        return np.array([params.X0, params.Y0, params.Z0])