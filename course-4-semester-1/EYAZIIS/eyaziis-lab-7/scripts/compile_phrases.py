"""Задание 3.3.2. Компиляция фраз из фонем.

Фразы собираются из фонемной базы задания 3.3.1: последовательность
фонем задаётся вручную, каждая фонема обрезается до типовой длительности
и приводится к типовому уровню, после чего фрагменты склеиваются.
Просодика (мелодика, ударение) на этом этапе не задаётся.
"""

import numpy as np

from speech_utils import AUDIO_ROOT, ROOT, db, f0_contour, load, ramp, write

BASE = AUDIO_ROOT / "3.3.1_phonemes"
OUT = AUDIO_ROOT / "3.3.2_phoneme_synth"

# типовые длительности (мс) и уровни (RMS или пик) по классам
DUR = {"m": 90, "l": 90, "r": 65, "j": 60, "d": 70, "p": 70, "t": 70}
VOWEL_DUR = {"stress": 220, "vowel": 160}
FAST_DUR = {"m": 80, "l": 80, "r": 60, "j": 55, "d": 70, "p": 70, "t": 70}
FAST_VOWEL = {"stress": 170, "vowel": 120}
LEVEL = {  # целевой уровень фрагмента
    "vowel": ("rms", -18.0),
    "sonor": ("rms", -23.0),
    "j": ("rms", -24.0),
    "d": ("peak", -12.0),
    "p": ("peak", -15.0),
    "t": ("peak", -15.0),
}

# фраза: список слов; слово — список (фонема, тип)
PHRASES = {
    "phrase1": {
        "text": "Мама мыла раму.",
        "words": [
            [("m", "sonor"), ("a", "stress"), ("m", "sonor"), ("a", "vowel")],
            [("m", "sonor"), ("y", "stress"), ("l", "sonor"), ("a", "vowel")],
            [("r", "sonor"), ("a", "stress"), ("m", "sonor"), ("u", "stress")],
        ],
        "pauses": [100, 100, 0],
    },
    "phrase2": {
        "text": "Мама, папа и я.",
        "words": [
            [("m", "sonor"), ("a", "stress"), ("m", "sonor"), ("a", "vowel")],
            [("p", "p"), ("a", "stress"), ("p", "p"), ("a", "vowel")],
            [("i", "vowel")],
            [("j", "j"), ("a", "stress")],
        ],
        "pauses": [450, 300, 40, 0],
    },
    "phrase3": {
        "text": "Ты дома?",
        "fast": True,
        "words": [
            [("t", "t"), ("y", "stress")],
            [("d", "d"), ("o", "stress"), ("m", "sonor"), ("a", "vowel")],
        ],
        "pauses": [30, 0],
    },
    "phrase4": {
        "text": "Ты дома.",
        "fast": True,
        "words": [
            [("t", "t"), ("y", "stress")],
            [("d", "d"), ("o", "stress"), ("m", "sonor"), ("a", "vowel")],
        ],
        "pauses": [30, 0],
    },
}


def take(seg: np.ndarray, n: int, where: str = "middle",
         sr: int = 16000) -> np.ndarray:
    """Взять n отсчётов из сегмента; короткий — дополнить тишиной."""
    if len(seg) >= n:
        if where == "start":
            s = 0
        elif where == "end":
            s = len(seg) - n
        else:
            s = (len(seg) - n) // 2
        y = seg[s:s + n].copy()
    else:
        y = seg.copy()
        pad = n - len(y)
        if where == "start":
            y = np.concatenate([np.zeros(pad), y])
        elif where == "end":
            y = np.concatenate([y, np.zeros(pad)])
        else:
            y = np.concatenate([np.zeros(pad // 2), y,
                                np.zeros(pad - pad // 2)])
    return y


def set_level(y: np.ndarray, kind: str) -> np.ndarray:
    key = "vowel" if kind in ("stress", "vowel") else kind
    mode, target = LEVEL[key]
    cur = db(np.sqrt(np.mean(y ** 2))) if mode == "rms" else db(np.max(np.abs(y)))
    if np.isfinite(cur):
        y = y * 10 ** ((target - cur) / 20)
    return y


def build_phrase(spec: dict) -> tuple[np.ndarray, list]:
    fast = spec.get("fast", False)
    dur = FAST_DUR if fast else DUR
    vdur = FAST_VOWEL if fast else VOWEL_DUR
    parts = []
    log = []
    for wi, word in enumerate(spec["words"]):
        for ph, kind in word:
            seg = load(BASE / f"{ph}.wav")[0]
            if ph in dur:
                n = int(dur[ph] * 16)
                where = "start" if ph in ("p", "t", "d") else "middle"
            else:
                n = int(vdur[kind] * 16)
                where = "middle"
            y = take(seg, n, where)
            y = set_level(y, kind)
            y = ramp(y, 16000, 3.0)
            parts.append(y)
            t, f = f0_contour(y, 16000)
            ok = ~np.isnan(f)
            log.append((ph, kind, len(y) / 16000,
                        db(np.sqrt(np.mean(y ** 2))),
                        float(np.median(f[ok])) if ok.any() else float("nan")))
        if spec["pauses"][wi] > 0:
            parts.append(np.zeros(int(spec["pauses"][wi] * 16)))
    return np.concatenate(parts), log


def main() -> None:
    lines = ["# Компиляция из фонем (задание 3.3.2)", ""]
    for name, spec in PHRASES.items():
        y, log = build_phrase(spec)
        y = y * 10 ** ((-6.0 - db(np.max(np.abs(y)))) / 20)
        write(OUT / f"{name}.wav", y, 16000)
        lines += [f"## {name}: {spec['text']}", "",
                  f"Длительность {len(y) / 16000:.2f} с, пик "
                  f"{db(np.max(np.abs(y))):.1f} дБFS.", "",
                  "| Фонема | Тип | Длит., с | RMS, дБFS | $F_0$, Гц |",
                  "|---|---|---|---|---|"]
        for ph, kind, d, rr, f0 in log:
            lines.append(f"| [{ph}] | {kind} | {d:.3f} | {rr:.1f} | "
                         f"{'' if np.isnan(f0) else f'{f0:.0f}'} |")
        lines.append("")
    (ROOT / "scripts" / "phoneme_synth.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
