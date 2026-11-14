"""Deterministic anomaly analysis for parsed log events."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timedelta
import re
from typing import Any
from .parser import Event, LEVELS, ParseResult

def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None

def _message_key(message: str) -> str:
    return re.sub(r"\s+", " ", message.strip())

def _error_bursts(events: list[Event], window_seconds: int, threshold: int) -> list[dict[str, Any]]:
    dated = sorted((event for event in events if event.timestamp and event.level in {"ERROR", "CRITICAL"}), key=lambda event: event.timestamp)
    bursts: list[dict[str, Any]] = []
    for start_index, start in enumerate(dated):
        end_index = start_index
        limit = start.timestamp + timedelta(seconds=window_seconds)
        while end_index + 1 < len(dated) and dated[end_index + 1].timestamp <= limit:
            end_index += 1
        if end_index - start_index + 1 >= threshold:
            window_events = dated[start_index : end_index + 1]
            start_time = window_events[0].timestamp
            end_time = window_events[-1].timestamp
            if not bursts or start_time > bursts[-1]["_end_datetime"]:
                bursts.append({
                    "start": _iso(start_time),
                    "end": _iso(end_time),
                    "count": len(window_events),
                    "levels": dict(Counter(event.level for event in window_events)),
                    "files": sorted({event.source_file for event in window_events}),
                    "_end_datetime": end_time,
                })
    for burst in bursts:
        del burst["_end_datetime"]
    return bursts

def _repeated_messages(events: list[Event], threshold: int) -> list[dict[str, Any]]:
    groups: dict[str, list[Event]] = {}
    for event in events:
        key = _message_key(event.message)
        if key:
            groups.setdefault(key, []).append(event)
    repeated = []
    for message, grouped in groups.items():
        if len(grouped) >= threshold:
            repeated.append({"message": message, "count": len(grouped), "levels": dict(Counter(event.level for event in grouped)), "files": sorted({event.source_file for event in grouped})})
    return sorted(repeated, key=lambda item: (-item["count"], item["message"]))

def _score(parsed: ParseResult, bursts: list[dict[str, Any]], repeated: list[dict[str, Any]]) -> dict[str, Any]:
    total = parsed.total_lines or 1
    levels = Counter(event.level for event in parsed.events)
    invalid_points = min(20.0, parsed.invalid_lines / total * 20)
    severe_points = min(40.0, (levels["ERROR"] + levels["CRITICAL"]) / total * 40)
    burst_points = min(20.0, len(bursts) * 10.0)
    repeat_points = min(20.0, len(repeated) * 10.0)
    value = round(min(100.0, invalid_points + severe_points + burst_points + repeat_points), 2)
    return {"value": int(value) if value.is_integer() else value, "components": {"invalid_lines": round(invalid_points, 2), "severe_levels": round(severe_points, 2), "error_bursts": round(burst_points, 2), "repeated_messages": round(repeat_points, 2)}, "method": "0-20 invalid-line ratio + 0-40 ERROR/CRITICAL ratio + 0-20 bursts + 0-20 repeated-message groups, capped at 100."}

def analyze_events(parsed: ParseResult, *, window_seconds: int = 60, burst_threshold: int = 3, repetition_threshold: int = 3) -> dict[str, Any]:
    if window_seconds <= 0 or burst_threshold <= 0 or repetition_threshold <= 0:
        raise ValueError("analysis thresholds must be positive")
    levels = {level: 0 for level in LEVELS}; levels["UNKNOWN"] = 0
    for event in parsed.events: levels[event.level] = levels.get(event.level, 0) + 1
    bursts = _error_bursts(parsed.events, window_seconds, burst_threshold); repeated = _repeated_messages(parsed.events, repetition_threshold)
    return {"tool": "LogSentinel", "version": "0.1.0", "statistics": {"files": len(parsed.files), "total_lines": parsed.total_lines, "parsed_events": len(parsed.events), "invalid_lines": parsed.invalid_lines, "levels": levels, "formats": parsed.format_counts}, "anomalies": {"error_bursts": bursts, "repeated_messages": repeated}, "file_errors": parsed.file_errors, "configuration": {"window_seconds": window_seconds, "burst_threshold": burst_threshold, "repetition_threshold": repetition_threshold}, "score": _score(parsed, bursts, repeated), "files": parsed.files}