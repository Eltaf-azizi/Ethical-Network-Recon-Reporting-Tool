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


class RateLimiter:
    """Async token bucket. `rate` tokens are added per second, capped at `rate`."""

    def __init__(self, rate: float):
        if rate <= 0:
            raise ValueError("rate must be > 0")
        self.rate = float(rate)
        self.tokens = float(rate)
        self.updated = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self.updated
                self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
                self.updated = now
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                wait = (1.0 - self.tokens) / self.rate
            await asyncio.sleep(wait)

