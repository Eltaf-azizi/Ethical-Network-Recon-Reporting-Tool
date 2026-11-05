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
