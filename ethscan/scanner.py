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



async def scan_single_port(
    host: str,
    port: int,
    timeout: float,
    sem: asyncio.Semaphore,
    limiter: RateLimiter,
    banners: bool,
) -> ScanResult:
    # Rate-limit BEFORE taking the semaphore, so a burst of fast timeouts
    # can't sneak past the target's budget by racing through the semaphore.
    await limiter.acquire()

    async with sem:
        start = time.monotonic()
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout
            )
            latency_ms = (time.monotonic() - start) * 1000.0
            service = service_for_port(port)

            # Close the probe connection before banner-grabbing so the
            # open/closed decision is not conflated with banner traffic.
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

            banner = ""
            if banners:
                banner = await grab_banner(host, port, timeout)

            return ScanResult(
                port=port,
                state="open",
                latency_ms=round(latency_ms, 2),
                service=service,
                banner=banner,
            )

        except asyncio.TimeoutError:
            return ScanResult(port=port, state="filtered", error="timeout")
        except ConnectionRefusedError:
            return ScanResult(port=port, state="closed", error="connection refused")
        except OSError as e:
            return ScanResult(port=port, state="error", error=str(e))
        except Exception as e:
            return ScanResult(port=port, state="error", error=repr(e))



async def scan_ports(
    host: str,
    ports: list[int],
    timeout: float = 1.0,
    concurrency: int = 200,
    rate: float = 500.0,
    banners: bool = True,
) -> list[ScanResult]:
    """Scan a list of ports concurrently. Returns results in input order."""
    sem = asyncio.Semaphore(concurrency)
    limiter = RateLimiter(rate)
    tasks = [
        asyncio.create_task(
            scan_single_port(host, port, timeout, sem, limiter, banners)
        )
        for port in ports
    ]
    return await asyncio.gather(*tasks)
    