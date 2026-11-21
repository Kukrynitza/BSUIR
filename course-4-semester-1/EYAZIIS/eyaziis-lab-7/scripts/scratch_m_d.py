"""Спектрограммы опорных сегментов: [м] из sample4, [д] из слога до."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import spectrogram

from speech_utils import AUDIO_ROOT, PNG_DIR, load, load_lab5

items = [
    ("sample4 [m]", *load_lab5("1.4.3_stops_nasals/sample4.wav")[0][
        int(4.01 * 16000):int(4.45 * 16000)], 16000),
]
x, sr = load_lab5("1.4.3_stops_nasals/sample4.wav")
items = [("sample4 [m]", x[int(4.01 * sr):int(4.45 * sr)], sr)]
x2, _ = load(AUDIO_ROOT / "3.3.5_syllables/syl_10_do.wav")
items.append(("syl_10_do", x2[:int(0.20 * sr)], sr))

fig, axes = plt.subplots(2, 1, figsize=(12, 6))
for ax, (name, y, sr) in zip(axes, items):
    f, t, S = spectrogram(y, sr, nperseg=256, noverlap=224, scaling="spectrum")
    Sdb = 10 * np.log10(np.maximum(S, 1e-12))
    ax.pcolormesh(t * 1000, f, Sdb, shading="auto", cmap="magma",
                  vmin=Sdb.max() - 45, vmax=Sdb.max())
    ax.set_ylim(0, 5000)
    ax.set_title(name)
    ax.set_ylabel("Гц")
    ax.set_xlabel("мс")
fig.tight_layout()
fig.savefig(PNG_DIR / "scratch_m_d.png", dpi=130)
print("ok")
