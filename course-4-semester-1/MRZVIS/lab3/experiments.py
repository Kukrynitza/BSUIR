#!/usr/bin/env python3
"""Reproducible experiment suite for lab 3 (variant 2).

Produces JSON data in ``output/experiments.json`` and report-ready plots in
``mrzvis-report-3/png``.  The main series use non-overlapping 8x8 blocks so
that all parameter sweeps have the same number of blocks Q; a separate run
with 50% overlap demonstrates the effect of block overlap.
"""

from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
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

ROOT = Path(__file__).resolve().parent
REPORT_PNG = ROOT / "mrzvis-report-3" / "png"
OUTPUT = ROOT / "output"

IMAGES = ("smooth", "contours", "texture")
LABELS = {"smooth": "Плавные переходы", "contours": "Контуры", "texture": "Текстура"}
BLOCK = 8
STEP = 8
P_BASE = 16
EPOCHS = 80
SEED = 42
BETAS = (0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
P_VALUES = (6, 8, 10, 12, 16, 20)
COMMON_MSE_TARGET = 0.012

warnings.filterwarnings("ignore", category=RuntimeWarning)


def first_crossing(errors: list[float], eps: float) -> int | None:
    for i, value in enumerate(errors, start=1):
        if np.isfinite(value) and value < eps:
            return i
    return None


def run_case(
    image: str,
    *,
    p: int = P_BASE,
    beta: float = 1.0,
    step: int = STEP,
    epochs: int = EPOCHS,
    save_images: bool = False,
) -> dict:
    path = ROOT / "samples" / f"{image}.bmp"
    pixels = load_bmp(path)
    height, width, channels = pixels.shape
    vectors_raw, positions, channels = extract_blocks(
        pixels, BLOCK, BLOCK, step_h=step, step_w=step
    )
    q, n = vectors_raw.shape
    samples = normalize(vectors_raw)

    started = time.perf_counter()
    net = RecirculationNetwork(n=n, p=p, seed=SEED, lr_scale=beta)
    result = net.train(
        samples, max_epochs=epochs, eps=1e-12, shuffle=True, seed=SEED
    )
    train_time = time.perf_counter() - started

    compressed = net.encode(samples)
    restored_norm = net.decode(compressed)
    restored_pixels = denormalize(restored_norm)
    restored_image = vectors_to_image(
        restored_pixels,
        positions,
        BLOCK,
        BLOCK,
        height,
        width,
        channels,
    )

    mse_norm = float(np.mean((restored_norm - samples) ** 2))
    mse_pixels = float(np.mean((pixels - restored_image) ** 2))
    psnr = float("inf") if mse_pixels == 0 else float(
        10.0 * np.log10(255.0**2 / mse_pixels)
    )

    if save_images:
        save_bmp(OUTPUT / f"original_{image}.bmp", pixels)
        save_bmp(OUTPUT / f"restored_{image}.bmp", restored_image)
        _save_comparison(image, pixels, restored_image)

    finite = bool(np.isfinite(result.final_error))
    return {
        "image": image,
        "p": p,
        "beta": beta,
        "step": step,
        "Q": q,
        "n": n,
        "epochs_done": result.epochs_done,
        "QT": q * result.epochs_done,
        "final_error": result.final_error if finite else None,
        "errors": [float(e) if np.isfinite(e) else None for e in result.errors],
        "mse_norm": mse_norm if finite else None,
        "mse_pixels": mse_pixels if finite else None,
        "psnr_db": psnr if finite else None,
        "Z": compression_ratio(q, n, p),
        "K_bytes": byte_compression_ratio(q, n, p),
        "train_time_s": train_time,
        "finite": finite,
    }


def _save_comparison(image: str, original: np.ndarray, restored: np.ndarray) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    for ax, data, title in (
        (axes[0], original, "Исходное"),
        (axes[1], restored, "Восстановленное"),
    ):
        shown = np.clip(data / 255.0, 0.0, 1.0)
        if shown.shape[2] == 1:
            shown = shown[:, :, 0]
        ax.imshow(shown)
        ax.set_title(title)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(REPORT_PNG / f"compare_{image}.png", dpi=140)
    plt.close(fig)


def plot_family_a(rows: list[dict], eps_by_image: dict[str, float]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for image in IMAGES:
        part = sorted(
            (r for r in rows if r["image"] == image), key=lambda r: r["beta"]
        )
        xs = [r["beta"] for r in part]
        ys = [r["T"] if r["T"] is not None else EPOCHS + 5 for r in part]
        ax.plot(xs, ys, marker="o", markersize=4, label=LABELS[image])
    ax.axhline(EPOCHS + 5, color="0.6", linestyle="--", linewidth=1)
    ax.text(BETAS[0], EPOCHS + 7, "порог не достигнут", fontsize=8, color="0.35")
    ax.set_xscale("log")
    ax.set_xlabel(r"масштаб адаптивного шага $\beta$")
    ax.set_ylabel("число эпох $T$")
    ax.set_title(r"Семейство A: $T(\beta)$")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(REPORT_PNG / "family_a.png", dpi=140)
    plt.close(fig)


def plot_family_b(rows: list[dict]) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    for image in IMAGES:
        part = sorted(
            (r for r in rows if r["image"] == image), key=lambda r: r["K_bytes"]
        )
        ks = [r["K_bytes"] for r in part]
        ts = [r["T"] if r["T"] is not None else EPOCHS + 5 for r in part]
        es = [r["final_error"] for r in part]
        ax1.plot(ks, ts, marker="o", markersize=4, label=LABELS[image])
        ax2.plot(ks, es, marker="o", markersize=4, label=LABELS[image])
    ax1.axhline(EPOCHS + 5, color="0.6", linestyle="--", linewidth=1)
    ax1.set_xlabel("коэффициент сжатия $K$ (байты)")
    ax1.set_ylabel("число эпох $T$")
    ax1.set_title("Семейство B: $T(K)$")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.set_xlabel("коэффициент сжатия $K$ (байты)")
    ax2.set_ylabel(r"итоговая ошибка $E$")
    ax2.set_title("Семейство B: $E(K)$")
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(REPORT_PNG / "family_b.png", dpi=140)
    plt.close(fig)


def plot_family_c(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.4))
    xs = np.arange(len(IMAGES))
    vals = [next(r["T_ind"] for r in rows if r["image"] == image) for image in IMAGES]
    common = [
        next(r["T_common"] for r in rows if r["image"] == image) for image in IMAGES
    ]
    width = 0.36
    ax.bar(xs - width / 2, vals, width, label="индивидуальный порог")
    ax.bar(xs + width / 2, common, width, label="общая MSE 0,012")
    ax.set_xticks(xs)
    ax.set_xticklabels([LABELS[i] for i in IMAGES], fontsize=9)
    ax.set_ylabel("число эпох $T$")
    ax.set_title("Семейство C: зависимость от изображения")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(REPORT_PNG / "family_c.png", dpi=140)
    plt.close(fig)


def plot_family_d(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for image in IMAGES:
        part = sorted(
            (r for r in rows if r["image"] == image),
            key=lambda r: r["eps"],
            reverse=True,
        )
        xs = [r["eps"] for r in part]
        ys = [r["T"] if r["T"] is not None else EPOCHS + 5 for r in part]
        ax.plot(xs, ys, marker="o", markersize=4, label=LABELS[image])
    ax.axhline(EPOCHS + 5, color="0.6", linestyle="--", linewidth=1)
    ax.text(3.2, EPOCHS + 22, "порог не достигнут", fontsize=8, color="0.35")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(top=EPOCHS * 1.6)
    ax.set_xlabel(r"порог ошибки $\varepsilon$")
    ax.set_ylabel("число эпох $T$")
    ax.set_title(r"Семейство D: $T(\varepsilon)$")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(REPORT_PNG / "family_d.png", dpi=140)
    plt.close(fig)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    REPORT_PNG.mkdir(parents=True, exist_ok=True)

    print("[baseline] non-overlapping, p=16")
    baselines = {
        image: run_case(image, p=P_BASE, step=STEP, save_images=True)
        for image in IMAGES
    }
    for image, row in baselines.items():
        print(
            f"  {image:9s} E={row['final_error']:.3f} "
            f"mse_n={row['mse_norm']:.6f} Z={row['Z']:.2f} K={row['K_bytes']:.2f}"
        )

    # Thresholds are fixed from the baseline trajectory (epoch 10), so the
    # sweeps compare runs at the same requirement for each image.
    eps_by_image = {
        image: float(row["errors"][9]) for image, row in baselines.items()
    }
    print("[eps] " + ", ".join(f"{k}={v:.3f}" for k, v in eps_by_image.items()))

    print("[overlap] step=4 (50%)")
    overlap = {}
    for image in IMAGES:
        overlap[image] = run_case(image, p=P_BASE, step=4)
        base = baselines[image]
        print(
            f"  {image:9s} mse_n {overlap[image]['mse_norm']:.6f} "
            f"vs {base['mse_norm']:.6f}; K {overlap[image]['K_bytes']:.2f} "
            f"vs {base['K_bytes']:.2f}"
        )

    print("[family A] beta sweep")
    family_a = []
    for image in IMAGES:
        for beta in BETAS:
            row = run_case(image, p=P_BASE, beta=beta, step=STEP)
            row["T"] = first_crossing(row["errors"], eps_by_image[image])
            family_a.append(row)
            print(
                f"  {image:9s} beta={beta:<5} T={row['T']} "
                f"E={row['final_error']}"
            )
    plot_family_a(family_a, eps_by_image)

    print("[family B] p sweep")
    family_b = []
    for image in IMAGES:
        for p in P_VALUES:
            row = run_case(image, p=p, step=STEP)
            row["T"] = first_crossing(row["errors"], eps_by_image[image])
            family_b.append(row)
            print(
                f"  {image:9s} p={p:<3} K={row['K_bytes']:.3f} "
                f"T={row['T']} E={row['final_error']}"
            )
    plot_family_b(family_b)

    print("[family C] image type")
    family_c = []
    qn = baselines[IMAGES[0]]["Q"] * baselines[IMAGES[0]]["n"]
    eps_common = 0.5 * qn * COMMON_MSE_TARGET
    for image in IMAGES:
        row = baselines[image]
        family_c.append(
            {
                "image": image,
                "eps_individual": eps_by_image[image],
                "T_ind": first_crossing(row["errors"], eps_by_image[image]),
                "eps_common": eps_common,
                "T_common": first_crossing(row["errors"], eps_common),
                "final_error": row["final_error"],
                "mse_norm": row["mse_norm"],
                "K_bytes": row["K_bytes"],
            }
        )
    plot_family_c(family_c)

    print("[family D] eps sweep from baseline trajectory")
    family_d = []
    checkpoints = (1, 2, 3, 5, 10, 20, 40, EPOCHS)
    for image in IMAGES:
        row = baselines[image]
        grid = sorted(
            {
                float(row["errors"][min(k, len(row["errors"])) - 1])
                for k in checkpoints
                if row["errors"][min(k, len(row["errors"])) - 1] is not None
            },
            reverse=True,
        )
        for eps in grid:
            family_d.append(
                {
                    "image": image,
                    "eps": eps,
                    "T": first_crossing(row["errors"], eps),
                }
            )
    plot_family_d(family_d)

    payload = {
        "config": {
            "variant": 2,
            "block": BLOCK,
            "step": STEP,
            "p_base": P_BASE,
            "epochs": EPOCHS,
            "seed": SEED,
            "betas": list(BETAS),
            "p_values": list(P_VALUES),
            "common_mse_target": COMMON_MSE_TARGET,
        },
        "baselines": baselines,
        "eps_by_image": eps_by_image,
        "overlap": overlap,
        "family_a": family_a,
        "family_b": family_b,
        "family_c": family_c,
        "family_d": family_d,
    }
    (OUTPUT / "experiments.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"done: {OUTPUT / 'experiments.json'}")


if __name__ == "__main__":
    main()
