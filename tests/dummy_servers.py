"""
Standalone dummy servers for manual testing.

    python tests/dummy_servers.py

Serves on 127.0.0.1:
    2222  — fake SSH banner
    8080  — fake HTTP response
    6379  — fake Redis PING
"""

import socket
import threading


def serve(port: int, banner: bytes, mode: str = "passive") -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(16)
    print(f"[dummy] listening on 127.0.0.1:{port} ({mode})")
