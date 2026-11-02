#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements-dev.txt

echo
echo "[+] Setup complete."
echo "[+] Activate with: source .venv/bin/activate"
echo "[+] Try: python -m ethscan 127.0.0.1 -p 80"