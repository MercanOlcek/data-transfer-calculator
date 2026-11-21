"""Local and public IP information utilities."""

from __future__ import annotations

import socket
from datetime import datetime
from typing import Any

import requests


def kullanici_ip() -> str:
    """Return the preferred local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def get_local_ip() -> str:
    """Return the preferred local IP address, or a fallback message."""
    try:
        return kullanici_ip()
    except OSError:
        return "Unavailable"


def get_public_ip_info(timeout: float = 4.0) -> dict[str, Any]:
    """Fetch public IP tracking information from a public API.

    Returns a dictionary with normalized fields and a status indicator.
    """
    result: dict[str, Any] = {
        "status": "error",
        "public_ip": "Unavailable",
        "city": "-",
        "region": "-",
        "country": "-",
        "isp": "-",
        "timezone": "-",
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "",
    }

    try:
        response = requests.get("http://ip-api.com/json/", timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:  # noqa: BLE001 - show friendly status in TUI
        result["message"] = str(exc)
        return result

    if data.get("status") != "success":
        result["message"] = str(data.get("message", "Lookup failed"))
        return result

    result.update(
        {
            "status": "success",
            "public_ip": data.get("query", "Unavailable"),
            "city": data.get("city", "-") or "-",
            "region": data.get("regionName", "-") or "-",
            "country": data.get("country", "-") or "-",
            "isp": data.get("isp", "-") or "-",
            "timezone": data.get("timezone", "-") or "-",
            "message": "",
        }
    )
    return result


if __name__ == "__main__":
    print("Local IP:", get_local_ip())
    print("Public IP info:", get_public_ip_info())