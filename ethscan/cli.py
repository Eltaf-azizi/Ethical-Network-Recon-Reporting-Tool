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
