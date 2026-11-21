"""Задание 3.3.6*. Просодическая обработка синтезированных фраз.

Задаются три группы параметров:
  * F0(t) — мелодический контур: сдвиг тона каждого слога в полутонах
    (сдвиг выполняется с сохранением формант);
  * A(t) — энергетический контур: добавка к уровню каждого слога, дБ;
  * T(t) — ритмический контур: коэффициент длительности каждого слога.
Значения подобраны по эталонным записям (измеренные контуры F0, уровни
и длительности слогов).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from speech_utils import (AUDIO_ROOT, PNG_DIR, ROOT, crossfade, db,
                          f0_contour, load, pitch_shift_curve, ramp,
                          stretch, write)
from compile_syllables import PHRASES, SPEC, get_syl

OUT = AUDIO_ROOT / "3.3.6_prosody"
SYL_SYNTH = AUDIO_ROOT / "3.3.5_syllable_synth"
REF = AUDIO_ROOT / "3.2_phrases"

ORDER = {
    "phrase1": ["ma", "ma", "my", "la", "ra", "mu"],
    "phrase2": ["ma", "ma", "pa", "pa", "i", "ya"],
    "phrase3": ["ty", "do", "ma"],
    "phrase4": ["ty", "do", "ma"],
}
STEM = {
    "phrase1": "phrase1_one_syntagma",
    "phrase2": "phrase2_enumeration",
    "phrase3": "phrase3_question",
    "phrase4": "phrase4_statement",
}

# просодические контуры: F0 (полутоны), A (дБ), T (коэффициент)
F0 = {
    "phrase1": [-1.0, 1.0, 4.5, 3.0, 0.0, -4.0],
    "phrase2": [-1.0, -2.5, 0.5, -2.5, -1.5, -4.0],
    "phrase3": [-2.0, 0.0, 5.0],
    "phrase4": [-1.0, -0.5, -3.0],
}
A = {
    "phrase1": [0.0, 0.0, 1.5, 0.0, 0.0, -1.5],
    "phrase2": [0.0, 0.0, 1.5, 0.0, -1.0, -1.5],
    "phrase3": [0.0, 1.5, 1.0],
    "phrase4": [0.0, 1.5, -1.5],
}
T = {
    "phrase1": [1.0, 1.0, 1.1, 1.0, 1.0, 1.15],
    "phrase2": [1.0, 1.0, 1.0, 1.0, 0.9, 1.2],
    "phrase3": [1.0, 1.1, 1.35],
    "phrase4": [1.0, 1.0, 1.25],
}


def build(phrase: str):
    """Сборка фразы из слогов; возвращает сигнал и центры слогов (с)."""
    sr = 16000
    _, words, pauses = PHRASES[phrase]
    factors = T[phrase]
    cache = {}
    y = None
    centers = []
    durs = []
    k = 0
    fade = int(0.012 * sr)
    for wi, word in enumerate(words):
        for key in word:
            if key not in cache:
                cache[key] = get_syl(key)
            p = stretch(cache[key], sr, factors[k])
            durs.append(len(p) / sr)
            if y is None:
                y = p
                centers.append(len(p) / 2 / sr)
            else:
                centers.append((len(y) - fade + len(p) / 2) / sr)
                y = crossfade(y, p, sr, 12.0)
            k += 1
        if wi < len(pauses) and pauses[wi] > 0:
            y = np.concatenate([y, np.zeros(int(pauses[wi] * sr / 1000))])
    return y, np.array(centers), durs


def gain_curve(y, sr, centers, gains):
    env = np.interp(np.arange(len(y)) / sr, centers, gains,
                    left=gains[0], right=gains[-1])
    return y * 10 ** (env / 20)


def main() -> None:
    sr = 16000
    lines = ["# Просодическая обработка (задание 3.3.6)", ""]
    fig, axes = plt.subplots(4, 3, figsize=(15, 13))
    for row, phrase in enumerate(ORDER):
        keys = ORDER[phrase]
        base, centers, durs = build(phrase)

        y = gain_curve(base, sr, centers, A[phrase])
        y = pitch_shift_curve(y, sr, centers, np.array(F0[phrase]))
        y = ramp(y, sr, 10.0, "in")
        y = ramp(y, sr, 30.0, "out")
        y = y * 10 ** ((-6.0 - db(np.max(np.abs(y)))) / 20)
        write(OUT / f"{phrase}.wav", y, sr)

        xr, _ = load(REF / f"{STEM[phrase]}.wav")
        xs, _ = load(SYL_SYNTH / f"{phrase}.wav")
        t_r, f_r = f0_contour(xr, sr)
        t_s, f_s = f0_contour(xs, sr)
        t_p, f_p = f0_contour(y, sr)
        ok = ~np.isnan(f_p)
        lines += [f"## {phrase}", "",
                  "| Слог | Сдвиг F0, пт | Добавка A, дБ | Коэф. T | "
                  "F0 до, Гц | F0 после, Гц |",
                  "|---|---|---|---|---|---|"]
        for k, (key, c, d) in enumerate(zip(keys, centers, durs)):
            m = (t_s >= c - 0.06) & (t_s <= c + 0.06)
            fs = np.median(f_s[m]) if m.any() else float("nan")
            m2 = (t_p >= c - 0.06) & (t_p <= c + 0.06)
            fp = np.median(f_p[m2]) if m2.any() else float("nan")
            lines.append(f"| {key} | {F0[phrase][k]:+.1f} | {A[phrase][k]:+.1f} | "
                         f"{T[phrase][k]:.2f} | {fs:.0f} | {fp:.0f} |")
        lines += ["", f"Итог: медиана $F_0$ {np.nanmedian(f_p):.0f} Гц, "
                  f"диапазон {np.nanmin(f_p):.0f}--{np.nanmax(f_p):.0f} Гц, "
                  f"длительность {len(y) / sr:.2f} с.", ""]

        # ---------------------------------------------------------- графики
        tr = t_r / t_r[-1]
        ts = t_s / t_s[-1]
        tp = t_p / t_p[-1]
        ax = axes[row, 0]
        ax.plot(tr, f_r, color="#2b5c8a", lw=1.5, label="эталон")
        ax.plot(ts, f_s, color="#95a5a6", lw=1.2, label="слоги")
        ax.plot(tp, f_p, color="#27ae60", lw=1.8, label="просодика")
        ax.set_ylabel("$F_0$, Гц")
        ax.set_title(f"{phrase}: $F_0(t)$", fontsize=10)
        ax.grid(alpha=0.3)
        if row == 0:
            ax.legend(fontsize=8)

        ax = axes[row, 1]
        for z, lab, c in ((xr, "эталон", "#2b5c8a"), (y, "просодика", "#27ae60")):
            n = int(0.02 * sr)
            e = np.array([np.sqrt(np.mean(z[i:i + n] ** 2))
                          for i in range(0, len(z) - n, n)])
            e = 20 * np.log10(np.maximum(e, 1e-9) / e.max())
            ax.plot(np.arange(len(e)) * 0.02 / (len(z) / sr), e,
                    color=c, lw=1.2, label=lab)
        ax.set_ylabel("уровень, дБ")
        ax.set_title("$A(t)$", fontsize=10)
        ax.set_ylim(-50, 2)
        ax.grid(alpha=0.3)
        if row == 0:
            ax.legend(fontsize=8)

        ax = axes[row, 2]
        ax.bar(range(1, len(durs) + 1), durs, color="#8e44ad", alpha=0.7)
        ax.set_xticks(range(1, len(durs) + 1))
        ax.set_xticklabels(keys, fontsize=8)
        ax.set_ylabel("длительность, с")
        ax.set_title("$T(t)$", fontsize=10)
        ax.grid(alpha=0.3, axis="y")

    for ax in axes[-1, :2]:
        ax.set_xlabel("относительное время")
    axes[-1, 2].set_xlabel("слог")
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_prosody_contours.png", dpi=150)
    plt.close(fig)

    (ROOT / "scripts" / "prosody_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
