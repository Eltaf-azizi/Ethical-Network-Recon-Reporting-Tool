import asyncio
import time

from ethscan.scanner import RateLimiter, scan_ports


def test_open_and_closed_detection(dummy_ssh, closed_port):
    results = asyncio.run(
        scan_ports(
            "127.0.0.1",
            [dummy_ssh.port, closed_port],
            timeout=1.0,
            concurrency=10,
            rate=100.0,
            banners=False,
        )
    )
    states = {r.port: r.state for r in results}
    assert states[dummy_ssh.port] == "open"
    assert states[closed_port] in ("closed", "filtered")


def test_banner_grab_over_second_connection(dummy_ssh):
    results = asyncio.run(
        scan_ports(
            "127.0.0.1",
            [dummy_ssh.port],
            timeout=1.0,
            concurrency=5,
            rate=100.0,
            banners=True,
        )
    )
    assert results[0].state == "open"
    assert "SSH-2.0" in results[0].banner


def test_rate_limiter_throttles():
    async def run():
        limiter = RateLimiter(rate=20.0)
        start = time.monotonic()
        for _ in range(40):
            await limiter.acquire()
        return time.monotonic() - start

    elapsed = asyncio.run(run())
    # 40 tokens at 20/sec means roughly 1s of additional waiting beyond
    # the initial burst of `rate` tokens. Allow plenty of slack.
    assert elapsed >= 0.5
