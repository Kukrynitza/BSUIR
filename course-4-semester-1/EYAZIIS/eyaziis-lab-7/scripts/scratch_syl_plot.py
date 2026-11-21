"""Рисунок для ручной разметки слогов: осциллограмма и энергия."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from speech_utils import AUDIO_ROOT, PNG_DIR, db, energy, load

SYL = AUDIO_ROOT / "3.3.5_syllables"
names = ["syl_01_ma", "syl_02_my", "syl_03_la", "syl_04_ra",
         "syl_05_mu", "syl_06_pa", "syl_07_i", "syl_08_ya",
         "syl_09_ty", "syl_10_do"]

fig, axes = plt.subplots(5, 2, figsize=(13, 14))
for ax, name in zip(axes.ravel(), names):
    x, sr = load(SYL / f"{name}.wav")
    t = np.arange(len(x)) / sr
    ax.plot(t, x, lw=0.5, color="#2b5c8a")
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlim(0, min(len(x) / sr, 0.6))
    ax.set_title(name, fontsize=10)
    ax.grid(alpha=0.25)
    e = energy(x, sr, 0.01)
    ax2 = ax.twinx()
    ax2.plot(np.arange(len(e)) * 0.01, 20 * np.log10(np.maximum(e, 1e-9) / e.max()),
             color="#c0392b", lw=1)
    ax2.set_ylim(-60, 2)
    ax2.set_yticks([-40, -20, 0])
    for g in np.arange(0, min(len(x) / sr, 0.6), 0.05):
        ax.axvline(g, color="gray", lw=0.4, alpha=0.5)
fig.tight_layout()
fig.savefig(PNG_DIR / "scratch_syllables.png", dpi=120)
print("saved")
