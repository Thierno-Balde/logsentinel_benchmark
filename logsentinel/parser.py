"""Parsing support for simple timestamped logs and JSON Lines."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

SUPPORTED_SUFFIXES = {".log", ".txt"}
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_SIMPLE = re.compile(
    r"^\s*(?P<timestamp>\S+)\s+(?:\[(?P<bracket_level>[A-Za-z]+)\]|(?P<level>[A-Za-z]+))\s+(?P<message>.*)$"
)

@dataclass(frozen=True)
class Event:
    timestamp: datetime | None
    level: str
    message: str
    source_file: str
    line_number: int
    format: str

@dataclass
class ParseResult:
    events: list[Event] = field(default_factory=list)
    total_lines: int = 0
    invalid_lines: int = 0
    format_counts: dict[str, int] = field(default_factory=lambda: {"simple": 0, "json_lines": 0})
    files: list[str] = field(default_factory=list)
    file_errors: list[dict[str, str]] = field(default_factory=list)

def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed

def _level(value: Any) -> str:
    normalized = str(value or "UNKNOWN").strip().upper()
    return normalized if normalized in LEVELS else "UNKNOWN"

def _json_event(data: dict[str, Any], source: str, line_number: int) -> tuple[Event | None, bool]:
    timestamp = data.get("timestamp", data.get("time", data.get("ts", data.get("date"))))
    level = data.get("level", data.get("severity", "UNKNOWN"))
    message = data.get("message", data.get("msg", data.get("text")))
    if message is None or timestamp is None:
        return None, True
    parsed_time = parse_timestamp(timestamp)
    return Event(parsed_time, _level(level), str(message), source, line_number, "json_lines"), parsed_time is None

def _simple_event(line: str, source: str, line_number: int) -> tuple[Event | None, bool]:
    match = _SIMPLE.match(line)
    if not match:
        return None, True
    timestamp = parse_timestamp(match.group("timestamp"))
    level = _level(match.group("bracket_level") or match.group("level"))
    return Event(timestamp, level, match.group("message"), source, line_number, "simple"), timestamp is None

def _parse_file(path: Path, result: ParseResult) -> None:
    result.files.append(str(path))
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        result.file_errors.append({"file": str(path), "kind": "invalid_encoding", "detail": str(exc)})
        return
    except OSError as exc:
        result.file_errors.append({"file": str(path), "kind": "read_error", "detail": str(exc)})
        return
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        result.total_lines += 1
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("{"):
            try:
                decoded = json.loads(line)
            except json.JSONDecodeError:
                event, invalid = None, True
            else:
                event, invalid = _json_event(decoded, str(path), line_number) if isinstance(decoded, dict) else (None, True)
        else:
            event, invalid = _simple_event(line, str(path), line_number)
        if event is None:
            result.invalid_lines += 1
            continue
        result.events.append(event)
        result.format_counts[event.format] += 1
        if invalid:
            result.invalid_lines += 1

def parse_path(path: str | Path) -> ParseResult:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(str(target))
    candidates = [target] if target.is_file() else sorted(
        item for item in target.rglob("*") if item.is_file() and item.suffix.lower() in SUPPORTED_SUFFIXES
    )
    result = ParseResult()
    for candidate in candidates:
        _parse_file(candidate, result)
    return result