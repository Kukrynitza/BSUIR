from __future__ import annotations

import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from activations import ACTIVATIONS
from network import ARCHS, RecurrentNetwork
from sequences import (
    SEQUENCES,
    denormalize,
    get_sequence,
    make_windows,
    normalize,
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

STYLE = {
    "asinh": {"color": "#1f77b4", "marker": "o"},
    "tanh": {"color": "#d62728", "marker": "s"},
    "elu": {"color": "#2ca02c", "marker": "^"},
    "leaky_relu": {"color": "#ff7f0e", "marker": "D"},
    "linear": {"color": "#9467bd", "marker": "x"},
}
ARCH_COLOR = {
    "jordan": "#1f77b4",
    "elman": "#d62728",
    "jordan_elman": "#2ca02c",
    "rnn": "#ff7f0e",
    "lstm": "#9467bd",
    "gru": "#8c564b",
}


def split_seq(seq: np.ndarray):
    cut = int(len(seq) * TRAIN_FRACTION)
    return seq[:cut], seq[cut:]


def train_net(
    seq: np.ndarray,
    arch: str,
    act: str,
    window: int,
    hidden: int,
    context: int,
    epochs: int,
    lr: float,
    linear_out: bool = True,
    zero_context: bool = True,
    effector_init: float | None = None,
):
    norm, lo, hi = normalize(seq)
    train, test = split_seq(norm)
    X, y = make_windows(train, window)
    net = RecurrentNetwork(
        arch=arch,
        hidden_size=hidden,
        context_size=context,
        window=window,
        act=act,
        linear_out=linear_out,
        effector_init=effector_init,
        seed=SEED,
    )
    res = net.train(X, y, epochs=epochs, lr=lr, zero_context=zero_context)
    seed_window = norm[ len(norm) - len(test) - window : len(norm) - len(test) ]
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
        "norm": norm,
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


def exp_architectures(epochs: int = 250, lr: float = 0.05):
    seq = get_sequence(PRIMARY_SEQ, N_POINTS)
    window, hidden, context = 6, 12, 4
    table = []
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ai, arch in enumerate(ARCHS):
        ax = axes[ai // 3][ai % 3]
        for act in ACTIVATIONS[:4]:
            if arch in ("lstm", "gru") and act != "elu":
                continue
            out = train_net(seq, arch, act, window, hidden, context, epochs, lr)
            table.append(
                {
                    "arch": arch,
                    "act": act,
                    "mse": mse(out["preds"], out["actual"]),
                    "mse_n": out["mse_n"],
                    "mae": mae(out["preds"], out["actual"]),
                    "r2": r2(out["preds"], out["actual"]),
                    "final_loss": out["losses"][-1],
                }
            )
            st = STYLE[act]
            ax.plot(
                range(1, len(out["losses"]) + 1),
                out["losses"],
                color=st["color"],
                marker=st["marker"],
                markevery=max(1, len(out["losses"]) // 8),
                linewidth=1.2,
                label=act,
            )
        ax.set_title(f"{arch}")
        ax.set_xlabel("Эпоха")
        ax.set_ylabel("MSE (обучение)")
        ax.set_yscale("log")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(
        f"Сходимость обучения: 6 архитектур x 4 активации (ряд {PRIMARY_SEQ})",
        fontsize=13,
    )
    _save(fig, "arch_convergence")
    with open(os.path.join(OUTPUT, "architectures.json"), "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    print(f"[exp_architectures] {len(table)} комбинаций, см. arch_convergence.png")
    return table


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
                "final_loss": out["losses"][-1],
            }
        )
    return rows


def exp_windows(epochs=200, lr=0.05):
    values = [2, 4, 6, 8, 12]
    base = dict(arch="elman", act="asinh", window=6, hidden=12, context=4)
    rows = _sweep("window", values, base, epochs=epochs, lr=lr)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        [r["window"] for r in rows],
        [r["mse"] for r in rows],
        color=ARCH_COLOR["elman"],
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
    out_by_arch = {}
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for arch in ("jordan", "elman", "jordan_elman"):
        base = dict(arch=arch, act="asinh", window=6, hidden=12, context=4)
        rows = _sweep("context", values, base, epochs=epochs, lr=lr)
        out_by_arch[arch] = rows
        ax.plot(
            [r["context"] for r in rows],
            [r["mse"] for r in rows],
            color=ARCH_COLOR[arch],
            marker="o",
            linewidth=1.5,
            label=arch,
        )
    ax.set_xlabel("Контекстных нейронов (context_size)")
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Влияние размера контекста")
    ax.grid(alpha=0.3)
    ax.legend()
    _save(fig, "context_sweep")
    with open(os.path.join(OUTPUT, "context.json"), "w", encoding="utf-8") as f:
        json.dump(out_by_arch, f, ensure_ascii=False, indent=2)
    print("[exp_context] context sweep готов")
    return out_by_arch


def exp_hidden(epochs=200, lr=0.05):
    values = [4, 8, 16, 32]
    base = dict(arch="rnn", act="asinh", window=6, hidden=8, context=4)
    rows = _sweep("hidden", values, base, epochs=epochs, lr=lr)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        [r["hidden"] for r in rows],
        [r["mse"] for r in rows],
        color=ARCH_COLOR["rnn"],
        marker="o",
        linewidth=1.5,
    )
    ax.set_xlabel("Нейронов на скрытом слое (hidden_size)")
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Влияние размера скрытого слоя (rnn/asinh)")
    ax.grid(alpha=0.3)
    _save(fig, "hidden_sweep")
    with open(os.path.join(OUTPUT, "hidden.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_hidden] hidden sweep готов")
    return rows


def exp_effector(epochs=250, lr=0.05):
    seq = get_sequence(PRIMARY_SEQ, N_POINTS)
    window, hidden, context = 6, 12, 4
    rows = []
    for arch in ARCHS:
        for linear_out in (True, False):
            out = train_net(
                seq, arch, "asinh", window, hidden, context, epochs, lr,
                linear_out=linear_out,
            )
            rows.append(
                {
                    "arch": arch,
                    "linear_out": linear_out,
                    "mse": mse(out["preds"], out["actual"]),
                    "final_loss": out["losses"][-1],
                }
            )
    fig, ax = plt.subplots(figsize=(9, 4.5))
    archs = list(ARCHS)
    lin = [r["mse"] for r in rows if r["linear_out"]]
    nl = [r["mse"] for r in rows if not r["linear_out"]]
    xpos = np.arange(len(archs))
    ax.bar(xpos - 0.18, lin, width=0.36, label="линейный эффектор", color="#4c72b0")
    ax.bar(xpos + 0.18, nl, width=0.36, label="нелинейный эффектор", color="#dd8452")
    ax.set_xticks(xpos)
    ax.set_xticklabels(archs, rotation=15)
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Эффект линейной активации эффекторов")
    ax.set_yscale("log")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    _save(fig, "effector_linear")
    with open(os.path.join(OUTPUT, "effector.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_effector] effector сравнение готово")
    return rows


def exp_zero_context(epochs=250, lr=0.05):
    seq = get_sequence(PRIMARY_SEQ, N_POINTS)
    window, hidden, context = 6, 12, 4
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for zi, zero in enumerate((True, False)):
        ax = axes[zi]
        for arch in ("elman", "jordan", "jordan_elman"):
            out = train_net(
                seq, arch, "asinh", window, hidden, context, epochs, lr,
                zero_context=zero,
            )
            rows.append(
                {
                    "arch": arch,
                    "zero_context": zero,
                    "mse": mse(out["preds"], out["actual"]),
                    "final_loss": out["losses"][-1],
                }
            )
            ax.plot(
                range(1, len(out["losses"]) + 1),
                out["losses"],
                color=ARCH_COLOR[arch],
                linewidth=1.3,
                label=arch,
            )
        ax.set_title(f"zero_context = {zero}")
        ax.set_xlabel("Эпоха")
        ax.set_ylabel("MSE (обучение)")
        ax.set_yscale("log")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Влияние зануления контекстных нейронов на каждой эпохе", fontsize=13)
    _save(fig, "zero_context")
    with open(os.path.join(OUTPUT, "zero_context.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_zero_context] zero_context сравнение готово")
    return rows


def exp_effector_init(epochs=250, lr=0.05):
    seq = get_sequence(PRIMARY_SEQ, N_POINTS)
    window, hidden, context = 6, 12, 4
    inits = [None, 0.0, 0.1, 0.5]
    rows = []
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for arch in ("jordan", "jordan_elman"):
        mses = []
        for init in inits:
            out = train_net(
                seq, arch, "asinh", window, hidden, context, epochs, lr,
                effector_init=init,
            )
            m = mse(out["preds"], out["actual"])
            mses.append(m)
            rows.append({"arch": arch, "effector_init": init, "mse": m})
        ax.plot(
            range(len(inits)), mses, color=ARCH_COLOR[arch], marker="o",
            linewidth=1.5, label=arch,
        )
    ax.set_xticks(range(len(inits)))
    ax.set_xticklabels(["random", "0.0", "0.1", "0.5"])
    ax.set_ylabel("MSE прогноза")
    ax.set_title("Начальные веса эффекторов (jordan, jordan_elman)")
    ax.grid(alpha=0.3)
    ax.legend()
    _save(fig, "effector_init")
    with open(os.path.join(OUTPUT, "effector_init.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_effector_init] effector_init сравнение готово")
    return rows


def exp_forecast(epochs=300, lr=0.05):
    window, hidden, context = 6, 16, 4
    demo_seqs = ["geometric_0.5", "harmonic", "periodic", "arithmetic", "fibonacci", "squares"]
    rows = []
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for si, sname in enumerate(demo_seqs):
        ax = axes[si // 3][si % 3]
        seq = get_sequence(sname, N_POINTS)
        best = None
        for arch in ARCHS:
            act = "elu" if arch in ("lstm", "gru") else "asinh"
            out = train_net(seq, arch, act, window, hidden, context, epochs, lr)
            mn = out["mse_n"]
            mo = mse(out["preds"], out["actual"])
            rows.append(
                {
                    "seq": sname,
                    "arch": arch,
                    "act": act,
                    "mse": mo,
                    "mse_n": mn,
                    "mae": mae(out["preds"], out["actual"]),
                    "r2": r2(out["preds"], out["actual"]) if np.isfinite(mn) else float("nan"),
                }
            )
            if np.isfinite(mn) and (best is None or mn < best["mse_n"]):
                best = {"arch": arch, "act": act, "out": out, "mse_n": mn}
        if best is None:
            best = {"arch": "rnn", "act": "asinh", "out": train_net(seq, "rnn", "asinh", window, hidden, context, epochs, lr), "mse_n": float("nan")}
        out = best["out"]
        n_train = len(out["norm"]) - len(out["actual"])
        ax.plot(range(len(out["norm"])), out["norm"], color="#333333", label="ряд (норм.)")
        ax.plot(
            range(n_train, n_train + len(out["preds_n"])),
            out["preds_n"],
            color=ARCH_COLOR[best["arch"]],
            marker="o",
            linewidth=1.6,
            label=f"прогноз {best['arch']}/{best['act']}",
        )
        ax.axvline(n_train - 0.5, color="#999999", linestyle="--", linewidth=1)
        ax.set_title(f"{sname}  MSEn={best['mse_n']:.4f}")
        ax.set_xlabel("Отсчёт")
        ax.set_ylabel("Значение (норм.)")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Многомерный прогноз скользящим окном (лучшая архитектура на ряд)", fontsize=13)
    _save(fig, "forecast_multi")
    with open(os.path.join(OUTPUT, "forecast.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("[exp_forecast] многомерный прогноз готов")
    return rows


def summary_table(epochs=300, lr=0.05):
    window, hidden, context = 6, 16, 4
    table = []
    for sname in SEQUENCES:
        seq = get_sequence(sname, N_POINTS)
        best = None
        for arch in ARCHS:
            acts = ("elu",) if arch in ("lstm", "gru") else ACTIVATIONS[:4]
            for act in acts:
                out = train_net(seq, arch, act, window, hidden, context, epochs, lr)
                mn = out["mse_n"]
                mo = mse(out["preds"], out["actual"])
                if not np.isfinite(mn):
                    continue
                if best is None or mn < best["mse_n"]:
                    best = {"arch": arch, "act": act, "mse_n": mn, "mse": mo}
        if best is None:
            best = {"arch": "-", "act": "-", "mse_n": float("nan"), "mse": float("nan")}
        table.append({"seq": sname, **best})
        print(f"  {sname:14s} -> {best['arch']}/{best['act']}  MSEn={best['mse_n']:.4f}")
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
        default=["arch", "window", "context", "hidden", "effector",
                 "zero", "einit", "forecast", "summary"],
    )
    args = ap.parse_args()

    results = {}
    if "arch" in args.exps:
        results["architectures"] = exp_architectures(args.epochs, args.lr)
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
    if "einit" in args.exps:
        results["effector_init"] = exp_effector_init(args.epochs, args.lr)
    if "forecast" in args.exps:
        results["forecast"] = exp_forecast(args.epochs + 50, args.lr)
    if "summary" in args.exps:
        print("[summary] подбор лучшей архитектуры по всем рядам ...")
        results["summary"] = summary_table(args.epochs + 50, args.lr)

    with open(os.path.join(OUTPUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nГотово. Результаты в {OUTPUT}")


if __name__ == "__main__":
    main()
