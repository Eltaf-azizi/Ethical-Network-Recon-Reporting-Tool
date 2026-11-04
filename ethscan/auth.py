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



def load_scope(scope_path: str | Path) -> dict:
    """Load and validate a scope file. Raises on any structural problem."""
    path = Path(scope_path)
    if not path.is_file():
        raise FileNotFoundError(f"scope file not found: {scope_path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("scope file must be a JSON object")

    targets = data.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("scope file must contain a non-empty 'targets' list")

    if not all(isinstance(t, str) for t in targets):
        raise ValueError("scope 'targets' must be a list of strings")

    return data


def scope_covers(scope: dict, target: str) -> bool:
    """Exact string match against the scope's targets list."""
    return target in scope.get("targets", [])


def scope_is_expired(scope: dict) -> bool:
    """Return True if the scope has an 'expires' field that is in the past."""
    raw = scope.get("expires")
    if not raw:
        return False
    try:
        when = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        return when < datetime.now(timezone.utc)
    except Exception:
        # Malformed date: don't block on it, but the CLI could warn.
        return False

