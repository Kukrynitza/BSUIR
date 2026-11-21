"""Нарезка дополнительной записи (задания 2.2.1 п.14 и 2.2.2 п.4).

Исходник: audio/lab2/2.4_extra/extra_phrases.wav — одна сессия с тремя
фразами, разделёнными паузами:
  1. длинная фраза из нескольких акцентных групп;
  2. короткая фраза с вопросительной интонацией;
  3. та же фраза с интонацией утверждения.

Результат: extra_long.wav, extra_q.wav, extra_st.wav (тот же коэффициент
усиления для всех трёх — относительные уровни внутри записи сохраняются).
"""

import numpy as np
import soundfile as sf

from speech_utils import AUDIO_ROOT, detect_segments, load

EXTRA_DIR = AUDIO_ROOT / "2.4_extra"
SRC = EXTRA_DIR / "extra_phrases.wav"
TARGET_PEAK_DB = -9.0


def main() -> None:
    x, sr = load("2.4_extra/extra_phrases.wav")
    segs = detect_segments(x, sr, min_dur=0.5, merge_gap=0.8)
    if len(segs) != 3:
        raise SystemExit(f"ожидалось 3 фразы, найдено {len(segs)}: {segs}")

    peak = np.max(np.abs(x))
    gain = 10 ** ((TARGET_PEAK_DB - 20 * np.log10(peak)) / 20)
    y = x * gain

    names = ["extra_long", "extra_q", "extra_st"]
    for name, (a, b) in zip(names, segs):
        a = max(0, a - int(0.03 * sr))
        b = min(len(y), b + int(0.03 * sr))
        sf.write(EXTRA_DIR / f"{name}.wav", y[a:b], sr, subtype="PCM_16")
        print(f"{name}.wav: {a / sr:.2f} - {b / sr:.2f} с "
              f"({(b - a) / sr:.2f} с), пик {20 * np.log10(np.max(np.abs(y[a:b]))):.1f} дБFS")


if __name__ == "__main__":
    main()
