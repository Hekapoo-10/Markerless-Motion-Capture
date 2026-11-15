"""P4: seberapa tahan kesimpulan P1-P2 terhadap galat dan asumsi (Monte Carlo; PROJECT_OVERVIEW §6.4).

Tiap simulasi (semua Asumsi, keputusan 15 Nov):
- sudut + galat tetap per sendi ~ N(bias, sd) dari configs/angle_error.yaml (galat sistematis satu sesi);
- batas sudut tiap sendi digeser seragam +-5 derajat;
- FmaxM ibu jari ~ segitiga(min, 80, maks) dari fmax_scenarios_thumb; FmaxM telunjuk tetap;
- gaya tiap gerakan x seragam(0,9; 1,1);
- label aksi digeser bersama +-3 frame terhadap sudut.
"""
import numpy as np
import pandas as pd

from kimcam.angles import oor_from_angles
from kimcam.attribution import attribute
from kimcam.whatif import whatif


def conclusions(frames, force_n, ctx, cfg):
    """Penyumbang terbesar P1 (gabungan per indikator x aksi x sendi x tangan), perbaikan nomor 1 P2, skor."""
    df, r = attribute(frames, force_n, ctx, cfg)
    act = df[df["move"] != ""].groupby(["indicator", "move", "joint", "hand"])["points"].sum()
    ind, move, joint, hand = act.idxmax()
    w = whatif(frames, force_n, ctx, cfg)
    return {"top": f"{ind}: {move} x {joint or '-'} x {hand}",
            "first_fix": f"{w['move'].iat[0]} {w['kind'].iat[0]}" if len(w) else "(tidak ada)",
            "score": r["score"], "category": r["category"]}


def shift_labels(frames, n):
    """Geser kolom move/finger n frame terhadap sudut, per tangan."""
    f = frames.sort_values(["hand", "t"]).copy()
    f[["move", "finger"]] = f.groupby("hand")[["move", "finger"]].shift(n, fill_value="")
    return f


def simulate(frames, force_n, ctx, cfg, thr, err, n=1000, seed=0, thr_shift=5, label_shift=3, force_rel=0.10):
    """frames berisi ang_<sendi>. Kembalikan (hasil tiap simulasi, ringkasan)."""
    rng = np.random.default_rng(seed)
    base = conclusions(oor_from_angles(frames, thr), force_n, ctx, cfg)
    lo, mode, hi = min(cfg["fmax_scenarios_thumb"]), cfg["fmax_n"]["thumb"], max(cfg["fmax_scenarios_thumb"])
    rows = []
    for _ in range(n):
        f = frames.copy()
        for j, e in err.items():
            if f"ang_{j}" in f:
                f[f"ang_{j}"] += rng.normal(e["bias"], e["sd"])
        t = {}
        for j, lim in thr.items():
            d = rng.uniform(-thr_shift, thr_shift)
            t[j] = {k: None if v is None else v + d for k, v in lim.items()}
        f = shift_labels(f, int(rng.integers(-label_shift, label_shift + 1)))
        c = {**cfg, "fmax_n": {**cfg["fmax_n"], "thumb": rng.triangular(lo, mode, hi)}}
        fn = {m: v * rng.uniform(1 - force_rel, 1 + force_rel) for m, v in force_n.items()}
        rows.append(conclusions(oor_from_angles(f, t), fn, ctx, c))
    sims = pd.DataFrame(rows)
    summary = {
        "n": n, "seed": seed,
        "base_top": base["top"], "same_top": (sims["top"] == base["top"]).mean(),
        "base_first_fix": base["first_fix"], "same_first_fix": (sims["first_fix"] == base["first_fix"]).mean(),
        "base_score": base["score"], "score_p5_p95": tuple(sims["score"].quantile([0.05, 0.95])),
    }
    return sims, summary


def fmax_scenarios(frames, force_n, ctx, cfg, thr):
    """Tabel skenario tetap FmaxM ibu jari (tanpa acak), supaya pengaruh pilihan FmaxM terlihat langsung."""
    f = oor_from_angles(frames, thr)
    return pd.DataFrame([{"fmax_thumb": F, **conclusions(f, force_n, ctx, {**cfg, "fmax_n": {**cfg["fmax_n"], "thumb": F}})}
                         for F in cfg["fmax_scenarios_thumb"]])
