"""
Report generation.

Separates:
  - building the report *data* (pure Python, testable),
  - rendering it (Jinja2),
  - writing it (filesystem).
"""

import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def build_report_data(
    target: str,
    resolved_ip: str | None,
    started: datetime,
    finished: datetime,
    results: list,
    scope_info: dict,
    os_hint: dict | None,
    options: dict,
    tool_version: str,
) -> dict:
    """Assemble the report data dict. Pure function — no I/O."""
    summary = {"open": 0, "closed": 0, "filtered": 0, "error": 0}
    for r in results:
        summary[r.state] = summary.get(r.state, 0) + 1

    return {
        "target": target,
        "resolved_ip": resolved_ip,
        "started": started,
        "finished": finished,
        "duration_seconds": round((finished - started).total_seconds(), 2),
        "tool_version": tool_version,
        "results": results,
        "scope": scope_info,
        "os_hint": os_hint,
        "options": options,
        "summary": summary,
    }

