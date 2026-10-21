# Changelog

## [1.0.0] — 2025-01-01
### Added
- Async TCP connect scanner with semaphore + token-bucket rate limiter
- Banner grabbing for SSH, HTTP, HTTPS/TLS, Redis, and generic TCP services
- Basic OS hint from banners
- Mandatory `--authorized` flag and scope-file enforcement
- HTML + JSON report generation via Jinja2
- Test suite with safe local dummy servers

## [0.1.0] — 2024-12-15
### Added
- Project skeleton and single-port probe