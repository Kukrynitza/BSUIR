"""Задание 3.3.4. Улучшение одной фразы правкой осциллограммы.

Выбрана фраза «Ты дома.». Что сделано по сравнению с заданием 3.3.2:
  * неудачные экземпляры [ы] и [о] (в списке гласных они произнесены с
    восходящей интонацией, 205 и 145 Гц) заменены ядрами этих же фонем,
    вырезанными из слогов «ты» и «до» (143 и 125 Гц);
  * уточнены границы и длительности всех сегментов;
  * выровнены уровни согласных относительно гласных;
  * сегменты сведены с перекрёстным затуханием 10 мс, в конце — плавное
    затухание 40 мс.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from speech_utils import (AUDIO_ROOT, PNG_DIR, ROOT, crossfade, db,
                          f0_contour, load, ramp, write)

BASE = AUDIO_ROOT / "3.3.1_phonemes"
SYL = AUDIO_ROOT / "3.3.5_syllables"
OUT = AUDIO_ROOT / "3.3.4_improved"
REF = AUDIO_ROOT / "3.2_phrases" / "phrase4_statement.wav"
BASELINE = AUDIO_ROOT / "3.3.2_phoneme_synth" / "phrase4.wav"


def take(seg, n, where="middle"):
    if len(seg) >= n:
        s = 0 if where == "start" else (len(seg) - n if where == "end"
                                       else (len(seg) - n) // 2)
        return seg[s:s + n].copy()
    y = seg.copy()
    pad = n - len(y)
    return np.concatenate([np.zeros(pad), y]) if where == "start" else \
        np.concatenate([np.zeros(pad // 2), y, np.zeros(pad - pad // 2)])


def level(y, mode, target):
    cur = db(np.sqrt(np.mean(y ** 2))) if mode == "rms" else db(np.max(np.abs(y)))
    return y * 10 ** ((target - cur) / 20)


def main() -> None:
    sr = 16000
    a, _ = load(BASE / "a.wav")
    o, _ = load(BASE / "o.wav")
    m, _ = load(BASE / "m.wav")
    t, _ = load(BASE / "t.wav")
    d, _ = load(BASE / "d.wav")
    ty, _ = load(SYL / "syl_09_ty.wav")
    do, _ = load(SYL / "syl_10_do.wav")

    # ядра гласных из слогов
    y_v = ty[int(0.09 * sr):int(0.26 * sr)]
    o_v = do[int(0.17 * sr):int(0.34 * sr)]

    parts = [
        level(take(t, int(0.070 * sr), "start"), "peak", -15.0),
        level(take(y_v, int(0.180 * sr), "middle"), "rms", -18.0),
        level(take(d, int(0.070 * sr), "start"), "peak", -16.0),
        level(take(o_v, int(0.170 * sr), "middle"), "rms", -18.0),
        level(take(m, int(0.080 * sr), "middle"), "rms", -24.0),
        level(take(a, int(0.190 * sr), "middle"), "rms", -18.0),
    ]
    y = parts[0]
    for p in parts[1:]:
        y = crossfade(y, p, sr, ms=10.0)
    y = ramp(y, sr, 8.0, "in")
    y = ramp(y, sr, 40.0, "out")
    y = y * 10 ** ((-6.0 - db(np.max(np.abs(y)))) / 20)
    write(OUT / "phrase4_improved.wav", y, sr)

    xr, _ = load(REF)
    xb, _ = load(BASELINE)

    lines = ["# Улучшение фразы «Ты дома.» (задание 3.3.4)", "",
             "| Вариант | Длит., с | Пик, дБFS | RMS, дБFS | Медиана $F_0$ | "
             "Мин--макс $F_0$ | Скачок $F_0$ |",
             "|---|---|---|---|---|---|---|"]
    for label, xx in (("эталон", xr), ("фонемный синтез", xb),
                      ("после правки", y)):
        tt, ff = f0_contour(xx, sr)
        ok = ~np.isnan(ff)
        f = ff[ok]
        jumps = np.abs(np.diff(f))
        lines.append(
            f"| {label} | {len(xx) / sr:.2f} | {db(np.max(np.abs(xx))):.1f} | "
            f"{db(np.sqrt(np.mean(xx ** 2))):.1f} | {np.median(f):.0f} | "
            f"{f.min():.0f}--{f.max():.0f} | {jumps.max():.0f} Гц |")
    (ROOT / "scripts" / "improved_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    for ax, (label, xx), color in zip(
            axes, (("эталон", xr), ("фонемный синтез", xb), ("после правки", y)),
            ("#2b5c8a", "#c0392b", "#27ae60")):
        ax.plot(np.arange(len(xx)) / sr, xx / np.max(np.abs(xx)), lw=0.6,
                color=color)
        ax.set_ylim(-1.05, 1.05)
        ax.set_ylabel("норм. амплитуда")
        ax.set_title(label)
        ax.grid(alpha=0.25)
    axes[-1].set_xlabel("время, с")
    fig.suptitle("«Ты дома.»: эталон, компиляция из фонем и результат правки",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_improved_wave.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.6))
    for label, xx, color in (("эталон", xr, "#2b5c8a"),
                             ("фонемный синтез", xb, "#c0392b"),
                             ("после правки", y, "#27ae60")):
        tt, ff = f0_contour(xx, sr)
        ax.plot(tt, ff, lw=1.8, color=color, label=label)
    ax.set_xlabel("время, с")
    ax.set_ylabel("$F_0$, Гц")
    ax.set_title("Контуры $F_0$ фразы «Ты дома.»")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_improved_f0.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
