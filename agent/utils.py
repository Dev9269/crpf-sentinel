"""Cross-platform system metrics for heartbeats (psutil if available)."""

from __future__ import annotations

import platform
import socket

try:
    import psutil  # type: ignore

    HAS_PSUTIL = True
except ImportError:  # pragma: no cover
    psutil = None
    HAS_PSUTIL = False


def system_metrics() -> dict:
    if not HAS_PSUTIL:
        return {"cpu_usage": 0.0, "memory_usage": 0.0}
    return {
        "cpu_usage": round(psutil.cpu_percent(interval=None) or 0.0, 1),
        "memory_usage": round(psutil.virtual_memory().percent or 0.0, 1),
    }


def local_ip() -> str | None:
    """Best-effort local IPv4 of the primary interface (no packets are sent)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        finally:
            sock.close()
    except OSError:
        return None


def os_info() -> dict:
    return {"os_version": platform.platform()}
