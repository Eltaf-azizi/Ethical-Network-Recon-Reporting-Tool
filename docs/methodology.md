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

## Rate limiting

Two independent limits are enforced:

1. **Semaphore (concurrency).** Caps how many connections are in flight at
   once. Protects *the scanner* from running out of file descriptors.
2. **Token bucket (rate).** Caps how many new connections are attempted per
   second. Protects *the target* from being flooded.

The token bucket holds up to `rate` tokens and refills at `rate` per second.
Each connection consumes one token. If no token is available, the caller
sleeps.

## Banner grabbing

Once a port is confirmed open, the scanner opens a **second connection** and
attempts to read a banner. For TLS ports it negotiates a handshake and reports
the cipher and protocol version. For HTTP ports it sends a `HEAD` request. For
Redis it sends `PING`. For everything else it does a generic read and a small
nudge.

Banner grabbing is a second connection. If you are counting connections, a
scan of *N* ports where *M* are open uses N + M connections.

## OS hint

The OS hint is derived from substrings in banners — `ubuntu`, `debian`,
`windows`, `freebsd`, etc. It is explicitly labelled as a hint and reported
with a confidence level. It is **not** a fingerprint. Do not treat it as one.