"""Model ODE functions for all predator-prey variants.

Registers class-based model rhs callables into the global MODEL_REGISTRY.
"""

from __future__ import annotations

from .base import ModelBase
from .baseline import BaselineModel
from .memory import MemoryModel
from .fear import FearStrategy, RationalFear, ExponentialFear, QuadraticFear, FEAR_STRATEGIES
from .food_chain import FoodChainModel
from .leslie_gower import LeslieGowerModel
from .discrete_map import DiscreteMapModel
from .delay_model import DelayModel

from core.registry import register_model


def _register(name, model_instance):
    register_model(name, model_instance.rhs)
    for alias in getattr(model_instance, 'aliases', []):
        register_model(alias, model_instance.rhs)


_baseline = BaselineModel(use_fear=False)
_register("no_fear", _baseline)

_baseline_fear = BaselineModel(use_fear=True)
_register("instant", _baseline_fear)

_memory = MemoryModel()
_register("memory", _memory)

_food_chain = FoodChainModel()
_register("tritrophic", _food_chain)

_leslie_gower = LeslieGowerModel()
_register("leslie_gower", _leslie_gower)

_discrete = DiscreteMapModel()
_register("discrete", _discrete)

_delay = DelayModel()
_register("delay", _delay)


def get_model_instance(name: str) -> ModelBase:
    instances = {
        "no_fear": _baseline,
        "instant": _baseline_fear,
        "memory": _memory,
        "tritrophic": _food_chain,
        "leslie_gower": _leslie_gower,
        "discrete": _discrete,
        "delay": _delay,
    }
    if name in instances:
        return instances[name]
    for inst in instances.values():
        if name in getattr(inst, 'aliases', []):
            return inst
    raise ValueError(f"Unknown model: {name}")


__all__ = [
    "ModelBase", "BaselineModel", "MemoryModel", "FoodChainModel",
    "LeslieGowerModel", "DiscreteMapModel", "DelayModel",
    "FearStrategy", "RationalFear", "ExponentialFear", "QuadraticFear",
    "FEAR_STRATEGIES", "get_model_instance",
]