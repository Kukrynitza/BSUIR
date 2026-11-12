from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ACTIVATIONS = ("asinh",)


def act_asinh(u: np.ndarray) -> np.ndarray:
    return np.arcsinh(u)


def dact_asinh(u: np.ndarray) -> np.ndarray:
    return 1.0 / np.hypot(1.0, u)


_FORWARD = {"asinh": act_asinh}
_DERIV = {"asinh": dact_asinh}


@dataclass(frozen=True)
class Activation:
    name: str
    forward: object
    derivative: object


def get_activation(name: str) -> Activation:
    if name not in _FORWARD:
        raise ValueError(f"unknown activation: {name}")
    return Activation(name=name, forward=_FORWARD[name], derivative=_DERIV[name])
