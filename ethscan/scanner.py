"""
Async TCP connect scanner.

- One async task per port.
- A semaphore caps how many connections are in flight at once.
- A token-bucket rate limiter caps how many connections per second we
  actually attempt. Both limits exist because they solve different problems:
  the semaphore protects *us* from running out of file descriptors; the rate
  limiter protects the *target* from being flooded.
"""

import asyncio
import time
from dataclasses import dataclass, field

from .services import grab_banner, service_for_port


@dataclass
class ScanResult:
    port: int
    state: str                       # 'open' | 'closed' | 'filtered' | 'error'
    latency_ms: float | None = None
    service: str = ""
    version: str = ""
    banner: str = ""
    error: str = ""
