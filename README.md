<h1 align="center">Ethical Network Recon Reporting Tool</h1>

An ethical network reconnaissance and reporting tool — built to be honest about what it does and what it refuses to do.

## Table of contents

 - Why I built this
 - What it does
 - What it deliberately does not do
 - Demo
 - Requirements
 - Installation
 - Quick start
 - Usage
 - CLI reference
 - Scope file format
 - How it works
 - Project structure
 - Testing
 - Ethics & legal
 - What I learned
 - Roadmap
 - License


## Why I built this
I'd already written a basic Python port scanner and it worked — but it was a toy. It scanned a couple of ports, printed whether they were open, and that was it. No authorization gate, no rate limiting, no report, no real understanding of why a filtered port is different from a closed one.

I wanted to build the next version properly:

 - Fast enough to be useful (async, not blocking)
 - Safe enough to be responsible (rate-limited, semaphore-capped)
 - Honest enough to be trustworthy (clear about what a "hint" is and what an "open port" means)
 - Presentable enough to hand to someone (a real HTML report, not terminal output)

And most importantly, I wanted a tool that cannot be used accidentally. That's why --authorized is mandatory. That's why non-loopback targets need a scope file. That's why the gate runs before DNS resolution, not after.

This is a learning project. It is not a replacement for nmap. But it is a complete, working, honest tool with an ethics frame built into the design.


## What it does
 - Async TCP connect scanning over a configurable port range (1-1024, 22,80,443, or 8000-8100, or any mix)
 - Service detection for ~70 common ports via a built-in table
 - Banner grabbing for SSH, HTTP, HTTPS/TLS, Redis, and generic TCP services
 - Basic OS hint derived from banner substrings, with confidence level and evidence shown in the report
 - Mandatory --authorized flag — the tool refuses to run without it
 - Scope file enforcement for non-loopback targets — the target must be listed by name
 - Rate limiting (token bucket) plus a semaphore to cap concurrency
 - HTML report with autoescaped output, methodology section, and full ethics section
 - Optional JSON export for downstream tooling
 - Test suite with safe local dummy servers so you can verify without scanning anything you don't own
 

## what it deliberately does not do
I want to be upfront about the things I left out, because each one is a deliberate choice:

 - No SYN (half-open) scan. That requires raw sockets and root privileges, and it's more aggressive on the target. Connect scan is honest: it uses the same primitives any application uses.

 - No OS fingerprinting beyond banner heuristics. Nmap-style TCP/IP fingerprinting is a rabbit hole, and I'd rather under-promise than ship a "hint" that pretends to be a fingerprint.

 - No exploit attempts. No payloads. No credential guessing. Those things turn a reconnaissance tool into an attack tool, and that's exactly what I wanted to avoid.

Every omission above is documented in `docs/ethics.md` with the reasoning.


## Demo
### Refusal (the point of the project)
```
text
PS> python -m ethscan 127.0.0.1 -p 80
[!] Refusing to run: missing --authorized flag.
You must explicitly assert that you own this target or have written permission to test it.
```
Exit code: 2.

### Loopback scan
```
text
PS> python -m ethscan 127.0.0.1 -p 22,80,443,2222,6379,8080 --authorized -o reports\local.html
[*] Scanning 127.0.0.1 (127.0.0.1) — 6 port(s)
[*] timeout=1.0s concurrency=200 rate=500.0/s banners=on
[+] HTML report written: reports\local.html
[+] Done in 0.42s — open=3 closed=3 filtered=0 error=0
```

## Authorized remote scan
```bash
python -m ethscan 192.168.56.10 -p 1-1024 --authorized \
  --scope scope.json \
  -o reports/vm.html --json reports/vm.json
```
The HTML report includes:

 - Summary cards (open / closed / filtered / error)
 - Authorization & scope section
 - OS hint with evidence
 - Open ports table with service names and banners
 - Full results (collapsible)
 - Methodology section
 - Ethics & legal section

## Requirements

 - Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.14)
 - jinja2 for the report template
 - Development: pytest, pytest-asyncio, ruff, mypy

No system dependencies. No compilers. No Docker required (though Docker makes a great test target).


## Installation
```bash
git clone https://github.com/<your-username>/ethscan.git
cd ethscan

python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```
**Windows note:** if your project folder path contains & (e.g., Recon & Reporting Tool), python -m venv will refuse to create the environment. Either move the project to a path without special characters (like C:\dev\ethscan), or skip the venv entirely — global pip install works fine for this project.

