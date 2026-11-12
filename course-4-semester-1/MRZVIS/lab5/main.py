from __future__ import annotations

import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from network import MODE, RecurrentNetwork
from sequences import (
    SEQUENCES,
    denormalize,
    get_sequence,
    make_windows,
    normalize_with_bounds,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "output")
REPORT_PNG = os.path.join(HERE, "mrzvis-report-5", "png")
os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(REPORT_PNG, exist_ok=True)

N_POINTS = 32
PRIMARY_SEQ = "geometric_0.5"
FORECAST_STEPS = 8
TRAIN_FRACTION = 0.75
SEED = 42
COLOR = "#1f77b4"


def split_seq(seq: np.ndarray):
    cut = int(len(seq) * TRAIN_FRACTION)
    return seq[:cut], seq[cut:]


def train_net(
    seq: np.ndarray,
    window: int,
    hidden: int,
    context: int,
    epochs: int,
    lr: float,
    linear_out: bool = True,
    zero_context: bool = True,
    shuffle: bool = False,
):
    train_raw, test_raw = split_seq(seq)
    # Fit normalization on the training part only; applying it to test keeps
    # future extrema out of the model's preprocessing.
    lo = float(train_raw.min())
    hi = float(train_raw.max())
    train, lo, hi = normalize_with_bounds(train_raw, lo, hi)
    test, _, _ = normalize_with_bounds(test_raw, lo, hi)
    X, y = make_windows(train, window)
    net = RecurrentNetwork(
        hidden_size=hidden,
        context_size=context,
        window=window,
        linear_out=linear_out,
        seed=SEED,
    )
    res = net.train(
        X, y, epochs=epochs, lr=lr, zero_context=zero_context, shuffle=shuffle
    )
    seed_window = train[-window:]
    preds_n = net.forecast(seed_window, steps=len(test))
    actual_n = test
    preds = denormalize(preds_n, lo, hi)
    actual = denormalize(actual_n, lo, hi)
    return {
        "net": net,
        "losses": res.losses,
        "preds": preds,
        "actual": actual,
        "preds_n": preds_n,
        "actual_n": actual_n,
        "lo": lo,
        "hi": hi,
        "norm": np.concatenate([train, test]),
        "mse_n": mse(preds_n, actual_n),
    }


def mse(a, b):
    return float(np.mean((np.asarray(a) - np.asarray(b)) ** 2))


def mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))


def r2(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ss_res = float(np.sum((a - b) ** 2))
    ss_tot = float(np.sum((a - np.mean(a)) ** 2))
    if ss_tot < 1e-12:
        return 0.0
    return 1.0 - ss_res / ss_tot


def _save(fig, base: str):
    for d in (OUTPUT, REPORT_PNG):
        fig.savefig(os.path.join(d, base + ".png"), dpi=140, bbox_inches="tight")
    plt.close(fig)


def exp_convergence(epochs: int = 250, lr: float = 0.05):
    seq = get_sequence(PRIMARY_SEQ, N_POINTS)
    out = train_net(seq, window=6, hidden=12, context=4, epochs=epochs, lr=lr)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        range(1, len(out["losses"]) + 1),
        out["losses"],
        color=COLOR,
        linewidth=1.4,
    )
    ax.set_xlabel("Эпоха")
    ax.set_ylabel("MSE (обучение)")
    ax.set_yscale("log")
    ax.set_title(f"Сходимость сети Элмана (arcsinh), ряд {PRIMARY_SEQ}")
    ax.grid(alpha=0.3)
    _save(fig, "convergence")
    row = {
        "arch": "elman",
        "act": "asinh",
        "mse": mse(out["preds"], out["actual"]),
        "mse_n": out["mse_n"],
        "mae": mae(out["preds"], out["actual"]),
        "r2": r2(out["preds"], out["actual"]),
        "final_loss": out["losses"][-1],
    }
    with open(os.path.join(OUTPUT, "convergence.json"), "w", encoding="utf-8") as f:
        json.dump(row, f, ensure_ascii=False, indent=2)
    print(f"[exp_convergence] loss {out['losses'][0]:.4f} -> {out['losses'][-1]:.4f}")
    return row


