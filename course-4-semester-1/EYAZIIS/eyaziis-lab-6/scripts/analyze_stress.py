"""Анализ словесного/фразового ударения (задание 2.2.1).

Для каждой записи фразы «Саша кушал кашу» измеряются характеристики
слов: длительность, пиковый и средний уровень, медианная F0.
Ударное слово выделяется повышенным уровнем и/или F0.
Границы слов определены визуально по осциллограммам и спектрограммам.
"""

import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from speech_utils import AUDIO_ROOT, PNG_DIR, ROOT, load, estimate_f0

PHR_DIR = AUDIO_ROOT / "2.2.1_stress" / "phrases"
WORDS = ["Саша", "кушал", "кашу"]
ACCENT = {"sample2_5.wav": 0, "sample2_5_s2.wav": 1, "sample2_5_s3.wav": 2,
          "sample2_6.wav": None}  # sample2_6 — переставленная фраза

# Границы слов (с) — по осциллограммам
BOUNDS = {
    "sample2_5.wav": [(0.95, 1.75), (1.75, 2.32), (2.32, 2.68)],
    "sample2_5_s2.wav": [(0.92, 1.54), (1.54, 2.33), (2.33, 2.75)],
    "sample2_5_s3.wav": [(1.06, 1.56), (1.56, 2.25), (2.25, 2.94)],
    "sample2_6.wav": [(0.20, 0.62), (0.62, 1.00), (1.35, 2.20)],
}
LABELS_2_6 = ["кушал", "кашу", "Саша"]


def db(x: float) -> float:
    return 20 * np.log10(max(x, 1e-9))


def word_stats(x: np.ndarray, sr: int, a: float, b: float) -> dict:
    seg = x[int(a * sr):int(b * sr)]
    f0s = []
    hop = int(0.02 * sr)
    for i in range(0, len(seg) - hop, hop):
        f = estimate_f0(seg[i:i + hop], sr)
        if not np.isnan(f):
            f0s.append(f)
    return {
        "dur": (b - a),
        "peak": db(np.max(np.abs(seg))),
        "rms": db(np.sqrt(np.mean(seg ** 2))),
        "f0": float(np.median(f0s)) if f0s else float("nan"),
    }


def main() -> None:
    lines = ["# Метрики ударения (задание 2.2.1)", "",
             "| Запись | Слово | Длит., с | Пик, дБFS | RMS, дБFS | F0, Гц |",
             "|---|---|---|---|---|---|"]
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    for ax, fname in zip(axes, BOUNDS):
        x, sr = load(f"2.2.1_stress/phrases/{fname}")
        t = np.arange(len(x)) / sr
        x_n = x / np.max(np.abs(x))
        ax.plot(t, x_n, lw=0.5, color="#2b5c8a")
        labels = LABELS_2_6 if fname == "sample2_6.wav" else WORDS
        for idx, ((a, b), label) in enumerate(zip(BOUNDS[fname], labels)):
            stats = word_stats(x, sr, a, b)
            mark = " (ударное)" if ACCENT.get(fname) == idx else ""
            lines.append(
                f"| {fname} | {label}{mark} | {stats['dur']:.2f} | "
                f"{stats['peak']:.1f} | {stats['rms']:.1f} | {stats['f0']:.0f} |")
            color = "#c0392b" if ACCENT.get(fname) == idx else "#7f8c8d"
            ax.axvspan(a, b, alpha=0.12, color=color)
            ax.text((a + b) / 2, 0.85, label, ha="center", fontsize=9, color=color)
        ax.set_ylim(-1, 1)
        ax.set_ylabel("амплитуда (норм.)")
        ax.set_title(fname, fontsize=9)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("время, с")
    fig.suptitle("Фразы «Саша кушал кашу» с разным положением ударения", fontsize=11)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_stress_waves.png", dpi=150)
    plt.close(fig)

    # Столбчатая диаграмма пиковых уровней слов
    fig, ax = plt.subplots(figsize=(9, 4.5))
    names, rows = ["s1 (САша)", "s2 (КУшал)", "s3 (КАшу)"], list(BOUNDS)[:3]
    width = 0.25
    for j, (w, name) in enumerate(zip(WORDS, names)):
        vals = []
        for fname in rows:
            x, sr = load(f"2.2.1_stress/phrases/{fname}")
            a, b = BOUNDS[fname][j]
            vals.append(word_stats(x, sr, a, b)["peak"])
        ax.bar(np.arange(len(rows)) + (j - 1) * width, vals, width, label=w)
    ax.set_xticks(np.arange(len(rows)), names)
    ax.set_ylabel("пиковый уровень слова, дБFS")
    ax.set_title("Уровень слов при разном положении фразового ударения")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_accent_levels.png", dpi=150)
    plt.close(fig)

    (ROOT / "scripts" / "stress_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
