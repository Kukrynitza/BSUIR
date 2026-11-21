"""Общие утилиты для третьей части работы (компиляционный синтез)."""

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.ndimage import median_filter
from scipy.signal import find_peaks

ROOT = Path(__file__).resolve().parents[1]
AUDIO_ROOT = ROOT / "audio" / "lab3"
PNG_DIR = ROOT / "eyazis-report-7" / "png"
LAB5_AUDIO = ROOT.parent / "eyaziis-lab-5" / "audio" / "lab1"

SR = 16000

MIN_DUR = 0.06   # с
MERGE_GAP = 0.10  # с


# --------------------------------------------------------------------- звук
def load(path, root: Path | None = None):
    p = Path(path)
    if not p.is_absolute() and root is not None:
        p = root / p
    x, sr = sf.read(p, dtype="float64")
    if x.ndim > 1:
        x = x[:, 0]
    return x, sr


def load_lab5(rel_path: str):
    return load(LAB5_AUDIO / rel_path)


def load_lab3(rel_path: str):
    return load(AUDIO_ROOT / rel_path)


def write(path, x: np.ndarray, sr: int, target_peak_db: float | None = None):
    """Запись файла; при необходимости — нормировка по пику."""
    if target_peak_db is not None:
        x = x * 10 ** ((target_peak_db - db(np.max(np.abs(x)))) / 20)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    sf.write(p, np.clip(x, -1.0, 1.0), sr, subtype="PCM_16")
    return p


def db(v: float) -> float:
    return 20 * np.log10(max(float(v), 1e-12))


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x ** 2)))


# -------------------------------------------------------------- сегментация
def energy(x: np.ndarray, sr: int, frame: float = 0.01):
    n = int(frame * sr)
    m = len(x) // n
    return np.sqrt(np.array([np.mean(x[i * n:(i + 1) * n] ** 2) for i in range(m)]))


def detect_segments(x: np.ndarray, sr: int,
                    min_dur: float = MIN_DUR, merge_gap: float = MERGE_GAP,
                    thr_fraction: float = 0.08):
    frame = int(0.01 * sr)
    e = energy(x, sr, 0.01)
    thr = e.max() * thr_fraction
    segs = []
    i = 0
    while i < len(e):
        if e[i] > thr:
            j = i
            while j < len(e) and e[j] > thr:
                j += 1
            segs.append([i * frame, j * frame])
            i = j
        else:
            i += 1
    merged = []
    for s, e_ in segs:
        if merged and (s - merged[-1][1]) / sr < merge_gap:
            merged[-1][1] = e_
        else:
            merged.append([s, e_])
    return [(s, e_) for s, e_ in merged if (e_ - s) / sr >= min_dur]


def trim(x: np.ndarray, sr: int, thr_db: float = -30.0,
         pad: float = 0.01):
    """Обрезать тишину по краям фрагмента."""
    e = energy(x, sr, 0.005)
    if len(e) == 0:
        return x
    thr = e.max() * 10 ** (thr_db / 20)
    idx = np.where(e > thr)[0]
    if len(idx) == 0:
        return x
    n = int(0.005 * sr)
    a = max(0, idx[0] * n - int(pad * sr))
    b = min(len(x), idx[-1] * n + n + int(pad * sr))
    return x[a:b]


