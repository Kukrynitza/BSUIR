from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ADAPTIVE = True
NORMALIZE_WEIGHTS = True


@dataclass
class TrainResult:
    epochs_done: int
    errors: list[float]
    final_error: float
    stopped_by_eps: bool


class RecirculationNetwork:
    def __init__(
        self,
        n: int,
        p: int,
        alpha: float = 0.01,
        seed: int | None = 42,
    ) -> None:
        if p <= 0 or p >= n:
            raise ValueError(f"bad p: n={n}, p={p}")
        self.n = n
        self.p = p
        self.alpha = alpha

        rng = np.random.default_rng(seed)
        self.W = rng.normal(0.0, 0.1, size=(n, p))
        self.Wp = rng.normal(0.0, 0.1, size=(p, n))
        if NORMALIZE_WEIGHTS:
            self._normalize_weights()

    def _normalize_weights(self) -> None:
        w_norm = np.linalg.norm(self.W, axis=0, keepdims=True)
        w_norm = np.maximum(w_norm, 1e-12)
        self.W = self.W / w_norm

        wp_norm = np.linalg.norm(self.Wp, axis=1, keepdims=True)
        wp_norm = np.maximum(wp_norm, 1e-12)
        self.Wp = self.Wp / wp_norm

    def encode(self, X: np.ndarray) -> np.ndarray:
        return X @ self.W

    def decode(self, Y: np.ndarray) -> np.ndarray:
        return Y @ self.Wp

    def reconstruct(self, X: np.ndarray) -> np.ndarray:
        return self.decode(self.encode(X))

    def _alpha_for_sample(self, X: np.ndarray, Y: np.ndarray) -> float:
        if not ADAPTIVE:
            return self.alpha
        denom = float(np.dot(X, X) + np.dot(Y, Y))
        return 1.0 / max(denom, 1e-12)

    def _train_sample(self, X: np.ndarray) -> float:
        Y = X @ self.W
        Xp = Y @ self.Wp
        err = Xp - X
        alpha = self._alpha_for_sample(X, Y)

        dWp = -alpha * np.outer(Y, err)
        dW = -alpha * np.outer(X, err @ self.Wp.T)

        self.Wp = self.Wp + dWp
        self.W = self.W + dW

        if NORMALIZE_WEIGHTS:
            self._normalize_weights()

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
