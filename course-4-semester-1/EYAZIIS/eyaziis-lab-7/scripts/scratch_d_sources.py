"""Поиск взрывных [д] в sample4, sample5 и слоге до."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import spectrogram

from speech_utils import (AUDIO_ROOT, PNG_DIR, db, load, load_lab5)

items = []
x, sr = load_lab5("1.4.3_stops_nasals/sample4.wav")
items.append(("sample4 [d] 2.39-2.87", x[int(2.39 * sr):int(2.87 * sr)], sr))
x5, _ = load_lab5("1.4.3_stops_nasals/sample5.wav")
items.append(("sample5 [da] 2.02-2.80", x5[int(2.02 * sr):int(2.80 * sr)], sr))
xd, _ = load(AUDIO_ROOT / "3.3.5_syllables/syl_10_do.wav")
items.append(("syl_10_do full", xd, sr))

fig, axes = plt.subplots(3, 1, figsize=(12, 9))
for ax, (name, y, sr) in zip(axes, items):
    f, t, S = spectrogram(y, sr, nperseg=256, noverlap=224, scaling="spectrum")
    Sdb = 10 * np.log10(np.maximum(S, 1e-12))
    ax.pcolormesh(t * 1000, f, Sdb, shading="auto", cmap="magma",
                  vmin=Sdb.max() - 45, vmax=Sdb.max())
    ax.set_ylim(0, 6000)
    ax.set_title(f"{name}  peak {db(np.max(np.abs(y))):.1f} dBFS")
    ax.set_ylabel("Гц")
    ax.set_xlabel("мс")
fig.tight_layout()
fig.savefig(PNG_DIR / "scratch_d_sources.png", dpi=130)

for name, y, sr in items:
    print("=" * 64)
    print(name, f"{len(y) / sr:.2f} s")
    n = int(0.01 * sr)
    for i in range(0, min(len(y), int(0.35 * sr)), n):
        w = y[i:i + n]
        print(f"  {i / sr * 1000:4.0f} ms peak {db(np.max(np.abs(w))):6.1f} "
              f"rms {db(np.sqrt(np.mean(w ** 2))):6.1f}")
