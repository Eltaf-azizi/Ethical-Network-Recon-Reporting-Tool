import asyncio

from ethscan.scanner import ScanResult
from ethscan.services import grab_banner, infer_os, service_for_port


def test_known_service_lookup():
    assert service_for_port(22) == "ssh"
    assert service_for_port(443) == "https"
    assert service_for_port(6379) == "redis"
    assert service_for_port(65535) == "unknown"


def test_grab_banner_returns_empty_on_closed_port(closed_port):
    banner = asyncio.run(grab_banner("127.0.0.1", closed_port, timeout=0.5))
    assert banner == ""


def test_grab_banner_reads_dummy_ssh(dummy_ssh):
    banner = asyncio.run(grab_banner("127.0.0.1", dummy_ssh.port, timeout=1.0))
    assert "SSH-2.0" in banner


def test_infer_os_with_no_evidence():
    results = [ScanResult(port=22, state="closed")]
    assert infer_os(results) is None


def test_infer_os_ubuntu():
    results = [
        ScanResult(
            port=22,
            state="open",
            banner="SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.4",
        )
    ]
    hint = infer_os(results)
    assert hint is not None
    assert hint["family"] == "Linux (Ubuntu)"
    assert hint["confidence"] == "medium"
    assert any("ubuntu" in e.lower() for e in hint["evidence"])


def test_infer_os_windows_takes_precedence():
    results = [
        ScanResult(port=80, state="open", banner="Microsoft-IIS/10.0 Windows"),
        ScanResult(port=22, state="open", banner="SSH Ubuntu"),
    ]
    hint = infer_os(results)
    assert hint["family"] == "Windows"