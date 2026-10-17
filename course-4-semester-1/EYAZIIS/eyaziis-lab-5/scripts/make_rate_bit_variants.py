"""Задание 1.3: влияние частоты дискретизации и разрядности на речевой сигнал.

Из эталонной записи (audio/lab1/test.wav, 16 кГц, 16 бит) создаются варианты
с частотами 4/8/16/32 кГц и разрядностями 16/8 бит, метрики и спектрограммы.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "audio" / "lab1" / "test.wav"
OUT_DIR = ROOT / "audio" / "lab1" / "rate_depth"
PNG_DIR = ROOT / "eyazis-report-5" / "png"

RATES = [4000, 8000, 16000, 32000]
BITS = [16, 8]


def quantize8(x: np.ndarray) -> np.ndarray:
    """Квантование сигнала [-1, 1] до 8 бит (знаковое, с возвратом в float)."""
    q = np.clip(np.round(x * 127.0), -127, 127)
    return q / 127.0


def snr_db(ref: np.ndarray, test: np.ndarray) -> float:
    noise = ref - test
    p_sig = np.mean(ref**2)
    p_noi = np.mean(noise**2)
    if p_noi == 0:
        return float("inf")
    return 10.0 * np.log10(p_sig / p_noi)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)

    x16, sr0 = sf.read(SRC, dtype="float64")
    if x16.ndim > 1:
        x16 = x16[:, 0]

    # обрезка начальной и конечной тишины (с запасом 0.3 с)
    frame = int(0.02 * sr0)
    n_frames = len(x16) // frame
    energy = np.sqrt(
        np.array(
            [(x16[i * frame : (i + 1) * frame] ** 2).mean() for i in range(n_frames)]
        )
    )
    thr = energy.max() * 0.03
    active = np.where(energy > thr)[0]
    if len(active):
        t0 = max(0, (active[0] - int(0.3 / 0.02)) * frame)
        t1 = min(len(x16), (active[-1] + int(0.3 / 0.02)) * frame)
        x16 = x16[t0:t1]

    print(f"source: {sr0} Hz, {len(x16)/sr0:.2f} s (после обрезки тишины)")

    metrics = []
    fig_spec, axes = plt.subplots(len(BITS), len(RATES), figsize=(14, 6))
    fig_wave, axes_w = plt.subplots(len(BITS), len(RATES), figsize=(14, 6))

    for row, bits in enumerate(BITS):
        for col, fs in enumerate(RATES):
            # ресемплинг
            if fs == sr0:
                y = x16.copy()
            else:
                g = np.gcd(fs, sr0)
                y = resample_poly(x16, fs // g, sr0 // g)
            y = y / max(np.abs(y).max(), 1e-12) * max(np.abs(x16).max(), 1e-12)

            # квантование
            if bits == 8:
                yq = quantize8(y)
                subtype = "PCM_U8"
            else:
                yq = np.clip(y, -1.0, 1.0 - 1 / 32768)
                subtype = "PCM_16"

            fname = OUT_DIR / f"phrase_{fs // 1000}k_{bits}bit.wav"
            sf.write(fname, yq, fs, subtype=subtype)
            size = fname.stat().st_size

            # SNR относительно сигнала с разрядностью 16 бит при той же частоте
            y16 = np.clip(y, -1.0, 1.0 - 1 / 32768)
            snr = snr_db(y16, yq)

            nyq = fs / 2
            bandwidth = min(4000, nyq)  # речь ~0–4 кГц
            metrics.append(
                {
                    "file": fname.name,
                    "fs": fs,
                    "bits": bits,
                    "size_kb": size / 1024,
                    "rate_kbps": fs * bits / 1000,
                    "snr": snr,
                    "bandwidth": bandwidth,
                }
            )
            print(f"  {fname.name:24s} {size/1024:8.1f} KB  SNR={snr:6.2f} dB")

            # спектрограмма
            ax = axes[row, col]
            ax.specgram(yq, NFFT=512, Fs=fs, noverlap=384, cmap="magma", vmin=-120)
            ax.set_title(f"{fs//1000} kHz, {bits} bit", fontsize=10)
            ax.set_ylabel("Частота, Гц" if col == 0 else "")
            ax.set_xlabel("Время, с" if row == len(BITS) - 1 else "")
            ax.set_ylim(0, min(4000, nyq))

            # осциллограмма (фрагмент 1 с в середине речи)
            axw = axes_w[row, col]
            t0 = len(yq) // 3
            seg = yq[t0 : t0 + fs]
            axw.plot(np.arange(len(seg)) / fs, seg, lw=0.4)
            axw.set_title(f"{fs//1000} kHz, {bits} bit", fontsize=10)
            axw.set_ylim(-0.2, 0.2)
            axw.set_xlabel("Время, с" if row == len(BITS) - 1 else "")
            axw.set_ylabel("Амплитуда" if col == 0 else "")

    fig_spec.suptitle(
        "Спектрограммы речевого сигнала при разных частотах дискретизации и разрядности",
        fontsize=12,
    )
    fig_spec.tight_layout(rect=(0, 0, 1, 0.96))
    fig_spec.savefig(PNG_DIR / "lab1_rate_bit_spectrograms.png", dpi=150)

    fig_wave.suptitle(
        "Осциллограммы (фрагмент 1 с) при разных частотах дискретизации и разрядности",
        fontsize=12,
    )
    fig_wave.tight_layout(rect=(0, 0, 1, 0.96))
    fig_wave.savefig(PNG_DIR / "lab1_rate_bit_waves.png", dpi=150)

    # таблица метрик в markdown
    lines = [
        "| Файл | F, кГц | Разрядность | Объём, КБ | Поток, кбит/с | Полоса, Гц | SNR квантования, дБ |",
        "|---|---|---|---|---|---|---|",
    ]
    for m in metrics:
        snr = "—" if np.isinf(m["snr"]) else f"{m['snr']:.1f}"
        lines.append(
            f"| {m['file']} | {m['fs']//1000} | {m['bits']} | {m['size_kb']:.1f} "
            f"| {m['rate_kbps']:.0f} | {m['bandwidth']} | {snr} |"
        )
    md = "\n".join(lines)
    (ROOT / "scripts" / "rate_depth_metrics.md").write_text(md, encoding="utf-8")
    print("\n" + md)


if __name__ == "__main__":
    main()
