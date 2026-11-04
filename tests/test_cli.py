import sys
from pathlib import Path

from ethscan.cli import main


def test_refuses_without_authorized(capsys):
    code = main(["127.0.0.1", "-p", "80"])
    captured = capsys.readouterr()
    assert code == 2
    assert "authorized" in captured.err.lower()


def test_refuses_nonloopback_without_scope(capsys):
    code = main(["8.8.8.8", "-p", "53", "--authorized"])
    captured = capsys.readouterr()
    assert code == 2
    assert "scope" in captured.err.lower()


def test_invalid_port_spec(capsys):
    code = main(["127.0.0.1", "-p", "not-a-port", "--authorized"])
    captured = capsys.readouterr()
    assert code == 2
    assert "invalid" in captured.err.lower() or "spec" in captured.err.lower()


def test_loopback_scan_writes_report(tmp_path, dummy_ssh):
    out = tmp_path / "out.html"
    code = main(
        [
            "127.0.0.1",
            "-p", str(dummy_ssh.port),
            "--authorized",
            "--no-banners",
            "-o", str(out),
        ]
    )
    assert code == 0
    assert out.is_file()
    assert "Network Reconnaissance Report" in out.read_text()


def test_json_output(tmp_path, dummy_ssh):
    out = tmp_path / "out.html"
    js = tmp_path / "out.json"
    code = main(
        [
            "127.0.0.1",
            "-p", str(dummy_ssh.port),
            "--authorized",
            "--no-banners",
            "-o", str(out),
            "--json", str(js),
        ]
    )
    assert code == 0
    assert js.is_file()
    