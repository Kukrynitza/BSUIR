"""Задание 2.3 — работа с мелодическими контурами (аналог Sound Forge).

Исходник: 2.3_melody/mono_student.wav — монотонная фраза
«Студент писал реферат».

Реализованы аналоги инструментов Sound Forge:
  * Effect -> Pitch -> Bend   — плавное изменение F0 по заданному контуру
                                 (гранулярный OLA-синтез, длительность сохраняется);
  * Effects -> Pitch -> Shift — постоянный сдвиг тона всего сигнала;
  * Process -> Fade -> Graphic — усиление амплитуды ударного слова;
  * Process -> Time Stretch    — удлинение ударного слова.

Результаты: audio/lab2/2.3_melody/derived/*.wav
"""

import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from speech_utils import AUDIO_ROOT, PNG_DIR, ROOT, load
from analyze_intonation import f0_track

SRC_DIR = AUDIO_ROOT / "2.3_melody"
OUT_DIR = SRC_DIR / "derived"

# Границы слов «Студент писал реферат» и их центры (по осциллограмме)
WORDS = [(0.99, 1.78), (1.90, 2.58), (2.78, 3.46)]
CENTERS = [1.38, 2.24, 3.12]
WORD_NAMES = ["Студент", "писал", "реферат"]


# ---------------------------------------------------------------- обработка
def pv_stretch(x: np.ndarray, sr: int, rate: float, n_fft: int = 1024,
               hop: int = 256) -> np.ndarray:
    """Растяжение/сжатие по времени в rate раз с сохранением тона.

    Фаза каждого бина переносится по мгновенной частоте (phase vocoder).
    """
    from scipy.signal import stft, istft
    n_fft = min(n_fft, 2 ** int(np.floor(np.log2(max(len(x) - 1, 32)))))
    hop = max(n_fft // 4, 1)
    _, _, Z = stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft - hop,
                   window="hann", boundary="zeros", padded=True)
    M = Z.shape[1]
    hop_out = max(int(round(hop * rate)), 1)
    T_out = max(int(round(M * rate)), 2)
    mag, ang = np.abs(Z), np.angle(Z)
    adv = 2 * np.pi * hop * np.arange(Z.shape[0]) / n_fft
    phase = ang[:, 0].copy()
    out = np.zeros((Z.shape[0], T_out), dtype=complex)
    out[:, 0] = mag[:, 0] * np.exp(1j * phase)
    for k in range(1, T_out):
        m = min(int(round(k * rate)), M - 1)
        prev = min(int(round((k - 1) * rate)), M - 1)
        dm = max(m - prev, 1)
        d = np.mod(ang[:, m] - ang[:, prev] - adv * dm + np.pi,
                   2 * np.pi) - np.pi
        phase = phase + adv * rate + d * (rate / dm)
        out[:, k] = mag[:, m] * np.exp(1j * phase)
    _, y = istft(out, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_out,
                 window="hann", boundary="zeros")
    return y


def pitch_shift(x: np.ndarray, sr: int, r: float) -> np.ndarray:
    """Постоянный сдвиг тона в r раз без изменения длительности."""
    from scipy.signal import resample_poly
    if abs(r - 1) < 1e-3:
        return x
    y = resample_poly(x, 100, max(int(round(r * 100)), 1))  # длина / r
    y = pv_stretch(y, sr, r)                                # назад к длине
    if len(y) >= len(x):
        return y[:len(x)]
    return np.pad(y, (0, len(x) - len(y)))


def granular_bend(x: np.ndarray, sr: int, ratio, block: float = 0.12,
                  hop: float = 0.06) -> np.ndarray:
    """Изменение F0 по кривой ratio(t) без изменения длительности.

    Сигнал обрабатывается блоками с постоянным коэффициентом тона,
    блоки складываются с перекрытием (плавный мелодический контур).
    """
    n_b, h = int(block * sr), int(hop * sr)
    win = np.hanning(n_b)
    out = np.zeros(len(x) + n_b)
    wsum = np.zeros(len(x) + n_b)
    for start in range(0, len(x), h):
        seg = x[start:start + n_b]
        if len(seg) < n_b:
            seg = np.pad(seg, (0, n_b - len(seg)))
        r = max(float(ratio(min((start + n_b / 2) / sr, (len(x) - 1) / sr))),
                0.3)
        y = pitch_shift(seg, sr, r)
        out[start:start + n_b] += y * win
        wsum[start:start + n_b] += win
    return out[:len(x)] / np.maximum(wsum[:len(x)], 1e-3)


