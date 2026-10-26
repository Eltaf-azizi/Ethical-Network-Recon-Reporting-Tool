"""Shared constants. Kept out of the logic so they're easy to find and change."""

DEFAULT_TIMEOUT: float = 1.0
DEFAULT_CONCURRENCY: int = 200
DEFAULT_RATE: float = 500.0
DEFAULT_PORT_SPEC: str = "1-1024"
DEFAULT_OUTPUT: str = "report.html"

MAX_BANNER_LENGTH: int = 300
MIN_PORT: int = 1
MAX_PORT: int = 65535

LOOPBACK_IPS: frozenset[str] = frozenset({"127.0.0.1", "::1"})
LOOPBACK_NAMES: frozenset[str] = frozenset({"localhost"})

# Exit codes
EXIT_OK: int = 0
EXIT_REFUSED: int = 2
EXIT_USAGE: int = 2
EXIT_INTERRUPTED: int = 130