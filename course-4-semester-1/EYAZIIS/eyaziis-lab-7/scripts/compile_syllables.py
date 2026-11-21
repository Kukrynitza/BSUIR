"""Задание 3.3.5. Компиляция фраз из слогов.

Слоги записаны отдельно (файлы syl_01...syl_10) и вырезаны из общей
записи. Каждый слог обрезается до типовой длительности (длинные
начальные сонорные сокращаются за счёт устойчивой части), уровни
выравниваются, стыки сглаживаются перекрёстным затуханием.
"""

import numpy as np

from speech_utils import (AUDIO_ROOT, ROOT, crossfade, db, f0_contour, load,
                          ramp, trim, write)

SYL = AUDIO_ROOT / "3.3.5_syllables"
OUT = AUDIO_ROOT / "3.3.5_syllable_synth"

# слог: (файл, смещение от начала после обрезки, целевая длительность, мс)
SPEC = {
    "ma": ("syl_01_ma", 20, 300),
    "my": ("syl_02_my", 100, 280),
    "la": ("syl_03_la", 180, 300),
    "ra": ("syl_04_ra", 40, 280),
    "mu": ("syl_05_mu", 60, 300),
    "pa": ("syl_06_pa", 0, 250),
    "i": ("syl_07_i", 60, 180),
    "ya": ("syl_08_ya", 100, 300),
    "ty": ("syl_09_ty", 0, 260),
    "do": ("syl_10_do", 50, 300),
}

PHRASES = {
    "phrase1": ("Мама мыла раму.",
                [["ma", "ma"], ["my", "la"], ["ra", "mu"]],
                [100, 100]),
    "phrase2": ("Мама, папа и я.",
                [["ma", "ma"], ["pa", "pa"], ["i"], ["ya"]],
                [450, 300, 40]),
    "phrase3": ("Ты дома?",
                [["ty"], ["do", "ma"]], [30]),
    "phrase4": ("Ты дома.",
                [["ty"], ["do", "ma"]], [30]),
}

STRESS = {"ma", "my", "ra", "ya", "do"}


def get_syl(key: str) -> np.ndarray:
    name, offset_ms, dur_ms = SPEC[key]
    x, sr = load(SYL / f"{name}.wav")
    x = trim(x, sr, thr_db=-38.0, pad=0.005)
    a = int(offset_ms * sr / 1000)
    n = int(dur_ms * sr / 1000)
    y = x[a:a + n].copy()
    if len(y) < n:
        y = np.concatenate([y, np.zeros(n - len(y))])
    y = ramp(y, sr, 8.0)
    target = -20.0 + (2.0 if key in STRESS else 0.0)
    cur = db(np.sqrt(np.mean(y ** 2)))
    return y * 10 ** ((target - cur) / 20)


def main() -> None:
    sr = 16000
    lines = ["# Компиляция из слогов (задание 3.3.5)", "",
             "| Слог | Длит., с | RMS, дБFS | $F_0$, Гц |",
             "|---|---|---|---|"]
    cache = {}
    for key in SPEC:
        y = get_syl(key)
        cache[key] = y
        t, f = f0_contour(y, sr)
        ok = ~np.isnan(f)
        lines.append(f"| {key} | {len(y) / sr:.2f} | "
                     f"{db(np.sqrt(np.mean(y ** 2))):.1f} | "
                     f"{np.median(f[ok]):.0f} |")
    lines.append("")

    for name, (text, words, pauses) in PHRASES.items():
        y = None
        for wi, word in enumerate(words):
            for key in word:
                y = cache[key] if y is None else crossfade(y, cache[key], sr, 12.0)
            if wi < len(pauses) and pauses[wi] > 0:
                y = np.concatenate([y, np.zeros(int(pauses[wi] * sr / 1000))])
        y = y * 10 ** ((-6.0 - db(np.max(np.abs(y)))) / 20)
        write(OUT / f"{name}.wav", y, sr)
        t, f = f0_contour(y, sr)
        ok = ~np.isnan(f)
        jumps = np.abs(np.diff(f[ok]))
        lines += [f"## {name}: {text}", "",
                  f"Длительность {len(y) / sr:.2f} с, медиана $F_0$ "
                  f"{np.median(f[ok]):.0f} Гц, макс. скачок {jumps.max():.0f} Гц.",
                  ""]
    (ROOT / "scripts" / "syllable_synth.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
