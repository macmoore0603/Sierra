"""
Sierra LAN discovery advertiser.

Advertises the backend as an mDNS/Bonjour service (`_sierra._tcp.local.`) so the
Sierra mobile app (and any other LAN client) can find the computer automatically
instead of the user having to type its IP address.

Best-effort: if zeroconf isn't installed or the network doesn't allow mDNS, this
fails quietly and the app's subnet scan still works as a fallback.
"""

import socket
from typing import Optional

try:
    from zeroconf import Zeroconf, ServiceInfo
    _HAVE_ZEROCONF = True
except Exception:  # pragma: no cover - optional dependency
    _HAVE_ZEROCONF = False

SERVICE_TYPE = "_sierra._tcp.local."

_zeroconf: Optional["Zeroconf"] = None
_service_info: Optional["ServiceInfo"] = None


def _primary_ip() -> str:
    """Best guess at this machine's LAN IP (no traffic actually sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def advertise(port: int = 8000) -> bool:
    """Register the Sierra backend on mDNS. Returns True on success."""
    global _zeroconf, _service_info
    if not _HAVE_ZEROCONF:
        print("[DISCOVERY] zeroconf not available — skipping mDNS advertisement.")
        return False
    if _zeroconf is not None:
        return True  # already advertising

    try:
        ip = _primary_ip()
        hostname = socket.gethostname().split(".")[0]
        name = f"Sierra @ {hostname}.{SERVICE_TYPE}"
        _service_info = ServiceInfo(
            SERVICE_TYPE,
            name,
            addresses=[socket.inet_aton(ip)],
            port=port,
            properties={
                b"service": b"Sierra Backend",
                b"path": b"/status",
            },
            server=f"{hostname}.local.",
        )
        _zeroconf = Zeroconf()
        _zeroconf.register_service(_service_info)
        print(f"[DISCOVERY] Advertising Sierra on mDNS as {name} at {ip}:{port}")
        return True
    except Exception as e:  # pragma: no cover - defensive
        print(f"[DISCOVERY] Could not advertise via mDNS (non-fatal): {e}")
        _zeroconf = None
        _service_info = None
        return False


def stop() -> None:
    global _zeroconf, _service_info
    if _zeroconf is not None:
        try:
            if _service_info is not None:
                _zeroconf.unregister_service(_service_info)
            _zeroconf.close()
        except Exception:
            pass
    _zeroconf = None
    _service_info = None
