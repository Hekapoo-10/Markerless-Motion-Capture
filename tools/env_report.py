"""Tahap 0: catat spesifikasi PC ke configs/environment.yaml."""
import platform
import re
import subprocess
import sys
from pathlib import Path

import psutil
import yaml


def run(cmd):
    try:
        return subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None

ps = lambda c: run(["powershell", "-NoProfile", "-Command", c])
smi = run(["nvidia-smi"]) or ""
env = {
    "os": platform.platform(),
    "python": sys.version.split()[0],
    "cpu": ps("(Get-CimInstance Win32_Processor).Name"),
    "cpu_cores_physical": psutil.cpu_count(logical=False),
    "ram_gb": round(psutil.virtual_memory().total / 2**30, 1),
    "disk_free_gb": {p.mountpoint: round(psutil.disk_usage(p.mountpoint).free / 2**30, 1)
                     for p in psutil.disk_partitions()},
    "gpu": run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
    # driver baru menulis "CUDA UMD Version", driver lama "CUDA Version"
    "cuda_driver": (re.search(r"CUDA (?:UMD )?Version:\s*([\d.]+)", smi) or [None, None])[1],
    "usb_host_controllers": (ps("Get-PnpDevice -PresentOnly | ? FriendlyName -match 'Host Controller' | % FriendlyName") or "").splitlines(),
    "cameras_seen": (ps("Get-PnpDevice -Class Camera -PresentOnly | % FriendlyName") or "").splitlines(),
}
Path("configs").mkdir(exist_ok=True)
text = yaml.safe_dump(env, allow_unicode=True, sort_keys=False)
Path("configs/environment.yaml").write_text(text, encoding="utf-8")
print(text)
