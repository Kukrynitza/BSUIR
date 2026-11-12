from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from weights import projection_weights

MODE = "continuous/sync"


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
    """Сеть Хопфилда, вариант 2: непрерывное состояние, синхронный режим."""

    def __init__(
        self,
        n: int,
        delta: float = 0.0,
        gain: float = 2.0,
    ) -> None:
        self.n = n
        self.delta = float(delta)
        self.gain = float(gain)
        self.W = np.zeros((n, n))
        self.patterns: np.ndarray | None = None
        self.training_patterns: np.ndarray | None = None

    def learn(
        self,
        patterns: np.ndarray,
        prototypes: np.ndarray | None = None,
    ) -> None:
        X = np.atleast_2d(np.asarray(patterns, dtype=np.float64))
        if X.shape[1] != self.n:
            raise ValueError(f"pattern size {X.shape[1]} != n={self.n}")
        self.training_patterns = X.copy()

        if prototypes is None:
            self.patterns = X.copy()
        else:
            P = np.atleast_2d(np.asarray(prototypes, dtype=np.float64))
            if P.shape[1] != self.n:
                raise ValueError(f"prototype size {P.shape[1]} != n={self.n}")
            self.patterns = P.copy()

        self.W = projection_weights(X, delta=self.delta)

    def energy(self, x: np.ndarray) -> float:
        e = -0.5 * float(x @ self.W @ x)
        v = np.clip(x, -1.0 + 1e-12, 1.0 - 1e-12)
        integral = v * np.arctanh(v) + 0.5 * np.log(1.0 - v * v)
        e += float(np.sum(integral)) / self.gain
        return e

    def relax(
        self,
        x0: np.ndarray,
        max_iter: int = 200,
        eps: float = 1e-6,
    ) -> RelaxResult:
        x = np.array(x0, dtype=np.float64, copy=True)

        energies = [self.energy(x)]
        deltas = [float("inf")]
        visited: dict[bytes, int] = {np.round(x, 9).tobytes(): 0}

        converged = False
        cycle = False
        cycle_length = 0
        iterations = 0

        for it in range(1, max_iter + 1):
            x_old = x.copy()
            x = np.tanh(self.gain * (self.W @ x))

            iterations = it
            delta = float(np.max(np.abs(x - x_old)))
            energies.append(self.energy(x))
            deltas.append(delta)

            if delta < eps:
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
    ) -> tuple[RelaxResult, int, int]:
        if self.patterns is None:
            raise RuntimeError("network is not trained")
        result = self.relax(x0, max_iter=max_iter, eps=eps)
        b = binarize(result.state)
        mismatches = np.sum(b[None, :] != self.patterns, axis=1)
        idx = int(np.argmin(mismatches))
        return result, idx, int(mismatches[idx])

    @property
    def mode_description(self) -> str:
        return MODE
