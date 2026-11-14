"""JSON and Markdown report generation."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"

def render_markdown(report: dict[str, Any]) -> str:
    stats = report["statistics"]
    score = report["score"]
    lines = [
        "# LogSentinel report", "", f"**Anomaly score:** {score['value']}/100", "",
        "## Summary", "", f"- Files: {stats['files']}", f"- Total lines: {stats['total_lines']}",
        f"- Parsed events: {stats['parsed_events']}", f"- Invalid lines: {stats['invalid_lines']}",
        "", "## Severity statistics", "",
    ]
    for level, count in stats["levels"].items():
        lines.append(f"- {level}: {count}")
    lines.extend(["", "## Error bursts", ""])
    bursts = report["anomalies"]["error_bursts"]
    lines.extend([f"- {item['count']} severe events from `{item['start']}` to `{item['end']}`" for item in bursts] or ["- None detected"])
    lines.extend(["", "## Repeated messages", ""])
    repeated = report["anomalies"]["repeated_messages"]
    lines.extend([f"- `{item['message']}` — {item['count']} occurrences" for item in repeated] or ["- None detected"])
    lines.extend(["", "## Score method", "", f"- {score['method']}", "", "## File errors", ""])
    lines.extend([f"- `{error['kind']}` in `{error['file']}`: {error['detail']}" for error in report["file_errors"]] or ["- None"])
    lines.extend(["", "## Limits", "", "This is a deterministic triage aid, not a complete SIEM, parser for every vendor format, or security investigation.", ""])
    return "\n".join(lines)

def write_reports(report: dict[str, Any], output: str | Path) -> tuple[Path, Path]:
    base = Path(output)
    base.parent.mkdir(parents=True, exist_ok=True)
    json_path = base.with_suffix(".json")
    markdown_path = base.with_suffix(".md")
    json_path.write_text(render_json(report), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path