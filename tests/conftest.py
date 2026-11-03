"""Shared pytest fixtures."""

import socket
import threading

import pytest


class _DummyServer:
    def __init__(self, banner: bytes, mode: str = "passive"):
        self.banner = banner
        self.mode = mode
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.sock.listen(8)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._running = True

    def start(self):
        self._thread.start()
        return self
    