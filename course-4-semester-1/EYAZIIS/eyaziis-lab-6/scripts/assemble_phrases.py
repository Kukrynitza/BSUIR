"""Сборка фраз из записанных слов (задание 2.2.1).

sample2_4.wav — шесть перестановок слов «Саша», «кушал», «кашу».
sample2_6.wav — фраза «Саша кушал кашу» с переносом слова «Саша» в конец
               (получается из sample2_5.wav вырезанием/вставкой фрагментов,
               аналог операций Cut/Paste в редакторе).
"""

import numpy as np
import soundfile as sf

from speech_utils import AUDIO_ROOT, load

PHRASES_DIR = AUDIO_ROOT / "2.2.1_stress" / "phrases"
WORDS_DIR = AUDIO_ROOT / "2.2.1_stress" / "words"

PERMUTATIONS = [
    ("sample2_1", "sample2_2", "sample2_3"),  # Саша кушал кашу
    ("sample2_2", "sample2_1", "sample2_3"),  # кушал Саша кашу
    ("sample2_2", "sample2_3", "sample2_1"),  # кушал кашу Саша
    ("sample2_1", "sample2_3", "sample2_2"),  # Саша кашу кушал
    ("sample2_3", "sample2_1", "sample2_2"),  # кашу Саша кушал
    ("sample2_3", "sample2_2", "sample2_1"),  # кашу кушал Саша
]


def normalize(x: np.ndarray, peak_db: float = -12.0) -> np.ndarray:
    peak = np.max(np.abs(x))
    return x if peak < 1e-9 else x * (10 ** (peak_db / 20) / peak)


def silence(sr: int, dur: float) -> np.ndarray:
    return np.zeros(int(dur * sr))


def build_sample2_4(sr: int) -> np.ndarray:
    words = {}
    for name in ("sample2_1", "sample2_2", "sample2_3"):
        w, _ = sf.read(WORDS_DIR / f"{name}.wav", dtype="float64")
        words[name] = w[:, 0] if w.ndim > 1 else w

    parts = [silence(sr, 0.3)]
    for perm in PERMUTATIONS:
        for i, name in enumerate(perm):
            if i:
                parts.append(silence(sr, 0.25))  # внутрифразовая пауза
            parts.append(words[name])
        parts.append(silence(sr, 0.6))  # пауза между вариантами
    return np.concatenate(parts)


def build_sample2_6(sr: int) -> np.ndarray:
    """«кушал кашу» + пауза + «Саша» из sample2_5.wav."""
    x, _ = load("2.2.1_stress/phrases/sample2_5.wav")
    sasha = x[int(0.93 * sr):int(1.78 * sr)]     # «Саша» (с [с] и [ш])
    tail = x[int(1.88 * sr):int(2.68 * sr)]      # «кушал кашу»
    return np.concatenate([silence(sr, 0.2), tail, silence(sr, 0.35), sasha,
                           silence(sr, 0.3)])


def main() -> None:
    sr = 16000
    sf.write(PHRASES_DIR / "sample2_4.wav", normalize(build_sample2_4(sr)), sr,
             subtype="PCM_16")
    sf.write(PHRASES_DIR / "sample2_6.wav", normalize(build_sample2_6(sr)), sr,
             subtype="PCM_16")
    print("sample2_4.wav: 6 перестановок записаны")
    print("sample2_6.wav: «кушал кашу» + «Саша» в конце")


if __name__ == "__main__":
    main()
