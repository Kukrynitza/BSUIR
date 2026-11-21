"""Общие утилиты для анализа речевых записей лабораторной работы (часть 2)."""

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import find_peaks

ROOT = Path(__file__).resolve().parents[1]
AUDIO_ROOT = ROOT / "audio" / "lab2"
PNG_DIR = ROOT / "eyazis-report-6" / "png"

MIN_DUR = 0.15  # с
MERGE_GAP = 0.15  # с


def load(rel_path: str):
    x, sr = sf.read(AUDIO_ROOT / rel_path, dtype="float64")
    if x.ndim > 1:
        x = x[:, 0]
    return x, sr


def detect_segments(x: np.ndarray, sr: int,
                    min_dur: float = MIN_DUR, merge_gap: float = MERGE_GAP):
    frame = int(0.01 * sr)
    n = len(x) // frame
    e = np.sqrt(
        np.array([(x[i * frame : (i + 1) * frame] ** 2).mean() for i in range(n)])
    )
    thr = e.max() * 0.08
    segs = []
    i = 0
    while i < len(e):
        if e[i] > thr:
            j = i
            while j < len(e) and e[j] > thr:
                j += 1
            segs.append([i * frame, j * frame])
            i = j
        else:
            i += 1
    merged = []
    for s, e_ in segs:
        if merged and (s - merged[-1][1]) / sr < merge_gap:
            merged[-1][1] = e_
        else:
            merged.append([s, e_])
    return [(s, e_) for s, e_ in merged if (e_ - s) / sr >= min_dur]


def estimate_f0(seg: np.ndarray, sr: int) -> float:
    n = min(int(0.04 * sr), len(seg))
    start = (len(seg) - n) // 2
    w = seg[start : start + n]
    w = w - w.mean()
    ac = np.correlate(w, w, mode="full")[len(w) - 1 :]
    lag_min, lag_max = sr // 400, sr // 60
    if lag_max >= len(ac):
        lag_max = len(ac) - 1
    peak_lags, _ = find_peaks(ac[lag_min:lag_max])
    if len(peak_lags) == 0:
        return float("nan")
    lag = peak_lags[np.argmax(ac[lag_min:lag_max][peak_lags])] + lag_min
    strength = ac[lag] / ac[0]
    if strength < 0.3:  # периодика слабая — не гласная
        return float("nan")
    return sr / lag


def periodicity_strength(seg: np.ndarray, sr: int) -> float:
    """Макс. нормированная автокорреляция в диапазоне 60..400 Гц."""
    n = min(int(0.04 * sr), len(seg))
    start = (len(seg) - n) // 2
    w = seg[start : start + n] - seg[start : start + n].mean()
    ac = np.correlate(w, w, mode="full")[len(w) - 1 :]
    lag_min, lag_max = sr // 400, sr // 60
    if lag_max >= len(ac):
        lag_max = len(ac) - 1
    return float((ac[lag_min:lag_max] / ac[0]).max())


def spectrum(seg: np.ndarray, sr: int, nfft: int = 4096):
    n = min(nfft, len(seg))
    start = (len(seg) - n) // 2
    w = seg[start : start + n] * np.hanning(n)
    sp = np.abs(np.fft.rfft(w, nfft))
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    db = 20 * np.log10(sp / max(sp.max(), 1e-12) + 1e-12)
    return freqs, db


def band_levels(seg: np.ndarray, sr: int, bands=((0, 500), (500, 1000),
                (1000, 2000), (2000, 4000), (4000, 8000))):
    freqs, db = spectrum(seg, sr)
    out = {}
    for f0, f1 in bands:
        b = (freqs >= f0) & (freqs < f1)
        out[f"{f0}-{f1}"] = db[b].max() if b.any() else float("-inf")
    return out
