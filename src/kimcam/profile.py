"""P3: profil kesalahan per orang lintas siklus (PROJECT_OVERVIEW §6.3)."""
import pandas as pd

from kimcam.attribution import oor_cols

CONSISTENT = 0.70  # penyumbang terbesar sama di >= 70% siklus (Asumsi)


def profile(frames):
    """Kembalikan (shares, cycles, summary).
    shares: % frame di luar batas per siklus x tangan x aksi x sendi.
    cycles: per siklus, penyumbang terbesar (aksi, sendi, tangan dengan frame di luar batas terbanyak) dan jari tekan.
    summary: penyumbang terbesar yang paling sering, bagian siklusnya, dan apakah konsisten."""
    cols = oor_cols(frames)
    f = frames[frames["move"] != ""]
    shares = f.groupby(["cycle", "hand", "move"])[cols].mean()

    counts = f.groupby(["cycle", "hand", "move"])[cols].sum().stack()
    counts = counts[counts > 0]
    cycles = pd.DataFrame({"top": ""}, index=pd.Index(sorted(frames["cycle"].unique()), name="cycle"))
    if len(counts):
        idx = counts.groupby(level="cycle").idxmax()  # (cycle, hand, move, oor_<sendi>)
        cycles.loc[idx.index, "top"] = [f"{k[2]} x {k[3][4:]} x {k[1]}" for k in idx]
    pressed = f[f["finger"] != ""]
    cycles["fingers"] = pressed.groupby("cycle")["finger"].agg(lambda s: "/".join(sorted(set(s)))).reindex(
        cycles.index).fillna("")

    top = cycles.loc[cycles["top"] != "", "top"]
    mode = top.mode().iat[0] if len(top) else ""
    share = (cycles["top"] == mode).mean() if mode else 0.0
    summary = {"top": mode, "share_of_cycles": share, "consistent": bool(mode) and share >= CONSISTENT}
    return shares, cycles, summary
