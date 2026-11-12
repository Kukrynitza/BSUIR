#!/usr/bin/env python3
"""Generate three reproducible 256x256 RGB BMP samples for lab 3.

The samples deliberately differ in spatial entropy:
  * smooth   -- smooth gradients and low-frequency colour transitions;
  * contours -- large uniform regions separated by sharp edges;
  * texture  -- fine high-frequency texture and noise.

They are only starting data: any BMP of the same or larger size can be used.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 256
OUT = Path(__file__).resolve().parent / "samples"


def _save(name: str, rgb: np.ndarray) -> None:
    rgb = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    Image.fromarray(rgb, mode="RGB").save(OUT / name)


def make_smooth(size: int) -> np.ndarray:
    y, x = np.mgrid[0:size, 0:size]
    u = x / (size - 1)
    v = y / (size - 1)
    r = 128 + 110 * u + 10 * np.sin(2 * np.pi * v)
    g = 128 + 100 * v + 12 * np.sin(2 * np.pi * u + 0.7)
    b = 128 + 80 * (u + v) / 2 + 15 * np.sin(2 * np.pi * (u - v))
    return np.stack([r, g, b], axis=-1)


def make_contours(size: int) -> np.ndarray:
    y, x = np.mgrid[0:size, 0:size]
    img = np.zeros((size, size, 3), dtype=np.float64)
    img[:] = (235, 235, 230)

    # Large rectangles with hard edges.
    img[20:110, 20:130] = (40, 90, 200)
    img[40:170, 150:235] = (220, 70, 50)
    img[140:235, 30:115] = (30, 160, 90)

    # Circles and a diagonal stripe.
    for cx, cy, rad, colour in (
        (185, 70, 32, (250, 210, 40)),
        (75, 190, 26, (250, 250, 250)),
        (200, 195, 38, (120, 40, 180)),
    ):
        mask = (x - cx) ** 2 + (y - cy) ** 2 <= rad**2
        img[mask] = colour

    stripe = np.abs((x - 40) - (y - 110)) < 5
    img[stripe & (x < 145) & (y > 95)] = (20, 20, 20)
    return img


def make_texture(size: int, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size]

    base = (
        110
        + 45 * np.sin(0.55 * x + 0.35 * y)
        + 22 * np.sin(1.9 * x - 1.3 * y)
        + 18 * np.cos(0.17 * x * y / size)
    )
    noise = rng.normal(0.0, 12.0, size=(size, size))
    fine = 12 * np.sin(2 * np.pi * (x + y) / 4.0)

    common = base + noise + fine
    r = common + 18 * np.sin(0.9 * y)
    g = common + 10 * np.cos(0.7 * x)
    b = common - 12 * np.sin(0.5 * (x + y))
    return np.stack([r, g, b], axis=-1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _save("smooth.bmp", make_smooth(SIZE))
    _save("contours.bmp", make_contours(SIZE))
    _save("texture.bmp", make_texture(SIZE))
    print(f"samples written to {OUT}")


if __name__ == "__main__":
    main()
