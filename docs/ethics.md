# Ethics & Legal

## Why this document exists

`ethscan` is a network scanner. A network scanner is a tool that sends packets
to ports on a remote machine to determine whether they are open. In the wrong
hands, that tool can be the first phase of an intrusion.

This project deliberately places a hard gate — the `--authorized` flag and,
for non-loopback targets, a scope file — in front of the scanner. This document
explains *why*.

## The law

Unauthorised scanning is illegal in many jurisdictions:

- **UK — Computer Misuse Act 1990**, s.1. Accessing a computer without
  authorisation is an offence. Scanning can constitute "access" even if
  nothing is exploited.
- **US — Computer Fraud and Abuse Act (18 U.S.C. § 1030).** Unauthorised
  access to a protected computer can be a federal crime.
- **EU — Directive 2013/40/EU**, transposed into national laws across the
  EU, criminalises unauthorised access and interference.
- **Elsewhere.** Most countries have equivalents. If you are unsure, assume
  the answer is "no."

Even where scanning is not criminal, it may breach a provider's terms of
service (cloud, ISP, hosting) and get your account terminated.

## What the gate does

1. **`--authorized` is required.** No exceptions.
2. **Loopback targets** (`127.0.0.1`, `localhost`, `::1`) are exempt from the
   scope-file requirement because they cannot affect any third party. The
   `--authorized` flag is still required.
3. **Non-loopback targets** require a scope file (`--scope <file>`) that
   names the target in a `targets` list. If the target isn't listed, the tool
   refuses to run.
4. **Expired scopes are refused.** If a scope has an `expires` date in the
   past, the tool refuses to run.

None of this is encryption. A determined operator can edit the source. The
gate exists to make unauthorised use *deliberate* rather than accidental.

## What the tool does NOT do

- No SYN (half-open) scan. That requires raw sockets and root, and is more
  aggressive.
- No OS fingerprinting beyond heuristics from banners. No Nmap-style
  TCP/IP fingerprinting.
- No exploit attempts, no payloads, no file transfers.
- No credential guessing, no brute force.

These are deliberate omissions. Every one of them would push the tool from
"reconnaissance" toward "attack."

## Operator responsibilities

If you run `ethscan` against anything other than loopback, you are asserting:

1. You own the target, **or**
2. You have **written permission** that names the target and the time window.

And you must:

- Scan only within that scope.
- Store results securely.
- Report findings responsibly.
- Not act on findings without authorisation.

If you are unsure, **stop and ask**.