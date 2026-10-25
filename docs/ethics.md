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
