from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from activations import get_activation

ARCHS = ("jordan", "elman", "jordan_elman", "rnn", "lstm", "gru")
SIMPLE_ARCHS = ("jordan", "elman", "jordan_elman", "rnn")
GATED_ARCHS = ("lstm", "gru")


def sigmoid(u: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-u))


@dataclass
class TrainResult:
    epochs_done: int
    losses: list[float]


class RecurrentNetwork:

    def __init__(
        self,
        arch: str,
        hidden_size: int,
        context_size: int,
        window: int,
        act: str = "asinh",
        linear_out: bool = True,
        effector_init: float | None = None,
        seed: int | None = 42,
    ) -> None:
        if arch not in ARCHS:
            raise ValueError(f"bad arch: {arch}")
        self.arch = arch
        self.hidden_size = hidden_size
        self.context_size = context_size
        self.window = window
        self.act = get_activation(act)
        self.linear_out = linear_out
        if arch in GATED_ARCHS:
            self.out_act = get_activation("elu")
        elif linear_out:
            self.out_act = get_activation("linear")
        else:
            self.out_act = self.act

        rng = np.random.default_rng(seed)
        H = hidden_size
        C = context_size
        self.ctx_elman = C if arch == "elman" else (C // 2 if arch == "jordan_elman" else 0)
        self.ctx_jordan = C if arch == "jordan" else (C - self.ctx_elman if arch == "jordan_elman" else 0)
        if arch == "jordan_elman":
            self.ctx_elman = max(1, C // 2)
            self.ctx_jordan = C - self.ctx_elman

        scale = 0.5
        if arch in ("jordan", "jordan_elman"):
            nin = 1 + C
            self.W_xh = rng.normal(0.0, scale, size=(H, nin))
            self.b_h = np.zeros(H)
            if effector_init is not None:
                self.W_ho = np.full((1, H), float(effector_init))
                self.b_o = np.zeros(1)
            else:
                self.W_ho = rng.normal(0.0, scale, size=(1, H))
                self.b_o = np.zeros(1)
            self.W_hh = None
        elif arch == "elman":
            nin = 1 + C
            self.W_xh = rng.normal(0.0, scale, size=(H, nin))
            self.b_h = np.zeros(H)
            self.W_ho = rng.normal(0.0, scale, size=(1, H))
            self.b_o = np.zeros(1)
            self.W_hh = None
        elif arch == "rnn":
            self.W_xh = rng.normal(0.0, scale, size=(H, 1))
            self.W_hh = rng.normal(0.0, scale / np.sqrt(H), size=(H, H))
            self.b_h = np.zeros(H)
            self.W_ho = rng.normal(0.0, scale, size=(1, H))
            self.b_o = np.zeros(1)
        elif arch == "lstm":
            self.W_xh = rng.normal(0.0, scale, size=(4 * H, 1))
            self.W_hh = rng.normal(0.0, scale / np.sqrt(H), size=(4 * H, H))
            self.b = np.zeros(4 * H)
            self.b[H:2 * H] = 1.0  # forget gate bias
            self.W_ho = rng.normal(0.0, scale, size=(1, H))
            self.b_o = np.zeros(1)
        elif arch == "gru":
            self.W_xz = rng.normal(0.0, scale, size=(H, 1))
            self.W_hz = rng.normal(0.0, scale / np.sqrt(H), size=(H, H))
            self.b_z = np.zeros(H)
            self.W_xr = rng.normal(0.0, scale, size=(H, 1))
            self.W_hr = rng.normal(0.0, scale / np.sqrt(H), size=(H, H))
            self.b_r = np.zeros(H)
            self.W_xh = rng.normal(0.0, scale, size=(H, 1))
            self.W_hh = rng.normal(0.0, scale / np.sqrt(H), size=(H, H))
            self.b_h = np.zeros(H)
            self.W_ho = rng.normal(0.0, scale, size=(1, H))
            self.b_o = np.zeros(1)

    def initial_state(self):
        if self.arch == "lstm":
            return (np.zeros(self.hidden_size), np.zeros(self.hidden_size))
        if self.arch in ("rnn", "gru"):
            return np.zeros(self.hidden_size)
        return np.zeros(self.context_size)

    def _step(self, x: float, state):
        if self.arch == "elman":
            inp = np.concatenate([[x], state])
            z = self.W_xh @ inp + self.b_h
            h = self.act.forward(z)
            pre = float((self.W_ho @ h + self.b_o)[0])
            y = float(self.out_act.forward(np.array([pre]))[0])
            new_state = h[: self.context_size].copy()
            cache = (inp, z, h, pre, state)
            return y, new_state, cache

        if self.arch == "jordan":
            inp = np.concatenate([[x], state])
            z = self.W_xh @ inp + self.b_h
            h = self.act.forward(z)
            pre = float((self.W_ho @ h + self.b_o)[0])
            y = float(self.out_act.forward(np.array([pre]))[0])
            new_state = np.zeros(self.context_size)
            new_state[0] = y
            if self.context_size > 1:
                new_state[1:] = state[:-1]
            cache = (inp, z, h, pre, state)
            return y, new_state, cache

        if self.arch == "jordan_elman":
            ce, cj = self.ctx_elman, self.ctx_jordan
            inp = np.concatenate([[x], state])
            z = self.W_xh @ inp + self.b_h
            h = self.act.forward(z)
            pre = float((self.W_ho @ h + self.b_o)[0])
            y = float(self.out_act.forward(np.array([pre]))[0])
            new_elman = h[:ce].copy()
            new_jordan = np.zeros(cj)
            if cj > 0:
                new_jordan[0] = y
                if cj > 1:
                    new_jordan[1:] = state[ce : ce + cj - 1]
            new_state = np.concatenate([new_elman, new_jordan])
            cache = (inp, z, h, pre, state)
            return y, new_state, cache

        if self.arch == "rnn":
            z = float((self.W_xh[0] * x)[0]) + self.W_hh @ state + self.b_h
            h = self.act.forward(z)
            pre = float((self.W_ho @ h + self.b_o)[0])
            y = float(self.out_act.forward(np.array([pre]))[0])
            cache = (x, z, h, pre, state)
            return y, h.copy(), cache

        if self.arch == "lstm":
            h_prev, c_prev = state
            z = self.W_xh[:, 0] * x + self.W_hh @ h_prev + self.b
            i = sigmoid(z[: self.hidden_size])
            f = sigmoid(z[self.hidden_size : 2 * self.hidden_size])
            o = sigmoid(z[2 * self.hidden_size : 3 * self.hidden_size])
            g = np.tanh(z[3 * self.hidden_size :])
            c = f * c_prev + i * g
            th = np.tanh(c)
            h = o * th
            pre = float((self.W_ho @ h + self.b_o)[0])
            y = float(self.out_act.forward(np.array([pre]))[0])
            cache = (x, h_prev, c_prev, i, f, o, g, c, th, h, pre)
            return y, (h.copy(), c.copy()), cache

        if self.arch == "gru":
            h_prev = state
            zz = sigmoid(self.W_xz[:, 0] * x + self.W_hz @ h_prev + self.b_z)
            r = sigmoid(self.W_xr[:, 0] * x + self.W_hr @ h_prev + self.b_r)
            h_tilde = np.tanh(self.W_xh[:, 0] * x + self.W_hh @ (r * h_prev) + self.b_h)
            h = (1.0 - zz) * h_prev + zz * h_tilde
            pre = float((self.W_ho @ h + self.b_o)[0])
            y = float(self.out_act.forward(np.array([pre]))[0])
            cache = (x, h_prev, zz, r, h_tilde, h, pre)
            return y, h.copy(), cache

        raise RuntimeError(self.arch)

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

        if self.arch == "elman":
            dh = np.zeros(self.hidden_size)
            for t in reversed(range(T)):
                inp, z, h, pre, state = caches[t]
                if t == T - 1:
                    dpre = dy * self.out_act.derivative(np.array([pre]))[0]
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

        if self.arch == "jordan":
            d_state_next = np.zeros(self.context_size)
            for t in reversed(range(T)):
                inp, z, h, pre, state = caches[t]
                dy_t = d_state_next[0]
                if t == T - 1:
                    dy_t += dy
                dpre = dy_t * self.out_act.derivative(np.array([pre]))[0]
                g["W_ho"] += dpre * h
                g["b_o"] += dpre
                dh = dpre * self.W_ho[0]
                dz = dh * self.act.derivative(z)
                g["W_xh"] += np.outer(dz, inp)
                g["b_h"] += dz
                d_inp = self.W_xh.T @ dz
                d_state_t = d_inp[1:].copy()
                if self.context_size > 1:
                    d_state_t[: self.context_size - 1] += d_state_next[1:]
                d_state_next = d_state_t
            return g

        if self.arch == "jordan_elman":
            ce, cj = self.ctx_elman, self.ctx_jordan
            d_state_next = np.zeros(ce + cj)
            for t in reversed(range(T)):
                inp, z, h, pre, state = caches[t]
                dy_t = d_state_next[ce] if cj > 0 else 0.0
                if t == T - 1:
                    dy_t += dy
                dpre = dy_t * self.out_act.derivative(np.array([pre]))[0]
                g["W_ho"] += dpre * h
                g["b_o"] += dpre
                dh = dpre * self.W_ho[0]
                dz = dh * self.act.derivative(z)
                g["W_xh"] += np.outer(dz, inp)
                g["b_h"] += dz
                d_inp = self.W_xh.T @ dz
                d_state_t = d_inp[1:].copy()
                d_state_t[:ce] += d_state_next[:ce]
                if cj > 1:
                    d_state_t[ce : ce + cj - 1] += d_state_next[ce + 1 :]
                d_state_next = d_state_t
            return g

        if self.arch == "rnn":
            dh = np.zeros(self.hidden_size)
            for t in reversed(range(T)):
                x, z, h, pre, h_prev = caches[t]
                if t == T - 1:
                    dpre = dy * self.out_act.derivative(np.array([pre]))[0]
                    g["W_ho"] += dpre * h
                    g["b_o"] += dpre
                    dh = dh + dpre * self.W_ho[0]
                dz = dh * self.act.derivative(z)
                g["W_xh"] += np.outer(dz, [x])
                g["W_hh"] += np.outer(dz, h_prev)
                g["b_h"] += dz
                dh = self.W_hh.T @ dz
            return g

        if self.arch == "lstm":
            H = self.hidden_size
            dh_next = np.zeros(H)
            dc_next = np.zeros(H)
            for t in reversed(range(T)):
                (x, h_prev, c_prev, i, f, o, g_, c, th, h, pre) = caches[t]
                if t == T - 1:
                    dpre = dy * self.out_act.derivative(np.array([pre]))[0]
                    g["W_ho"] += dpre * h
                    g["b_o"] += dpre
                    dh_next = dh_next + dpre * self.W_ho[0]
                do = dh_next * th
                dc = dc_next + dh_next * o * (1.0 - th * th)
                df = dc * c_prev
                di = dc * g_
                dg = dc * i
                dc_prev = dc * f
                dz = np.concatenate(
                    [
                        di * i * (1.0 - i),
                        df * f * (1.0 - f),
                        do * o * (1.0 - o),
                        dg * (1.0 - g_ * g_),
                    ]
                )
                g["W_xh"] += np.outer(dz, [x])
                g["W_hh"] += np.outer(dz, h_prev)
                g["b"] += dz
                dh_next = self.W_hh.T @ dz
                dc_next = dc_prev
            return g

        if self.arch == "gru":
            H = self.hidden_size
            dh_next = np.zeros(H)
            for t in reversed(range(T)):
                (x, h_prev, zz, r, h_tilde, h, pre) = caches[t]
                if t == T - 1:
                    dpre = dy * self.out_act.derivative(np.array([pre]))[0]
                    g["W_ho"] += dpre * h
                    g["b_o"] += dpre
                    dh_next = dh_next + dpre * self.W_ho[0]
                dzz = dh_next * (h_prev - h_tilde)
                dh_tilde = dh_next * zz
                dh_prev_from_h = dh_next * (1.0 - zz)
                dzpre = dzz * zz * (1.0 - zz)
                g["W_xz"] += np.outer(dzpre, [x])
                g["W_hz"] += np.outer(dzpre, h_prev)
                g["b_z"] += dzpre
                dh_prev_total = dh_prev_from_h + self.W_hz.T @ dzpre
                dr_hprev = (self.W_hh.T @ (dh_tilde * (1.0 - h_tilde * h_tilde)))
                dr = dr_hprev * h_prev
                drpre = dr * r * (1.0 - r)
                g["W_xr"] += np.outer(drpre, [x])
                g["W_hr"] += np.outer(drpre, h_prev)
                g["b_r"] += drpre
                dh_prev_total += self.W_hr.T @ drpre
                dz_h = dh_tilde * (1.0 - h_tilde * h_tilde)
                g["W_xh"] += np.outer(dz_h, [x])
                g["W_hh"] += np.outer(dz_h, r * h_prev)
                g["b_h"] += dz_h
                dh_prev_total += self.W_hh.T @ (dz_h * r)
                dh_next = dh_prev_total
            return g

        raise RuntimeError(self.arch)

    def _zero_grads(self) -> dict:
        if self.arch in ("jordan", "jordan_elman", "elman"):
            return {
                "W_xh": np.zeros_like(self.W_xh),
                "b_h": np.zeros_like(self.b_h),
                "W_ho": np.zeros_like(self.W_ho),
                "b_o": np.zeros_like(self.b_o),
            }
        if self.arch == "rnn":
            return {
                "W_xh": np.zeros_like(self.W_xh),
                "W_hh": np.zeros_like(self.W_hh),
                "b_h": np.zeros_like(self.b_h),
                "W_ho": np.zeros_like(self.W_ho),
                "b_o": np.zeros_like(self.b_o),
            }
        if self.arch == "lstm":
            return {
                "W_xh": np.zeros_like(self.W_xh),
                "W_hh": np.zeros_like(self.W_hh),
                "b": np.zeros_like(self.b),
                "W_ho": np.zeros_like(self.W_ho),
                "b_o": np.zeros_like(self.b_o),
            }
        if self.arch == "gru":
            return {
                "W_xz": np.zeros_like(self.W_xz),
                "W_hz": np.zeros_like(self.W_hz),
                "b_z": np.zeros_like(self.b_z),
                "W_xr": np.zeros_like(self.W_xr),
                "W_hr": np.zeros_like(self.W_hr),
                "b_r": np.zeros_like(self.b_r),
                "W_xh": np.zeros_like(self.W_xh),
                "W_hh": np.zeros_like(self.W_hh),
                "b_h": np.zeros_like(self.b_h),
                "W_ho": np.zeros_like(self.W_ho),
                "b_o": np.zeros_like(self.b_o),
            }
        raise RuntimeError(self.arch)

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
        shuffle: bool = True,
        seed: int | None = 42,
    ) -> TrainResult:
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
                pred, carry, caches = self.forward_window(xs, state=carry)
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
        return f"{self.arch}/{self.act.name}"
