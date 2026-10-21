"""Задание 1.4.2: шипящие согласные фонемы [ф с ш х] и слоги «фа са ша ха»."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from speech_utils import (
    AUDIO_ROOT,
    PNG_DIR,
    band_levels,
    detect_segments,
    estimate_f0,
    load,
    periodicity_strength,
    spectrum,
)

FRICATIVES = ["ф", "с", "ш", "х"]
SYLLABLES = ["фа", "са", "ша", "ха"]


def draw_wave_labels(x, sr, segs, labels, title, fname, ylim=None):
    fig, ax = plt.subplots(figsize=(11, 3))
    t = np.arange(len(x)) / sr
    ax.plot(t, x, lw=0.3)
    ymin, ymax = (ylim if ylim else ax.get_ylim())
    for (s, e_), lab in zip(segs, labels):
        ts, te = s / sr, e_ / sr
        ax.axvspan(ts, te, alpha=0.25, color="orange")
        ax.text((ts + te) / 2, ymin + (ymax - ymin) * 0.85,
                lab if len(lab) > 2 else f"[{lab}]",
                ha="center", fontsize=12)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlabel("Время, с")
    ax.set_ylabel("Амплитуда")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(PNG_DIR / fname, dpi=150)
    plt.close(fig)


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    metrics = []

    # ---------- sample2: отдельные шипящие ----------
    x2, sr = load("1.4.2_fricatives/sample2.wav")
    segs2 = detect_segments(x2, sr)
    # щелчки между фонемами отсекаем: оставляем 4 самых длинных
    segs2 = sorted(segs2, key=lambda se: se[1] - se[0], reverse=True)[:4]
    segs2.sort()
    assert len(segs2) == 4, f"sample2: найдено {len(segs2)} сегментов"
    print("sample2.wav (шипящие в изоляции):")
    for (s, e_), lab in zip(segs2, FRICATIVES):
        seg = x2[s:e_]
        per = periodicity_strength(seg, sr)
        f0 = estimate_f0(seg, sr)
        bl = band_levels(seg, sr)
        print(f"  [{lab}] {s/sr:.2f}–{e_/sr:.2f} с  периодичность={per:.2f}  "
              f"F0={'н/д' if not np.isfinite(f0) else f'{f0:.0f} Гц'}")
        metrics.append({"grp": "шипящая", "ph": lab, "t0": s / sr,
                        "t1": e_ / sr, "per": per, "f0": f0, "bands": bl})

    draw_wave_labels(
        x2, sr, segs2, FRICATIVES,
        "Осциллограмма шипящих согласных [ф с ш х] (sample2.wav)",
        "lab1_fricatives_wave.png",
    )

    # спектрограммы шипящих в изоляции
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), sharey=True)
    for ax, (s, e_), lab in zip(axes, segs2, FRICATIVES):
        seg = x2[s:e_]
        n = min(4096, len(seg))
        start = (len(seg) - n) // 2
        ax.specgram(seg[start:start + n], NFFT=512, Fs=sr, noverlap=448,
                    cmap="magma", vmin=-120)
        ax.set_title(f"[{lab}]", fontsize=12)
        ax.set_ylim(0, 8000)
        ax.set_xlabel("Время, с")
    axes[0].set_ylabel("Частота, Гц")
    fig.suptitle("Спектрограммы шипящих согласных: шумоподобный сигнал без гармоник")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(PNG_DIR / "lab1_fricatives_spectrograms.png", dpi=150)
    plt.close(fig)

    # спектры (энергетические профили)
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), sharey=True)
    for ax, (s, e_), lab in zip(axes, segs2, FRICATIVES):
        freqs, db = spectrum(x2[s:e_], sr)
        ax.plot(freqs, db, lw=0.7)
        ax.set_xlim(0, 8000)
        ax.set_ylim(-60, 5)
        ax.set_title(f"[{lab}]", fontsize=12)
        ax.set_xlabel("Частота, Гц")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Спектр, дБ")
    fig.suptitle("Спектры шипящих согласных в изоляции")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(PNG_DIR / "lab1_fricatives_spectra.png", dpi=150)
    plt.close(fig)

    # ---------- sample3: слоги ----------
    x3, sr3 = load("1.4.2_fricatives/sample3.wav")
    segs3 = detect_segments(x3, sr3)[:4]
    segs3.sort()
    assert len(segs3) == 4, f"sample3: найдено {len(segs3)} сегментов"
    print("sample3.wav (слоги):")
    for (s, e_), lab in zip(segs3, SYLLABLES):
        print(f"  «{lab}» {s/sr3:.2f}–{e_/sr3:.2f} с")

    draw_wave_labels(
        x3, sr3, segs3, SYLLABLES,
        "Осциллограмма слогов «фа са ша ха» (sample3.wav)",
        "lab1_syllables_wave.png",
    )

    # сравнение: шипящая в изоляции vs в слоге (осциллограмма)
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.5))
    for col, lab in enumerate(FRICATIVES):
        s2, e2 = segs2[col]
        s3, e3 = segs3[col]
        # в слоге берём первую треть (доля шипящей перед гласной)
        syl = x3[s3:e3]
        cut = len(syl) // 3
        fric_in_syl = syl[:cut]
        vow_in_syl = syl[cut:]

        ax = axes[0, col]
        n = min(len(x2[s2:e2]), int(0.5 * sr))
        ax.plot(np.arange(n) / sr, x2[s2:s2 + n], lw=0.5)
        ax.set_title(f"[{lab}] в изоляции", fontsize=10)
        ax.set_xlabel("Время, с")
        ax.set_ylabel("Амплитуда")

        ax = axes[1, col]
        n3 = min(len(fric_in_syl), int(0.5 * sr3))
        ax.plot(np.arange(n3) / sr3, fric_in_syl[:n3], lw=0.5, color="darkorange")
        ax.set_title(f"начало «{lab}а»", fontsize=10)
        ax.set_xlabel("Время, с")
        ax.set_ylabel("Амплитуда")
    fig.suptitle(
        "Шипящая в изоляции (верх) и в слоге после гласной части (низ):\n"
        "в слоге шипящая звучит в контексте — накладывается артикуляция гласной",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(PNG_DIR / "lab1_fricative_in_syllable.png", dpi=150)
    plt.close(fig)

    # спектрограммы слогов
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), sharey=True)
    for ax, (s, e_), lab in zip(axes, segs3, SYLLABLES):
        seg = x3[s:e_]
        ax.specgram(seg, NFFT=512, Fs=sr3, noverlap=448, cmap="magma", vmin=-120)
        ax.set_title(f"«{lab}»", fontsize=12)
        ax.set_ylim(0, 8000)
        ax.set_xlabel("Время, с")
    axes[0].set_ylabel("Частота, Гц")
    fig.suptitle("Спектрограммы слогов: шипящая + гласная (гармоническая структура справа)")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(PNG_DIR / "lab1_syllables_spectrograms.png", dpi=150)
    plt.close(fig)

    # таблица метрик
    lines = [
        "| Фонема | Начало, с | Конец, с | Периодичность (АКФ) | Вывод |",
        "|---|---|---|---|---|",
    ]
    for m in metrics:
        per = "слабая" if m["per"] < 0.5 else "выраженная"
        concl = "шум, нет периодика" if m["per"] < 0.5 else "есть периодик"
        lines.append(
            f"| [{m['ph']}] | {m['t0']:.2f} | {m['t1']:.2f} | {m['per']:.2f} ({per}) | {concl} |"
        )
    (Path(__file__).parent / "fricatives_metrics.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
