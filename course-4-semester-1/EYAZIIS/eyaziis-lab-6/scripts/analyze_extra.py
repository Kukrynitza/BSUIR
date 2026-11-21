"""Анализ дополнительной записи (задания 2.2.1 п.14 и 2.2.2 п.4).

Длинная фраза: автоматическое выделение акцентных групп по глубоким
энергетическим минимумам (паузам между синтагмами) и определение главного
ударного слога в каждой группе.

Пара «вопрос / утверждение»: сопоставление мелодических контуров F0 одной
и той же фразы при разной интонации.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d, median_filter

from speech_utils import AUDIO_ROOT, PNG_DIR, ROOT, load

EXTRA_DIR = AUDIO_ROOT / "2.4_extra"


def energy_db(x: np.ndarray, sr: int, smooth: int = 3):
    fr = int(0.01 * sr)
    e = np.array([np.sqrt(np.mean(x[i * fr:(i + 1) * fr] ** 2))
                  for i in range(len(x) // fr)])
    es = uniform_filter1d(e, smooth)
    return 20 * np.log10(np.maximum(es, 1e-9) / es.max())


def f0_contour(x: np.ndarray, sr: int, win: float = 0.05,
               hop: float = 0.01, strength_min: float = 0.30):
    """Контур F0 по нормированной автокорреляции кадров 50 мс."""
    n, h = int(win * sr), int(hop * sr)
    t, f, rms = [], [], []
    for i in range(0, len(x) - n, h):
        w = x[i:i + n].copy()
        rms.append(np.sqrt(np.mean(w ** 2)))
        w -= w.mean()
        ac = np.correlate(w, w, "full")[len(w) - 1:]
        ac /= max(ac[0], 1e-12)
        lo, hi = sr // 340, sr // 70
        k = lo + int(np.argmax(ac[lo:hi]))
        t.append((i + n / 2) / sr)
        f.append(sr / k if ac[k] >= strength_min else np.nan)
    t, f = np.array(t), np.array(f)
    rms = np.array(rms)
    # кадры с малой энергией (паузы, затухание) не анализируем
    f[rms < 0.06 * rms.max()] = np.nan
    ok = ~np.isnan(f)
    if ok.sum() > 5:
        f[~ok] = np.interp(t[~ok], t[ok], f[ok])
        f = median_filter(f, 5)
        # устранение октавных ошибок: приводим каждый кадр к ближайшей
        # октаве относительно плавно обновляемой опорной частоты
        prev = float(np.median(f))
        for i in range(len(f)):
            # только понижение на октаву: ошибки оценивания дают завышение
            k = max(0, int(round(np.log2(f[i] / prev))))
            f[i] /= 2 ** k
            prev = 0.9 * prev + 0.1 * f[i]
        f = median_filter(f, 5)
    return t, f


def db(x: float) -> float:
    return 20 * np.log10(max(x, 1e-9))


def accent_groups(x: np.ndarray, sr: int):
    """Границы акцентных групп по глубоким минимумам энергии."""
    edb = energy_db(x, sr)
    mins, _ = find_peaks(-edb, prominence=40, distance=int(0.4 * 100))
    bounds = [0.0] + [float(i) * 0.01 for i in mins] + [len(x) / sr]
    return list(zip(bounds[:-1], bounds[1:])), edb


def group_stats(x: np.ndarray, sr: int, a: float, b: float,
                t: np.ndarray, f0: np.ndarray) -> dict:
    seg = x[int(a * sr):int(b * sr)]
    m = (t >= a) & (t <= b)
    ff = f0[m]
    fr = int(0.01 * sr)
    e = np.array([np.sqrt(np.mean(seg[i * fr:(i + 1) * fr] ** 2))
                  for i in range(max(len(seg) // fr, 1))])
    es = uniform_filter1d(e, 3)
    i_acc = int(np.argmax(es))
    return {
        "dur": b - a,
        "peak": db(np.max(np.abs(seg))),
        "rms": db(np.sqrt(np.mean(seg ** 2))),
        "f0_med": float(np.median(ff)),
        "f0_max": float(np.max(ff)),
        "acc_time": a + i_acc * 0.01,
    }


def contour_stats(x: np.ndarray, sr: int) -> dict:
    """Параметры мелодического контура: начало, максимум, конец, диапазон."""
    t, f0 = f0_contour(x, sr)
    head = np.median(f0[:max(len(f0) // 5, 1)])
    i = int(np.argmax(f0))
    tail = np.median(f0[-max(len(f0) // 7, 1):])
    q10, q90 = np.percentile(f0, [10, 90])
    return {
        "head": float(head),
        "peak": float(f0[i]),
        "peak_pos": float(t[i] / t[-1]),
        "tail": float(tail),
        "rise_st": 12 * np.log2(f0[i] / head),
        "fall_st": 12 * np.log2(tail / f0[i]),
        "range_st": 12 * np.log2(q90 / q10),
    }


def main() -> None:
    xl, sr = load("2.4_extra/extra_long.wav")
    xq, _ = load("2.4_extra/extra_q.wav")
    xs, _ = load("2.4_extra/extra_st.wav")

    groups, edb = accent_groups(xl, sr)
    t, f0 = f0_contour(xl, sr)

    lines = ["# Дополнительная проверка (задание 2.2.1 п. 14, 2.2.2 п. 4)", "",
             "## Акцентные группы в длинной фразе", "",
             "| Группа | Интервал, с | Длит., с | Пик, дБFS | RMS, дБFS | "
             "Медиана F0, Гц | Макс. F0, Гц | Ударный слог, с |",
             "|---|---|---|---|---|---|---|---|"]
    for k, (a, b) in enumerate(groups, 1):
        st = group_stats(xl, sr, a, b, t, f0)
        lines.append(
            f"| АГ{k} | {a:.2f}--{b:.2f} | {st['dur']:.2f} | {st['peak']:.1f} | "
            f"{st['rms']:.1f} | {st['f0_med']:.0f} | {st['f0_max']:.0f} | "
            f"{st['acc_time']:.2f} |")

    q = contour_stats(xq, sr)
    s = contour_stats(xs, sr)
    lines += ["", "## Пара «вопрос / утверждение»", "",
              "| Фраза | Начало, Гц | Максимум, Гц | Положение макс. | "
              "Конец, Гц | Подъём до макс., пт | Спад после макс., пт | "
              "Диапазон, пт |",
              "|---|---|---|---|---|---|---|---|",
              f"| вопрос | {q['head']:.0f} | {q['peak']:.0f} | {q['peak_pos']:.2f} | "
              f"{q['tail']:.0f} | {q['rise_st']:+.1f} | {q['fall_st']:+.1f} | "
              f"{q['range_st']:.1f} |",
              f"| утверждение | {s['head']:.0f} | {s['peak']:.0f} | "
              f"{s['peak_pos']:.2f} | {s['tail']:.0f} | {s['rise_st']:+.1f} | "
              f"{s['fall_st']:+.1f} | {s['range_st']:.1f} |"]

    # ------------------------------------------------------------ рисунок 1
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    tt = np.arange(len(xl)) / sr
    ax = axes[0]
    ax.plot(tt, xl / np.max(np.abs(xl)), lw=0.5, color="#2b5c8a")
    for k, (a, b) in enumerate(groups, 1):
        ax.axvspan(a, b, alpha=0.12, color="#f39c12")
        ax.text((a + b) / 2, 0.92, f"АГ{k}", ha="center", fontsize=10,
                color="#b9770e")
    ax.set_ylabel("амплитуда (норм.)")
    ax.set_ylim(-1.05, 1.05)
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(t, f0, color="#c0392b", lw=1.8, label="F0")
    for k, (a, b) in enumerate(groups, 1):
        ax.axvspan(a, b, alpha=0.12, color="#f39c12")
        m = (t >= a) & (t <= b)
        ax.plot(t[m][int(np.argmax(f0[m]))], np.max(f0[m]), "o",
                color="#2b5c8a", ms=5)
    ax.set_ylabel("F0, Гц")
    ax.set_xlabel("время, с")
    ax.set_ylim(80, max(300, f0.max() * 1.1))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower left")
    fig.suptitle("Акцентные группы в длинной фразе: границы — по паузам "
                 "между синтагмами, точки — главные ударные слоги", fontsize=11)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_extra_accents.png", dpi=150)
    plt.close(fig)

    # ------------------------------------------------------------ рисунок 2
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for y, name, color in ((xq, "вопрос «Ты дома?»", "#c0392b"),
                           (xs, "утверждение «Ты дома.»", "#2b5c8a")):
        t2, f2 = f0_contour(y, sr)
        rel = t2 / t2[-1]
        ax.plot(rel, f2, lw=2, color=color, label=name)
    ax.set_xlabel("относительное время фразы")
    ax.set_ylabel("F0, Гц")
    ax.set_title("Одна и та же фраза с разной интонацией")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab2_extra_qs.png", dpi=150)
    plt.close(fig)

    (ROOT / "scripts" / "extra_metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
