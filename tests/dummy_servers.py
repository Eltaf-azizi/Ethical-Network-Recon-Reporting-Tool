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


    while True:
        try:
            conn, _ = srv.accept()
        except OSError:
            break

        def handle(c=conn):
            try:
                if mode == "active":
                    c.settimeout(2.0)
                    try:
                        c.recv(1024)
                    except Exception:
                        pass
                    c.sendall(banner)
                else:
                    c.sendall(banner)
                    c.settimeout(1.0)
                    try:
                        c.recv(64)
                    except Exception:
                        pass
            finally:
                try:
                    c.close()
                except Exception:
                    pass

        threading.Thread(target=handle, daemon=True).start()



if __name__ == "__main__":
    threads = [
        threading.Thread(
            target=serve,
            args=(2222, b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.4\r\n", "passive"),
            daemon=True,
        ),
        threading.Thread(
            target=serve,
            args=(8080, b"HTTP/1.1 200 OK\r\nServer: nginx/1.24.0 (Ubuntu)\r\n\r\n", "active"),
            daemon=True,
        ),
        threading.Thread(
            target=serve,
            args=(6379, b"+PONG\r\n", "active"),
            daemon=True,
        ),
    ]
    for t in threads:
        t.start()

    print("[dummy] press Ctrl+C to stop")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\n[dummy] bye")