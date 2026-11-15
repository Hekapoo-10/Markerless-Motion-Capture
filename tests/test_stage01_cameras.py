import pytest

from kimcam.cameras import BACKENDS, LABELS, camera_ports, load_cfg

cfg = load_cfg()


def test_labels_and_ports_unique():
    assert list(cfg["cameras"]) == LABELS
    ports = [c["usb_port"] for c in cfg["cameras"].values()]
    assert all(ports), "ada label tanpa usb_port; jalankan tools/identify_cameras.py"
    assert len(set(ports)) == len(ports)


@pytest.mark.parametrize("backend", BACKENDS)
def test_every_label_finds_a_camera(backend):
    found = camera_ports(BACKENDS[backend])
    idx = {label: found.get(c["usb_port"]) for label, c in cfg["cameras"].items()}
    assert None not in idx.values(), f"label tanpa kamera: {[k for k, v in idx.items() if v is None]}"
    assert len(set(idx.values())) == len(LABELS)
