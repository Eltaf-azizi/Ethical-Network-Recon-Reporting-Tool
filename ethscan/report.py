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


def render_html(report_data: dict, template_dir: str | Path) -> str:
    """Render the HTML report. Autoescaping is ON."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.html.j2")
    open_results = [r for r in report_data["results"] if r.state == "open"]
    return template.render(report=report_data, open_results=open_results)


def write_html(html: str, output_path: str | Path) -> None:
    path = Path(output_path)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def write_json(report_data: dict, output_path: str | Path) -> None:
    path = Path(output_path)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)

    def default(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)

    with path.open("w", encoding="utf-8") as f:
        json.dump(report_data, f, default=default, indent=2)