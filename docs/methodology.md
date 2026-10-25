# Methodology

## Connect scan vs SYN scan

`ethscan` performs a **TCP connect scan**. It asks the operating system to
open a full TCP connection to each port using the normal `connect()` call.

- **Connect scan** — full three-way handshake. Logged by the target's kernel.
  Requires no privileges.
- **SYN scan** (a.k.a. half-open) — sends a SYN, waits for SYN-ACK, then
  sends RST. Faster, stealthier, but requires raw sockets and root.

We chose connect scan because it is honest: it uses the same primitives any
application uses, requires no elevated privileges, and leaves a clear trail.

## Port states

| State | Meaning | Typical cause |
|---|---|---|
| `open` | Three-way handshake completed | A program is listening |
| `closed` | Target replied with RST | Nothing listening, but host reachable |
| `filtered` | No reply within timeout | Firewall dropped the packet |
| `error` | Non-timeout, non-refusal error | Network unreachable, etc. |

The `filtered` distinction matters: a "closed" port is a definite answer; a
"filtered" port is an absence of information. Reports should never conflate
the two.
