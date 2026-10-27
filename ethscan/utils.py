"""Small helpers used across the package."""

from datetime import datetime, timezone

from .constants import MAX_PORT, MIN_PORT
from .exceptions import PortSpecError


def parse_port_spec(spec: str) -> list[int]:
    """
    Parse a port spec string into a sorted list of unique ports.

    Accepted forms:
        "80"                  → [80]
        "22,80,443"           → [22, 80, 443]
        "1-1024"              → [1, 2, ..., 1024]
        "22,80,8000-8100"     → mixed

    Raises PortSpecError on invalid input.
    """
    if not spec or not spec.strip():
        raise PortSpecError("empty port spec")

    ports: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, _, end_s = part.partition("-")
            try:
                start = int(start_s)
                end = int(end_s)
            except ValueError as e:
                raise PortSpecError(f"invalid port range: {part!r}") from e
            if not (MIN_PORT <= start <= end <= MAX_PORT):
                raise PortSpecError(f"port range out of bounds: {part!r}")
            ports.update(range(start, end + 1))
        else:
            try:
                p = int(part)
            except ValueError as e:
                raise PortSpecError(f"invalid port: {part!r}") from e
            if not (MIN_PORT <= p <= MAX_PORT):
                raise PortSpecError(f"port out of bounds: {part!r}")
            ports.add(p)

    if not ports:
        raise PortSpecError("port spec produced no ports")

    return sorted(ports)


def utcnow() -> datetime:
    """Timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def humanize_duration(seconds: float) -> str:
    """Turn a float number of seconds into a compact human string."""
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {sec:.0f}s"
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m"


def safe_truncate(s: str, limit: int) -> str:
    """Truncate a string, adding an ellipsis if it was cut."""
    if s is None:
        return ""
    if len(s) <= limit:
        return s
    return s[:limit] + "…"