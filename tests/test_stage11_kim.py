import pytest
import yaml

from kimcam.kim import (
    force_level,
    force_points,
    kim_score,
    level_frequencies,
    time_points,
    time_word_points,
)

with open("configs/kim.yaml", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)
with open("tests/data/kim_cases.yaml", encoding="utf-8") as f:
    CASES = yaml.safe_load(f)  # kasus resmi A55, jawaban dihitung BAuA


def low_move(x):
    return force_points({"low": x}, {}, CFG)


@pytest.mark.parametrize(("per_min", "points"), [
    (4.5, 0.5), (4.99, 0.5), (5, 1), (15, 1), (15.5, 2.5), (16, 2.5),
    (30, 2.5), (30.5, 5), (60, 5), (61, 7), (90, 7),
])
def test_move_boundaries_raw_values(per_min, points):
    assert low_move(per_min) == points


@pytest.mark.parametrize("per_min", [90.5, 91])
def test_above_table_raises(per_min):
    with pytest.raises(ValueError, match="di atas tabel"):
        low_move(per_min)


@pytest.mark.parametrize(("seconds", "points"), [(15, 1.5), (15.5, 3), (16, 3), (30, 3), (31, 5.5), (60, 5.5)])
def test_hold_boundaries(seconds, points):
    assert force_points({}, {"low": seconds}, CFG) == points


@pytest.mark.parametrize(("move", "hold"), [({"very_high": 70}, {}), ({"peak": 20}, {}), ({}, {"peak": 20})])
def test_grey_cells_are_100(move, hold):
    assert force_points(move, hold, CFG) == 100


def test_hatched_cell_raises():
    with pytest.raises(ValueError, match="diarsir"):
        force_points({}, {"powerful_hitting": 10}, CFG)


@pytest.mark.parametrize(("newton", "finger", "level"), [
    (12, "thumb", "low"), (12.1, "thumb", "moderate"), (30, "thumb", "high"), (30, "index", "very_high"),
    (40, "index", "very_high"), (40.1, "index", "peak"),
])
def test_force_level(newton, finger, level):
    assert force_level(newton, CFG["fmax_n"][finger], CFG["levels"]) == level


@pytest.mark.parametrize("hours", [0, 10.5])
def test_time_points_outside_table(hours):
    with pytest.raises(ValueError):
        time_points(hours)


@pytest.mark.parametrize(("share", "points"), [(0.049, 0), (0.05, 1), (0.249, 1), (0.25, 2), (0.749, 2), (0.75, 3)])
def test_time_word_points(share, points):
    assert time_word_points(share) == points


def test_same_level_frequencies_summed_first():
    force_n = {"move_1": 2, "move_2": 2, "move_3": 30}
    actions = [{"move": m, "finger": "thumb", "per_min": 15} for m in force_n]
    freq = level_frequencies(actions, force_n, CFG)
    assert freq == {"low": 30, "high": 15}
    assert force_points(freq, {}, CFG) == 2.5 + 3  # bukan 1 + 1 + 3 bila dilihat per aksi


def test_scale_value_outside_form_raises():
    x = {"scenario_hours": 4, "left": {"move": {}, "hold": {}}, "right": {"move": {}, "hold": {}},
         "out_of_range_share": {"wrist_fe_right": 0}, "grip": 3, "conditions": 0, "posture": 0, "organisation": 0}
    with pytest.raises(ValueError, match="grip=3"):
        kim_score(x, CFG)


# --- kasus resmi A55 (tests/data/kim_cases.yaml) ---

@pytest.mark.parametrize("c", CASES["time_points"], ids=lambda c: f"{c['hours']}h")
def test_a55_time_points(c):
    assert time_points(c["hours"]) == c["expected"]


@pytest.mark.parametrize("c", [
    pytest.param(c, id=c["id"], marks=[pytest.mark.skip(reason="butuh versi interpolasi (v2)")] if c["mode"] == "interp" else [])
    for c in CASES["force_cases"]
])
def test_a55_force_cases(c):
    got = {side: force_points(c[side].get("moving", {}), c[side].get("holding", {}), CFG)
           for side in ("left", "right") if side in c}
    assert {side: c["expected"][side] for side in got} == got
    if "force" in c["expected"]:
        assert max(got.values()) == c["expected"]["force"]


def test_a55_p47_full_score():
    fc = CASES["full_score_case"]
    i = fc["indicators"]
    x = {"scenario_hours": fc["time_hours"], "left": {"move": {}, "hold": {}},
         "right": {"move": {"low": 90}, "hold": {}},           # 7 poin gaya, sama dengan contoh
         "out_of_range_share": {"wrist_fe_right": 0.10},         # "kadang" -> 1 poin
         "grip": i["gripping"], "conditions": i["working_conditions"], "posture": i["body_posture"],
         "organisation": i["work_organisation"]}
    r = kim_score(x, CFG)
    assert (r["force"], r["handarm"]) == (i["force"], i["hand_arm"])
    assert (r["indicators"], r["score"]) == (fc["expected"]["indicator_sum"], fc["expected"]["score"])
    assert r["category"] == "slightly_increased"                # risiko 2 (A55 cetak hlm. 48)
