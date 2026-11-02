#!/usr/bin/env bash
# Spin up (or tear down) local Docker targets for realistic banner testing.
set -euo pipefail

case "${1:-up}" in
  up)
    docker run -d --name eth-web   -p 8080:80    nginx:alpine
    docker run -d --name eth-redis -p 6379:6379  redis:7-alpine
    docker run -d --name eth-ssh   -p 2222:2222  linuxserver/openssh-server \
      -e PUID=1000 -e PGID=1000 -e USER_NAME=tester \
      -e PASSWORD_ACCESS=true -e USER_PASSWORD=test
    echo "[+] Targets up. Scan with:"
    echo "    python -m ethscan 127.0.0.1 -p 2222,6379,8080 --authorized -o reports/docker.html"
    ;;
  down)
    docker rm -f eth-web eth-redis eth-ssh 2>/dev/null || true
    echo "[+] Targets down."
    ;;
  *)
    echo "Usage: $0 [up|down]" >&2
    exit 2
    ;;
esac