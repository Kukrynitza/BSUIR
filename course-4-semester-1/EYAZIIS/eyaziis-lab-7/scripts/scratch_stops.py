"""Детальный разбор взрывных и носовых в sample4."""

import numpy as np

from speech_utils import db, load_lab5

x, sr = load_lab5("1.4.3_stops_nasals/sample4.wav")
for name, a, b in [("b", 0.70, 1.26), ("d", 2.39, 2.87),
                   ("m", 4.01, 4.45), ("n", 5.54, 6.00)]:
    seg = x[int(a * sr):int(b * sr)]
    n = int(0.005 * sr)
    print("=" * 60)
    print(name, f"len {len(seg) / sr:.2f} s, clip {int(np.sum(np.abs(seg) > 0.99))}")
    for i in range(0, min(len(seg), int(0.30 * sr)), n):
        w = seg[i:i + n]
        print(f"  {i / sr * 1000:5.0f} ms  peak {db(np.max(np.abs(w))):6.1f}  rms {db(np.sqrt(np.mean(w ** 2))):6.1f}")
