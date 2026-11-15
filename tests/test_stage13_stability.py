"""Tahap 13 (uji dini): P4 dengan label buatan Tahap 12 + kolom sudut."""
import numpy as np
import pytest
import yaml
from test_stage12_p123 import CFG, CTX, FORCE_N, make_frames

from kimcam.angles import oor_from_angles
from kimcam.stability import fmax_scenarios, simulate

with open("configs/thresholds.yaml", encoding="utf-8") as f:
    THR = yaml.safe_load(f)
with open("configs/angle_error.yaml", encoding="utf-8") as f:
    ERR = yaml.safe_load(f)


def with_angles(bent_deg, **kw):
    """15 + 15 siklus seperti uji A; tekuk saat tekan = bent_deg (batas 45), selain itu 20 derajat."""
    f = make_frames(bent_cycles=range(15, 30), **kw)
    f["ang_wrist_fe"] = np.where(f["oor_wrist_fe"], bent_deg, 20.0)
    f["ang_wrist_rud"] = np.where(f["oor_wrist_rud"], 18.0, 5.0)  # batas radial 15
    return f.drop(columns=["oor_wrist_fe", "oor_wrist_rud"])


def test_oor_from_angles_reproduces_labels():
    f = oor_from_angles(with_angles(55), THR)
    ref = make_frames(bent_cycles=range(15, 30))
    assert (f["oor_wrist_fe"].values == ref["oor_wrist_fe"].values).all()
    assert (f["oor_wrist_rud"].values == ref["oor_wrist_rud"].values).all()


def test_oor_from_angles_null_direction_and_negative():
    f = with_angles(55).head(3).assign(ang_shoulder_abd=[-90.0, 44.0, 46.0], ang_wrist_fe=[-46.0, -44.0, 0.0])
    f = oor_from_angles(f, THR)
    assert list(f["oor_shoulder_abd"]) == [False, False, True]   # neg = null: aduksi tidak dinilai
    assert list(f["oor_wrist_fe"]) == [True, False, False]       # ekstensi > 45


def test_clear_case_is_stable_and_borderline_is_not():
    clear = simulate(with_angles(55), FORCE_N, CTX, CFG, THR, ERR, n=40, seed=1)[1]
    border = simulate(with_angles(46), FORCE_N, CTX, CFG, THR, ERR, n=40, seed=1)[1]
    assert clear["base_top"] == border["base_top"] == "force: move_3 x - x right"
    assert clear["base_first_fix"] == "move_3 posture"
    assert clear["same_first_fix"] >= 0.9                         # 55 vs 45: 10 derajat di atas batas
    assert border["same_first_fix"] < clear["same_first_fix"]      # 46 vs 45: mudah berbalik


def test_simulation_is_reproducible():
    a = simulate(with_angles(46), FORCE_N, CTX, CFG, THR, ERR, n=10, seed=7)[0]
    b = simulate(with_angles(46), FORCE_N, CTX, CFG, THR, ERR, n=10, seed=7)[0]
    assert a.equals(b)


@pytest.mark.parametrize(("fmax", "force"), [(56, 7.5), (70, 5.5), (80, 5.5), (137, 4.5)])
def test_fmax_scenarios(fmax, force):
    # tekan 30 N, 6/menit: 56 N = 54% sangat tinggi (5) · 70/80 N = 43%/38% tinggi (3) · 137 N = 22% sedang (2);
    # ditambah gerakan ringan 18/menit = 2,5
    s = fmax_scenarios(with_angles(55), FORCE_N, CTX, CFG, THR).set_index("fmax_thumb")
    assert s.loc[fmax, "score"] == CTX["scenario_hours"] * (force + 1 + CTX["posture"])
