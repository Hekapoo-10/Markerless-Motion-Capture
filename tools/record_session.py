"""Tahap 5: pendataan peserta, lalu rekam 6 kamera sampai durasi habis atau Enter ditekan.

Pakai: python tools/record_session.py --participant P001 --session S01 [--minutes 15] [--exposure -7] [--skip-intake]
Hasil: data/raw/<peserta>/<sesi>/<label>.avi + <label>_ts.csv (frame, t_ns, dup) + meta.yaml; baris SHA-256
di data/manifest.csv.
"""
import argparse
import csv
import datetime
import hashlib
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import yaml

from kimcam.cameras import LABELS, load_cfg, open_camera
from kimcam.intake import intake

ap = argparse.ArgumentParser()
ap.add_argument("--participant", required=True)
ap.add_argument("--session", required=True)
ap.add_argument("--minutes", type=float, default=15)
ap.add_argument("--exposure", type=float)
ap.add_argument("--skip-intake", action="store_true", help="rekaman uji tanpa peserta")
args = ap.parse_args()

cfg = load_cfg()
if args.exposure is not None:
    cfg["exposure"] = args.exposure
if cfg["exposure"] is None:
    sys.exit("Exposure belum diisi (cameras.yaml atau --exposure); kamera mengingat nilai lama.")
out = Path("data/raw") / args.participant / args.session
if out.exists():
    sys.exit(f"{out} sudah ada; pakai sesi lain supaya rekaman lama tidak tertimpa.")
free_gb = shutil.disk_usage("data").free / 2**30
if free_gb < 40:
    sys.exit(f"Ruang disk data tinggal {free_gb:.0f} GB (< 40 GB).")
with open("configs/session.yaml", encoding="utf-8") as fh:
    session = yaml.safe_load(fh)
person = {"id": args.participant, "test": True} if args.skip_intake else intake(args.participant, session["moves"])

fmt = cfg["format"]
caps = {label: open_camera(label, cfg) for label in LABELS}
out.mkdir(parents=True)
stop = threading.Event()
stats = {label: {"frames": 0, "dup": 0, "dup_consecutive": 0, "gaps_over_67ms": 0, "max_gap_ms": 0.0, "read_fail": 0}
         for label in LABELS}
stamps = {label: [] for label in LABELS}


def warn(label, msg):
    print(f"!! {time.perf_counter() - t_start:6.1f} s  {label}: {msg}", flush=True)


def wait_enter():
    try:
        input()
    except EOFError:  # tanpa keyboard (dijalankan di latar): berhenti hanya saat durasi habis
        return
    stop.set()


def record(label, cap):
    w = cv2.VideoWriter(str(out / f"{label}.avi"), cv2.VideoWriter_fourcc(*"MJPG"), fmt["fps"],
                        (fmt["width"], fmt["height"]), isColor=False)
    if not w.isOpened():
        warn(label, "VideoWriter gagal dibuka")
        return
    s, prev, first, last, was_dup = stats[label], None, None, None, False
    with open(out / f"{label}_ts.csv", "w", encoding="utf-8") as fh:
        fh.write("frame,t_ns,dup\n")
        while not stop.is_set():
            ok, frame = cap.read()  # bukan grab(): di DSHOW grab() tidak menunggu frame baru
            t = time.perf_counter_ns()
            if not ok:
                s["read_fail"] += 1
                if s["read_fail"] == 1:
                    warn(label, "read() gagal")
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            small = gray[::8, ::8].copy()
            dup = prev is not None and np.array_equal(small, prev)
            if dup:
                s["dup"] += 1
                s["dup_consecutive"] += was_dup
                warn(label, "frame dobel berturut-turut (kamera beku?)" if was_dup else "frame dobel")
            was_dup = dup
            if last is not None and (gap := (t - last) / 1e6) > 67:
                s["gaps_over_67ms"] += 1
                warn(label, f"jeda {gap:.0f} ms")
            if last is not None:
                s["max_gap_ms"] = round(max(s["max_gap_ms"], (t - last) / 1e6), 1)
            w.write(gray)
            fh.write(f"{s['frames']},{t},{int(dup)}\n")
            stamps[label].append(t)
            s["frames"] += 1
            prev, last, first = small, t, first or t
    w.release()
    cap.release()
    s["fps"] = round((s["frames"] - 1) * 1e9 / (last - first), 3) if s["frames"] > 1 else 0.0


threads = [threading.Thread(target=record, args=item) for item in caps.items()]
start, t_start = datetime.datetime.now(), time.perf_counter()
for t in threads:
    t.start()
threading.Thread(target=wait_enter, daemon=True).start()
print(f"REKAM ke {out} ({args.minutes:g} menit). Tekan Enter untuk berhenti.", flush=True)
while not stop.wait(5) and time.perf_counter() - t_start < args.minutes * 60:
    n = [stats[label]["frames"] for label in LABELS]
    print(f"{time.perf_counter() - t_start:6.0f} s  frame {min(n)}-{max(n)}", flush=True)
stop.set()
for t in threads:
    t.join()
dur = time.perf_counter() - t_start

git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
meta = {
    "participant": person,
    "session": args.session,
    "start": start.isoformat(timespec="seconds"),
    "duration_s": round(dur, 1),
    "backend": cfg["backend"],
    "format": fmt,
    "exposure": cfg["exposure"],
    "cameras": {label: cfg["cameras"][label]["usb_port"] for label in LABELS},
    "calibration_id": None,  # diisi setelah Tahap 7
    "scenario_hours": session["scenario_hours"],
    "moves": session["moves"],
    "git_commit": git or None,
    "camera_stats": stats,
}
with open(out / "meta.yaml", "w", encoding="utf-8") as fh:
    yaml.safe_dump(meta, fh, allow_unicode=True, sort_keys=False)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


manifest = Path("data/manifest.csv")
new = not manifest.exists()
with manifest.open("a", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    if new:
        w.writerow(["path", "size", "sha256", "date"])
    for p in sorted(out.iterdir()):
        w.writerow([p.relative_to("data").as_posix(), p.stat().st_size, sha256(p), start.date().isoformat()])

# kriteria Tahap 5 (15 Nov): fps tiap kamera +-0,5% dari fps terukur; jumlah frame di jendela waktu bersama
# (kamera tidak mulai/berhenti tepat bersamaan) sama di 6 kamera +-2; tanpa jeda > 67 ms; dobel <= dup_max_fraction
# dan tidak berturut-turut (16 Nov: frame dup=1 di <label>_ts.csv dibuang per kamera saat analisis)
lo = max(stamps[label][0] for label in LABELS)
hi = min(stamps[label][-1] for label in LABELS)
common = {label: int(np.searchsorted(stamps[label], hi, "right") - np.searchsorted(stamps[label], lo)) for label in LABELS}
ok = (all(abs(stats[label]["fps"] - fmt["fps_measured"]) <= 0.005 * fmt["fps_measured"] for label in LABELS)
      and max(common.values()) - min(common.values()) <= 2
      and all(stats[label]["dup"] <= cfg["dup_max_fraction"] * stats[label]["frames"]
              and stats[label]["dup_consecutive"] == 0 and stats[label]["gaps_over_67ms"] == 0 for label in LABELS))
for label in LABELS:
    print(f"  {label:12} frame_jendela_bersama={common[label]} {stats[label]}")
print(f"durasi {dur:.1f} s, jendela bersama {(hi - lo) / 1e9:.1f} s. Tersimpan: {out}")
print("CEK REKAMAN: LULUS" if ok else "CEK REKAMAN: GAGAL")
sys.exit(0 if ok else 1)
