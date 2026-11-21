"""Спектрограммы слогов для разметки границ согласный/гласный."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import spectrogram

from speech_utils import AUDIO_ROOT, PNG_DIR, load

SYL = AUDIO_ROOT / "3.3.5_syllables"
names = ["syl_01_ma", "syl_02_my", "syl_03_la", "syl_04_ra",
         "syl_05_mu", "syl_06_pa", "syl_07_i", "syl_08_ya",
         "syl_09_ty", "syl_10_do"]

fig, axes = plt.subplots(5, 2, figsize=(13, 13), sharex=False)
for ax, name in zip(axes.ravel(), names):
    x, sr = load(SYL / f"{name}.wav")
    f, t, S = spectrogram(x, sr, nperseg=256, noverlap=224, scaling="spectrum")
    Sdb = 10 * np.log10(np.maximum(S, 1e-12))
    ax.pcolormesh(t * 1000, f, Sdb, shading="auto", cmap="magma",
                  vmin=Sdb.max() - 45, vmax=Sdb.max())
    ax.set_ylim(0, 5000)
    ax.set_title(name, fontsize=10)
    ax.set_ylabel("Гц")
    ax.set_xlabel("мс")
    for g in np.arange(0, t[-1] * 1000, 25):
        ax.axvline(g, color="white", lw=0.3, alpha=0.35)
fig.tight_layout()
fig.savefig(PNG_DIR / "scratch_syl_spec.png", dpi=130)
print("saved")
