"""Tahap 8: pose 2D keenam kamera satu sesi -> pose_<label>.npz, gambar overlay, angka getaran pergelangan.

Pakai: python tools/support/check_pose.py data/raw/TEST/S8_05 [detik_diam=10]
Klip diam: kedua tangan diam di jig sepanjang `detik_diam` terakhir. Lulus/tidak dinilai visual dari overlay
(skor RTMW tidak membedakan tangan asli dari tebakan; keputusan 16 Nov); angka getaran dicatat sebagai baseline.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from rtmlib import draw_skeleton

from kimcam.cameras import LABELS
from kimcam.pose2d import HAND, WRIST, load_model, run_pose

session = Path(sys.argv[1])
still_s = float(sys.argv[2]) if len(sys.argv) > 2 else 10
K = 15  # rata-rata bergerak 0,5 s: sisanya = noise cepat model, bukan gerak tubuh pelan

model = load_model()
tiles = []
for label in LABELS:
    out = session / f"pose_{label}.npz"
    speed = run_pose(model, session / f"{label}.avi", session / f"{label}_ts.csv", out)
    d = np.load(out)
    t = pd.read_csv(session / f"{label}_ts.csv")["t_ns"].to_numpy()
    t = (t - t[0]) / 1e9
    still = t > t[-1] - still_s
    line = [f"{label:12} {speed:5.1f} frame/s"]
    for h in ("left", "right"):
        p = d["kps"][still, WRIST[h]].astype(float)
        smooth = np.stack([np.convolve(p[:, i], np.ones(K) / K, mode="same") for i in range(2)], 1)
        fast = (p - smooth)[K:-K].std(axis=0).max()
        line.append(f"{h}: skor_tangan={d['scores'][:, HAND[h]].mean():.1f} "
                    f"SD_total={np.nanstd(p, axis=0).max():.1f}px noise_cepat={fast:.1f}px")
    print("  ".join(line), flush=True)

    i = len(t) // 2  # frame tengah klip
    cap = cv2.VideoCapture(str(session / f"{label}.avi"))
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    img = cap.read()[1]
    cap.release()
    if not np.isnan(d["kps"][i]).any():  # frame tanpa orang / dobel tidak digambar
        img = draw_skeleton(img, d["kps"][i][None], d["scores"][i][None], openpose_skeleton=False, kpt_thr=0.3)
    tile = cv2.resize(img, (640, 400))
    cv2.putText(tile, label, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    tiles.append(tile)

cv2.imwrite(str(session / "pose_overlay.png"), np.vstack([np.hstack(tiles[:3]), np.hstack(tiles[3:])]))
print(f"Cek visual: {session / 'pose_overlay.png'} (lulus bila tangan tepat di >= 3 kamera termasuk top)")