def fade_words(x: np.ndarray, sr: int, gains) -> np.ndarray:
    """Плавное изменение амплитуды слов gains=[g1, g2, g3]."""
    env = np.ones(len(x))
    ramp = int(0.02 * sr)
    for (a, b), g in zip(WORDS, gains):
        i0, i1 = int(a * sr), int(b * sr)
        seg = np.full(i1 - i0, g)
        if len(seg) > 2 * ramp:
            seg[:ramp] = np.linspace(1, g, ramp)
            seg[-ramp:] = np.linspace(g, 1, ramp)
        env[i0:i1] = seg
    return x * env


def time_stretch_word(x: np.ndarray, sr: int, a: float, b: float,
                      factor: float) -> np.ndarray:
    """Удлинение участка [a, b] в factor раз (phase vocoder)."""
    i0, i1 = int(a * sr), int(b * sr)
    seg = pv_stretch(x[i0:i1], sr, factor)
    need = int((i1 - i0) * factor)
    seg = seg[:need] if len(seg) >= need else np.pad(seg, (0, need - len(seg)))
    return np.concatenate([x[:i0], seg, x[i1:]])


def make_ratio(kind: str, accent: int, t0: float, t1: float, f0_src):
    """Кривая коэффициента F0: отношение целевого контура к исходному."""
    span = t1 - t0
    center = CENTERS[accent]
    width = (WORDS[accent][1] - WORDS[accent][0]) * 0.6

    def target(t: float) -> float:
        if kind == "stmt":
            base = 140 - 30 * (t - t0) / span          # понижение тона к концу
            shift = -0.25 * width                      # максимум левее центра
        else:
            base = 130
            shift = 0.0
            if t > t1 - 0.45:                          # конечный подъём
                u = (t - (t1 - 0.45)) / 0.45
                base += 75 * u ** 1.5
        return base + 50 * np.exp(-((t - center - shift) ** 2)
                                  / (2 * (width / 2.0) ** 2))

    def ratio(t: float) -> float:
        src = float(np.interp(t, f0_src[0], f0_src[1]))
        return float(np.clip(target(t) / max(src, 80), 0.5, 2.0))

    return ratio


# ------------------------------------------------------------------ метрики
def _source_f0(x: np.ndarray, sr: int):
    """Сглаженный контур F0 исходной записи (для построения ratio)."""
    t, f0 = f0_track(x, sr)
    ok = ~np.isnan(f0)
    f = f0.copy()
    f[~ok] = np.interp(t[~ok], t[ok], f0[ok])
    return t, f


