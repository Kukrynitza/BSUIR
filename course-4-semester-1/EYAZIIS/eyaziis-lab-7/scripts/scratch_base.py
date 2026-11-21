"""Черновой разбор фонетической базы лабораторной работы 1."""

import numpy as np

from speech_utils import (db, detect_segments, energy, f0_contour,
                          load_lab5)

FILES = ["1.4.1_vowels/sample1.wav", "1.4.1_vowels/sample1b.wav",
         "1.4.2_fricatives/sample2.wav", "1.4.2_fricatives/sample3.wav",
         "1.4.3_stops_nasals/sample4.wav", "1.4.3_stops_nasals/sample5.wav"]

for f in FILES:
    x, sr = load_lab5(f)
    segs = detect_segments(x, sr, min_dur=0.08, merge_gap=0.12)
    print("=" * 78)
    print(f, f"{len(x) / sr:.2f} s, пик {db(np.max(np.abs(x))):.1f} dBFS, сегментов {len(segs)}")
    for k, (a, b) in enumerate(segs, 1):
        seg = x[a:b]
        t, fc = f0_contour(seg, sr)
        ok = ~np.isnan(fc)
        f0 = float(np.median(fc[ok])) if ok.any() else float("nan")
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        fr = np.fft.rfftfreq(len(seg), 1 / sr)
        cent = float((sp * fr).sum() / max(sp.sum(), 1e-12))
        # профиль огибающей внутри сегмента (20 отсчётов)
        e = energy(seg, sr, 0.01)
        prof = "".join(" .:-=+*#%@"[min(9, int(10 * np.sqrt(v / max(e.max(), 1e-12))))]
                       for v in e[::max(1, len(e) // 30)][:30])
        print(f"  {k}: {a / sr:5.2f}-{b / sr:5.2f} ({len(seg) / sr:.2f} s) "
              f"пик {db(np.max(np.abs(seg))):5.1f} rms {db(np.sqrt(np.mean(seg ** 2))):5.1f} "
              f"F0 {f0:5.0f} центр {cent:5.0f} |{prof}|")
