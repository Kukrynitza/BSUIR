"""Анализ интонации (задание 2.2.2).

Строятся мелодические контуры F0 для фраз «Саша кушал кашу» с интонацией
завершённости, незавершённости, вопроса и восклицания, а также для
эмоционально окрашенных вариантов. Определяется положение мелодического
максимума и направление движения тона в конце фразы.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter

from speech_utils import AUDIO_ROOT, PNG_DIR, ROOT, load

INT_DIR = AUDIO_ROOT / "2.2.2_intonation"

ITEMS = [
    ("int_statement.wav", "завершённость (.)"),
    ("int_continuation.wav", "незавершённость (,)"),
    ("int_question.wav", "вопрос (?)"),
    ("int_exclamation.wav", "восклицание (!)"),
]
EMOTIONS = [
    ("int_statement.wav", "нейтрально"),
    ("emotional_joy.wav", "радость"),
    ("emotional_sad.wav", "огорчение"),
]


def _f0_frame(w: np.ndarray, sr: int, strength_min: float = 0.45) -> float:
    w = w - w.mean()
    ac = np.correlate(w, w, mode="full")[len(w) - 1:]
    lag_min, lag_max = sr // 400, sr // 60
    if lag_max >= len(ac):
        lag_max = len(ac) - 1
    lag = lag_min + int(np.argmax(ac[lag_min:lag_max]))
    if ac[lag] / ac[0] < strength_min:
        return float("nan")
    return sr / lag


def f0_track(x: np.ndarray, sr: int, frame: float = 0.04, hop: float = 0.01):
    nf, nh = int(frame * sr), int(hop * sr)
    times, f0, levels = [], [], []
    for i in range(0, len(x) - nf, nh):
        times.append((i + nf / 2) / sr)
        f0.append(_f0_frame(x[i:i + nf], sr))
        levels.append(np.sqrt(np.mean(x[i:i + nf] ** 2)))
    f0 = np.array(f0)
    levels = np.array(levels)
    # кадры с малой энергией (фон, паузы) не анализируем
    f0[levels < 0.08 * levels.max()] = np.nan
    ok = ~np.isnan(f0)
    # отбрасываем одиночные октавные выбросы
    for i in range(len(f0)):
        lo, hi = max(0, i - 4), min(len(f0), i + 5)
        neigh = f0[lo:hi][~np.isnan(f0[lo:hi])]
        if not np.isnan(f0[i]) and len(neigh) > 2:
            med = np.median(neigh)
            if abs(f0[i] - med) > 0.25 * med:
                f0[i] = np.nan
    ok = ~np.isnan(f0)
    f0f = f0.copy()
    if ok.sum() > 5:
        idx = np.arange(len(f0))
        f0f[~ok] = np.interp(idx[~ok], idx[ok], f0[ok])
        f0f = median_filter(f0f, 5)
        # маскируем длинные невокализованные участки
        bad = ~ok
        run = np.convolve(bad, np.ones(15), "same")
        f0f[run > 7] = np.nan
    else:
        f0f[:] = np.nan
    return np.array(times), f0f


def speech_span(x: np.ndarray, sr: int):
    fr = int(0.01 * sr)
    e = np.array([np.sqrt((x[i * fr:(i + 1) * fr] ** 2).mean())
                  for i in range(len(x) // fr)])
    idx = np.where(e > e.max() * 0.08)[0]
    return idx[0] * fr / sr, idx[-1] * fr / sr, e / e.max()


def stats(times: np.ndarray, f0: np.ndarray, t0: float, t1: float) -> dict:
    m = (times >= t0) & (times <= t1) & ~np.isnan(f0)
    tt, ff = times[m], f0[m]
    if len(ff) < 5:
        return {}
    v0, v1 = tt[0], tt[-1]
    span = max(v1 - v0, 1e-6)
    i_max = int(np.argmax(ff))
    q1, q2 = np.percentile(ff, [25, 75])
    tail = ff[tt >= v1 - 0.25 * span].mean()
    mid = ff[(tt >= v0 + 0.25 * span) & (tt <= v0 + 0.6 * span)].mean()
    return {
        "median": float(np.median(ff)),
        "max": float(ff.max()),
        "max_pos": float((tt[i_max] - v0) / span),
        "max_time": float(tt[i_max]),
        "range_st": 12 * np.log2(q2 / q1),
        "tail_delta_st": 12 * np.log2(tail / mid),
    }


def draw_contours() -> list[str]:
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    lines = ["# Метрики интонации (задание 2.2.2)", "",
             "| Интонация | Длит. речи, с | Медиана F0, Гц | Макс. F0, Гц | "
             "Положение макс. | ΔF0 конца, полутона |",
             "|---|---|---|---|---|---|"]
    for ax, (fname, title) in zip(axes.ravel(), ITEMS):
        x, sr = load(f"2.2.2_intonation/{fname}")
        times, f0 = f0_track(x, sr)
        t0, t1, env = speech_span(x, sr)
        st = stats(times, f0, t0, t1)

        t_env = np.arange(len(env)) * 0.01
        ax.plot(t_env, env * 40 + 60, color="#95a5a6", lw=0.8, alpha=0.7,
                label="огибающая (масштаб)")
        ax.plot(times, f0, color="#c0392b", lw=2, label="F0")
        if st:
            ax.axvline(st["max_time"], color="#2980b9", ls="--", lw=1)
            ax.plot(st["max_time"], st["max"], "o", color="#2980b9")
            for lvl, lab in [(np.nanmin(f0), "низкий"),
                             (st["median"], "средний"),
                             (st["max"], "высокий")]:
                ax.axhline(lvl, color="#bdc3c7", ls=":", lw=0.8)
                ax.text(t1 + 0.05, lvl, lab, va="center", fontsize=7,
                        color="#7f8c8d")
            lines.append(
                f"| {title} | {t1 - t0:.2f} | {st['median']:.0f} | "
                f"{st['max']:.0f} | {st['max_pos']:.2f} | "
                f"{st['tail_delta_st']:+.1f} |")
        ax.set_title(f"{title} — {fname}", fontsize=9)
        ax.set_xlabel("время, с")
        ax.set_ylabel("F0, Гц")
        ax.set_xlim(0, times[-1])
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc="lower left")
    fig.suptitle("Мелодические контуры F0 для разных интонационных типов", fontsize=11)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_intonation_contours.png", dpi=150)
    plt.close(fig)
    return lines


def draw_emotions() -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#7f8c8d", "#e67e22", "#2980b9"]
    for (fname, title), color in zip(EMOTIONS, colors):
        x, sr = load(f"2.2.2_intonation/{fname}")
        times, f0 = f0_track(x, sr)
        t0, t1, _ = speech_span(x, sr)
        m = (times >= t0) & (times <= t1) & ~np.isnan(f0)
        tt = (times[m] - t0) / (t1 - t0)
        med = np.nanmedian(f0[m])
        ax.plot(tt, 12 * np.log2(f0[m] / med), lw=1.8, label=title, color=color)
    ax.set_xlabel("относительное время фразы")
    ax.set_ylabel("F0 относительно медианы, полутона")
    ax.set_title("Влияние эмоциональной окраски на мелодический контур")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_emotion_contours.png", dpi=150)
    plt.close(fig)


def main() -> None:
    lines = draw_contours()
    draw_emotions()
    (ROOT / "scripts" / "intonation_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
