"""
Authorization and scope enforcement.

This module is deliberately the first thing the CLI calls. It must refuse to
let the scanner touch the network unless the operator has explicitly asserted
authorization AND, for non-loopback targets, provided a scope file that names
the target.
"""

import json
import socket
from datetime import datetime, timezone
from pathlib import Path

from .constants import LOOPBACK_IPS, LOOPBACK_NAMES


def is_loopback(target: str) -> bool:
    """Best-effort check that a target resolves to this machine."""
    if target in LOOPBACK_NAMES or target in LOOPBACK_IPS:
        return True
    try:
        ip = socket.gethostbyname(target)
    except Exception:
        return False
    if ip in LOOPBACK_IPS:
        return True
    return ip.startswith("127.")
