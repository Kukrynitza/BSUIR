from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

C_MAX = 255.0


def load_bmp(path: str | Path) -> np.ndarray:
    image = Image.open(path)
    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")
    arr = np.asarray(image, dtype=np.float64)
    if arr.ndim == 2:
        arr = arr[:, :, None]
    return arr


def save_bmp(path: str | Path, pixels: np.ndarray) -> None:
    clipped = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    if clipped.shape[2] == 1:
        Image.fromarray(clipped[:, :, 0], mode="L").save(path)
    else:
        Image.fromarray(clipped, mode="RGB").save(path)


def normalize(pixels: np.ndarray) -> np.ndarray:
    return (2.0 * pixels / C_MAX) - 1.0


def denormalize(values: np.ndarray) -> np.ndarray:
    clipped = np.minimum(1.0, np.maximum(-1.0, values))
    return C_MAX * (clipped + 1.0) / 2.0


def extract_blocks(
    pixels: np.ndarray,
    block_h: int,
    block_w: int,
) -> tuple[np.ndarray, int, int, int]:
    height, width, channels = pixels.shape
    if block_h < 4 or block_w < 4:
        raise ValueError("r,m >= 4")
    if block_h > height or block_w > width:
        raise ValueError("block > image")

    rows = height // block_h
    cols = width // block_w
    if rows == 0 or cols == 0:
        raise ValueError("image too small")

    height_used = rows * block_h
    width_used = cols * block_w
    cropped = pixels[:height_used, :width_used]

    blocks = cropped.reshape(rows, block_h, cols, block_w, channels)
    blocks = blocks.transpose(0, 2, 1, 3, 4).reshape(-1, block_h, block_w, channels)

    vectors = blocks.reshape(blocks.shape[0], -1)
    return vectors, height_used, width_used, channels


def vectors_to_image(
    vectors: np.ndarray,
    block_h: int,
    block_w: int,
    rows: int,
    cols: int,
    channels: int,
) -> np.ndarray:
    blocks = vectors.reshape(-1, block_h, block_w, channels)
    grid = blocks.reshape(rows, cols, block_h, block_w, channels)
    image = grid.transpose(0, 2, 1, 3, 4).reshape(
        rows * block_h, cols * block_w, channels
    )
    return image


def compression_ratio(q: int, n: int, p: int) -> float:
    return (q * n) / ((n + q) * p)
