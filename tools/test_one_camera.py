"""Tahap 2: ukur fps, jeda, dan frame dobel satu kamera; baca balik format/exposure; simpan 1 frame.

Pakai: python tools/test_one_camera.py [label=top] [detik=60] [exposure, misalnya -7]
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from kimcam.cameras import load_cfg, open_camera

label = sys.argv[1] if len(sys.argv) > 1 else "top"
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 60
cfg = load_cfg()
if len(sys.argv) > 3:
    cfg["exposure"] = float(sys.argv[3])

cap = open_camera(label, cfg)
for _ in range(10):  # buang frame awal
    cap.read()
ts, dup, prev = [], 0, None
t_end = time.perf_counter() + dur
while time.perf_counter() < t_end:
    ok, frame = cap.read()  # DSHOW: grab() tidak menunggu frame baru, read() menunggu (dicek 15 Nov)
    if ok:
        ts.append(time.perf_counter_ns())
        dup += prev is not None and np.array_equal(frame, prev)
        prev = frame

gap_ms = np.diff(ts) / 1e6
fps = 1000 / gap_ms.mean()
fourcc = int(cap.get(cv2.CAP_PROP_FOURCC)).to_bytes(4, "little").decode(errors="replace")
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
f = cfg["format"]
fmt_ok = fourcc == f["fourcc"] and size == (f["width"], f["height"])
exp_read = cap.get(cv2.CAP_PROP_EXPOSURE)
exp_ok = cfg["exposure"] is None or exp_read == cfg["exposure"]
cap.release()

out = Path(f"data/interim/stage02_{label}.png")
out.parent.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(out), prev)
print(f"{label} ({cfg['backend']}): frame={len(ts)} fps={fps:.2f} jeda_maks={gap_ms.max():.1f} ms "
      f"jeda>67ms={int((gap_ms > 67).sum())} dobel={dup}")
print(f"format={fourcc} {size[0]}x{size[1]} exposure diminta={cfg['exposure']} terbaca={exp_read} "
      f"terang_rata2={prev.mean():.0f} contoh={out}")
ok = fps >= 29.5 and gap_ms.max() <= 67 and dup == 0 and fmt_ok and exp_ok
print("UJI DINI: LULUS" if ok else f"UJI DINI: GAGAL (format_ok={fmt_ok}, exposure_ok={exp_ok})")
sys.exit(0 if ok else 1)
