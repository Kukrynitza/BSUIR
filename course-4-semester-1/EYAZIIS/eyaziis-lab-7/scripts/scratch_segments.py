"""Черновая разметка исходных записей: сегменты при разных паузах."""

import numpy as np

from speech_utils import AUDIO_ROOT, detect_segments, energy, load

for name in ("phrases_all.wav", "syllables_all.wav"):
    x, sr = load(AUDIO_ROOT.parent.parent / name)
    print("=" * 70)
    print(name, f"{len(x) / sr:.2f} s, peak {20 * np.log10(np.max(np.abs(x))):.1f} dBFS")
    for gap in (0.25, 0.35, 0.45, 0.6):
        segs = detect_segments(x, sr, min_dur=0.05, merge_gap=gap)
        print(f"  gap {gap:.2f}: {len(segs)} ->",
              ", ".join(f"{a / sr:.2f}-{b / sr:.2f}" for a, b in segs))
    e = energy(x, sr, 0.01)
    print("  профиль (1 символ = 100 мс):")
    line = ""
    for i in range(0, len(e), 10):
        v = 20 * np.log10(max(e[i:i + 10].max(), 1e-9) / e.max())
        line += "#" if v > -6 else ("o" if v > -12 else ("+" if v > -20 else ("-" if v > -30 else ".")))
    print("  " + line)
