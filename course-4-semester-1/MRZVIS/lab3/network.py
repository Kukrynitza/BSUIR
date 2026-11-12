from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TrainResult:
    epochs_done: int
    errors: list[float]
    final_error: float
    stopped_by_eps: bool


class RecirculationNetwork:
    """Линейная рециркуляционная сеть, вариант 2.

    Адаптивный коэффициент обучения, веса не нормируются.
    """

    def __init__(
        self,
        n: int,
        p: int,
        seed: int | None = 42,
        lr_scale: float = 1.0,
    ) -> None:
        if p <= 0 or p >= n:
            raise ValueError(f"bad p: n={n}, p={p}")
        if lr_scale <= 0.0:
            raise ValueError(f"lr_scale must be positive, got {lr_scale}")
        self.n = n
        self.p = p
        self.lr_scale = float(lr_scale)

        rng = np.random.default_rng(seed)
        self.W = rng.normal(0.0, 0.1, size=(n, p))
        self.Wp = rng.normal(0.0, 0.1, size=(p, n))

    def encode(self, X: np.ndarray) -> np.ndarray:
        return X @ self.W

    def decode(self, Y: np.ndarray) -> np.ndarray:
        return Y @ self.Wp

    def reconstruct(self, X: np.ndarray) -> np.ndarray:
        return self.decode(self.encode(X))

    def _alpha_for_sample(self, X: np.ndarray, Y: np.ndarray) -> float:
        denom = float(np.dot(X, X) + np.dot(Y, Y))
        return self.lr_scale / max(denom, 1e-12)

    def _train_sample(self, X: np.ndarray) -> float:
        Y = X @ self.W
        Xp = Y @ self.Wp
        err = Xp - X
        alpha = self._alpha_for_sample(X, Y)

        dWp = -alpha * np.outer(Y, err)
        dW = -alpha * np.outer(X, err @ self.Wp.T)

        self.Wp = self.Wp + dWp
        self.W = self.W + dW

        return float(np.dot(err, err))

    def train(
        self,
        samples: np.ndarray,
        max_epochs: int = 1000,
        eps: float = 1e-3,
        shuffle: bool = True,
        seed: int | None = 42,
    ) -> TrainResult:
        rng = np.random.default_rng(seed)
        errors: list[float] = []
        stopped = False
        epochs_done = 0

        for epoch in range(1, max_epochs + 1):
            order = np.arange(samples.shape[0])
            if shuffle:
                rng.shuffle(order)

            total_sq = 0.0
            for idx in order:
                total_sq += self._train_sample(samples[idx])

            epoch_error = 0.5 * total_sq
            errors.append(epoch_error)
            epochs_done = epoch

            if epoch_error <= eps:
                stopped = True
                break

        return TrainResult(
            epochs_done=epochs_done,
            errors=errors,
            final_error=errors[-1] if errors else float("inf"),
            stopped_by_eps=stopped,
        )
