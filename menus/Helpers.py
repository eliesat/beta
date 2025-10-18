# -*- coding: utf-8 -*-
"""
Helpers.py
Common helpers for ElieSatPanel plugin (network, image, python, storage, ram).
"""

import socket
import subprocess
import os
import sys
from typing import Optional, Dict


# ---------------- NETWORK HELPERS ----------------
def get_local_ip() -> str:
    """Return the primary local IPv4 address or 'No IP'."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1.0)
            # UDP connect doesn't actually send packets; it picks a source IP.
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "No IP"


def check_internet(host: str = "8.8.8.8", timeout: int = 1) -> str:
    """Ping `host` once. Returns 'Online' or 'Offline'."""
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return "Online"
    except Exception:
        return "Offline"


# ---------------- IMAGE / PYTHON HELPERS ----------------
def get_image_name() -> str:
    """Try to get the image/creator name from /etc/image-version or /etc/issue."""
    try:
        path = "/etc/image-version"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    lines = [ln.strip() for ln in f if ln.strip()]
                    for line in lines:
                        lower = line.lower()
                        if lower.startswith("creator="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
                        if lower.startswith("imagename=") or lower.startswith("image="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
                    if lines:
                        return lines[0].split()[-1]
            except Exception:
                pass

        issue = "/etc/issue"
        if os.path.exists(issue):
            try:
                with open(issue, "r") as f:
                    first = f.readline().strip()
                    if first:
                        return first.split()[0]
            except Exception:
                pass
    except Exception:
        pass
    return "Unknown"


def get_python_version() -> str:
    """Return the running Python version like '3.10.6' or 'Unknown'."""
    try:
        vi = sys.version_info
        return f"{vi.major}.{vi.minor}.{vi.micro}"
    except Exception:
        return "Unknown"


# ---------------- STORAGE / RAM HELPERS ----------------
def get_storage_info(mounts: Optional[Dict[str, str]] = None) -> str:
    """
    Return a multi-line string with storage usage.
    mounts: dict of display-name -> path. Defaults to {'Hdd': '/media/hdd'}.
    """
    if mounts is None:
        mounts = {"Hdd": "/media/hdd"}

    info = []
    for name, path in mounts.items():
        if os.path.ismount(path):
            try:
                stat = os.statvfs(path)
                total = (stat.f_blocks * stat.f_frsize) / (1024 ** 3)
                free = (stat.f_bfree * stat.f_frsize) / (1024 ** 3)
                used = total - free
                info.append(f"{name}: {used:.1f}GB / {total:.1f}GB")
            except Exception:
                info.append(f"{name}: Error")
        else:
            info.append(f"{name}: Not Available")
    return "\n".join(info)


def get_ram_info() -> str:
    """Return RAM usage as 'Ram: usedMB / totalMB' or 'Ram: Not Available'."""
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    mem[parts[0]] = parts[1].strip()
        total_kb = int(mem.get("MemTotal", "0 kB").split()[0])
        # Prefer MemAvailable if present, otherwise fall back to MemFree.
        avail_kb = int(mem.get("MemAvailable", mem.get("MemFree", "0 kB")).split()[0])
        total_mb = total_kb // 1024
        avail_mb = avail_kb // 1024
        used_mb = total_mb - avail_mb
        return f"Ram: {used_mb}MB / {total_mb}MB"
    except Exception:
        return "Ram: Not Available"

