from abc import ABC, abstractmethod
import numpy as np
from typing import Optional


class ModelBase(ABC):
    name: str = ""
    aliases: list[str] = []
    state_names: list[str] = []

    @abstractmethod
    def rhs(self, t, state, params, fear_strategy=None, **extra):
        ...

    def default_initial(self, params):
        ...

    @property
    def n_vars(self):
        return len(self.state_names)