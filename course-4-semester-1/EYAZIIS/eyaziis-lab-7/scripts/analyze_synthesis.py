"""Задание 3.3.3. Сравнение эталонных и скомпилированных фраз."""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from speech_utils import (AUDIO_ROOT, PNG_DIR, ROOT, contour_stats, db,
                          detect_segments, f0_contour, load)

REF = AUDIO_ROOT / "3.2_phrases"
PHON = AUDIO_ROOT / "3.3.2_phoneme_synth"
SYL = AUDIO_ROOT / "3.3.5_syllable_synth"
PROS = AUDIO_ROOT / "3.3.6_prosody"

PAIRS = [
    ("phrase1", "phrase1_one_syntagma", "Мама мыла раму."),
    ("phrase2", "phrase2_enumeration", "Мама, папа и я."),
    ("phrase3", "phrase3_question", "Ты дома?"),
    ("phrase4", "phrase4_statement", "Ты дома."),
]


def stats(x, sr):
    st = contour_stats(x, sr)
    segs = detect_segments(x, sr, min_dur=0.05, merge_gap=0.08)
    t, f = f0_contour(x, sr)
    ok = ~np.isnan(f)
    ff = f[ok]
    jumps = np.abs(np.diff(ff))
    return {
        "dur": len(x) / sr,
        "peak": db(np.max(np.abs(x))),
        "rms": db(np.sqrt(np.mean(x ** 2))),
        "segments": len(segs),
        "f0_med": st["f0_med"],
        "f0_min": st["f0_min"],
        "f0_max": st["f0_max"],
        "f0_std": st["f0_std"],
        "delta_st": st["delta_st"],
        "jump_max": float(np.max(jumps)) if len(jumps) else 0.0,
        "jump_mean": float(np.mean(jumps)) if len(jumps) else 0.0,
        "voiced": int(ok.sum()),
    }


def main() -> None:
    lines = ["# Сравнение эталонных и синтезированных фраз", ""]
    fig, axes = plt.subplots(4, 2, figsize=(13, 12), sharex="col")
    for row, (name, stem, text) in enumerate(PAIRS):
        xr, sr = load(REF / f"{stem}.wav")
        variants = [("эталон", xr)]
        p = PHON / f"{name}.wav"
        if p.exists():
            variants.append(("фонемы", load(p)[0]))
        s = SYL / f"{name}.wav"
        if s.exists():
            variants.append(("слоги", load(s)[0]))
        q = PROS / f"{name}.wav"
        if q.exists():
            variants.append(("просодика", load(q)[0]))

        lines += [f"## {name}: {text}", "",
                  "| Вариант | Длит., с | Пик, дБFS | RMS, дБFS | Сегментов | "
                  "Медиана $F_0$ | Мин--макс $F_0$ | Скачок $F_0$ (макс/сред.) |",
                  "|---|---|---|---|---|---|---|---|"]
        for label, x in variants:
            st = stats(x, sr)
            lines.append(
                f"| {label} | {st['dur']:.2f} | {st['peak']:.1f} | {st['rms']:.1f} | "
                f"{st['segments']} | {st['f0_med']:.0f} | "
                f"{st['f0_min']:.0f}--{st['f0_max']:.0f} | "
                f"{st['jump_max']:.0f} / {st['jump_mean']:.1f} Гц |")
            ax = axes[row, 0] if label == "эталон" else axes[row, 1]
            if label in ("эталон", "фонемы"):
                ax.plot(np.arange(len(x)) / sr, x / max(np.max(np.abs(x)), 1e-9),
                        lw=0.5, color="#2b5c8a" if label == "эталон" else "#c0392b")
                ax.set_ylim(-1.05, 1.05)
                ax.set_yticks([])
                ax.grid(alpha=0.25)
        axes[row, 0].set_title(f"эталон: {text}", fontsize=10)
        axes[row, 1].set_title("фонемный синтез", fontsize=10)
        axes[row, 1].set_xlabel("время, с")
        lines.append("")

    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_wave_compare.png", dpi=150)
    plt.close(fig)

    # контуры F0: эталон против фонемного синтеза
    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    for ax, (name, stem, text) in zip(axes, [PAIRS[0], PAIRS[2]]):
        for label, folder, color in (
                ("эталон", REF, "#2b5c8a"),
                ("фонемы", PHON, "#c0392b")):
            fname = stem if label == "эталон" else name
            x, sr = load(folder / f"{fname}.wav")
            t, f = f0_contour(x, sr)
            ax.plot(t, f, lw=1.6, color=color, label=label)
        ax.set_title(text)
        ax.set_xlabel("время, с")
        ax.set_ylabel("$F_0$, Гц")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_f0_compare.png", dpi=150)
    plt.close(fig)

    (ROOT / "scripts" / "synthesis_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
