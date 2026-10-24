# Usage

## Install

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Refusal check

```bash
python -m ethscan 127.0.0.1 -p 80
# [!] Refusing to run: missing --authorized flag.
```

## Loopback scan

```bash
python -m ethscan 127.0.0.1 -p 1-1024 --authorized -o reports/local.html
```

## Authorized remote scan

Create `scope.json` (copy from `scope.example.json`) listing the target.
Then:

```bash
python -m ethscan 192.168.56.10 -p 1-1024 --authorized \
  --scope scope.json \
  -o reports/vm.html --json reports/vm.json
```

## Port spec syntax

| Spec | Meaning |
|---|---|
| `80` | Single port |
| `22,80,443` | List |
| `1-1024` | Range |
| `22,80,8000-8100` | Mixed |

## Quiet scans

```bash
python -m ethscan 127.0.0.1 -p 1-1024 --authorized --no-banners \
  --rate 200 --concurrency 50
```

## Testing locally with dummy servers

Terminal 1:

```bash
python tests/dummy_servers.py
```

Terminal 2:

```bash
python -m ethscan 127.0.0.1 -p 2222,6379,8080 --authorized -o reports/local.html
```