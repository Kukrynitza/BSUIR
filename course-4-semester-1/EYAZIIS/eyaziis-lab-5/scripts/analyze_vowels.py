"""Задание 1.4.1: исследование гласных фонем речевого сигнала.

sample1.wav  — гласные [а о у э ы и]
sample1b.wav — йотированные «я ё ю е» (= [й] + гласная)

Сегментация по паузам, зарисовки осциллограмм/огибающих,
поиск периода F0 автокорреляцией, спектры с гармониками.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.signal import find_peaks, hilbert

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio" / "lab1"
PNG = ROOT / "eyazis-report-5" / "png"

VOWELS = ["а", "о", "у", "э", "ы", "и"]
IOTED = ["я", "ё", "ю", "е"]

MIN_DUR = 0.2  # с — минимальная длительность фонемы
MERGE_GAP = 0.15  # с — склеивать сегменты с паузой короче этого


def load(name: str):
    x, sr = sf.read(AUDIO / name, dtype="float64")
    if x.ndim > 1:
        x = x[:, 0]
    return x, sr


def detect_segments(x: np.ndarray, sr: int):
    frame = int(0.01 * sr)
    n = len(x) // frame
    e = np.sqrt(
        np.array([(x[i * frame : (i + 1) * frame] ** 2).mean() for i in range(n)])
    )
    thr = e.max() * 0.05
    active = e > thr

    # грубые сегменты
    segs = []
    i = 0
    while i < len(active):
        if active[i]:
            j = i
            while j < len(active) and active[j]:
                j += 1
            segs.append([i * frame, j * frame])
            i = j
        else:
            i += 1

    # склейка близких + отсечение коротких щелчков
    merged = []
    for s, e_ in segs:
        if merged and (s - merged[-1][1]) / sr < MERGE_GAP:
            merged[-1][1] = e_
        else:
            merged.append([s, e_])
    return [(s, e_) for s, e_ in merged if (e_ - s) / sr >= MIN_DUR]


def estimate_f0(seg: np.ndarray, sr: int) -> float:
    """F0 автокорреляцией по центральному окну 40 мс."""
    n = min(int(0.04 * sr), len(seg))
    start = (len(seg) - n) // 2
    w = seg[start : start + n]
    w = w - w.mean()
    ac = np.correlate(w, w, mode="full")[len(w) - 1 :]
    lag_min, lag_max = sr // 400, sr // 60  # 60..400 Гц
    if lag_max >= len(ac):
        lag_max = len(ac) - 1
    peak_lags, _ = find_peaks(ac[lag_min:lag_max])
    if len(peak_lags) == 0:
        return float("nan")
    lag = peak_lags[np.argmax(ac[lag_min : lag_max][peak_lags])] + lag_min
    return sr / lag


def spectrum(seg: np.ndarray, sr: int, nfft: int = 4096):
    n = min(nfft, len(seg))
    start = (len(seg) - n) // 2
    w = seg[start : start + n] * np.hanning(n)
    sp = np.abs(np.fft.rfft(w, nfft))
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    db = 20 * np.log10(sp / max(sp.max(), 1e-12) + 1e-12)
    return freqs, db


def main() -> None:
    PNG.mkdir(parents=True, exist_ok=True)
    metrics = []

    # ---------- sample1: гласные ----------
    x, sr = load("sample1.wav")
    segs = detect_segments(x, sr)
    assert len(segs) == 6, f"ожидалось 6 гласных, найдено {len(segs)}"
    print(f"sample1.wav: {len(segs)} гласных")

    # осциллограмма всего файла с подписями
    fig, ax = plt.subplots(figsize=(12, 3))
    t = np.arange(len(x)) / sr
    ax.plot(t, x, lw=0.3)
    for (s, e_), lab in zip(segs, VOWELS):
        ts, te = s / sr, e_ / sr
        ax.axvspan(ts, te, alpha=0.25, color="orange")
        ax.text((ts + te) / 2, ax.get_ylim()[1] * 0.85, f"[{lab}]",
                ha="center", fontsize=12)
        f0 = estimate_f0(x[s:e_], sr)
        metrics.append(
            {"ph": lab, "t0": ts, "t1": te, "dur": te - ts, "f0": f0}
        )
        print(f"  [{lab}] {ts:.2f}–{te:.2f} с  F0={f0:.1f} Гц")
    ax.set_xlabel("Время, с")
    ax.set_ylabel("Амплитуда")
    ax.set_title("Осциллограмма гласных фонем [а о у э ы и] (sample1.wav)")
    fig.tight_layout()
    fig.savefig(PNG / "lab1_sample1_wave.png", dpi=150)

    # зарисовки огибающих (2×3)
    fig, axes = plt.subplots(2, 3, figsize=(12, 6))
    for ax, (s, e_), lab in zip(axes.flat, segs, VOWELS):
        seg = x[s:e_]
        tt = np.arange(len(seg)) / sr
        env = np.abs(hilbert(seg))
        # сглаживание огибающей
        k = max(1, int(0.01 * sr))
        env = np.convolve(env, np.ones(k) / k, mode="same")
        ax.plot(tt, seg, lw=0.4, color="steelblue", label="сигнал")
        ax.plot(tt, env, lw=1.2, color="darkorange", label="огибающая")
        ax.set_title(f"[{lab}]  F0≈{estimate_f0(seg, sr):.0f} Гц", fontsize=11)
        ax.set_xlabel("Время, с")
        ax.set_ylabel("Амплитуда")
        ax.set_ylim(-0.35, 0.35)
    axes[0, 0].legend(fontsize=8, loc="upper right")
    fig.suptitle("Осциллограммы и огибающие гласных фонем")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(PNG / "lab1_vowels_envelopes.png", dpi=150)

    # один период фонемы [а]
    s, e_ = segs[0]
    seg = x[s:e_]
    f0 = estimate_f0(seg, sr)
    period = int(round(sr / f0))
    start = (len(seg) - 2 * period) // 2
    two_periods = seg[start : start + 2 * period]
    tt = np.arange(len(two_periods)) / sr * 1000  # мс
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(tt, two_periods, lw=1.5)
    ax.axvline(period / sr * 1000, color="red", ls="--", lw=1)
    ax.text(period / sr * 1000 * 1.04, ax.get_ylim()[0] + 0.02,
            f"период T0 ≈ {period/sr*1000:.2f} мс\n(F0 ≈ {f0:.0f} Гц)", color="red",
            va="bottom")
    ax.set_xlabel("Время, мс")
    ax.set_ylabel("Амплитуда")
    ax.set_title("Два периода фонемы [а] (выделяется один период для Play Looped)")
    fig.tight_layout()
    fig.savefig(PNG / "lab1_vowel_a_period.png", dpi=150)

    # спектры всех гласных
    fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharey=True)
    for ax, (s, e_), lab in zip(axes.flat, segs, VOWELS):
        freqs, db = spectrum(x[s:e_], sr)
        ax.plot(freqs, db, lw=0.7)
        # гармоники: локальные пики вблизи F0, 2F0, 3F0...
        f0 = estimate_f0(x[s:e_], sr)
        if np.isfinite(f0):
            for h in range(1, 8):
                fh = h * f0
                if fh > 4000:
                    break
                band = (freqs >= fh - f0 * 0.4) & (freqs <= fh + f0 * 0.4)
                idx_band = np.where(band)[0]
                if len(idx_band) == 0:
                    continue
                idx = idx_band[np.argmax(db[idx_band])]
                ax.plot([freqs[idx]], [db[idx]], "rv", ms=5)
        ax.set_xlim(0, 4000)
        ax.set_ylim(-60, 5)
        ax.set_title(f"[{lab}]  F0≈{f0:.0f} Гц", fontsize=11)
        ax.set_xlabel("Частота, Гц")
        ax.set_ylabel("Спектр, дБ")
        ax.grid(alpha=0.3)
    fig.suptitle("Спектры гласных фонем (▲ — гармоники F0, 2F0, 3F0...)")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(PNG / "lab1_vowels_spectra.png", dpi=150)

    # ---------- sample1b: йотированные ----------
    xb, srb = load("sample1b.wav")
    segsb = detect_segments(xb, srb)
    assert len(segsb) == 4, f"ожидалось 4 фонемы, найдено {len(segsb)}"
    print(f"sample1b.wav: {len(segsb)} йотированные")

    fig, axes = plt.subplots(4, 2, figsize=(11, 10))
    for row, ((s, e_), lab) in enumerate(zip(segsb, IOTED)):
        seg = xb[s:e_]
        tt = np.arange(len(seg)) / srb

        ax = axes[row, 0]
        ax.plot(tt, seg, lw=0.5)
        ax.set_title(f"«{lab}» = [й + ...] — осциллограмма", fontsize=10)
        ax.set_ylabel("Амплитуда")
        ax.set_xlabel("Время, с")

        ax = axes[row, 1]
        n = min(4096, len(seg))
        start = (len(seg) - n) // 2
        ax.specgram(seg[start : start + n], NFFT=512, Fs=srb,
                    noverlap=448, cmap="magma", vmin=-120)
        ax.set_ylim(0, 4000)
        ax.set_title("Спектрограмма (фрагмент)", fontsize=10)
        ax.set_xlabel("Время, с")
        ax.set_ylabel("Частота, Гц")
        print(f"  «{lab}» {s/srb:.2f}–{e_/srb:.2f} с")
    fig.suptitle("Йотированные гласные: две компоненты [й] + гласная")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(PNG / "lab1_ioted.png", dpi=150)

    # метрики
    lines = [
        "| Фонема | Начало, с | Конец, с | Длительность, с | F0, Гц |",
        "|---|---|---|---|---|",
    ]
    for m in metrics:
        lines.append(
            f"| [{m['ph']}] | {m['t0']:.2f} | {m['t1']:.2f} "
            f"| {m['dur']:.2f} | {m['f0']:.0f} |"
        )
    (ROOT / "scripts" / "vowels_metrics.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
