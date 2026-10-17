from __future__ import annotations

import numpy as np


def geometric(ratio: float, n: int = 32, start: float = 1.0) -> np.ndarray:
    return start * np.power(ratio, np.arange(n, dtype=np.float64))


def arithmetic(start: float, step: float, n: int = 32) -> np.ndarray:
    return start + step * np.arange(n, dtype=np.float64)


def harmonic(n: int = 32) -> np.ndarray:
    return 1.0 / np.arange(1, n + 1, dtype=np.float64)


def squares(n: int = 32) -> np.ndarray:
    k = np.arange(1, n + 1, dtype=np.float64)
    return k * k


def odds(n: int = 32) -> np.ndarray:
    return arithmetic(1.0, 2.0, n)


def fibonacci(n: int = 32) -> np.ndarray:
    out = np.zeros(n, dtype=np.float64)
    if n > 0:
        out[0] = 1.0
    if n > 1:
        out[1] = 1.0
    for i in range(2, n):
        out[i] = out[i - 1] + out[i - 2]
    return out


def factorial(n: int = 32) -> np.ndarray:
    out = np.empty(n, dtype=np.float64)
    out[0] = 1.0
    for i in range(1, n):
        out[i] = out[i - 1] * i
    return out


def periodic(n: int = 32) -> np.ndarray:
    x = np.zeros(n, dtype=np.float64)
    x[::2] = 1.0
    return x


def aperiodic(n: int = 32) -> np.ndarray:
    x = np.zeros(n, dtype=np.float64)
    pos = 0
    gap = 1
    while pos < n:
        x[pos] = 1.0
        gap += 1
        pos += gap
    return x


def bell(n: int = 32) -> np.ndarray:
    out = np.zeros(n, dtype=np.float64)
    if n > 0:
        out[0] = 1.0
    row = [1.0]
    for i in range(1, n):
        nxt = [row[-1]]
        for j in range(len(row)):
            nxt.append(nxt[-1] + row[j])
        row = nxt
        out[i] = row[0]
    return out


SEQUENCES: dict[str, object] = {
    "geometric_0.5": lambda n: geometric(0.5, n),
    "harmonic": harmonic,
    "geometric_0.2": lambda n: geometric(0.2, n),
    "periodic": periodic,
    "aperiodic": aperiodic,
    "arithmetic": lambda n: arithmetic(1.0, 1.0, n),
    "squares": squares,
    "odds": odds,
    "geometric_2": lambda n: geometric(2.0, n),
    "bell": bell,
    "factorial": factorial,
    "fibonacci": fibonacci,
}


def get_sequence(name: str, n: int = 32) -> np.ndarray:
    if name not in SEQUENCES:
        raise ValueError(f"unknown sequence: {name}")
    fn = SEQUENCES[name]
    return np.asarray(fn(n), dtype=np.float64)


def normalize(seq: np.ndarray) -> tuple[np.ndarray, float, float]:
    lo = float(seq.min())
    hi = float(seq.max())
    if hi - lo < 1e-12:
        return np.zeros_like(seq), lo, hi
    scaled = 2.0 * (seq - lo) / (hi - lo) - 1.0
    return scaled, lo, hi


def denormalize(values: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return (values + 1.0) * 0.5 * (hi - lo) + lo


def make_windows(
    seq: np.ndarray, window: int
) -> tuple[np.ndarray, np.ndarray]:
    xs: list[list[float]] = []
    ys: list[float] = []
    for t in range(window - 1, len(seq) - 1):
        xs.append(list(seq[t - window + 1 : t + 1]))
        ys.append(float(seq[t + 1]))
    return np.asarray(xs, dtype=np.float64), np.asarray(ys, dtype=np.float64)
