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

