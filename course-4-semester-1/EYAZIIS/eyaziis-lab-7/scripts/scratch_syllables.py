"""Покадровый разбор слогов: энергия, центроид, F0 (для разметки границ)."""

import numpy as np

from speech_utils import AUDIO_ROOT, f0_contour, load, load_lab5

SYL = AUDIO_ROOT / "3.3.5_syllables"


def profile(x, sr, label):
    win = int(0.02 * sr)
    hop = int(0.01 * sr)
    print("=" * 78)
    print(label, f"{len(x) / sr:.2f} s")
    _, f0 = f0_contour(x, sr)
    print("  t(ms)  E(dB)  centroid  F0")
    for i in range(0, len(x) - win, hop):
        w = x[i:i + win]
        e = 20 * np.log10(max(np.sqrt(np.mean(w ** 2)), 1e-9))
        sp = np.abs(np.fft.rfft(w * np.hanning(win), 2048))
        fr = np.fft.rfftfreq(2048, 1 / sr)
        c = (sp * fr).sum() / max(sp.sum(), 1e-12)
        k = min(i // hop, len(f0) - 1)
        mark = ""
        if i < 0.06 * sr:
            mark = " <"
        print(f"  {i / sr * 1000:5.0f}  {e:6.1f}  {c:7.0f}  {f0[k]:5.0f}{mark}")


for name in ("syl_06_pa", "syl_09_ty", "syl_10_do", "syl_03_la",
             "syl_04_ra", "syl_08_ya", "syl_01_ma", "syl_07_i"):
    x, sr = load(SYL / f"{name}.wav")
    profile(x[:int(0.35 * sr)], sr, name)

x, sr = load_lab5("1.4.1_vowels/sample1b.wav")
profile(x[int(0.89 * sr):int(1.58 * sr)], sr, "sample1b [ja]")
