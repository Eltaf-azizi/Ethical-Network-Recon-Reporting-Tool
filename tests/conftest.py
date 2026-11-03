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
    
    def _serve(self):
        while self._running:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            try:
                if self.mode == "active":
                    conn.settimeout(2.0)
                    try:
                        conn.recv(1024)
                    except Exception:
                        pass
                conn.sendall(self.banner)
                if self.mode == "passive":
                    conn.settimeout(1.0)
                    try:
                        conn.recv(64)
                    except Exception:
                        pass
            except Exception:
                pass
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

    def stop(self):
        self._running = False
        try:
            self.sock.close()
        except Exception:
            pass
