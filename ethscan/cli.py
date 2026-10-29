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
