"""Buka kamera berdasarkan label (front_left, ..., wing_right), lewat alamat fisik port USB."""
import os

# shortcut: diasumsikan dibaca saat backend MSMF pertama dipakai, bukan saat import cv2; cek di Tahap 3
os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")
import subprocess

import cv2
import yaml
from cv2_enumerate_cameras import enumerate_cameras

BACKENDS = {"dshow": cv2.CAP_DSHOW, "msmf": cv2.CAP_MSMF}
LABELS = ["front_left", "front", "front_right", "top", "wing_left", "wing_right"]

# instance id kamera | alamat port fisik perangkat induknya. Dipakai port, bukan instance id,
# karena semua kamera berseri sama (SN0001): kamera yang dapat ID berbasis seri bisa berganti setelah reboot.
PS_PORTS = (
    "Get-PnpDevice -Class Camera -PresentOnly | % { "
    "$p = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_Parent).Data; "
    "$l = (Get-PnpDeviceProperty -InstanceId $p -KeyName DEVPKEY_Device_LocationPaths).Data; "
    "if ($l) { $_.InstanceId + '|' + $l[0] } }"
)


def load_cfg(path="configs/cameras.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def camera_ports(backend):
    """{alamat port USB: index OpenCV} untuk semua kamera yang terlihat sekarang."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_PORTS],
                         capture_output=True, text=True, check=True).stdout
    ports = dict(line.split("|", 1) for line in out.splitlines() if "|" in line)
    found = {}
    for c in enumerate_cameras(backend):
        for inst, port in ports.items():
            if inst.replace("\\", "#").lower() in c.path.lower():  # path DSHOW/MSMF memuat instance id
                found[port] = c.index
    return found


def open_camera(label, cfg=None):
    cfg = cfg or load_cfg()
    backend = BACKENDS[cfg["backend"]]
    port = cfg["cameras"][label]["usb_port"]
    idx = camera_ports(backend).get(port)  # cari ulang tiap kali; index bisa berubah
    if idx is None:
        raise RuntimeError(f"Kamera {label} tidak ditemukan di port {port}; cek kabel/hub")
    cap = cv2.VideoCapture(idx, backend)
    f = cfg["format"]
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, f["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, f["height"])
    cap.set(cv2.CAP_PROP_FPS, f["fps"])
    # FOURCC terakhir: di DSHOW, set ukuran sesudahnya mengembalikan format ke YUY2 (dicek 15 Nov)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*f["fourcc"]))
    if cfg.get("exposure") is not None:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # manual (cek)
        cap.set(cv2.CAP_PROP_EXPOSURE, cfg["exposure"])
    if not cap.isOpened():
        raise RuntimeError(f"Kamera {label} gagal dibuka")
    return cap
