"""Canonical model catalog for the final project.

This keeps the strongest idea from the zcq branch: treat model variants as
named, structured objects instead of loose strings scattered across scripts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    canonical_name: str
    aliases: tuple[str, ...]
    state_dim: int
    role: str
    family: str


MODEL_SPECS: dict[str, ModelSpec] = {
    "no_fear": ModelSpec("no_fear", ("M0", "baseline"), 2, "main", "ode"),
    "instant": ModelSpec("instant", ("M1", "instant_fear"), 2, "main", "ode"),
    "memory": ModelSpec("memory", ("M2", "memory_fear"), 3, "main", "ode"),
    "alt_logistic": ModelSpec("alt_logistic", ("compatibility",), 3, "comparison", "ode"),
    "tritrophic": ModelSpec("tritrophic", ("M3", "food_chain"), 3, "extension", "ode"),
    "leslie_gower": ModelSpec("leslie_gower", ("lg",), 2, "extension", "ode"),
}


ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical_name, spec in MODEL_SPECS.items():
    ALIAS_TO_CANONICAL[canonical_name.lower()] = canonical_name
    for alias in spec.aliases:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical_name


def resolve_model_name(name: str) -> str:
    key = name.lower()
    if key not in ALIAS_TO_CANONICAL:
        raise ValueError(f"unknown model name: {name}")
    return ALIAS_TO_CANONICAL[key]
