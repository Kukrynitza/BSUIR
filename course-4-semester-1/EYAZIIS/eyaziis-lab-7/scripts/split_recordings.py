"""Нарезка исходных записей части 3 на эталонные фразы и слоги."""

import numpy as np

from speech_utils import (AUDIO_ROOT, ROOT, db, detect_segments, load,
                          write)

SRC_PHRASES = AUDIO_ROOT.parent.parent / "phrases_all.wav"
SRC_SYLLABLES = AUDIO_ROOT.parent.parent / "syllables_all.wav"

PHRASE_DIR = AUDIO_ROOT / "3.2_phrases"
SYL_DIR = AUDIO_ROOT / "3.3.5_syllables"

# границы, полученные автоматической сегментацией по паузам (см. отчёт)
PHRASE_SPANS = [
    ("phrase1_one_syntagma", 2.11, 4.20),
    ("phrase2_enumeration", 6.06, 9.05),
    ("phrase3_question", 10.70, 11.23),
    ("phrase4_statement", 12.90, 13.34),
]
PHRASE2_PARTS = [
    ("phrase2_1_mama", 6.06, 6.46),
    ("phrase2_2_papa", 7.69, 8.04),
    ("phrase2_3_iya", 8.72, 9.05),
]
SYLLABLES = [
    ("syl_01_ma", 1.64, 1.97),
    ("syl_02_my", 3.38, 3.72),
    ("syl_03_la", 5.19, 5.64),
    ("syl_04_ra", 7.08, 7.42),
    ("syl_05_mu", 8.82, 9.23),
    ("syl_06_pa", 10.85, 11.06),
    ("syl_07_i", 12.59, 12.84),
    ("syl_08_ya", 14.26, 14.64),
    ("syl_09_ty", 16.04, 16.29),
    ("syl_10_do", 17.68, 18.00),
]

PAD = 0.04
TARGET_PEAK = -6.0


def cut(x: np.ndarray, sr: int, a: float, b: float, pad: float = PAD):
    return x[max(0, int((a - pad) * sr)):min(len(x), int((b + pad) * sr))]


def main() -> None:
    xp, sr = load(SRC_PHRASES)
    xs, _ = load(SRC_SYLLABLES)
    assert sr == 16000

    # контроль: автоматическая сегментация должна дать те же границы
    segs = detect_segments(xp, sr, min_dur=0.2, merge_gap=0.25)
    print("автосегментов в phrases_all:", len(segs))
    for a, b in segs:
        print(f"  {a / sr:.2f}-{b / sr:.2f}")

    peak = max(np.max(np.abs(cut(xp, sr, a, b))) for _, a, b in PHRASE_SPANS)
    gain = 10 ** ((TARGET_PEAK - db(peak)) / 20)
    print(f"общий коэффициент усиления: {20 * np.log10(gain):+.1f} дБ")

    lines = ["# Эталонные фразы и слоги", "",
             "| Файл | Интервал, с | Длит., с | Пик, дБFS | RMS, дБFS |",
             "|---|---|---|---|---|"]
    for name, a, b in PHRASE_SPANS:
        y = cut(xp, sr, a, b) * gain
        write(PHRASE_DIR / f"{name}.wav", y, sr)
        lines.append(f"| {name}.wav | {a:.2f}--{b:.2f} | {len(y) / sr:.2f} | "
                     f"{db(np.max(np.abs(y))):.1f} | {db(np.sqrt(np.mean(y ** 2))):.1f} |")
    for name, a, b in PHRASE2_PARTS:
        y = cut(xp, sr, a, b) * gain
        write(PHRASE_DIR / f"{name}.wav", y, sr)

    lines += ["", "| Файл | Интервал, с | Длит., с | Пик, дБFS | RMS, дБFS |",
              "|---|---|---|---|---|"]
    for name, a, b in SYLLABLES:
        y = cut(xs, sr, a, b, pad=0.03)
        write(SYL_DIR / f"{name}.wav", y, sr)
        lines.append(f"| {name}.wav | {a:.2f}--{b:.2f} | {len(y) / sr:.2f} | "
                     f"{db(np.max(np.abs(y))):.1f} | {db(np.sqrt(np.mean(y ** 2))):.1f} |")

    (ROOT / "scripts" / "reference_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
