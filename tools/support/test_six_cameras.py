"""Tahap 3: enam kamera bersamaan; fps, jeda, frame dobel per kamera, dan pemakaian CPU.

Pakai: python tools/support/test_six_cameras.py [backend=dshow|msmf] [detik=300] [exposure, misalnya -7]
"""
import sys
import threading
import time

import numpy as np
import psutil

from kimcam.cameras import LABELS, load_cfg, open_camera

cfg = load_cfg()
if len(sys.argv) > 1:
    cfg["backend"] = sys.argv[1]
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 300
if len(sys.argv) > 3:
    cfg["exposure"] = float(sys.argv[3])

caps = {label: open_camera(label, cfg) for label in LABELS}  # dibuka berurutan, bukan bersamaan
ts, dup, consec = {}, {}, {}


def worker(label, cap):
    for _ in range(10):  # buang frame awal
        cap.read()
    out, d, c, prev, was_dup = [], 0, 0, None, False
    t_end = time.perf_counter() + dur
    while time.perf_counter() < t_end:
        ok, frame = cap.read()  # bukan grab(): di DSHOW grab() tidak menunggu frame baru
        if ok:
            out.append(time.perf_counter_ns())
            small = frame[::8, ::8].copy()  # cukup untuk mengenali frame dobel, jauh lebih murah
            is_dup = prev is not None and np.array_equal(small, prev)
            d += is_dup
            c += is_dup and was_dup  # dobel berturut-turut = kamera mulai beku
            prev, was_dup = small, is_dup
    cap.release()
    ts[label], dup[label], consec[label] = out, d, c


threads = [threading.Thread(target=worker, args=item) for item in caps.items()]
for t in threads:
    t.start()
cpu = []
while any(t.is_alive() for t in threads):
    cpu.append(psutil.cpu_percent(interval=1))
for t in threads:
    t.join()

ok_all = True
print(f"backend={cfg['backend']} detik={dur:.0f} exposure={cfg['exposure']}")
for label in LABELS:
    g = np.diff(ts[label]) / 1e6
    fps = 1000 / g.mean()
    # dobel langka ditoleransi (ditandai di rekaman, dibuang per kamera saat analisis); keputusan pengguna 16 Nov
    ok = (fps >= 29.5 and g.max() <= 67 and dup[label] <= cfg["dup_max_fraction"] * len(ts[label])
          and consec[label] == 0)
    ok_all &= ok
    when = (np.array(ts[label][1:])[g > 67] - ts[label][0]) / 1e9  # detik ke berapa jeda terjadi
    print(f"  {label:12} frame={len(ts[label]):5} fps={fps:.2f} jeda_maks={g.max():6.1f} ms "
          f"jeda>67ms={int((g > 67).sum())} dobel={dup[label]} berturut={consec[label]} {'OK' if ok else 'GAGAL'}"
          + (f" jeda_di_detik={np.round(when[:10], 1).tolist()}" if len(when) else ""))
print(f"CPU rata2={np.mean(cpu):.0f}% maks={np.max(cpu):.0f}%")
print("UJI DINI: LULUS" if ok_all else "UJI DINI: GAGAL")
sys.exit(0 if ok_all else 1)
