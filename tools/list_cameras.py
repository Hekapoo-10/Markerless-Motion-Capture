"""Tahap 1: tampilkan semua kamera per backend (index, nama, VID/PID, device path)."""
import cv2
from cv2_enumerate_cameras import enumerate_cameras

for name, backend in (("DSHOW", cv2.CAP_DSHOW), ("MSMF", cv2.CAP_MSMF)):
    for c in enumerate_cameras(backend):
        print(name, c.index, c.name, hex(c.vid or 0), hex(c.pid or 0), c.path)
