#!/usr/bin/env python3

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from image_processing import (
    compression_ratio,
    denormalize,
    extract_blocks,
    load_bmp,
    normalize,
    save_bmp,
    vectors_to_image,
)
from network import ADAPTIVE, NORMALIZE_WEIGHTS, RecirculationNetwork


@dataclass
class RunConfig:
    image: Path
    block_h: int
    block_w: int
    hidden: int
    alpha: float
    epochs: int
    eps: float
    seed: int
    out_dir: Path
    shuffle: bool


def mode_description() -> str:
    rate = "adaptive" if ADAPTIVE else "constant"
    weights = "norm" if NORMALIZE_WEIGHTS else "raw"
    return f"{rate}, {weights}"


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


def ask_float(prompt: str, default: float) -> float:
    while True:
        raw = ask_str(prompt, str(default))
        try:
            return float(raw.replace(",", "."))
        except ValueError:
            print("Нужно число.")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = ask_str(f"{prompt} ({hint})", "y" if default else "n").lower()
    return raw in {"y", "yes", "д", "да", "1"}


def interactive_config() -> RunConfig:
    print(f"Режим: {mode_description()}")
    print("Enter = по умолчанию\n")

    image = Path(ask_str("BMP", "samples/test.bmp"))
    while not image.is_file():
        print("Файл не найден.")
        image = Path(ask_str("BMP"))

    block_h = ask_int("r", default=8, min_value=4)
    block_w = ask_int("m", default=8, min_value=4)
    hidden = ask_int("p", default=32, min_value=1)

    alpha = 0.01
    if not ADAPTIVE:
        alpha = ask_float("alpha", default=0.01)

    epochs = ask_int("эпохи", default=200, min_value=1)
    eps = ask_float("eps", default=1e-2)
    shuffle = ask_yes_no("shuffle", default=True)
    seed = ask_int("seed", default=42, min_value=0)

    return RunConfig(
        image=image,
        block_h=block_h,
        block_w=block_w,
        hidden=hidden,
        alpha=alpha,
        epochs=epochs,
        eps=eps,
        seed=seed,
        out_dir=Path("output"),
        shuffle=shuffle,
    )


def plot_error_curve(errors: list[float], path: Path, title: str) -> None:
    plt.figure(figsize=(8, 4.5))
    plt.plot(range(1, len(errors) + 1), errors, linewidth=1.5)
    plt.xlabel("epoch")
    plt.ylabel("E")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def run(config: RunConfig) -> int:
    out_dir = config.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    pixels = load_bmp(config.image)
    height, width, channels = pixels.shape
    print(f"\nimg {width}x{height} c={channels}")

    vectors_raw, h_used, w_used, channels = extract_blocks(
        pixels, config.block_h, config.block_w
    )
    rows = h_used // config.block_h
    cols = w_used // config.block_w
    q, n = vectors_raw.shape
    p = config.hidden

    z = compression_ratio(q, n, p)
    if z <= 1:
        print(f"Z={z:.4f} <= 1, уменьши p")

    samples = normalize(vectors_raw)
    print(f"{config.block_h}x{config.block_w} Q={q} n={n} p={p} Z={z:.4f}")
    print(f"режим: {mode_description()}")
    print("train...")

    net = RecirculationNetwork(
        n=n,
        p=p,
        alpha=config.alpha,
        seed=config.seed,
    )
    result = net.train(
        samples,
        max_epochs=config.epochs,
        eps=config.eps,
        shuffle=config.shuffle,
        seed=config.seed,
    )

    compressed = net.encode(samples)
    restored_norm = net.decode(compressed)
    restored_pixels = denormalize(restored_norm)
    restored_image = vectors_to_image(
        restored_pixels,
        config.block_h,
        config.block_w,
        rows,
        cols,
        channels,
    )

    original_crop = pixels[:h_used, :w_used]
    save_bmp(out_dir / "original_crop.bmp", original_crop)
    save_bmp(out_dir / "restored.bmp", restored_image)

    plot_error_curve(
        result.errors,
        out_dir / "error_curve.png",
        title=f"E ({mode_description()})",
    )

    mse_pixels = float(np.mean((original_crop - restored_image) ** 2))
    meta = {
        "image": str(config.image.resolve()),
        "mode_description": mode_description(),
        "adaptive": ADAPTIVE,
        "normalize_weights": NORMALIZE_WEIGHTS,
        "block_h": config.block_h,
        "block_w": config.block_w,
        "channels": channels,
        "Q": q,
        "n": n,
        "p": p,
        "Z": z,
        "alpha": config.alpha if not ADAPTIVE else "adaptive 1/(||X||^2+||Y||^2)",
        "epochs_done": result.epochs_done,
        "final_error_E": result.final_error,
        "stopped_by_eps": result.stopped_by_eps,
        "pixel_mse": mse_pixels,
        "seed": config.seed,
    }
    (out_dir / "metrics.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    np.save(out_dir / "compressed.npy", compressed)
    np.save(out_dir / "W.npy", net.W)
    np.save(out_dir / "Wp.npy", net.Wp)

    print(
        f"epochs={result.epochs_done} E={result.final_error:.6f} "
        f"mse={mse_pixels:.4f}"
    )
    print(f"out: {out_dir.resolve()}")
    return 0


def main() -> int:
    return run(interactive_config())


if __name__ == "__main__":
    raise SystemExit(main())
