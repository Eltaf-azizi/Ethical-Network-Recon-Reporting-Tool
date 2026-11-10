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