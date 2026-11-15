"""Sudut sendi -> label di luar batas. Perhitungan sudut 3D menyusul di Tahap 9."""


def oor_from_angles(frames, thr):
    """ang_<sendi> (derajat) -> oor_<sendi>, untuk sendi yang ada di frames. thr: {sendi: {pos, neg}} dari
    configs/thresholds.yaml; null = arah itu tidak dinilai. Sudut NaN (pose hilang) dihitung di dalam batas."""
    f = frames.copy()
    for j, lim in thr.items():
        if f"ang_{j}" not in f:
            continue
        a = f[f"ang_{j}"]
        f[f"oor_{j}"] = ((a > lim["pos"]) if lim["pos"] is not None else False) | (
            (a < -lim["neg"]) if lim["neg"] is not None else False)
    return f
