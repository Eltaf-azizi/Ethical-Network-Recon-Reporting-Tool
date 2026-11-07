import json
import tempfile
from datetime import timedelta
from pathlib import Path

from ethscan.report import build_report_data, render_html, write_json
from ethscan.scanner import ScanResult
from ethscan.utils import utcnow

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "ethscan" / "templates"


def _make_report():
    started = utcnow()
    finished = started + timedelta(seconds=1.5)
    results = [
        ScanResult(port=22, state="open", latency_ms=12.3, service="ssh",
                   banner="SSH-2.0-OpenSSH_8.9p1 Ubuntu"),
        ScanResult(port=80, state="closed", error="connection refused"),
        ScanResult(port=443, state="filtered", error="timeout"),
        ScanResult(port=9999, state="error", error="network unreachable"),
    ]

    return build_report_data(
        target="127.0.0.1",
        resolved_ip="127.0.0.1",
        started=started,
        finished=finished,
        results=results,
        scope_info={
            "loopback": True, "authorized_by": "loopback",
            "issued": "", "expires": "", "source": "",
            "targets": [], "consent": "",
        },
        os_hint={"family": "Linux (Ubuntu)", "confidence": "medium",
                 "ttl": None, "evidence": ["Port 22 banner contains 'ubuntu'"]},
        options={"timeout": 1.0, "concurrency": 200, "rate": 500.0,
                 "banners": True, "port_spec": "22,80,443,9999"},
        tool_version="1.0.0",
    )


def test_summary_counts():
    data = _make_report()
    assert data["summary"] == {"open": 1, "closed": 1, "filtered": 1, "error": 1}


def test_render_html_contains_sections():
    data = _make_report()
    html = render_html(data, TEMPLATE_DIR)
    assert "Authorization" in html
    assert "Ethics" in html
    assert "Methodology" in html
    assert "SSH-2.0" in html
    assert "Ubuntu" in html


def test_render_html_escapes_banner():
    data = _make_report()
    data["results"][0].banner = "<script>alert(1)</script>"
    html = render_html(data, TEMPLATE_DIR)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_write_json_roundtrips():
    data = _make_report()
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "out.json"
        write_json(data, path)
        loaded = json.loads(path.read_text())
    assert loaded["target"] == "127.0.0.1"
    assert loaded["summary"]["open"] == 1
    assert loaded["results"][0]["port"] == 22