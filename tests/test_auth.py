import json
import tempfile
from pathlib import Path

from ethscan.auth import (
    check_authorization,
    is_loopback,
    load_scope,
    scope_covers,
    scope_is_expired,
)


def test_is_loopback():
    assert is_loopback("127.0.0.1")
    assert is_loopback("localhost")
    assert not is_loopback("8.8.8.8")


def test_refuses_without_authorized_flag():
    ok, reason = check_authorization("127.0.0.1", authorized_flag=False, scope_path=None)
    assert not ok
    assert "authorized" in reason.lower()


def test_allows_loopback_with_flag():
    ok, info = check_authorization("127.0.0.1", authorized_flag=True, scope_path=None)
    assert ok
    assert info["loopback"] is True


def test_refuses_nonloopback_without_scope():
    ok, reason = check_authorization("8.8.8.8", authorized_flag=True, scope_path=None)
    assert not ok
    assert "scope" in reason.lower()


def test_scope_must_cover_target():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"targets": ["192.168.1.1"], "authorized_by": "x"}, f)
        path = f.name
    try:
        ok, reason = check_authorization("8.8.8.8", True, path)
        assert not ok
        assert "not listed" in reason.lower()
    finally:
        Path(path).unlink()


def test_scope_expired_is_refused():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "targets": ["10.0.0.1"],
                "authorized_by": "x",
                "expires": "2000-01-01",
            },
            f,
        )
        path = f.name
    try:
        ok, reason = check_authorization("10.0.0.1", True, path)
        assert not ok
        assert "expired" in reason.lower()
    finally:
        Path(path).unlink()


def test_valid_scope_is_allowed():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "targets": ["10.0.0.1"],
                "authorized_by": "Eltaf",
                "expires": "2999-01-01",
            },
            f,
        )
        path = f.name
    try:
        ok, info = check_authorization("10.0.0.1", True, path)
        assert ok
        assert info["authorized_by"] == "Eltaf"
    finally:
        Path(path).unlink()