def word_f0(x: np.ndarray, sr: int) -> list[float]:
    t, f0 = f0_track(x, sr)
    out = []
    for a, b in WORDS:
        m = (t >= a) & (t <= b) & ~np.isnan(f0)
        out.append(float(np.median(f0[m])) if m.any() else float("nan"))
    return out


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    x, sr = load("2.3_melody/mono_student.wav")
    t_all = np.arange(len(x)) / sr
    t0, t1 = 0.99, 3.46  # границы речи
    f0_src = _source_f0(x, sr)

    variants = {}
    for kind, suffix in (("stmt", "завершённость"), ("question", "вопрос")):
        for acc in range(3):
            name = f"{'stmt' if kind == 'stmt' else 'quest'}_acc{acc + 1}_f0"
            y = granular_bend(x, sr, make_ratio(kind, acc, t0, t1, f0_src))
            variants[name] = y
            sf.write(OUT_DIR / f"{name}.wav", y, sr, subtype="PCM_16")
            print(f"{name:18s} {suffix}, ударение на «{WORD_NAMES[acc]}»")

    # Fade: усиление ударного (2-го) слова, ослабление остальных
    base = variants["stmt_acc2_f0"]
    faded = fade_words(base, sr, [0.8, 1.7, 0.8])
    sf.write(OUT_DIR / "stmt_acc2_fade.wav", faded, sr, subtype="PCM_16")
    print("stmt_acc2_fade      Fade: амплитуда «писал» ×1.7")

    # Time Stretch: удлинение ударного слова (Fade уже применён)
    stretched = time_stretch_word(base, sr, *WORDS[1], factor=1.35)
    sf.write(OUT_DIR / "stmt_acc2_stretch.wav", stretched, sr, subtype="PCM_16")
    print("stmt_acc2_stretch   Time Stretch: «писал» ×1.35")

    # обе операции вместе (сначала Fade, затем растяжение)
    stretched_faded = time_stretch_word(faded, sr, *WORDS[1], factor=1.35)
    sf.write(OUT_DIR / "stmt_acc2_fade_stretch.wav", stretched_faded, sr,
             subtype="PCM_16")
    print("stmt_acc2_fade_stretch  Fade + Time Stretch")

    # Pitch Shift (постоянный сдвиг) — аналог для второй копии записи
    for ratio, tag in ((1.15, "shift_up"), (0.88, "shift_down")):
        y = pitch_shift(x, sr, ratio)
        sf.write(OUT_DIR / f"{tag}.wav", y, sr, subtype="PCM_16")
        print(f"{tag:18s} Pitch Shift ×{ratio}")

    # ------------------------------------------------ рисунки и метрики
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for row, kind in enumerate(("stmt", "quest")):
        for acc in range(3):
            ax = axes[row, acc]
            y = variants[f"{kind}_acc{acc + 1}_f0"]
            t, f0 = f0_track(y, sr)
            ax.plot(t_all, np.full_like(t_all, np.nan), alpha=0)  # масштаб
            ax.plot(t, f0, color="#c0392b", lw=1.6)
            tt, ff = f0_track(x, sr)
            ax.plot(tt, ff, color="#95a5a6", lw=1, ls="--", alpha=0.8,
                    label="исходная (монотонная)")
            ax.axvspan(*WORDS[acc], color="#f39c12", alpha=0.15)
            ax.set_xlim(0.8, 3.7)
            ax.set_ylim(85, 200)
            ax.grid(alpha=0.3)
            title = "завершённость" if kind == "stmt" else "вопрос"
            ax.set_title(f"{title}, ударение на «{WORD_NAMES[acc]}»", fontsize=9)
            if acc == 0:
                ax.set_ylabel("F0, Гц")
            if row == 1:
                ax.set_xlabel("время, с")
    fig.suptitle("Контуры F0, синтезированные наклоном тона (Pitch Bend)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_melody_f0_contours.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    word2_stretched = (WORDS[1][0],
                       WORDS[1][0] + (WORDS[1][1] - WORDS[1][0]) * 1.35)
    for ax, (y, title, span) in zip(axes, [
            (variants["stmt_acc2_f0"], "исходный (после Pitch Bend)", WORDS[1]),
            (faded, "Fade: «писал» громче", WORDS[1]),
            (stretched_faded, "Fade + Time Stretch", word2_stretched)]):
        env = np.abs(y)
        k = int(0.01 * sr)
        env = np.convolve(env, np.ones(k) / k, "same")[::k]
        tt = np.arange(len(env)) / 100
        ax.plot(tt, 20 * np.log10(env + 1e-9), color="#2b5c8a", lw=1)
        ax.axvspan(*span, color="#f39c12", alpha=0.15)
        ax.set_xlim(0.8, 4.5)
        ax.set_ylim(-70, -10)
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("время, с")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("амплитуда, дБ")
    fig.suptitle("Контуры амплитуды A при усилении и удлинении ударного слова",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_melody_amplitude.png", dpi=150)
    plt.close(fig)

    lines = ["# Метрики мелодических контуров (задание 2.3)", "",
             "Медианная F0 слов «Студент», «писал», «реферат» и превышение "
             "ударного слова над остальными.", "",
             "| Вариант | F0 слова 1, Гц | F0 слова 2, Гц | F0 слова 3, Гц | "
             "Ударное слово | Превышение, полутона |",
             "|---|---|---|---|---|---|"]
    src = word_f0(x, sr)
    lines.append(f"| исходная монотонная | {src[0]:.0f} | {src[1]:.0f} | "
                 f"{src[2]:.0f} | — | — |")
    words_lists = {"stmt_acc1_f0": (0, 1), "stmt_acc2_f0": (1, 2),
                   "stmt_acc3_f0": (2, 3), "quest_acc1_f0": (0, 1),
                   "quest_acc2_f0": (1, 2), "quest_acc3_f0": (2, 3)}
    for name, (acc, num) in words_lists.items():
        wf = word_f0(variants[name], sr)
        others = [wf[i] for i in range(3) if i != acc]
        prom = 12 * np.log2(wf[acc] / np.mean(others))
        lines.append(f"| {name}.wav | {wf[0]:.0f} | {wf[1]:.0f} | {wf[2]:.0f} | "
                     f"«{WORD_NAMES[acc]}» (№{num}) | {prom:+.1f} |")
    (ROOT / "scripts" / "melody_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
