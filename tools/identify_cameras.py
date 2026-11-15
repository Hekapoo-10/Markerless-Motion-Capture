"""Tahap 1: beri label tiap port USB (default), atau cek label dengan uji tutup lensa (argumen `check`).

Beri label: jendela menampilkan satu kamera; tekan angka 1-6 sesuai posisinya. Esc = batal.
Check: jendela menampilkan kamera per label; tutup lensanya, lalu tekan y (gelap) atau n.
"""
import sys

import cv2
import yaml

from kimcam.cameras import BACKENDS, LABELS, camera_ports, load_cfg

WIN = "identify"


def show_until_key(idx, backend, lines, keys):
    """Tampilkan kamera idx sampai salah satu `keys` ditekan; kembalikan tombol itu."""
    cap = cv2.VideoCapture(idx, backend)
    try:
        while True:
            ok, frame = cap.read()
            if ok:
                for i, t in enumerate(lines):
                    cv2.putText(frame, t, (10, 30 + 28 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.imshow(WIN, frame)
            k = cv2.waitKey(30) & 0xFF
            if k == 27:
                raise SystemExit("Dibatalkan; cameras.yaml tidak diubah.")
            if chr(k) in keys:
                return chr(k)
    finally:
        cap.release()


cfg = load_cfg()
backend = BACKENDS[cfg["backend"]]
ports = camera_ports(backend)
print(f"{len(ports)} kamera terlihat.")

if sys.argv[1:] == ["check"]:
    bad = []
    for label in LABELS:
        idx = ports.get(cfg["cameras"][label]["usb_port"])
        if idx is None:
            bad.append(label)
            print(f"{label}: TIDAK DITEMUKAN")
            continue
        k = show_until_key(idx, backend, [f"{label}: tutup lensanya", "y = gelap, n = tidak"], "yn")
        print(f"{label}: {'OK' if k == 'y' else 'SALAH'}")
        bad += [] if k == "y" else [label]
    cv2.destroyAllWindows()
    if bad:
        raise SystemExit(f"Gagal: {bad}")
    print("Uji tutup lensa: semua label benar.")
    sys.exit(0)

assigned = {}
for n, (port, idx) in enumerate(sorted(ports.items()), 1):
    free = {str(i + 1): label for i, label in enumerate(LABELS) if label not in assigned}  # label terpakai ditolak
    menu = [f"{k} = {label}" for k, label in free.items()]
    label = free[show_until_key(idx, backend, [f"kamera {n}/{len(ports)}: posisi apa?", *menu], "".join(free))]
    print(f"{port} -> {label}")
    assigned[label] = port
cv2.destroyAllWindows()

if sorted(assigned) != sorted(LABELS) or len(ports) != len(LABELS):
    raise SystemExit(f"Label dobel atau kurang ({sorted(assigned)}); ulangi. cameras.yaml tidak diubah.")
for label, port in assigned.items():
    cfg["cameras"][label]["usb_port"] = port
with open("configs/cameras.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
print("configs/cameras.yaml diperbarui.")
