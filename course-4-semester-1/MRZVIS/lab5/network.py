from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from activations import get_activation

MODE = "elman/asinh"


@dataclass
class TrainResult:
    epochs_done: int
    losses: list[float]


class RecurrentNetwork:
    """Сеть Элмана, вариант 2: скрытая активация arcsinh."""

    def __init__(
        self,
        hidden_size: int,
        context_size: int,
        window: int,
        linear_out: bool = True,
        seed: int | None = 42,
    ) -> None:
        if hidden_size < 1:
            raise ValueError(f"hidden_size must be positive, got {hidden_size}")
        if not 1 <= context_size <= hidden_size:
            raise ValueError(
                "context_size must satisfy 1 <= context_size <= hidden_size, "
                f"got context_size={context_size}, hidden_size={hidden_size}"
            )

        self.hidden_size = hidden_size
        self.context_size = context_size
        self.window = window
        self.act = get_activation("asinh")
        self.linear_out = linear_out

        rng = np.random.default_rng(seed)
        H = hidden_size
        C = context_size
        scale = 0.5
        self.W_xh = rng.normal(0.0, scale, size=(H, 1 + C))
        self.b_h = np.zeros(H)
        self.W_ho = rng.normal(0.0, scale, size=(1, H))
        self.b_o = np.zeros(1)

    def initial_state(self) -> np.ndarray:
        return np.zeros(self.context_size)

    def _step(self, x: float, state: np.ndarray):
        inp = np.concatenate([[x], state])
        z = self.W_xh @ inp + self.b_h
        h = self.act.forward(z)
        pre = float((self.W_ho @ h + self.b_o)[0])
        y = pre if self.linear_out else float(np.arcsinh(pre))
        new_state = h[: self.context_size].copy()
        cache = (inp, z, h, pre, state)
        return y, new_state, cache

    def forward_window(self, xs: np.ndarray, state=None):
        if state is None:
            state = self.initial_state()
        caches = []
        y = 0.0
        for x in xs:
            y, state, cache = self._step(float(x), state)
            caches.append(cache)
        return y, state, caches

    def _backward(self, caches: list, dy: float) -> dict:
        T = len(caches)
        g = self._zero_grads()
        dh = np.zeros(self.hidden_size)
        for t in reversed(range(T)):
            inp, z, h, pre, state = caches[t]
            if t == T - 1:
                dpre = dy * (1.0 if self.linear_out else self.act.derivative(np.array([pre]))[0])
                g["W_ho"] += dpre * h
                g["b_o"] += dpre
                dh = dh + dpre * self.W_ho[0]
            dz = dh * self.act.derivative(z)
            g["W_xh"] += np.outer(dz, inp)
            g["b_h"] += dz
            d_state = self.W_xh[:, 1:].T @ dz
            dh = np.zeros(self.hidden_size)
            dh[: self.context_size] = d_state
        return g

    def _zero_grads(self) -> dict:
        return {
            "W_xh": np.zeros_like(self.W_xh),
            "b_h": np.zeros_like(self.b_h),
            "W_ho": np.zeros_like(self.W_ho),
            "b_o": np.zeros_like(self.b_o),
        }

    def _apply_grads(self, g: dict, lr: float, clip: float = 5.0) -> None:
        for name, grad in g.items():
            grad = np.clip(grad, -clip, clip)
            w = getattr(self, name) - lr * grad
            setattr(self, name, np.clip(w, -100.0, 100.0))

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 300,
        lr: float = 0.02,
        zero_context: bool = True,
        shuffle: bool = False,
        seed: int | None = 42,
    ) -> TrainResult:
        """Train the network on sliding windows.

        Windows must be processed in chronological order if the context is
        carried between them: otherwise a window receives the hidden state of
        an unrelated part of the series.  ``shuffle`` is therefore disabled by
        default and should only be enabled together with per-window state
        reset (see ``main.train_net``).
        """
        rng = np.random.default_rng(seed)
        losses: list[float] = []
        N = X.shape[0]
        carry = self.initial_state()
        for epoch in range(1, epochs + 1):
            if zero_context:
                carry = self.initial_state()
            order = np.arange(N)
            if shuffle:
                rng.shuffle(order)
            total = 0.0
            bad = False
            for idx in order:
                xs = X[idx]
                target = float(y[idx])
                state = self.initial_state() if shuffle else carry
                pred, carry, caches = self.forward_window(xs, state=state)
                err = pred - target
                if not np.isfinite(err):
                    bad = True
                    break
                total += 0.5 * err * err
                g = self._backward(caches, err)
                self._apply_grads(g, lr)
            if bad:
                losses.append(float("nan"))
                break
            losses.append(total / N)
        return TrainResult(epochs_done=len(losses), losses=losses)

    def forecast(self, seed_window: np.ndarray, steps: int) -> np.ndarray:
        state = self.initial_state()
        w = np.asarray(seed_window, dtype=np.float64).copy()
        y = 0.0
        for x in w:
            y, state, _ = self._step(float(x), state)
        preds = [y]
        for _ in range(steps - 1):
            y, state, _ = self._step(float(y), state)
            preds.append(y)
        return np.asarray(preds, dtype=np.float64)

    @property
    def mode_description(self) -> str:
        return MODE
