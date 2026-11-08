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

