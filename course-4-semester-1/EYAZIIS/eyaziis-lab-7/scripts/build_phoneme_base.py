"""Задание 3.3.1. Формирование фонетической базы.

Изолированные фонемы берутся из записей лабораторной работы 1
(sample1, sample1b, sample4); отсутствующие в ней согласные [л], [р],
[п], [т], [д] вырезаются из слогов, записанных для задания 3.3.5.
Границы размечены вручную по осциллограммам и спектрограммам.
"""

import numpy as np

from speech_utils import (AUDIO_ROOT, LAB5_AUDIO, ROOT, db, f0_contour,
                          load, load_lab5, write)

OUT = AUDIO_ROOT / "3.3.1_phonemes"
SYL = AUDIO_ROOT / "3.3.5_syllables"

# имя, источник, начало, конец (в файле-источнике)
SPECS = [
    ("a", ("lab5", "1.4.1_vowels/sample1.wav"), 0.92, 1.16),
    ("o", ("lab5", "1.4.1_vowels/sample1.wav"), 3.02, 3.26),
    ("u", ("lab5", "1.4.1_vowels/sample1.wav"), 4.955, 5.195),
    ("e", ("lab5", "1.4.1_vowels/sample1.wav"), 7.14, 7.38),
    ("y", ("lab5", "1.4.1_vowels/sample1.wav"), 9.15, 9.39),
    ("i", ("lab5", "1.4.1_vowels/sample1.wav"), 11.31, 11.55),
    ("m", ("syl", "syl_01_ma.wav"), 0.035, 0.135),
    ("j", ("lab5", "1.4.1_vowels/sample1b.wav"), 0.91, 1.03),
    ("l", ("syl", "syl_03_la.wav"), 0.04, 0.19),
    ("r", ("syl", "syl_04_ra.wav"), 0.035, 0.130),
    ("p", ("syl", "syl_06_pa.wav"), 0.00, 0.055),
    ("t", ("syl", "syl_09_ty.wav"), 0.00, 0.060),
    ("d", ("lab5", "1.4.3_stops_nasals/sample5.wav"), 2.02, 2.10),
]


def main() -> None:
    lines = ["# Фонетическая база (задание 3.3.1)", "",
             "| Фонема | Источник | Интервал, с | Длит., с | $F_0$, Гц | "
             "Пик, дБFS | RMS, дБFS |",
             "|---|---|---|---|---|---|---|"]
    for name, (kind, src), a, b in SPECS:
        if kind == "lab5":
            x, sr = load_lab5(src)
        else:
            x, sr = load(SYL / src)
        seg = x[int(a * sr):int(b * sr)].copy()
        # плавные фронты 5 мс, чтобы при склейке не было щелчков
        n = int(0.005 * sr)
        w = np.linspace(0, 1, n)
        seg[:n] *= w
        seg[-n:] *= w[::-1]
        write(OUT / f"{name}.wav", seg, sr)
        t, f = f0_contour(seg, sr)
        ok = ~np.isnan(f)
        f0 = float(np.median(f[ok])) if ok.any() else float("nan")
        print(f"{name}: {src} {a:.3f}-{b:.3f} -> {len(seg) / sr:.3f} с, "
              f"пик {db(np.max(np.abs(seg))):.1f}, rms {db(np.sqrt(np.mean(seg ** 2))):.1f}, "
              f"F0 {f0:.0f}")
        lines.append(
            f"| [{name}] | {src} | {a:.2f}--{b:.2f} | {len(seg) / sr:.2f} | "
            f"{f0:.0f} | {db(np.max(np.abs(seg))):.1f} | "
            f"{db(np.sqrt(np.mean(seg ** 2))):.1f} |")

    (ROOT / "scripts" / "phoneme_base.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
