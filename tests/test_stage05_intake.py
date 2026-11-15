import builtins
import csv

import pytest

from kimcam.intake import intake

MOVES = ["move_1", "move_2"]


def feed(monkeypatch, answers):
    it = iter(answers)
    monkeypatch.setattr(builtins, "input", lambda _="": next(it))


def rows(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.reader(f))


def test_bad_input_is_reasked_and_name_stays_private(monkeypatch, tmp_path):
    f = tmp_path / "p.csv"
    feed(monkeypatch, ["Budi", "x", "l", "kiri", "2 thn", "", "abc", "-3", "nan", "30,5", "4", "y"])
    p = intake("P001", MOVES, f)
    assert p == {"id": "P001", "gender": "L", "dominant_hand": "kiri", "experience": "2 thn",
                 "force_n": {"move_1": 30.5, "move_2": 4.0}}
    assert "Budi" not in str(p)
    assert rows(f) == [["id", "name"], ["P001", "Budi"]]


def test_same_id_needs_same_name(monkeypatch, tmp_path):
    f = tmp_path / "p.csv"
    feed(monkeypatch, ["Budi", "L", "kanan", "-", "1", "2", "y"])
    intake("P001", MOVES, f)
    feed(monkeypatch, ["budi", "L", "kanan", "-", "1", "2", "y"])  # sesi kedua orang yang sama
    intake("P001", MOVES, f)
    assert rows(f) == [["id", "name"], ["P001", "Budi"]]
    feed(monkeypatch, ["Ani"])
    with pytest.raises(SystemExit):
        intake("P001", MOVES, f)


def test_cancel_saves_nothing(monkeypatch, tmp_path):
    f = tmp_path / "p.csv"
    feed(monkeypatch, ["Ani", "P", "kanan", "-", "1", "2", "n"])
    with pytest.raises(SystemExit):
        intake("P002", MOVES, f)
    assert not f.exists()
