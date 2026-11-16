"""Tahap 8: titik tubuh + tangan 2D (RTMW, 133 titik COCO-WholeBody) per frame untuk satu video kamera."""
import time

import cv2
import numpy as np
import onnxruntime as ort
import pandas as pd
from rtmlib import Wholebody

# indeks dicek di rtmlib 0.0.16 (visualization/skeleton/coco133.py); kiri/kanan = sisi tubuh orangnya
WRIST = {"left": 9, "right": 10}
HAND = {"left": slice(91, 112), "right": slice(112, 133)}


def load_model(device="cuda"):
    ort.preload_dlls()  # DLL CUDA/cuDNN dari paket pip nvidia-*; tanpa ini sesi diam-diam jatuh ke CPU
    return Wholebody(mode="performance", backend="onnxruntime", device=device, to_openpose=False)


def run_pose(model, video, ts_csv, out):
    """Simpan kps (frame, 133, 2) dan scores (frame, 133) ke `out`; kembalikan kecepatan model (frame/detik)."""
    dup = pd.read_csv(ts_csv)["dup"].to_numpy(bool)
    cap = cv2.VideoCapture(str(video))
    kps, scs, t0 = [], [], time.perf_counter()
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        k, s = model(frame)
        if len(s) and not dup[len(kps)]:  # frame dobel = gambar lama -> NaN (keputusan 16 Nov)
            # lebih dari satu orang: ambil yang terbesar (peserta paling dekat kamera); skor tertinggi
            # sempat memilih orang lain di latar belakang wing_right (16 Nov, S8_04)
            i = int(np.argmax(np.ptp(k[:, :17], axis=1).prod(axis=1)))
            kps.append(k[i])
            scs.append(s[i])
        else:
            kps.append(np.full((133, 2), np.nan))
            scs.append(np.zeros(133))
    cap.release()
    assert len(kps) == len(dup), f"{video}: {len(kps)} frame video vs {len(dup)} baris ts"
    np.savez_compressed(out, kps=np.array(kps, np.float32), scores=np.array(scs, np.float32))
    return len(kps) / (time.perf_counter() - t0)
