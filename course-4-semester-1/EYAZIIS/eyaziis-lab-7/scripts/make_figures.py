"""Иллюстрации для отчёта: фонетическая база, эталонные фразы, слоги."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from speech_utils import (AUDIO_ROOT, PNG_DIR, db, f0_contour, load)

PHON = AUDIO_ROOT / "3.3.1_phonemes"
REF = AUDIO_ROOT / "3.2_phrases"
SYL = AUDIO_ROOT / "3.3.5_syllables"
SYNTH = AUDIO_ROOT / "3.3.5_syllable_synth"
PROS = AUDIO_ROOT / "3.3.6_prosody"
PHON_SYNTH = AUDIO_ROOT / "3.3.2_phoneme_synth"

PHONEMES = ["a", "o", "u", "e", "y", "i", "m", "j", "l", "r", "p", "t", "d"]


def norm(y):
    return y / max(np.max(np.abs(y)), 1e-9)


def phoneme_base():
    fig, axes = plt.subplots(4, 4, figsize=(13, 9))
    axes = axes.ravel()
    for ax, name in zip(axes, PHONEMES):
        x, sr = load(PHON / f"{name}.wav")
        t = np.arange(len(x)) / sr * 1000
        ax.plot(t, norm(x), lw=0.6, color="#2b5c8a")
        ax.set_ylim(-1.1, 1.1)
        ax.set_xlim(0, t[-1])
        ax.set_title(f"[{name}]  {len(x) / sr * 1000:.0f} мс", fontsize=10)
        ax.grid(alpha=0.25)
        ax.set_yticks([])
        ax.set_xlabel("мс", fontsize=8)
    for ax in axes[len(PHONEMES):]:
        ax.axis("off")
    fig.suptitle("Фонетическая база: изолированные фонемы (задание 3.3.1)",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_phoneme_base.png", dpi=150)
    plt.close(fig)


def reference():
    items = [
        ("phrase1_one_syntagma", "Мама мыла раму. (одна синтагма)"),
        ("phrase2_enumeration", "Мама, папа и я. (перечисление)"),
        ("phrase3_question", "Ты дома? (вопрос)"),
        ("phrase4_statement", "Ты дома. (утверждение)"),
    ]
    fig, axes = plt.subplots(4, 2, figsize=(13, 10),
                             gridspec_kw={"width_ratios": [3, 2]})
    for row, (stem, title) in enumerate(items):
        x, sr = load(REF / f"{stem}.wav")
        t = np.arange(len(x)) / sr
        axes[row, 0].plot(t, norm(x), lw=0.5, color="#2b5c8a")
        axes[row, 0].set_ylim(-1.05, 1.05)
        axes[row, 0].set_yticks([])
        axes[row, 0].set_title(title, fontsize=10, loc="left")
        axes[row, 0].grid(alpha=0.25)
        tf, f = f0_contour(x, sr)
        axes[row, 1].plot(tf, f, lw=1.8, color="#c0392b")
        axes[row, 1].set_title("$F_0(t)$", fontsize=10, loc="left")
        axes[row, 1].grid(alpha=0.3)
    for ax in axes[-1]:
        ax.set_xlabel("время, с")
    axes[0, 1].set_ylabel("Гц")
    axes[1, 1].set_ylabel("Гц")
    axes[2, 1].set_ylabel("Гц")
    axes[3, 1].set_ylabel("Гц")
    fig.suptitle("Эталонные фразы и их мелодические контуры (задание 3.2)",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_reference.png", dpi=150)
    plt.close(fig)


def syllables():
    names = ["syl_01_ma", "syl_02_my", "syl_03_la", "syl_04_ra",
             "syl_05_mu", "syl_06_pa", "syl_07_i", "syl_08_ya",
             "syl_09_ty", "syl_10_do"]
    labels = ["ма", "мы", "ла", "ра", "му", "па", "и", "я", "ты", "до"]
    fig, axes = plt.subplots(5, 2, figsize=(13, 11))
    for ax, name, lab in zip(axes.ravel(), names, labels):
        x, sr = load(SYL / f"{name}.wav")
        t = np.arange(len(x)) / sr * 1000
        ax.plot(t, norm(x), lw=0.6, color="#2b5c8a")
        ax.set_ylim(-1.05, 1.05)
        ax.set_xlim(0, t[-1])
        ax.set_title(f"«{lab}»  ({name})  {len(x) / sr * 1000:.0f} мс",
                     fontsize=10)
        ax.grid(alpha=0.25)
        ax.set_yticks([])
        ax.set_xlabel("мс", fontsize=8)
    fig.suptitle("Слоги для слоговой компиляции (задание 3.3.5)", fontsize=13)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_syllables.png", dpi=150)
    plt.close(fig)


def variants():
    items = [
        ("эталон", REF / "phrase4_statement.wav", "#2b5c8a"),
        ("компиляция из фонем", PHON_SYNTH / "phrase4.wav", "#c0392b"),
        ("компиляция из слогов", SYNTH / "phrase4.wav", "#e67e22"),
        ("с просодической обработкой", PROS / "phrase4.wav", "#27ae60"),
    ]
    fig, axes = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
    for ax, (label, path, color) in zip(axes, items):
        x, sr = load(path)
        ax.plot(np.arange(len(x)) / sr, norm(x), lw=0.6, color=color)
        ax.set_ylim(-1.05, 1.05)
        ax.set_yticks([])
        ax.set_title(label, fontsize=10, loc="left")
        ax.grid(alpha=0.25)
    axes[-1].set_xlabel("время, с")
    fig.suptitle("Фраза «Ты дома.»: эталон и три способа компиляции",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(PNG_DIR / "lab3_variants_compare.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    phoneme_base()
    reference()
    syllables()
    variants()
    print("saved")
