from typing import Callable

MODEL_REGISTRY: dict[str, Callable] = {}


def register_model(name: str, func: Callable) -> None:
    MODEL_REGISTRY[name] = func


def resolve_model(name: str) -> Callable:
    if name in MODEL_REGISTRY:
        return MODEL_REGISTRY[name]
    lower = name.lower()
    for key in MODEL_REGISTRY:
        if key.lower() == lower:
            return MODEL_REGISTRY[key]
    raise ValueError(f"Unknown model: {name}. Available: {list(MODEL_REGISTRY.keys())}")