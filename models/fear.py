from abc import ABC, abstractmethod
import numpy as np


class FearStrategy(ABC):
    name: str = ""

    @abstractmethod
    def compute(self, k: float, risk: float) -> float:
        ...

    def __call__(self, k, risk):
        return self.compute(k, risk)


class RationalFear(FearStrategy):
    name = "rational"
    def compute(self, k, risk):
        return 1.0 / (1.0 + k * risk)


class ExponentialFear(FearStrategy):
    name = "exponential"
    def compute(self, k, risk):
        return np.exp(-k * risk)


class QuadraticFear(FearStrategy):
    name = "quadratic"
    def compute(self, k, risk):
        return 1.0 / (1.0 + k * risk + 0.5 * (k * risk)**2)


FEAR_STRATEGIES = {
    "rational": RationalFear(),
    "exponential": ExponentialFear(),
    "quadratic": QuadraticFear(),
}