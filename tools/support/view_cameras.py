"""Lihat keenam kamera sekaligus (grid 3 x 2). q / Esc = tutup; gambar terakhir disimpan ke data/interim/.

Pakai: python tools/support/view_cameras.py [exposure; default dari cameras.yaml] [pose]
`pose` = gambar kerangka RTMW live (±5 gambar/detik per kamera) untuk mengarahkan kamera.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

from kimcam.cameras import LABELS, load_cfg, open_camera

W, H = 480, 300  # ukuran tiap kotak di layar
args = [a for a in sys.argv[1:] if a != "pose"]
cfg = load_cfg()
cfg["exposure"] = float(args[0]) if args else cfg["exposure"]
model = None
if "pose" in sys.argv[1:]:
    from rtmlib import draw_skeleton

    from kimcam.pose2d import load_model
    model = load_model()
caps = {label: open_camera(label, cfg) for label in LABELS}
tiles = {label: np.zeros((H, W, 3), np.uint8) for label in LABELS}
grid = None

try:
    while True:
        for label, cap in caps.items():
            ok, frame = cap.read()
            if ok and model is not None:  # semua orang digambar, supaya kerangka palsu juga terlihat
                k, s = model(frame)
                frame = draw_skeleton(frame, k, s, openpose_skeleton=False, kpt_thr=0.3, radius=4, line_width=4)
            tile =cv2.resize(frame, (W, H)) if ok else np.zeros((H, W, 3), np.uint8)
            cv2.putText(tile, label if ok else f"{label}: TIDAK ADA GAMBAR", (8, 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            tiles[label] = tile
        grid = np.vstack([np.hstack([tiles[x] for x in LABELS[:3]]), np.hstack([tiles[x] for x in LABELS[3:]])])
        cv2.imshow("kimcam: 6 kamera (q = tutup)", grid)
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break
finally:
    for cap in caps.values():
        cap.release()
    cv2.destroyAllWindows()
    if grid is not None:
        out = Path("data/interim/view_last.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out), grid)
        print(f"Gambar terakhir: {out}")
