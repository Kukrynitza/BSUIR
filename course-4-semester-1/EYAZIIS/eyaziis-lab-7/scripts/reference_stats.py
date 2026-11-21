"""Метрики эталонных фраз для отчёта."""

from speech_utils import AUDIO_ROOT, contour_stats, db, load

for stem in ("phrase1_one_syntagma", "phrase2_enumeration",
             "phrase3_question", "phrase4_statement"):
    x, sr = load(AUDIO_ROOT / "3.2_phrases" / f"{stem}.wav")
    st = contour_stats(x, sr)
    print(f"{stem} dur {len(x) / sr:.2f} med {st['f0_med']:.0f} "
          f"min {st['f0_min']:.0f} max {st['f0_max']:.0f} "
          f"head {st['head']:.0f} tail {st['tail']:.0f} "
          f"dst {st['delta_st']:+.1f} peak {db(x.max()):.1f}")
