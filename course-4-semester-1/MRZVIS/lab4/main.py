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

from network import STATE_MODES, UPDATE_MODES, HopfieldNetwork, binarize
from patterns import (
    GRID,
    add_noise,
    get_pattern,
    grid_image,
    pattern_names,
    patterns_matrix,
    repeat_patterns,
)

NOISE_LEVELS = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
TRIALS = 30


@dataclass
class RunConfig:
    state: str
    update: str
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


def ask_choice(prompt: str, choices: tuple[str, ...], default: str) -> str:
    while True:
        raw = ask_str(f"{prompt} {'/'.join(choices)}", default).lower()
        if raw in choices:
            return raw
        print(f"Введите одно из: {'/'.join(choices)}")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = ask_str(f"{prompt} ({hint})", "y" if default else "n").lower()
    return raw in {"y", "yes", "д", "да", "1"}


def interactive_config() -> RunConfig:
    print("Лабораторная 4: сеть Хопфилда")
    print("Enter = значение по умолчанию\n")

    state = ask_choice("состояние (discrete/continuous)", STATE_MODES, "continuous")
    update = ask_choice("время (sync/async)", UPDATE_MODES, "async")
    delta = ask_float("дельта-проекция delta (0 = проекция)", default=0.0, min_value=0.0)
    gain = ask_float("gain (масштаб локального поля)", default=2.0, min_value=0.1)
    noise = ask_float("уровень шума для демо", default=0.2, min_value=0.0)
    max_iter = ask_int("max итераций", default=200, min_value=1)
    eps = ask_float("eps релаксации", default=1e-6, min_value=0.0)
    repeat_k = ask_int("кратные включения k", default=1, min_value=1)
    use_letters = ask_yes_no("буквы", default=True)
    use_digits = ask_yes_no("цифры", default=True)
    if not use_letters and not use_digits:
        print("Нужен хотя бы один набор, включаю буквы.")
        use_letters = True
    seed = ask_int("seed", default=42, min_value=0)

    return RunConfig(
        state=state,
        update=update,
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


def make_net(n: int, state: str, update: str, delta: float, gain: float) -> HopfieldNetwork:
    return HopfieldNetwork(n=n, state=state, update=update, delta=delta, gain=gain)


def train_net(
    X: np.ndarray, state: str, update: str, delta: float, gain: float, repeat_k: int
) -> HopfieldNetwork:
    net = make_net(X.shape[1], state, update, delta, gain)
    net.learn(repeat_patterns(X, repeat_k))
    return net


def experiment_energy_curves(
    X: np.ndarray, config: RunConfig, rng: np.random.Generator
) -> dict[str, dict[str, list[float]]]:
    x0 = add_noise(X[0], 0.25, rng)
    curves: dict[str, dict[str, list[float]]] = {}
    for state in STATE_MODES:
        for update in UPDATE_MODES:
            net = train_net(X, state, update, config.delta, config.gain, config.repeat_k)
            res = net.relax(x0, max_iter=config.max_iter, eps=config.eps, seed=config.seed)
            key = f"{state}/{update}"
            curves[key] = {
                "energies": res.energies,
                "deltas": res.deltas,
                "iterations": float(res.iterations),
                "converged": res.converged,
                "cycle": res.cycle,
            }
            print(
                f"  {key}: итер={res.iterations} "
                f"релакс={res.converged} цикл={res.cycle}"
            )
    return curves


def experiment_noise_sweep(
    X: np.ndarray, config: RunConfig, rng: np.random.Generator
) -> dict[str, dict[str, list[float]]]:
    results: dict[str, dict[str, list[float]]] = {}
    for state in STATE_MODES:
        for update in UPDATE_MODES:
            net = train_net(X, state, update, config.delta, config.gain, config.repeat_k)
            key = f"{state}/{update}"
            rates: list[float] = []
            iters: list[float] = []
            for p in NOISE_LEVELS:
                success = 0
                iter_sum = 0
                for t in range(TRIALS):
                    idx = int(rng.integers(0, X.shape[0]))
                    x0 = add_noise(X[idx], p, rng)
                    res, guessed, _ = net.recognize(
                        x0, max_iter=config.max_iter, eps=config.eps, seed=config.seed + t
                    )
                    success += int(guessed == idx)
                    iter_sum += res.iterations
                rates.append(success / TRIALS)
                iters.append(iter_sum / TRIALS)
            results[key] = {"noise": list(NOISE_LEVELS), "rates": rates, "iters": iters}
            print(f"  {key}: готово")
    return results


def experiment_capacity(
    X: np.ndarray, config: RunConfig, rng: np.random.Generator, noise: float = 0.2
) -> dict[str, dict[str, list[float]]]:
    results: dict[str, dict[str, list[float]]] = {}
    max_q = X.shape[0]
    q_values = list(range(2, max_q + 1))
    for state in STATE_MODES:
        for update in UPDATE_MODES:
            key = f"{state}/{update}"
            rates: list[float] = []
            for q in q_values:
                net = train_net(X[:q], state, update, config.delta, config.gain, config.repeat_k)
                success = 0
                trials = min(TRIALS, 3 * q)
                for t in range(trials):
                    idx = int(rng.integers(0, q))
                    x0 = add_noise(X[idx], noise, rng)
                    _, guessed, _ = net.recognize(
                        x0, max_iter=config.max_iter, eps=config.eps, seed=config.seed + t
                    )
                    success += int(guessed == idx)
                rates.append(success / trials)
            results[key] = {"q": q_values, "rates": rates}
            print(f"  {key}: готово")
    return results


def save_visual_grid(
    X: np.ndarray,
    names: list[str],
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
            res, _, _ = net.recognize(
                x0, max_iter=config.max_iter, eps=config.eps, seed=config.seed
            )
            restored = grid_image(binarize(res.state))
            img = Image.fromarray(restored).resize((cell, cell), Image.NEAREST)
            x = (1 + c) * cell
            canvas[r * cell : (r + 1) * cell, x : x + cell] = np.asarray(img)
    Image.fromarray(canvas).save(path)


def plot_energy_curves(
    curves: dict[str, dict[str, list[float]]], path: Path
) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    for key, data in curves.items():
        e = data["energies"]
        ax1.plot(range(len(e)), e, linewidth=1.4, label=key)
        d = data["deltas"][1:]
        ax2.semilogy(range(1, len(data["deltas"])), np.maximum(d, 1e-16), linewidth=1.4, label=key)
    ax1.set_xlabel("iteration")
    ax1.set_ylabel("E")
    ax1.set_title("Energy")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.set_xlabel("iteration")
    ax2.set_ylabel("max |dx|")
    ax2.set_title("State change")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_noise_sweep(results: dict[str, dict[str, list[float]]], path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    for key, data in results.items():
        ax1.plot(data["noise"], data["rates"], marker="o", markersize=3, label=key)
        ax2.plot(data["noise"], data["iters"], marker="o", markersize=3, label=key)
    ax1.set_xlabel("noise p")
    ax1.set_ylabel("success rate")
    ax1.set_title(f"Recognition vs noise ({TRIALS} trials)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.set_xlabel("noise p")
    ax2.set_ylabel("iterations")
    ax2.set_title("Relaxation iterations vs noise")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_capacity(results: dict[str, dict[str, list[float]]], path: Path) -> None:
    fig = plt.figure(figsize=(8, 4.5))
    for key, data in results.items():
        plt.plot(data["q"], data["rates"], marker="o", markersize=3, label=key)
    plt.xlabel("stored patterns Q")
    plt.ylabel("success rate")
    plt.title("Capacity (noise = 0.2)")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
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
    print(f"режимы: {', '.join(f'{s}/{u}' for s in STATE_MODES for u in UPDATE_MODES)}")

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
    demo_net = train_net(X, config.state, config.update, config.delta, config.gain, config.repeat_k)
    save_visual_grid(
        X, names, demo_net, config, rng, out_dir / "visual_grid.png"
    )

    _, guessed, mm = demo_net.recognize(
        add_noise(X[0], config.noise, rng),
        max_iter=config.max_iter,
        eps=config.eps,
        seed=config.seed,
    )
    print(f"демо: {names[0]} шум={config.noise} -> {names[guessed]} (ошибок {mm})")

    meta = {
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
        "energy_curves": {
            k: {
                "iterations": v["iterations"],
                "converged": v["converged"],
                "cycle": v["cycle"],
            }
            for k, v in curves.items()
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
