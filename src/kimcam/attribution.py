"""P1: pecah skor resmi KIM-MHO ke aksi x bagian tubuh x tangan (PROJECT_OVERVIEW §6.1).

Label (satu baris per frame per tangan): t [s], cycle, hand (left/right), move ('' = tidak ada), finger
(thumb/index/''), dan kolom oor_<sendi> (True = sendi di luar batas).
"""
import numpy as np
import pandas as pd

from kimcam.kim import force_level, force_points, kim_score

HANDS = ("left", "right")


def oor_cols(frames):
    cols = [c for c in frames.columns if c.startswith("oor_")]
    if not cols:
        raise ValueError("Label tidak punya kolom oor_<sendi>")
    return cols


def duration_min(frames):
    t = np.sort(frames["t"].unique())
    return len(t) * np.median(np.diff(t)) / 60


def occurrences(frames, force_n, cfg):
    """Satu baris per kejadian aksi (frame berurutan dengan move sama, per tangan), plus tingkat gayanya."""
    f = frames.sort_values(["hand", "t"])
    f = f.assign(run=(f["move"] != f.groupby("hand")["move"].shift()).cumsum())
    f = f[f["move"] != ""]
    occ = f.groupby("run").agg(hand=("hand", "first"), move=("move", "first"), cycle=("cycle", "first"),
                               finger=("finger", lambda s: s.mode().iat[0]), frames=("t", "size"))
    # aksi tanpa label jari (ambil, letakkan) memakai FmaxM telunjuk: lebih kecil, jadi lebih konservatif (Asumsi)
    occ["level"] = [force_level(force_n[m], cfg["fmax_n"][fg or "index"], cfg["levels"])
                    for m, fg in zip(occ["move"], occ["finger"])]
    return occ.reset_index(drop=True)


def kim_input(frames, force_n, ctx, cfg):
    """Label -> masukan kim_score. ctx: scenario_hours, grip, conditions, posture, organisation."""
    occ = occurrences(frames, force_n, cfg)
    minutes = duration_min(frames)
    x = dict(ctx)
    for h in HANDS:
        # shortcut: tahan (statis >= 4 s) belum dihitung; tambahkan saat Tahap 10 punya label tahan
        x[h] = {"move": (occ[occ["hand"] == h].groupby("level").size() / minutes).to_dict(), "hold": {}}
    x["out_of_range_share"] = {f"{c[4:]}_{h}": g[c].mean() for h, g in frames.groupby("hand") for c in oor_cols(frames)}
    return x, occ


def attribute(frames, force_n, ctx, cfg):
    """Kembalikan (tabel penyumbang, hasil kim_score). Jumlah kolom points = poin indikator resmi."""
    x, occ = kim_input(frames, force_n, ctx, cfg)
    r = kim_score(x, cfg)
    rows = []

    # gaya: poin tiap tingkat di tangan penentu dibagi ke aksi sebanding jumlah kejadian; tangan seri -> dibagi dua
    top = [h for h in HANDS if r[f"force_{h}"] == r["force"]]
    for h in top:
        o = occ[occ["hand"] == h]
        for lvl, g in o.groupby("level"):
            pts = force_points({lvl: x[h]["move"][lvl]}, {}, cfg)
            for move, n in g["move"].value_counts().items():
                rows.append(("force", h, move, "", pts * n / len(g) / len(top)))

    # posisi tangan/lengan: poin dibagi ke aksi sebanding frame di luar batas pada sendi terburuk; seri -> dibagi rata
    if r["handarm"] > 0:
        shares = x["out_of_range_share"]
        worst = [k for k, v in shares.items() if v == max(shares.values())]
        for key in worst:
            joint, h = key.rsplit("_", 1)
            bad = frames[(frames["hand"] == h) & frames[f"oor_{joint}"]]
            for move, n in bad["move"].replace("", "(tanpa aksi)").value_counts().items():
                rows.append(("handarm", h, move, joint, r["handarm"] * n / len(bad) / len(worst)))

    for k in ("grip", "conditions", "posture", "organisation"):
        rows.append((k, "", "", "", r[k]))

    df = pd.DataFrame(rows, columns=["indicator", "hand", "move", "joint", "points"])
    df["score"] = df["points"] * r["time"]
    assert abs(df["points"].sum() - r["indicators"]) < 1e-9, "jumlah atribusi != poin indikator resmi"
    return df, r
