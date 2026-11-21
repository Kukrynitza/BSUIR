"""Эксперимент: сдвиг тона с сохранением спектральной оболочки."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import istft, stft

from speech_utils import PNG_DIR, db, f0_contour, load, pitch_shift

SR = 16000


def envelope(mag, nfft, order=36):
    logm = np.log(mag + 1e-10)
    cep = np.fft.irfft(logm, n=nfft, axis=0)
    cep[order:nfft - order] = 0
    return np.exp(np.fft.rfft(cep, axis=0).real)


def princarg(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def shift_fp(x, sr, semitones, nfft=1024, hop=256, order=36):
    r = 2 ** (semitones / 12)
    _, _, Z = stft(x, fs=sr, window="hann", nperseg=nfft,
                   noverlap=nfft - hop, boundary=None, padded=False)
    mag, phase = np.abs(Z), np.angle(Z)
    env = envelope(mag, nfft, order)
    res = mag / np.maximum(env, 1e-8)
    bins = np.arange(nfft // 2 + 1)
    src = bins / r
    res_s = np.empty_like(res)
    for m in range(res.shape[1]):
        res_s[:, m] = np.interp(src, bins, res[:, m], left=0, right=0)
    mag_out = env * res_s

    phase_out = np.zeros_like(phase)
    phase_out[:, 0] = phase[:, 0]
    for m in range(1, phase.shape[1]):
        dphi = princarg(phase[:, m] - phase[:, m - 1]
                        - 2 * np.pi * bins * hop / nfft)
        f_src = (bins + dphi * nfft / (2 * np.pi * hop)) * sr / nfft
        f_out = r * np.interp(src, bins, f_src, left=0, right=0)
        phase_out[:, m] = phase_out[:, m - 1] + 2 * np.pi * f_out * hop / sr

    _, y = istft(mag_out * np.exp(1j * phase_out), fs=sr, window="hann",
                 nperseg=nfft, noverlap=nfft - hop)
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    return y[:len(x)]


def smooth_spectrum(x, sr, nfft=4096, order=36):
    w = x * np.hanning(len(x))
    mag = np.abs(np.fft.rfft(w, nfft))[:, None]
    env = envelope(mag, nfft, order)[:, 0]
    fr = np.fft.rfftfreq(nfft, 1 / sr)
    return fr, 20 * np.log10(np.maximum(env, 1e-12))


def peaks(fr, spec_db, lo=200, hi=3500, n=3):
    from scipy.signal import find_peaks
    idx, _ = find_peaks(spec_db, distance=int(150 / (fr[1] - fr[0])))
    idx = [i for i in idx if lo <= fr[i] <= hi]
    idx = sorted(idx, key=lambda i: spec_db[i], reverse=True)[:n]
    return sorted(fr[i] for i in idx)


x, sr = load(r"D:\git\bsuir-projects\BSUIR\course-4-semester-1\EYAZIIS\eyaziis-lab-7\audio\lab3\3.3.1_phonemes\a.wav")
for st in (2.0, 5.0):
    y = shift_fp(x, sr, st)
    y_plain = pitch_shift(x, sr, st)
    for name, z in (("исходный", x), (f"FP +{st}", y), (f"plain +{st}", y_plain)):
        t, f = f0_contour(z, sr)
        ok = ~np.isnan(f)
        fr, sp = smooth_spectrum(z, sr)
        print(f"{name:12s} F0 {np.median(f[ok]):5.0f} Гц, "
              f"пики оболочки {['%.0f' % p for p in peaks(fr, sp)]}")
    fig, ax = plt.subplots(figsize=(10, 4))
    for name, z, c in (("исходный", x, "#2b5c8a"), (f"FP +{st}", y, "#27ae60"),
                       (f"plain +{st}", y_plain, "#c0392b")):
        fr, sp = smooth_spectrum(z, sr)
        ax.plot(fr, sp, color=c, label=name)
    ax.set_xlim(0, 3500)
    ax.set_ylim(-60, 5)
    ax.set_xlabel("Гц")
    ax.set_ylabel("дБ")
    ax.set_title(f"Спектральная оболочка при сдвиге на {st:+.0f} полутона")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PNG_DIR / f"scratch_shift_{int(st)}.png", dpi=140)
    plt.close(fig)
