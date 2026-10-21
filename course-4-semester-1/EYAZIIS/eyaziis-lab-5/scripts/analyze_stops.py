"""Задание 1.4.3: взрывные [б д] и носовые [м н], слоги «ба да ма на».

Демонстрация коартикуляции: взрывные/носовые согласные не выделяются
отдельно от гласной — артикуляции накладываются.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from speech_utils import (
    PNG_DIR,
    detect_segments,
    estimate_f0,
    load,
    periodicity_strength,
)

PHONEMES = ["б", "д", "м", "н"]
SYLLABLES = ["ба", "да", "ма", "на"]
KIND = {"б": "взрывная", "д": "взрывная", "м": "носовая", "н": "носовая"}


def draw_wave_labels(x, sr, segs, labels, title, fname):
    fig, ax = plt.subplots(figsize=(11, 3))
    t = np.arange(len(x)) / sr
    ax.plot(t, x, lw=0.3)
    ymin, ymax = ax.get_ylim()
    for (s, e_), lab in zip(segs, labels):
        ts, te = s / sr, e_ / sr
        ax.axvspan(ts, te, alpha=0.25, color="orange")
        ax.text((ts + te) / 2, ymin + (ymax - ymin) * 0.85, lab,
                ha="center", fontsize=12)
    ax.set_xlabel("Время, с")
    ax.set_ylabel("Амплитуда")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(PNG_DIR / fname, dpi=150)
    plt.close(fig)


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)

    # ---------- sample4: отдельные согласные ----------
    x4, sr = load("1.4.3_stops_nasals/sample4.wav")
    segs4 = detect_segments(x4, sr)[:4]
    segs4.sort()
    assert len(segs4) == 4, f"sample4: найдено {len(segs4)}"
    print("sample4.wav ([б д м н] в изоляции):")
    metrics = []
    for (s, e_), lab in zip(segs4, PHONEMES):
        seg = x4[s:e_]
        per = periodicity_strength(seg, sr)
        f0 = estimate_f0(seg, sr)
        print(f"  [{lab}] {s/sr:.2f}–{e_/sr:.2f} с ({(e_-s)/sr:.2f} с)  "
              f"периодичность={per:.2f}  "
              f"F0={'н/д' if not np.isfinite(f0) else f'{f0:.0f} Гц'}")
        metrics.append((lab, s / sr, e_ / sr, per))

    draw_wave_labels(
        x4, sr, segs4, [f"[{l}]\n({KIND[l]})" for l in PHONEMES],
        "Осциллограмма взрывных и носовых согласных [б д м н] (sample4.wav)",
        "lab1_stops_wave.png",
    )

    # спектрограммы отдельных согласных
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), sharey=True)
    for ax, (s, e_), lab in zip(axes, segs4, PHONEMES):
        seg = x4[s:e_]
        ax.specgram(seg, NFFT=512, Fs=sr, noverlap=448, cmap="magma", vmin=-120)
        ax.set_title(f"[{lab}] ({KIND[lab]})", fontsize=11)
        ax.set_ylim(0, 8000)
        ax.set_xlabel("Время, с")
    axes[0].set_ylabel("Частота, Гц")
    fig.suptitle("Спектрограммы согласных в изоляции")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(PNG_DIR / "lab1_stops_spectrograms.png", dpi=150)
    plt.close(fig)

    # ---------- sample5: слоги ----------
    x5, sr5 = load("1.4.3_stops_nasals/sample5.wav")
    segs5 = detect_segments(x5, sr5)[:4]
    segs5.sort()
    assert len(segs5) == 4, f"sample5: найдено {len(segs5)}"
    print("sample5.wav (слоги):")
    for (s, e_), lab in zip(segs5, SYLLABLES):
        print(f"  «{lab}» {s/sr5:.2f}–{e_/sr5:.2f} с ({(e_-s)/sr5:.2f} с)")

    draw_wave_labels(
        x5, sr5, segs5, SYLLABLES,
        "Осциллограмма слогов «ба да ма на» (sample5.wav)",
        "lab1_syllables2_wave.png",
    )

    # спектрограммы слогов — видно «слияние» согласной с гласной
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), sharey=True)
    for ax, (s, e_), lab in zip(axes, segs5, SYLLABLES):
        seg = x5[s:e_]
        ax.specgram(seg, NFFT=512, Fs=sr5, noverlap=448, cmap="magma", vmin=-120)
        ax.set_title(f"«{lab}»", fontsize=12)
        ax.set_ylim(0, 8000)
        ax.set_xlabel("Время, с")
    axes[0].set_ylabel("Частота, Гц")
    fig.suptitle(
        "Спектрограммы слогов: начало [б]/[д] — короткий взрыв, далее форманты гласной [а];\n"
        "артикуляция согласной накладывается на гласную (коартикуляция)",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(PNG_DIR / "lab1_syllables2_spectrograms.png", dpi=150)
    plt.close(fig)

    # детальный вид начала «ба» и «да» (взрыв + переход к гласной)
    fig, axes = plt.subplots(2, 1, figsize=(10, 5.5))
    for ax, (s, e_), lab in zip(axes, segs5[:2], SYLLABLES[:2]):
        seg = x5[s:e_]
        t = np.arange(len(seg)) / sr5 * 1000  # мс
        ax.plot(t, seg, lw=0.5)
        # граница взрывной — по максимуму производной огибающей громкости
        k = max(1, int(0.004 * sr5))
        env = np.sqrt(np.convolve(seg**2, np.ones(k) / k, mode="same"))
        burst_end = int(np.argmax(np.diff(env[: len(env) // 3]))) * 1
        ax.axvline(burst_end / sr5 * 1000, color="red", ls="--", lw=1,
                   label="конец взрыва (оценка)")
        ax.set_title(f"«{lab}»: начало слога (взрывной согласный → гласная)", fontsize=11)
        ax.set_xlabel("Время, мс")
        ax.set_ylabel("Амплитуда")
        ax.legend(fontsize=9)
    fig.suptitle(
        "Взрывная согласная в слоге: отделить [б]/[д] от [а] невозможно —\n"
        "их артикуляции сливаются (эффект коартикуляции)",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(PNG_DIR / "lab1_coarticulation.png", dpi=150)
    plt.close(fig)

    # таблица
    lines = [
        "| Фонема | Тип | Начало, с | Конец, с | Длительность, с | Периодичность (АКФ) |",
        "|---|---|---|---|---|---|",
    ]
    for lab, t0, t1, per in metrics:
        lines.append(
            f"| [{lab}] | {KIND[lab]} | {t0:.2f} | {t1:.2f} | {t1 - t0:.2f} | {per:.2f} |"
        )
    (Path(__file__).parent / "stops_metrics.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
