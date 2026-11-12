#!/usr/bin/env python3

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from network import HopfieldNetwork, binarize
from patterns import (
    GRID,
    add_noise,
    grid_image,
    pattern_names,
    patterns_matrix,
    repeat_patterns,
)

NOISE_LEVELS = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
TRIALS = 30


@dataclass
class RunConfig:
    delta: float
    gain: float
    noise: float
    max_iter: int
    eps: float
    seed: int
    repeat_k: int
    use_letters: bool
    use_digits: bool
    out_dir: Path


def ask_str(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw:
            return raw
        if default is not None:
            return default
        print("Пусто.")


def ask_int(prompt: str, default: int | None = None, min_value: int | None = None) -> int:
    while True:
        raw = ask_str(prompt, None if default is None else str(default))
        try:
            value = int(raw)
        except ValueError:
            print("Нужно целое.")
            continue
        if min_value is not None and value < min_value:
            print(f"Минимум {min_value}.")
            continue
        return value


def ask_float(prompt: str, default: float, min_value: float | None = None) -> float:
    while True:
        raw = ask_str(prompt, str(default))
        try:
            value = float(raw.replace(",", "."))
        except ValueError:
            print("Нужно число.")
            continue
        if min_value is not None and value < min_value:
            print(f"Минимум {min_value}.")
            continue
        return value


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = ask_str(f"{prompt} ({hint})", "y" if default else "n").lower()
    return raw in {"y", "yes", "д", "да", "1"}


def interactive_config() -> RunConfig:
    print("Лабораторная 4: сеть Хопфилда")
    print("Вариант 2: непрерывное состояние, синхронный режим")
    print("Enter = значение по умолчанию\n")

    delta = ask_float("дельта-проекция delta (0 = проекция)", default=0.0, min_value=0.0)
    gain = ask_float("gain (масштаб локального поля)", default=2.0, min_value=0.1)
    noise = ask_float("уровень шума для демо", default=0.2, min_value=0.0)
    max_iter = ask_int("max итераций", default=200, min_value=1)
    eps = ask_float("eps релаксации", default=1e-6, min_value=0.0)
    repeat_k = ask_int("кратные включения k", default=1, min_value=1)
    if repeat_k > 1 and delta == 0.0:
        print(
            "Примечание: при чистом проекционном правиле (delta=0) точные "
            "дубликаты эталонов не меняют W. Для влияния повторов задайте delta > 0."
        )
    use_letters = ask_yes_no("буквы", default=True)
    use_digits = ask_yes_no("цифры", default=True)
    if not use_letters and not use_digits:
        print("Нужен хотя бы один набор, включаю буквы.")
        use_letters = True
    seed = ask_int("seed", default=42, min_value=0)

    return RunConfig(
        delta=delta,
        gain=gain,
        noise=noise,
        max_iter=max_iter,
        eps=eps,
        seed=seed,
        repeat_k=repeat_k,
        use_letters=use_letters,
        use_digits=use_digits,
        out_dir=Path("output"),
    )


def make_net(n: int, delta: float, gain: float) -> HopfieldNetwork:
    return HopfieldNetwork(n=n, delta=delta, gain=gain)


def train_net(X: np.ndarray, delta: float, gain: float, repeat_k: int) -> HopfieldNetwork:
    net = make_net(X.shape[1], delta, gain)
    net.learn(repeat_patterns(X, repeat_k), prototypes=X)
    return net


def experiment_energy_curves(
    X: np.ndarray, config: RunConfig, rng: np.random.Generator
) -> dict[str, object]:
    x0 = add_noise(X[0], 0.25, rng)
    net = train_net(X, config.delta, config.gain, config.repeat_k)
    res = net.relax(x0, max_iter=config.max_iter, eps=config.eps)
    print(f"  итер={res.iterations} релакс={res.converged} цикл={res.cycle}")
    return {
        "energies": res.energies,
        "deltas": res.deltas,
        "iterations": float(res.iterations),
        "converged": res.converged,
        "cycle": res.cycle,
    }


def experiment_noise_sweep(
    X: np.ndarray, config: RunConfig, rng: np.random.Generator
) -> dict[str, list[float]]:
    net = train_net(X, config.delta, config.gain, config.repeat_k)
    rates: list[float] = []
    iters: list[float] = []
    for p in NOISE_LEVELS:
        success = 0
        iter_sum = 0
        for t in range(TRIALS):
            idx = int(rng.integers(0, X.shape[0]))
            x0 = add_noise(X[idx], p, rng)
            res, guessed, _ = net.recognize(x0, max_iter=config.max_iter, eps=config.eps)
            success += int(guessed == idx)
            iter_sum += res.iterations
        rates.append(success / TRIALS)
        iters.append(iter_sum / TRIALS)
    print("  готово")
    return {"noise": list(NOISE_LEVELS), "rates": rates, "iters": iters}


def experiment_capacity(
    X: np.ndarray, config: RunConfig, rng: np.random.Generator, noise: float = 0.2
) -> dict[str, list[float]]:
    max_q = X.shape[0]
    q_values = list(range(2, max_q + 1))
    rates: list[float] = []
    for q in q_values:
        net = train_net(X[:q], config.delta, config.gain, config.repeat_k)
        success = 0
        trials = min(TRIALS, 3 * q)
        for t in range(trials):
            idx = int(rng.integers(0, q))
            x0 = add_noise(X[idx], noise, rng)
            _, guessed, _ = net.recognize(x0, max_iter=config.max_iter, eps=config.eps)
            success += int(guessed == idx)
        rates.append(success / trials)
    print("  готово")
    return {"q": q_values, "rates": rates}


def save_visual_grid(
    X: np.ndarray,
    net: HopfieldNetwork,
    config: RunConfig,
    rng: np.random.Generator,
    path: Path,
) -> None:
    noise_levels = (0.1, 0.2, 0.3, 0.4)
    cell = GRID * 6
    cols = 2 + len(noise_levels)
    rows = min(6, X.shape[0])
    canvas = np.full((rows * cell, cols * cell), 255, dtype=np.uint8)
    for r in range(rows):
        orig = grid_image(X[r])
        img = Image.fromarray(orig).resize((cell, cell), Image.NEAREST)
        canvas[r * cell : (r + 1) * cell, 0:cell] = np.asarray(img)
        for c, p in enumerate(noise_levels):
            x0 = add_noise(X[r], p, rng)
            res, _, _ = net.recognize(x0, max_iter=config.max_iter, eps=config.eps)
            restored = grid_image(binarize(res.state))
            img = Image.fromarray(restored).resize((cell, cell), Image.NEAREST)
            x = (1 + c) * cell
            canvas[r * cell : (r + 1) * cell, x : x + cell] = np.asarray(img)
    Image.fromarray(canvas).save(path)


def plot_energy_curves(curve: dict[str, object], path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    e = curve["energies"]
    ax1.plot(range(len(e)), e, linewidth=1.4, color="C0")
    d = curve["deltas"][1:]
    ax2.semilogy(range(1, len(curve["deltas"])), np.maximum(d, 1e-16), linewidth=1.4, color="C0")
    ax1.set_xlabel("iteration")
    ax1.set_ylabel("E")
    ax1.set_title("Energy")
    ax1.grid(True, alpha=0.3)
    ax2.set_xlabel("iteration")
    ax2.set_ylabel("max |dx|")
    ax2.set_title("State change")
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_noise_sweep(results: dict[str, list[float]], path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.plot(results["noise"], results["rates"], marker="o", markersize=3, color="C0")
    ax2.plot(results["noise"], results["iters"], marker="o", markersize=3, color="C0")
    ax1.set_xlabel("noise p")
    ax1.set_ylabel("success rate")
    ax1.set_title(f"Recognition vs noise ({TRIALS} trials)")
    ax1.grid(True, alpha=0.3)
    ax2.set_xlabel("noise p")
    ax2.set_ylabel("iterations")
    ax2.set_title("Relaxation iterations vs noise")
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_capacity(results: dict[str, list[float]], path: Path) -> None:
    fig = plt.figure(figsize=(8, 4.5))
    plt.plot(results["q"], results["rates"], marker="o", markersize=3, color="C0")
    plt.xlabel("stored patterns Q")
    plt.ylabel("success rate")
    plt.title("Capacity (noise = 0.2)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


def run(config: RunConfig) -> int:
    out_dir = config.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    names = pattern_names(config.use_letters, config.use_digits)
    X = patterns_matrix(names)
    n = X.shape[1]
    rng = np.random.default_rng(config.seed)

    print(f"\nэталонов Q={X.shape[0]} n={n} k={config.repeat_k} delta={config.delta}")
    print("режим: continuous/sync (вариант 2)")

    print("\n1) энергия / релаксация...")
    curves = experiment_energy_curves(X, config, rng)
    plot_energy_curves(curves, out_dir / "energy_curves.png")

    print("\n2) распознавание vs шум...")
    sweep = experiment_noise_sweep(X, config, rng)
    plot_noise_sweep(sweep, out_dir / "noise_sweep.png")

    print("\n3) ёмкость...")
    capacity = experiment_capacity(X, config, rng)
    plot_capacity(capacity, out_dir / "capacity.png")

    print("\n4) визуальная сетка...")
    demo_net = train_net(X, config.delta, config.gain, config.repeat_k)
    save_visual_grid(X, demo_net, config, rng, out_dir / "visual_grid.png")

    _, guessed, mm = demo_net.recognize(
        add_noise(X[0], config.noise, rng),
        max_iter=config.max_iter,
        eps=config.eps,
    )
    print(f"демо: {names[0]} шум={config.noise} -> {names[guessed]} (ошибок {mm})")

    meta = {
        "variant": 2,
        "mode": "continuous/sync",
        "Q": int(X.shape[0]),
        "n": n,
        "names": names,
        "delta": config.delta,
        "gain": config.gain,
        "repeat_k": config.repeat_k,
        "max_iter": config.max_iter,
        "eps": config.eps,
        "seed": config.seed,
        "noise_levels": list(NOISE_LEVELS),
        "trials": TRIALS,
        "energy_curve": {
            "iterations": curves["iterations"],
            "converged": curves["converged"],
            "cycle": curves["cycle"],
        },
        "noise_sweep": sweep,
        "capacity": capacity,
        "demo": {"pattern": names[0], "noise": config.noise, "guessed": names[guessed]},
    }
    (out_dir / "metrics.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    np.save(out_dir / "W_demo.npy", demo_net.W)
    print(f"\nout: {out_dir.resolve()}")
    return 0


def main() -> int:
    return run(interactive_config())


if __name__ == "__main__":
    raise SystemExit(main())
