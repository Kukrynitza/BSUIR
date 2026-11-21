"""Нарезка записанных слов из words_all.wav на отдельные файлы.

Слова произнесены подряд: «Саша» … «кушал» … «кашу».
Результат: sample2_1.wav (Саша), sample2_2.wav (кушал), sample2_3.wav (кашу).
"""

from pathlib import Path

import numpy as np
import soundfile as sf

from speech_utils import AUDIO_ROOT, load

WORDS_DIR = AUDIO_ROOT / "2.2.1_stress" / "words"
NAMES = ["sample2_1.wav", "sample2_2.wav", "sample2_3.wav"]
LABELS = ["Саша", "кушал", "кашу"]


def segments(x: np.ndarray, sr: int, thr_rel: float = 0.03,
             merge_gap: float = 0.12, min_dur: float = 0.25):
    frame = int(0.01 * sr)
    n = len(x) // frame
    e = np.array([np.sqrt((x[i * frame:(i + 1) * frame] ** 2).mean())
                  for i in range(n)])
    thr = e.max() * thr_rel
    segs, i = [], 0
    while i < n:
        if e[i] > thr:
            j = i
            while j < n and e[j] > thr:
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


def normalize(x: np.ndarray, peak_db: float = -12.0) -> np.ndarray:
    peak = np.max(np.abs(x))
    if peak < 1e-9:
        return x
    return x * (10 ** (peak_db / 20) / peak)


def main() -> None:
    x, sr = load("2.2.1_stress/words/words_all.wav")
    segs = segments(x, sr)
    if len(segs) != len(LABELS):
        raise SystemExit(f"ожидалось {len(LABELS)} сегмента, найдено {len(segs)}: "
                         f"{[(round(s / sr, 2), round(e / sr, 2)) for s, e in segs]}")

    pad = int(0.015 * sr)  # 15 мс запаса с каждой стороны
    for (s, e), name, label in zip(segs, NAMES, LABELS):
        s0, e0 = max(0, s - pad), min(len(x), e + pad)
        seg = normalize(x[s0:e0])
        sf.write(WORDS_DIR / name, seg, sr, subtype="PCM_16")
        print(f"{name:14s} {label:6s} {s / sr:6.3f}-{e / sr:6.3f} c  "
              f"dur={(e0 - s0) / sr:.3f} c  peak=-12.0 dBFS")


if __name__ == "__main__":
    main()