def _sweep(param, values, base_kw, seq_name=PRIMARY_SEQ, epochs=200, lr=0.05):
    seq = get_sequence(seq_name, N_POINTS)
    rows = []
    for v in values:
        kw = dict(base_kw)
        kw[param] = v
        out = train_net(seq, epochs=epochs, lr=lr, **kw)
        rows.append(
            {
                param: v,
                "mse": mse(out["preds"], out["actual"]),
                "mse_n": out["mse_n"],
                "final_loss": out["losses"][-1],
            }
        )
    return rows


def exp_windows(epochs=200, lr=0.05):
    values = [2, 4, 6, 8, 12]
    base = dict(window=6, hidden=12, context=4)
    rows = _sweep("window", values, base, epochs=epochs, lr=lr)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        [r["window"] for r in rows],
        [r["mse"] for r in rows],
        color=COLOR,
        marker="o",
        linewidth=1.5,
    )
    ax.set_xlabel("Размер окна (window)")
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Влияние размера окна (elman/asinh)")
    ax.grid(alpha=0.3)
    _save(fig, "window_sweep")
    with open(os.path.join(OUTPUT, "windows.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_windows] window sweep готов")
    return rows


def exp_context(epochs=200, lr=0.05):
    values = [1, 2, 4, 8]
    base = dict(window=6, hidden=12, context=4)
    rows = _sweep("context", values, base, epochs=epochs, lr=lr)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        [r["context"] for r in rows],
        [r["mse"] for r in rows],
        color=COLOR,
        marker="o",
        linewidth=1.5,
    )
    ax.set_xlabel("Контекстных нейронов (context_size)")
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Влияние размера контекста (elman/asinh)")
    ax.grid(alpha=0.3)
    _save(fig, "context_sweep")
    with open(os.path.join(OUTPUT, "context.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_context] context sweep готов")
    return rows


def exp_hidden(epochs=200, lr=0.05):
    values = [4, 8, 16, 32]
    base = dict(window=6, hidden=8, context=4)
    rows = _sweep("hidden", values, base, epochs=epochs, lr=lr)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        [r["hidden"] for r in rows],
        [r["mse"] for r in rows],
        color=COLOR,
        marker="o",
        linewidth=1.5,
    )
    ax.set_xlabel("Нейронов на скрытом слое (hidden_size)")
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Влияние размера скрытого слоя (elman/asinh)")
    ax.grid(alpha=0.3)
    _save(fig, "hidden_sweep")
    with open(os.path.join(OUTPUT, "hidden.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_hidden] hidden sweep готов")
    return rows


def exp_effector(epochs=250, lr=0.05):
    seq = get_sequence(PRIMARY_SEQ, N_POINTS)
    rows = []
    for linear_out in (True, False):
        out = train_net(
            seq, window=6, hidden=12, context=4, epochs=epochs, lr=lr,
            linear_out=linear_out,
        )
        rows.append(
            {
                "linear_out": linear_out,
                "mse": mse(out["preds"], out["actual"]),
                "mse_n": out["mse_n"],
                "final_loss": out["losses"][-1],
            }
        )
    fig, ax = plt.subplots(figsize=(7, 4.5))
    labels = ["линейный", "arcsinh"]
    ax.bar(
        range(2),
        [r["mse"] for r in rows],
        color=["#4c72b0", "#dd8452"],
    )
    ax.set_xticks(range(2))
    ax.set_xticklabels(labels)
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Эффект активации эффектора (elman/asinh)")
    ax.set_yscale("log")
    ax.grid(alpha=0.3, axis="y")
    _save(fig, "effector_linear")
    with open(os.path.join(OUTPUT, "effector.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_effector] effector сравнение готово")
    return rows


def exp_zero_context(epochs=250, lr=0.05):
    seq = get_sequence(PRIMARY_SEQ, N_POINTS)
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for zi, zero in enumerate((True, False)):
        ax = axes[zi]
        out = train_net(
            seq, window=6, hidden=12, context=4, epochs=epochs, lr=lr,
            zero_context=zero,
        )
        rows.append(
            {
                "zero_context": zero,
                "mse": mse(out["preds"], out["actual"]),
                "mse_n": out["mse_n"],
                "final_loss": out["losses"][-1],
            }
        )
        ax.plot(
            range(1, len(out["losses"]) + 1),
            out["losses"],
            color=COLOR,
            linewidth=1.3,
        )
        ax.set_title(f"zero_context = {zero}")
        ax.set_xlabel("Эпоха")
        ax.set_ylabel("MSE (обучение)")
        ax.set_yscale("log")
        ax.grid(alpha=0.3)
    fig.suptitle("Влияние зануления контекстных нейронов на каждой эпохе", fontsize=13)
    _save(fig, "zero_context")
    with open(os.path.join(OUTPUT, "zero_context.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_zero_context] zero_context сравнение готово")
    return rows


def exp_forecast(epochs=300, lr=0.05):
    window, hidden, context = 6, 16, 4
    demo_seqs = ["geometric_0.5", "harmonic", "periodic", "arithmetic", "fibonacci", "squares"]
    rows = []
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for si, sname in enumerate(demo_seqs):
        ax = axes[si // 3][si % 3]
        seq = get_sequence(sname, N_POINTS)
        out = train_net(seq, window, hidden, context, epochs, lr)
        mn = out["mse_n"]
        rows.append(
            {
                "seq": sname,
                "arch": "elman",
                "act": "asinh",
                "mse": mse(out["preds"], out["actual"]),
                "mse_n": mn,
                "mae": mae(out["preds"], out["actual"]),
                "r2": r2(out["preds"], out["actual"]) if np.isfinite(mn) else float("nan"),
            }
        )
        n_train = len(out["norm"]) - len(out["actual"])
        ax.plot(range(len(out["norm"])), out["norm"], color="#333333", label="ряд (норм.)")
        ax.plot(
            range(n_train, n_train + len(out["preds_n"])),
            out["preds_n"],
            color=COLOR,
            marker="o",
            linewidth=1.6,
            label="прогноз elman/asinh",
        )
        ax.axvline(n_train - 0.5, color="#999999", linestyle="--", linewidth=1)
        ax.set_title(f"{sname}  MSEn={mn:.4f}")
        ax.set_xlabel("Отсчёт")
        ax.set_ylabel("Значение (норм.)")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Многошаговый прогноз сетью Элмана (arcsinh)", fontsize=13)
    _save(fig, "forecast_multi")
    with open(os.path.join(OUTPUT, "forecast.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_forecast] многошаговый прогноз готов")
    return rows


def summary_table(epochs=300, lr=0.05):
    window, hidden, context = 6, 16, 4
    table = []
    for sname in SEQUENCES:
        seq = get_sequence(sname, N_POINTS)
        out = train_net(seq, window, hidden, context, epochs, lr)
        row = {
            "seq": sname,
            "arch": "elman",
            "act": "asinh",
            "mse_n": out["mse_n"],
            "mse": mse(out["preds"], out["actual"]),
            "mae": mae(out["preds"], out["actual"]),
            "r2": r2(out["preds"], out["actual"]),
        }
        table.append(row)
        print(f"  {sname:14s} MSEn={row['mse_n']:.6f}")
    with open(os.path.join(OUTPUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    return table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=250)
    ap.add_argument("--lr", type=float, default=0.05)
    ap.add_argument(
        "--exps",
        nargs="*",
        default=["conv", "window", "context", "hidden", "effector",
                 "zero", "forecast", "summary"],
    )
    args = ap.parse_args()

    print(f"Режим: {MODE} (вариант 2)")
    results = {"variant": 2, "mode": MODE}
    if "conv" in args.exps:
        results["convergence"] = exp_convergence(args.epochs, args.lr)
    if "window" in args.exps:
        results["windows"] = exp_windows(args.epochs, args.lr)
    if "context" in args.exps:
        results["context"] = exp_context(args.epochs, args.lr)
    if "hidden" in args.exps:
        results["hidden"] = exp_hidden(args.epochs, args.lr)
    if "effector" in args.exps:
        results["effector"] = exp_effector(args.epochs, args.lr)
    if "zero" in args.exps:
        results["zero_context"] = exp_zero_context(args.epochs, args.lr)
    if "forecast" in args.exps:
        results["forecast"] = exp_forecast(args.epochs + 50, args.lr)
    if "summary" in args.exps:
        print("[summary] сводка по всем рядам ...")
        results["summary"] = summary_table(args.epochs + 50, args.lr)

    with open(os.path.join(OUTPUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nГотово. Результаты в {OUTPUT}")


if __name__ == "__main__":
    main()