# --------------------------------------------------------------------- F0
def f0_contour(x: np.ndarray, sr: int, win: float = 0.04,
               hop: float = 0.01, strength_min: float = 0.30,
               rms_gate: float = 0.06):
    n, h = int(win * sr), int(hop * sr)
    t, f, lev = [], [], []
    for i in range(0, len(x) - n, h):
        w = x[i:i + n]
        lev.append(np.sqrt(np.mean(w ** 2)))
        w = w - w.mean()
        ac = np.correlate(w, w, "full")[len(w) - 1:]
        ac /= max(ac[0], 1e-12)
        lo, hi = max(sr // 340, 1), sr // 70
        seg = ac[lo:hi]
        # первый достаточно сильный максимум АКФ: защита от выбора
        # субгармоники (половины истинного периода)
        pk, _ = find_peaks(seg)
        strong = pk[seg[pk] >= 0.90 * seg.max()] if len(pk) else np.array([])
        k = lo + int(strong[0]) if len(strong) else lo + int(np.argmax(seg))
        t.append((i + n / 2) / sr)
        f.append(sr / k if ac[k] >= strength_min else np.nan)
    t, f = np.array(t), np.array(f)
    lev = np.array(lev)
    if len(f) == 0:
        return t, f
    f[lev < rms_gate * lev.max()] = np.nan
    ok = ~np.isnan(f)
    if ok.sum() > 5:
        idx = np.where(~ok)[0]
        # длинные паузы не заполняем: контур должен разрываться
        breaks = []
        if len(idx):
            start = idx[0]
            prev = idx[0]
            for i in idx[1:]:
                if i - prev > 1:
                    breaks.append((start, prev))
                    start = i
                prev = i
            breaks.append((start, prev))
        f[~ok] = np.interp(t[~ok], t[ok], f[ok])
        f = median_filter(f, 5)
        # октавные ошибки: только понижение относительно опорной частоты
        prev = float(np.nanmedian(f))
        for i in range(len(f)):
            if np.isnan(f[i]):
                continue
            k = max(0, int(round(np.log2(f[i] / prev))))
            f[i] /= 2 ** k
            prev = 0.9 * prev + 0.1 * f[i]
        f = median_filter(f, 5)
        # глобальная проверка октавных ошибок
        med = float(np.nanmedian(f))
        if np.isfinite(med) and med > 0:
            f[f > 1.7 * med] /= 2
            f[f < 0.55 * med] *= 2
        f = median_filter(f, 5)
        # длинные паузы не заполняем: контур должен разрываться
        for a, b in breaks:
            if (b - a + 1) * hop > 0.12:
                f[a:b + 1] = np.nan
    return t, f


def contour_stats(x: np.ndarray, sr: int):
    t, f = f0_contour(x, sr)
    ok = ~np.isnan(f)
    ff = f[ok]
    if len(ff) < 5:
        return dict(f0_med=float("nan"), f0_min=float("nan"),
                    f0_max=float("nan"), f0_std=0.0,
                    head=float("nan"), tail=float("nan"),
                    delta_st=float("nan"))
    q = max(len(ff) // 4, 1)
    head, tail = float(np.median(ff[:q])), float(np.median(ff[-q:]))
    return dict(f0_med=float(np.median(ff)), f0_min=float(np.min(ff)),
                f0_max=float(np.max(ff)), f0_std=float(np.std(ff)),
                head=head, tail=tail,
                delta_st=12 * np.log2(tail / head))


def pitch_shift(x: np.ndarray, sr: int, semitones: float,
                frame: int = 1024, hop: int = 256) -> np.ndarray:
    """Сдвиг тона без изменения длительности (фазовый вокодер)."""
    from scipy.signal import istft, stft
    if abs(semitones) < 1e-3:
        return x.copy()
    _, _, z = stft(x, fs=sr, window="hann", nperseg=frame,
                   noverlap=frame - hop, padded=False, boundary=None)
    n_bins = z.shape[0]
    factor = 2 ** (semitones / 12)
    src = np.arange(n_bins) / factor
    out = np.zeros_like(z)
    for k in range(z.shape[1]):
        real = np.interp(src, np.arange(n_bins), z[:, k].real, left=0, right=0)
        imag = np.interp(src, np.arange(n_bins), z[:, k].imag, left=0, right=0)
        out[:, k] = real + 1j * imag
    _, y = istft(out, fs=sr, window="hann", nperseg=frame,
                 noverlap=frame - hop, input_onesided=True)
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    return y[:len(x)]


def stretch(x: np.ndarray, sr: int, factor: float,
            frame: int = 1024, hop: int = 256) -> np.ndarray:
    """Изменение длительности без изменения тона (фазовый вокодер)."""
    from scipy.signal import istft, stft
    if abs(factor - 1.0) < 1e-3:
        return x.copy()
    _, _, z = stft(x, fs=sr, window="hann", nperseg=frame,
                   noverlap=frame - hop, padded=False, boundary=None)
    n = z.shape[1]
    m = max(int(round(n / factor)), 2)
    src = np.linspace(0, n - 1, m)
    out = np.zeros((z.shape[0], m), dtype=z.dtype)
    for i, s in enumerate(src):
        a = int(np.floor(s))
        b = min(a + 1, n - 1)
        w = s - a
        out[:, i] = (1 - w) * z[:, a] + w * z[:, b]
    _, y = istft(out, fs=sr, window="hann", nperseg=frame,
                 noverlap=frame - hop, input_onesided=True)
    return y


def _envelope(mag: np.ndarray, nfft: int, order: int = 36) -> np.ndarray:
    """Сглаженная спектральная оболочка (кепстральное сглаживание)."""
    logm = np.log(mag + 1e-10)
    cep = np.fft.irfft(logm, n=nfft, axis=0)
    cep[order:nfft - order] = 0
    return np.exp(np.fft.rfft(cep, axis=0).real)


def _princarg(a: np.ndarray) -> np.ndarray:
    return (a + np.pi) % (2 * np.pi) - np.pi


def pitch_shift_curve(x: np.ndarray, sr: int, times: np.ndarray,
                      semitones: np.ndarray, frame: int = 1024,
                      hop: int = 256, order: int = 36) -> np.ndarray:
    """Сдвиг тона по заданному контуру с сохранением формант.

    times — моменты (с), semitones — сдвиг в полутонах в этих точках;
    между точками сдвиг интерполируется. Оболочка спектра не сдвигается,
    поэтому форманты (и тембр гласных) сохраняются.
    """
    from scipy.signal import istft, stft
    if len(times) == 0:
        return x.copy()
    _, _, z = stft(x, fs=sr, window="hann", nperseg=frame,
                   noverlap=frame - hop, boundary=None, padded=False)
    mag, phase = np.abs(z), np.angle(z)
    env = _envelope(mag, frame, order)
    res = mag / np.maximum(env, 1e-8)
    bins = np.arange(frame // 2 + 1)
    n_frames = mag.shape[1]
    t_frames = (np.arange(n_frames) * hop + frame / 2) / sr
    st = np.interp(t_frames, times, semitones, left=semitones[0],
                   right=semitones[-1])
    ratios = 2 ** (st / 12)
    out = np.zeros_like(mag)
    phase_out = np.zeros_like(phase)
    phase_out[:, 0] = phase[:, 0]
    for m in range(n_frames):
        r = ratios[m]
        src = bins / r
        out[:, m] = env[:, m] * np.interp(src, bins, res[:, m], left=0, right=0)
        if m > 0:
            dphi = _princarg(phase[:, m] - phase[:, m - 1]
                             - 2 * np.pi * bins * hop / frame)
            f_src = (bins + dphi * frame / (2 * np.pi * hop)) * sr / frame
            f_out = r * np.interp(src, bins, f_src, left=0, right=0)
            phase_out[:, m] = phase_out[:, m - 1] + 2 * np.pi * f_out * hop / sr
    _, y = istft(out * np.exp(1j * phase_out), fs=sr, window="hann",
                 nperseg=frame, noverlap=frame - hop, input_onesided=True)
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    return y[:len(x)]


# ------------------------------------------------------------------- склейка
def ramp(x: np.ndarray, sr: int, ms: float = 8.0,
         mode: str = "both") -> np.ndarray:
    n = min(int(ms * sr / 1000), len(x) // 2)
    if n <= 0:
        return x.copy()
    y = x.copy()
    w = np.linspace(0, 1, n)
    if mode in ("both", "in"):
        y[:n] *= w
    if mode in ("both", "out"):
        y[-n:] *= w[::-1]
    return y


def join(parts, sr: int, fade_ms: float = 8.0) -> np.ndarray:
    """Последовательная склейка фрагментов с плавными фронтами."""
    out = np.zeros(0)
    for p in parts:
        out = np.concatenate([out, ramp(p, sr, fade_ms)])
    return out


def crossfade(a: np.ndarray, b: np.ndarray, sr: int,
              ms: float = 10.0) -> np.ndarray:
    n = min(int(ms * sr / 1000), len(a), len(b))
    if n <= 0:
        return np.concatenate([a, b])
    w = np.linspace(0, 1, n)
    return np.concatenate([a[:-n], a[-n:] * (1 - w) + b[:n] * w, b[n:]])
