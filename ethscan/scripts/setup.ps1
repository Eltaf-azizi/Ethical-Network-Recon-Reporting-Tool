$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

python -m venv .venv
& .\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements-dev.txt

Write-Host ""
Write-Host "[+] Setup complete."
Write-Host "[+] Activate with: .\.venv\Scripts\Activate.ps1"
Write-Host "[+] Try: python -m ethscan 127.0.0.1 -p 80"