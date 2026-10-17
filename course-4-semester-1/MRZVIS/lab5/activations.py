from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ACTIVATIONS = ("asinh", "tanh", "elu", "leaky_relu", "linear")
ELU_ALPHA = 1.0
LEAKY_SLOPE = 0.01


def act_asinh(u: np.ndarray) -> np.ndarray:
    return np.arcsinh(u)


def dact_asinh(u: np.ndarray) -> np.ndarray:
    return 1.0 / np.hypot(1.0, u)


def act_tanh(u: np.ndarray) -> np.ndarray:
    return np.tanh(u)


def dact_tanh(u: np.ndarray) -> np.ndarray:
    t = np.tanh(u)
    return 1.0 - t * t


def act_elu(u: np.ndarray) -> np.ndarray:
    return np.where(u >= 0.0, u, ELU_ALPHA * (np.exp(np.minimum(u, 0.0)) - 1.0))


def dact_elu(u: np.ndarray) -> np.ndarray:
    return np.where(u >= 0.0, 1.0, ELU_ALPHA * np.exp(np.minimum(u, 0.0)))


def act_leaky_relu(u: np.ndarray) -> np.ndarray:
    return np.where(u >= 0.0, u, LEAKY_SLOPE * u)


def dact_leaky_relu(u: np.ndarray) -> np.ndarray:
    return np.where(u >= 0.0, 1.0, LEAKY_SLOPE)


def act_linear(u: np.ndarray) -> np.ndarray:
    return u


def dact_linear(u: np.ndarray) -> np.ndarray:
    return np.ones_like(u)


_FORWARD = {
    "asinh": act_asinh,
    "tanh": act_tanh,
    "elu": act_elu,
    "leaky_relu": act_leaky_relu,
    "linear": act_linear,
}

_DERIV = {
    "asinh": dact_asinh,
    "tanh": dact_tanh,
    "elu": dact_elu,
    "leaky_relu": dact_leaky_relu,
    "linear": dact_linear,
}


@dataclass(frozen=True)
class Activation:
    name: str
    forward: object
    derivative: object


def get_activation(name: str) -> Activation:
    if name not in _FORWARD:
        raise ValueError(f"unknown activation: {name}")
    return Activation(name=name, forward=_FORWARD[name], derivative=_DERIV[name])
