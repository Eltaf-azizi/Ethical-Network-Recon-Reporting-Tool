"""
ethscan CLI.

Order of operations (this order matters):
  1. Parse arguments.
  2. Run the authorization gate. If it refuses, exit before touching the network.
  3. Parse the port list.
  4. Resolve the target (DNS) — first network activity.
  5. Scan.
  6. Build the report data.
  7. Write HTML and (optionally) JSON.
"""

import argparse
import asyncio
import socket
import sys
from pathlib import Path

from . import __version__
from .auth import check_authorization
from .constants import (
    DEFAULT_CONCURRENCY,
    DEFAULT_OUTPUT,
    DEFAULT_PORT_SPEC,
    DEFAULT_RATE,
    DEFAULT_TIMEOUT,
    EXIT_INTERRUPTED,
    EXIT_OK,
    EXIT_REFUSED,
)
from .exceptions import PortSpecError
from .report import build_report_data, render_html, write_html, write_json
from .scanner import scan_ports
from .services import infer_os
from .utils import parse_port_spec, utcnow


TEMPLATE_DIR = Path(__file__).parent / "templates"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ethscan",
        description="Ethical network reconnaissance and reporting tool.",
        epilog=(
            "You must own the target or have written permission. "
            "Pass --authorized to confirm. For non-loopback targets, "
            "also pass --scope <file>."
        ),
    )
    p.add_argument("target", help="Hostname or IP to scan.")
    p.add_argument(
        "-p", "--ports", default=DEFAULT_PORT_SPEC,
        help=f"Port spec, e.g. '22,80,443' or '1-1024' or a mix. "
             f"Default: {DEFAULT_PORT_SPEC}",
    )
    p.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT,
        help=f"Per-port timeout in seconds. Default: {DEFAULT_TIMEOUT}",
    )
    p.add_argument(
        "--concurrency", type=int, default=DEFAULT_CONCURRENCY,
        help=f"Max simultaneous in-flight connections. Default: {DEFAULT_CONCURRENCY}",
    )
    p.add_argument(
        "--rate", type=float, default=DEFAULT_RATE,
        help=f"Max connection attempts per second (token bucket). "
             f"Default: {DEFAULT_RATE}",
    )
    p.add_argument(
        "--no-banners", action="store_true",
        help="Disable banner grabbing (faster, quieter).",
    )
    p.add_argument(
        "--authorized", action="store_true",
        help="Assert you own the target or have written permission. REQUIRED.",
    )
    p.add_argument(
        "--scope", default=None,
        help="Path to a JSON scope file. Required for non-loopback targets.",
    )
    p.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT,
        help=f"Output HTML file. Default: {DEFAULT_OUTPUT}",
    )
    p.add_argument(
        "--json", dest="json_path", default=None,
        help="Optional path to also write a JSON report.",
    )
    p.add_argument(
        "--version", action="version", version=f"ethscan {__version__}",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- 1) Authorization gate ----------------------------------------
    allowed, scope_info = check_authorization(
        target=args.target,
        authorized_flag=args.authorized,
        scope_path=args.scope,
    )
    if not allowed:
        print(f"[!] {scope_info}", file=sys.stderr)
        return EXIT_REFUSED

    # --- 2) Port parsing (no network yet) -----------------------------
    try:
        ports = parse_port_spec(args.ports)
    except PortSpecError as e:
        print(f"[!] Invalid port spec: {e}", file=sys.stderr)
        return EXIT_REFUSED

    # --- 3) DNS resolution (first network activity) -------------------
    resolved_ip: str | None = None
    try:
        resolved_ip = socket.gethostbyname(args.target)
    except Exception:
        resolved_ip = None

    # --- 4) Scan ------------------------------------------------------
    started = utcnow()
    print(
        f"[*] Scanning {args.target}"
        + (f" ({resolved_ip})" if resolved_ip else "")
        + f" — {len(ports)} port(s)"
    )
    print(
        f"[*] timeout={args.timeout}s concurrency={args.concurrency} "
        f"rate={args.rate}/s banners={'off' if args.no_banners else 'on'}"
    )

    try:
        results = asyncio.run(
            scan_ports(
                host=args.target,
                ports=ports,
                timeout=args.timeout,
                concurrency=args.concurrency,
                rate=args.rate,
                banners=not args.no_banners,
            )
        )
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.", file=sys.stderr)
        return EXIT_INTERRUPTED

    finished = utcnow()


    # --- 5) OS hint ---------------------------------------------------
    os_hint = infer_os(results)

    # --- 6) Report ----------------------------------------------------
    options = {
        "timeout": args.timeout,
        "concurrency": args.concurrency,
        "rate": args.rate,
        "banners": not args.no_banners,
        "port_spec": args.ports,
    }

    report_data = build_report_data(
        target=args.target,
        resolved_ip=resolved_ip,
        started=started,
        finished=finished,
        results=results,
        scope_info=scope_info,
        os_hint=os_hint,
        options=options,
        tool_version=__version__,
    )

    html = render_html(report_data, TEMPLATE_DIR)
    write_html(html, args.output)
    print(f"[+] HTML report written: {args.output}")

    if args.json_path:
        write_json(report_data, args.json_path)
        print(f"[+] JSON report written: {args.json_path}")

    s = report_data["summary"]
    print(
        f"[+] Done in {report_data['duration_seconds']}s — "
        f"open={s['open']} closed={s['closed']} "
        f"filtered={s['filtered']} error={s['error']}"
    )
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
