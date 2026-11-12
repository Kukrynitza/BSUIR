#!/usr/bin/env python3

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from image_processing import (
    byte_compression_ratio,
    compression_ratio,
    denormalize,
    extract_blocks,
    load_bmp,
    normalize,
    save_bmp,
    vectors_to_image,
)
from network import RecirculationNetwork


@dataclass
class RunConfig:
    image: Path
    block_h: int
    block_w: int
    step_h: int
    step_w: int
    hidden: int
    epochs: int
    eps: float
    seed: int
    out_dir: Path
    shuffle: bool
    lr_scale: float = 1.0


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
    print("Вариант 2: адаптивный коэффициент обучения, ненормированные веса")
    print("Enter = по умолчанию\n")

    image = Path(ask_str("BMP", "samples/test.bmp"))
    while not image.is_file():
        print("Файл не найден.")
        image = Path(ask_str("BMP"))

    block_h = ask_int("r", default=16, min_value=4)
    block_w = ask_int("m", default=16, min_value=4)
    step_h = ask_int("шаг по вертикали sh", default=block_h, min_value=1)
    step_w = ask_int("шаг по горизонтали sw", default=block_w, min_value=1)
    hidden = ask_int("p", default=48, min_value=1)

    epochs = ask_int("эпохи", default=200, min_value=1)
    eps = ask_float("eps", default=1e-2)
    beta = ask_float("масштаб адаптивного шага beta", 1.0)
    shuffle = ask_yes_no("shuffle", default=True)
    seed = ask_int("seed", default=42, min_value=0)

    return RunConfig(
        image=image,
        block_h=block_h,
        block_w=block_w,
        step_h=step_h,
        step_w=step_w,
        hidden=hidden,
        epochs=epochs,
        eps=eps,
        seed=seed,
        out_dir=Path("output"),
        shuffle=shuffle,
        lr_scale=beta,
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

    started = time.perf_counter()
    vectors_raw, positions, channels = extract_blocks(
        pixels,
        config.block_h,
        config.block_w,
        step_h=config.step_h,
        step_w=config.step_w,
    )
    q, n = vectors_raw.shape
    p = config.hidden

    z = compression_ratio(q, n, p)
    k_bytes = byte_compression_ratio(q, n, p)
    if z <= 1:
        print(f"Z={z:.4f} <= 1, уменьшите p")
    if k_bytes <= 1:
        print(f"K(byte)={k_bytes:.4f} <= 1, уменьшите p или перекрытие")

    samples = normalize(vectors_raw)
    print(f"{config.block_h}x{config.block_w} step={config.step_h}x{config.step_w} "
          f"Q={q} n={n} p={p} Z={z:.4f} K={k_bytes:.4f}")
    print("режим: адаптивный шаг, ненормированные веса")
    print("train...")

    net = RecirculationNetwork(
        n=n,
        p=p,
        seed=config.seed,
        lr_scale=config.lr_scale,
    )
    train_start = time.perf_counter()
    result = net.train(
        samples,
        max_epochs=config.epochs,
        eps=config.eps,
        shuffle=config.shuffle,
        seed=config.seed,
    )
    train_time = time.perf_counter() - train_start

    compressed = net.encode(samples)
    restored_norm = net.decode(compressed)
    restored_pixels = denormalize(restored_norm)

    assemble_start = time.perf_counter()
    restored_image = vectors_to_image(
        restored_pixels,
        positions,
        config.block_h,
        config.block_w,
        height,
        width,
        channels,
    )
    assemble_time = time.perf_counter() - assemble_start

    save_bmp(out_dir / "original_crop.bmp", pixels)
    save_bmp(out_dir / "restored.bmp", restored_image)

    plot_error_curve(
        result.errors,
        out_dir / "error_curve.png",
        title="E (адаптивный шаг, ненормированные веса)",
    )

    mse_norm = float(np.mean((restored_norm - samples) ** 2))
    mse_pixels = float(np.mean((pixels - restored_image) ** 2))
    psnr = float("inf") if mse_pixels == 0 else float(
        10.0 * np.log10(255.0**2 / mse_pixels)
    )

    meta = {
        "image": str(config.image.resolve()),
        "variant": 2,
        "learning_rate": "adaptive 1/(||X||^2+||Y||^2), scaled by beta",
        "lr_scale": config.lr_scale,
        "normalize_weights": False,
        "block_h": config.block_h,
        "block_w": config.block_w,
        "step_h": config.step_h,
        "step_w": config.step_w,
        "channels": channels,
        "Q": q,
        "n": n,
        "p": p,
        "Z": z,
        "K_bytes": k_bytes,
        "epochs_done": result.epochs_done,
        "QT": q * result.epochs_done,
        "final_error_E": result.final_error,
        "stopped_by_eps": result.stopped_by_eps,
        "mse_norm": mse_norm,
        "pixel_mse": mse_pixels,
        "psnr_db": psnr,
        "train_time_s": train_time,
        "assemble_time_s": assemble_time,
        "total_time_s": time.perf_counter() - started,
        "seed": config.seed,
    }
    (out_dir / "metrics.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    np.save(out_dir / "compressed.npy", compressed)
    np.save(out_dir / "W.npy", net.W)
    np.save(out_dir / "Wp.npy", net.Wp)

    print(
        f"epochs={result.epochs_done} E={result.final_error:.6f} "
        f"mse={mse_pixels:.4f} psnr={psnr:.2f} Z={z:.4f} K={k_bytes:.4f}"
    )
    print(f"out: {out_dir.resolve()}")
    return 0


def main() -> int:
    return run(interactive_config())


if __name__ == "__main__":
    raise SystemExit(main())
