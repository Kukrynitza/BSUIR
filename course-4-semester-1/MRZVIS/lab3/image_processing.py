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


def block_positions(
    height: int,
    width: int,
    block_h: int,
    block_w: int,
    step_h: int | None = None,
    step_w: int | None = None,
) -> list[tuple[int, int]]:
    """Return block origins covering the whole image without crossing its border.

    The last origin on each axis is shifted to ``size - block`` so that the
    remainder of the image is covered even when the step does not divide the
    image size.  This adds a partially overlapping edge block, as required by
    the lab manual (blocks must cover the image completely).
    """
    if block_h < 1 or block_w < 1:
        raise ValueError("block size must be positive")
    if block_h > height or block_w > width:
        raise ValueError("block is larger than the image")

    step_h = block_h if step_h is None else step_h
    step_w = block_w if step_w is None else step_w
    if not 1 <= step_h <= block_h:
        raise ValueError("step_h must satisfy 1 <= step_h <= block_h")
    if not 1 <= step_w <= block_w:
        raise ValueError("step_w must satisfy 1 <= step_w <= block_w")

    ys = list(range(0, height - block_h + 1, step_h))
    xs = list(range(0, width - block_w + 1, step_w))
    if ys[-1] != height - block_h:
        ys.append(height - block_h)
    if xs[-1] != width - block_w:
        xs.append(width - block_w)
    return [(y, x) for y in ys for x in xs]


def extract_blocks(
    pixels: np.ndarray,
    block_h: int,
    block_w: int,
    step_h: int | None = None,
    step_w: int | None = None,
) -> tuple[np.ndarray, list[tuple[int, int]], int]:
    """Cut ``pixels`` into blocks and flatten every block into a row vector.

    Returns ``(vectors, positions, channels)`` where ``vectors`` has shape
    ``(Q, block_h * block_w * channels)`` and ``positions`` stores the
    top-left corner of every block in the original image.
    """
    height, width, channels = pixels.shape
    positions = block_positions(
        height, width, block_h, block_w, step_h=step_h, step_w=step_w
    )
    vectors = np.empty(
        (len(positions), block_h * block_w * channels), dtype=np.float64
    )
    for i, (y, x) in enumerate(positions):
        block = pixels[y : y + block_h, x : x + block_w, :]
        vectors[i] = block.reshape(-1)
    return vectors, positions, channels


def vectors_to_image(
    vectors: np.ndarray,
    positions: list[tuple[int, int]],
    block_h: int,
    block_w: int,
    height: int,
    width: int,
    channels: int,
) -> np.ndarray:
    """Assemble an image from block vectors, averaging overlapping pixels."""
    accum = np.zeros((height, width, channels), dtype=np.float64)
    counts = np.zeros((height, width, channels), dtype=np.float64)
    for vector, (y, x) in zip(vectors, positions):
        block = vector.reshape(block_h, block_w, channels)
        accum[y : y + block_h, x : x + block_w, :] += block
        counts[y : y + block_h, x : x + block_w, :] += 1.0
    counts = np.maximum(counts, 1.0)
    return accum / counts


def compression_ratio(q: int, n: int, p: int) -> float:
    """Compression ratio from the lab manual: Z = Qn / (2 + (n + Q)p)."""
    return (q * n) / (2.0 + (n + q) * p)


def byte_compression_ratio(
    q: int,
    n: int,
    p: int,
    source_bytes: int = 1,
    value_bytes: int = 8,
    service_bytes: int = 8,
) -> float:
    """Byte-aware compression ratio used as a refinement of ``Z``.

    The source BMP stores one byte per channel value, while the compressed
    representation stores ``Q*p`` latent values and one shared ``p*n`` decoder
    in ``value_bytes`` each.  ``service_bytes`` accounts for the two stored
    dimensions (n and p).
    """
    numerator = q * n * source_bytes
    denominator = q * p * value_bytes + p * n * value_bytes + service_bytes
    return numerator / denominator
