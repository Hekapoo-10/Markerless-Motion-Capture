"""Formulir pendataan peserta (Tahap 5). Nama hanya ke file privat; hasil fungsi tanpa nama."""
import csv
import math
from pathlib import Path

import yaml

PRIVATE = Path("data/participants_private.csv")


def ask(prompt, ok):
    """Tanya ulang sampai jawaban lolos ok()."""
    while True:
        a = input(prompt).strip()
        if ok(a):
            return a
        print("  Input tidak valid, ulangi.")


def is_force(a):
    try:
        v = float(a.replace(",", "."))  # terima 30,5 dan 30.5
    except ValueError:
        return False
    return math.isfinite(v) and v >= 0


def intake(pid, moves, private=PRIVATE):
    known = {}
    if private.exists():
        with private.open(encoding="utf-8") as f:
            known = {r["id"]: r["name"] for r in csv.DictReader(f)}
    name = ask("Nama: ", bool)
    if pid in known and known[pid].casefold() != name.casefold():  # ID sama boleh untuk sesi berikutnya orang yang sama
        raise SystemExit(f"{pid} sudah dipakai orang lain; pakai ID lain.")
    p = {
        "id": pid,
        "gender": ask("Gender (L/P): ", lambda a: a.upper() in {"L", "P"}).upper(),
        "dominant_hand": ask("Tangan dominan (kanan/kiri): ", lambda a: a.lower() in {"kanan", "kiri"}).lower(),
        "experience": ask("Pengalaman perakitan: ", bool),
        "force_n": {m: float(ask(f"Gaya {m} (N): ", is_force).replace(",", ".")) for m in moves},
    }
    print(yaml.safe_dump({"name": name, **p}, allow_unicode=True, sort_keys=False))
    if input("Data benar? (y/n): ").strip().lower() != "y":
        raise SystemExit("Dibatalkan; tidak ada yang disimpan.")
    if pid not in known:
        new = not private.exists()
        private.parent.mkdir(parents=True, exist_ok=True)
        with private.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["id", "name"])
            w.writerow([pid, name])
    return p
