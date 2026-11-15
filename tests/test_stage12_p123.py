"""Tahap 12 (uji dini): P1-P3 dengan label buatan. Siklus 10 s, 30 fps, tangan kanan bekerja, kiri diam:
move_1 0-2 s (ambil), move_2 2-4 s (posisikan), move_3 4-7 s (tekan 30 N), move_4 7-9 s (letakkan), 9-10 s jeda."""
import numpy as np
import pandas as pd
import pytest
import yaml

from kimcam.attribution import attribute
from kimcam.profile import profile
from kimcam.whatif import whatif

with open("configs/kim.yaml", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)
FORCE_N = {"move_1": 2, "move_2": 2, "move_3": 30, "move_4": 2}
CTX = {"scenario_hours": 4, "grip": 0, "conditions": 0, "posture": 2, "organisation": 0}
FPS, CYCLE_S = 30, 10


def make_frames(n_cycles=30, bent_cycles=(), finger=lambda c: "thumb", rud_frames=9):
    """bent_cycles: siklus dengan pergelangan ditekuk (oor_wrist_fe) selama move_3.
    rud_frames: frame awal move_1 tiap siklus dengan oor_wrist_rud (penyumbang kecil, 3% < 5%)."""
    s = np.arange(n_cycles * CYCLE_S * FPS) / FPS
    cycle, phase = (s // CYCLE_S).astype(int), s % CYCLE_S
    move = np.select([phase < 2, phase < 4, phase < 7, phase < 9], ["move_1", "move_2", "move_3", "move_4"], "")
    right = pd.DataFrame({
        "t": s, "cycle": cycle, "hand": "right", "move": move,
        "finger": [finger(c) if m == "move_3" else "" for c, m in zip(cycle, move)],
        "oor_wrist_fe": (move == "move_3") & np.isin(cycle, bent_cycles),
        "oor_wrist_rud": (move == "move_1") & (phase * FPS < rud_frames - 0.5),
    })
    left = right.assign(hand="left", move="", finger="", oor_wrist_fe=False, oor_wrist_rud=False)
    return pd.concat([right, left], ignore_index=True)


def test_attribution_sums_to_official_score():
    df, r = attribute(make_frames(bent_cycles=range(15, 30)), FORCE_N, CTX, CFG)
    assert df["points"].sum() == pytest.approx(r["indicators"], abs=1e-9)
    assert df["score"].sum() == pytest.approx(r["score"], abs=1e-9)


def test_force_points_from_labels():
    # 6 kejadian/menit per aksi: rendah 18/menit -> 2,5; tekan 30 N ibu jari = 38% -> tinggi 6/menit -> 3
    _, r = attribute(make_frames(), FORCE_N, CTX, CFG)
    assert (r["force_right"], r["force_left"]) == (5.5, 0)


def test_known_answer_A_bent_wrist_during_press():
    frames = make_frames(bent_cycles=range(15, 30))  # 15 normal + 15 tekuk saat tekan -> 15% waktu -> 1 poin
    df, r = attribute(frames, FORCE_N, CTX, CFG)
    assert r["handarm"] == 1
    top = df[df["indicator"] == "handarm"].sort_values("points").iloc[-1]
    assert (top["move"], top["joint"], top["hand"]) == ("move_3", "wrist_fe", "right")
    first = whatif(frames, FORCE_N, CTX, CFG).iloc[0]
    assert (first["move"], first["kind"]) == ("move_3", "posture")
    assert first["delta"] == r["time"] * 1


def test_known_answer_B_index_instead_of_thumb():
    thumb = make_frames()
    index = make_frames(finger=lambda c: "index")  # 30 N telunjuk = 60% -> sangat tinggi 6/menit -> 5
    _, rt = attribute(thumb, FORCE_N, CTX, CFG)
    df, ri = attribute(index, FORCE_N, CTX, CFG)
    assert (rt["force"], ri["force"]) == (5.5, 7.5)
    press = df[(df["indicator"] == "force") & (df["move"] == "move_3")]["points"].sum()
    assert press == 5
    first = whatif(index, FORCE_N, CTX, CFG).iloc[0]
    assert (first["move"], first["kind"], first["delta"]) == ("move_3", "thumb", ri["time"] * 2)


def test_whatif_stops_when_nothing_helps():
    assert whatif(make_frames(), FORCE_N, CTX, CFG).empty  # rud 3% -> 0 poin; tidak ada yang bisa diturunkan


def test_profile_consistency():
    _, cycles, summary = profile(make_frames(bent_cycles=range(15, 30)))
    assert set(cycles.loc[:14, "top"]) == {"move_1 x wrist_rud x right"}
    assert set(cycles.loc[15:, "top"]) == {"move_3 x wrist_fe x right"}
    assert summary["share_of_cycles"] == 0.5 and not summary["consistent"]
    _, _, all_bent = profile(make_frames(bent_cycles=range(30)))
    assert all_bent["top"] == "move_3 x wrist_fe x right" and all_bent["consistent"]


def test_profile_records_finger_per_cycle():
    _, cycles, _ = profile(make_frames(finger=lambda c: "index" if c % 2 else "thumb"))
    assert list(cycles["fingers"].iloc[:2]) == ["thumb", "index"]
