from __future__ import annotations

import numpy as np

import sequences as seqmod
from activations import ACTIVATIONS
from network import ARCHS, RecurrentNetwork


def test_sequences():
    print("== SEQUENCES ==")
    for name, fn in seqmod.SEQUENCES.items():
        s = seqmod.get_sequence(name, 32)
        assert s.ndim == 1 and s.size >= 10, f"{name}: bad shape {s.shape}"
        assert np.all(np.isfinite(s)), f"{name}: non-finite values"
        print(f"  {name:12s} len={s.size:3d} first={s[:4]}")
    assert np.allclose(seqmod.geometric(0.5, 5), [1, 0.5, 0.25, 0.125, 0.0625])
    assert np.allclose(seqmod.harmonic(4), [1, 0.5, 1 / 3, 0.25])
    assert np.allclose(seqmod.squares(5), [1, 4, 9, 16, 25])
    assert np.allclose(seqmod.odds(5), [1, 3, 5, 7, 9])
    assert np.allclose(seqmod.fibonacci(8), [1, 1, 2, 3, 5, 8, 13, 21])
    assert np.allclose(seqmod.factorial(5), [1, 1, 2, 6, 24])
    assert np.allclose(seqmod.periodic(6), [1, 0, 1, 0, 1, 0])
    ap = seqmod.aperiodic(10)
    assert ap[0] == 1 and ap[1] == 0 and ap[2] == 1 and ap[3] == 0 and ap[4] == 0 and ap[5] == 1
    bell = seqmod.bell(7)
    assert np.allclose(bell, [1, 1, 2, 5, 15, 52, 203]), f"bell={bell}"
    s = seqmod.geometric(0.5, 20)
    n = seqmod.normalize(s)[0]
    assert n.min() >= -1.0 and n.max() <= 1.0
    rec = seqmod.denormalize(n, *seqmod.normalize(s)[1:])
    assert np.allclose(rec, s, atol=1e-9)
    X, y = seqmod.make_windows(n, window=5)
    assert X.shape[1] == 5 and X.shape[0] == y.size
    print("  OK")


def test_activations():
    print("== ACTIVATIONS ==")
    u = np.linspace(-3, 3, 13)
    for name in ACTIVATIONS:
        from activations import get_activation
        act = get_activation(name)
        v = act.forward(u)
        assert v.shape == u.shape
        eps = 1e-6
        num = (act.forward(u + eps) - act.forward(u - eps)) / (2 * eps)
        an = act.derivative(u)
        mask = np.abs(u) > 1e-3
        assert np.allclose(num[mask], an[mask], atol=1e-4), f"{name}: num={num} an={an}"
        print(f"  {name:12s} ok")
    print("  OK")


def test_network_train_and_forecast():
    print("== NETWORK ==")
    rng = np.random.default_rng(0)
    base = seqmod.geometric(0.5, 40)
    norm, lo, hi = seqmod.normalize(base)
    X, y = seqmod.make_windows(norm, window=6)
    for arch in ARCHS:
        for act_name in ("asinh", "tanh"):
            net = RecurrentNetwork(
                arch=arch, hidden_size=8, context_size=4, window=6,
                act=act_name, linear_out=True, seed=1,
            )
            res = net.train(X, y, epochs=40, lr=0.05, zero_context=True)
            assert len(res.losses) == 40
            assert all(np.isfinite(l) for l in res.losses)
            preds = net.forecast(norm[-6:], steps=5)
            assert preds.shape == (5,)
            assert np.all(np.isfinite(preds))
            print(f"  {arch:12s}/{act_name:10s} loss {res.losses[0]:.4f} -> {res.losses[-1]:.4f}")
    print("  OK")


if __name__ == "__main__":
    test_sequences()
    test_activations()
    test_network_train_and_forecast()
    print("ALL SMOKE TESTS PASSED")
