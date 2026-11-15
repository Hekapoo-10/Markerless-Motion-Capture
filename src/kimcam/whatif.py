"""P2: bagaimana jika satu aksi diperbaiki; urutan perbaikan secara greedy (PROJECT_OVERVIEW §6.2).

Perbaikan yang dicoba per aksi: 'posture' (semua sendi aksi itu di dalam batas) dan 'thumb' (tekan dengan ibu jari,
bukan telunjuk). Greedy dan hitung ulang wajib: aturan sendi terburuk dan tangan tertinggi membuat penyumbang
berikutnya bisa berpindah setelah satu perbaikan.
"""
import pandas as pd

from kimcam.attribution import kim_input, oor_cols
from kimcam.kim import kim_score


def apply(frames, move, kind):
    f = frames.copy()
    rows = f["move"] == move
    if kind == "posture":
        f.loc[rows, oor_cols(f)] = False
    else:
        f.loc[rows & (f["finger"] == "index"), "finger"] = "thumb"
    return f


def candidates(frames):
    moves = sorted(m for m in frames["move"].unique() if m)
    pressed_index = set(frames.loc[frames["finger"] == "index", "move"])
    return [(m, "posture") for m in moves] + [(m, "thumb") for m in moves if m in pressed_index]


def whatif(frames, force_n, ctx, cfg):
    """Kembalikan tabel urutan perbaikan: rank, move, kind, delta (penurunan skor), score_after."""
    def score(f):
        return kim_score(kim_input(f, force_n, ctx, cfg)[0], cfg)["score"]

    cur, now, steps = frames, score(frames), []
    while True:
        deltas = {c: now - score(apply(cur, *c)) for c in candidates(cur)}
        if not deltas or max(deltas.values()) <= 0:
            break
        best = max(deltas, key=deltas.get)
        cur, now = apply(cur, *best), now - deltas[best]
        steps.append((len(steps) + 1, *best, deltas[best], now))
    return pd.DataFrame(steps, columns=["rank", "move", "kind", "delta", "score_after"])
