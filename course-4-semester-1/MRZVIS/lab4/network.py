from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from weights import projection_weights

STATE_MODES = ("discrete", "continuous")
UPDATE_MODES = ("sync", "async")


def modified_sign(u: np.ndarray | float) -> np.ndarray:
    arr = np.asarray(u, dtype=np.float64)
    out = np.sign(arr)
    m = np.abs(arr) < 1.0
    uu = arr[m]
    out[m] = 0.5 * uu * (1.0 + np.cos(np.pi * uu))
    return out


def modified_sign_scalar(u: float) -> float:
    if u >= 1.0:
        return 1.0
    if u <= -1.0:
        return -1.0
    return 0.5 * u * (1.0 + np.cos(np.pi * u))


def binarize(x: np.ndarray) -> np.ndarray:
    return np.where(x >= 0.0, 1.0, -1.0)


@dataclass
class RelaxResult:
    state: np.ndarray
    iterations: int
    converged: bool
    cycle: bool
    cycle_length: int
    energies: list[float]
    deltas: list[float]


class HopfieldNetwork:
    def __init__(
        self,
        n: int,
        state: str = "discrete",
        update: str = "async",
        delta: float = 0.0,
        gain: float = 2.0,
    ) -> None:
        if state not in STATE_MODES:
            raise ValueError(f"bad state: {state}")
        if update not in UPDATE_MODES:
            raise ValueError(f"bad update: {update}")
        self.n = n
        self.state = state
        self.update = update
        self.delta = float(delta)
        self.gain = float(gain)
        self.W = np.zeros((n, n))
        self.patterns: np.ndarray | None = None

    def learn(self, patterns: np.ndarray) -> None:
        X = np.atleast_2d(np.asarray(patterns, dtype=np.float64))
        if X.shape[1] != self.n:
            raise ValueError(f"pattern size {X.shape[1]} != n={self.n}")
        self.patterns = X.copy()
        self.W = projection_weights(X, delta=self.delta)

    def energy(self, x: np.ndarray) -> float:
        e = -0.5 * float(x @ self.W @ x)
        if self.state == "continuous":
            v = np.clip(x, -1.0 + 1e-12, 1.0 - 1e-12)
            integral = v * np.arctanh(v) + 0.5 * np.log(1.0 - v * v)
            e += float(np.sum(integral)) / self.gain
        return e

    def relax(
        self,
        x0: np.ndarray,
        max_iter: int = 200,
        eps: float = 1e-6,
        seed: int | None = 42,
    ) -> RelaxResult:
        rng = np.random.default_rng(seed)
        x = np.array(x0, dtype=np.float64, copy=True)
        discrete = self.state == "discrete"
        sync = self.update == "sync"

        energies = [self.energy(x)]
        deltas = [float("inf")]
        visited: dict[bytes, int] = {np.round(x, 9).tobytes(): 0}

        converged = False
        cycle = False
        cycle_length = 0
        iterations = 0

        for it in range(1, max_iter + 1):
            x_old = x.copy()
            if sync:
                h = self.gain * (self.W @ x)
                x = modified_sign(h) if discrete else np.tanh(h)
            else:
                order = rng.permutation(self.n)
                if discrete:
                    for i in order:
                        x[i] = modified_sign_scalar(self.gain * float(self.W[i] @ x))
                else:
                    for i in order:
                        x[i] = np.tanh(self.gain * float(self.W[i] @ x))

            iterations = it
            delta = float(np.max(np.abs(x - x_old)))
            energies.append(self.energy(x))
            deltas.append(delta)

            if discrete:
                if np.array_equal(binarize(x), binarize(x_old)):
                    converged = True
                    break
            elif delta < eps:
                converged = True
                break

            key = np.round(x, 9).tobytes()
            if key in visited:
                cycle = True
                cycle_length = it - visited[key]
                break
            visited[key] = it

        return RelaxResult(
            state=x,
            iterations=iterations,
            converged=converged,
            cycle=cycle,
            cycle_length=cycle_length,
            energies=energies,
            deltas=deltas,
        )

    def recognize(
        self,
        x0: np.ndarray,
        max_iter: int = 200,
        eps: float = 1e-6,
        seed: int | None = 42,
    ) -> tuple[RelaxResult, int, int]:
        if self.patterns is None:
            raise RuntimeError("network is not trained")
        result = self.relax(x0, max_iter=max_iter, eps=eps, seed=seed)
        b = binarize(result.state)
        mismatches = np.sum(b[None, :] != self.patterns, axis=1)
        idx = int(np.argmin(mismatches))
        return result, idx, int(mismatches[idx])

    @property
    def mode_description(self) -> str:
        return f"{self.state}/{self.update}"
