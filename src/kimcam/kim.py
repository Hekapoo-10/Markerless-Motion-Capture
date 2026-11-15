"""KIM-MHO v12.5: skor resmi, versi fungsi tangga (tanpa interpolasi gaya). Fungsi murni; tabel dari configs/kim.yaml."""
import math


def time_points(hours, max_hours=10):
    """Linear: 3,5 jam = 3,5 poin, minimal 1 (A55 cetak hlm. 23 dan 47; formulir hlm. 4)."""
    if not 0 < hours <= max_hours:
        raise ValueError(f"{hours} jam di luar tabel poin waktu (0-{max_hours}); tanya pengguna")
    return max(1.0, hours)


def time_word_points(share):
    """A55 hlm. 24: < 5% = 0 · 5-<25% = 1 · 25-<75% = 2 · >= 75% = 3."""
    return 0 if share < 0.05 else 1 if share < 0.25 else 2 if share < 0.75 else 3


def force_level(newton, fmax_n, levels):
    r = newton / fmax_n
    return next((name for upper, name in levels if r <= upper), "peak")


def lookup(points, uppers, x, first_exclusive=False):
    """Nilai mentah tanpa pembulatan. first_exclusive: kolom pertama "< 5" (A55 cetak hlm. 34: 4,5 -> "< 5")."""
    if not (x >= 0 and math.isfinite(x)):
        raise ValueError(f"Nilai {x} tidak sah")
    if first_exclusive and x < uppers[0]:
        i = 0
    else:
        start = 1 if first_exclusive else 0  # x >= 5 tidak boleh masuk kolom "< 5"
        i = next((i for i in range(start, len(uppers)) if x <= uppers[i]), None)
    if i is None:
        raise ValueError(f"{x} di atas tabel (catatan 3 formulir: ekstrapolasi atau KIM-MHO-E); tanya pengguna")
    if points[i] is None:
        raise ValueError(f"Nilai {x} jatuh di sel diarsir (tidak berlaku) formulir KIM")
    return points[i]


def level_frequencies(actions, force_n, cfg):
    """actions: [{'move': ..., 'finger': 'thumb'|'index', 'per_min': x}] satu tangan.
    Frekuensi aksi dengan tingkat gaya sama dijumlah dulu, baru dilihat di tabel (A55 hlm. 30-35)."""
    out = {}
    for a in actions:
        lvl = force_level(force_n[a["move"]], cfg["fmax_n"][a["finger"]], cfg["levels"])
        out[lvl] = out.get(lvl, 0) + a["per_min"]
    return out


def force_cells(move, hold, cfg):
    """Poin tiap sel yang terisi: [(tingkat, 'move'|'hold', nilai, poin)]. Gerak dan tahan pada tingkat yang
    sama sama-sama dihitung (A55 cetak hlm. 32)."""
    t = cfg["force"]
    return ([(lvl, "move", x, lookup(t[lvl]["move"], t["move_upper"], x, first_exclusive=True))
             for lvl, x in move.items()]
            + [(lvl, "hold", x, lookup(t[lvl]["hold"], t["hold_upper"], x)) for lvl, x in hold.items()])


def force_points(move, hold, cfg):
    """move: {tingkat: gerak/menit}, hold: {tingkat: detik tahan/menit} satu tangan; poin dijumlah (A55 hlm. 25)."""
    return sum(c[3] for c in force_cells(move, hold, cfg))


def kim_score(x, cfg):
    """x: scenario_hours, left/right {move, hold}, out_of_range_share {sendi: 0-1}, grip, conditions, posture,
    organisation. Kembalikan rincian poin, skor, kategori, dan peringatan."""
    for k, allowed in cfg["scales"].items():
        if x[k] not in allowed:
            raise ValueError(f"{k}={x[k]} bukan nilai formulir {allowed}")
    cells = {h: force_cells(x[h]["move"], x[h]["hold"], cfg) for h in ("left", "right")}
    hands = {h: sum(c[3] for c in cells[h]) for h in cells}
    r = {
        "time": time_points(x["scenario_hours"], cfg["time_max_hours"]),
        "force_left": hands["left"],
        "force_right": hands["right"],
        "force": max(hands.values()),  # tangan yang lebih tinggi (A55 hlm. 25)
        "grip": x["grip"],
        "handarm": max(time_word_points(s) for s in x["out_of_range_share"].values()),  # sendi terburuk
        "conditions": x["conditions"],
        "posture": x["posture"],
        "organisation": x["organisation"],
    }
    r["indicators"] = sum(r[k] for k in ("force", "grip", "handarm", "conditions", "posture", "organisation"))
    r["score"] = r["time"] * r["indicators"]
    r["category"] = next((name for upper, name in cfg["risk"] if r["score"] < upper), "high")
    all_cells = cells["left"] + cells["right"]
    r["warnings"] = []
    if any(c[0] in ("peak", "powerful_hitting") for c in all_cells):
        r["warnings"].append("Gaya puncak/memukul: nilai juga dengan KIM-BF (catatan 2 formulir)")
    if any(c[3] == 100 for c in all_cells):
        r["warnings"].append("Sel abu-abu (100 poin): beban tinggi, kemungkinan overload (A55 cetak hlm. 28)")
    if not cfg.get("verified"):
        r["warnings"].append("configs/kim.yaml belum dicek ulang dengan formulir PDF asli")
    return r
