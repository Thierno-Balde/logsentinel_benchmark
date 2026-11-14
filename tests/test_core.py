import json
import tempfile
import unittest
from pathlib import Path
from datetime import timezone

from logsentinel.analyzer import analyze_events
from logsentinel.parser import parse_path
from logsentinel.report import render_json, render_markdown


class LogSentinelAcceptanceTests(unittest.TestCase):
    def write(self, root: Path, name: str, content: bytes) -> Path:
        path = root / name
        path.write_bytes(content)
        return path

    def test_simple_log_parsing_and_severity_statistics(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "events.log", b"2026-11-14T10:00:00Z INFO started\n2026-11-14T10:00:01Z ERROR failed\n")
            parsed = parse_path(path)
            report = analyze_events(parsed, window_seconds=60)
            self.assertEqual(len(parsed.events), 2)
            self.assertEqual(report["statistics"]["levels"]["INFO"], 1)
            self.assertEqual(report["statistics"]["levels"]["ERROR"], 1)
            self.assertEqual(parsed.events[0].timestamp.tzinfo, timezone.utc)

    def test_json_lines_parsing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "events.txt", b'{"timestamp":"2026-11-14T10:00:00Z","level":"WARNING","message":"slow"}\n')
            parsed = parse_path(path)
            self.assertEqual(parsed.format_counts["json_lines"], 1)
            self.assertEqual(parsed.events[0].message, "slow")
            self.assertEqual(parsed.events[0].level, "WARNING")

    def test_invalid_date_is_kept_as_invalid_without_stopping(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "events.log", b"not-a-date ERROR broken\n2026-11-14T10:00:00Z INFO valid\n")
            parsed = parse_path(path)
            self.assertEqual(len(parsed.events), 2)
            self.assertEqual(parsed.invalid_lines, 1)

    def test_error_burst_detection_uses_configured_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = [f"2026-11-14T10:00:0{i}Z ERROR failure-{i}\n" for i in range(4)]
            path = self.write(Path(tmp), "events.log", "".join(lines).encode())
            report = analyze_events(parse_path(path), window_seconds=10, burst_threshold=3)
            self.assertGreaterEqual(len(report["anomalies"]["error_bursts"]), 1)
            self.assertEqual(report["configuration"]["window_seconds"], 10)

    def test_repeated_messages_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = [f"2026-11-14T10:00:0{i}Z WARNING retry later\n" for i in range(3)]
            path = self.write(Path(tmp), "events.log", "".join(lines).encode())
            report = analyze_events(parse_path(path), repetition_threshold=3)
            self.assertEqual(report["anomalies"]["repeated_messages"][0]["count"], 3)

    def test_empty_directory_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = analyze_events(parse_path(Path(tmp)))
            self.assertEqual(report["statistics"]["total_lines"], 0)
            self.assertEqual(report["score"]["value"], 0)

    def test_missing_path_is_rejected(self):
        with self.assertRaises(FileNotFoundError):
            parse_path(Path("/definitely/missing/logsentinel-path"))

    def test_invalid_encoding_is_counted_and_does_not_abort_other_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "bad.log", b"\xff\xfe\xfa")
            self.write(root, "good.log", b"2026-11-14T10:00:00Z INFO valid\n")
            parsed = parse_path(root)
            self.assertEqual(len(parsed.events), 1)
            self.assertEqual(parsed.file_errors[0]["kind"], "invalid_encoding")

    def test_reports_are_valid_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "events.log", b"2026-11-14T10:00:00Z ERROR failed\n")
            report = analyze_events(parse_path(root))
            encoded = render_json(report)
            markdown = render_markdown(report)
            self.assertEqual(json.loads(encoded)["score"]["value"], report["score"]["value"])
            self.assertIn("# LogSentinel report", markdown)
            self.assertIn("Anomaly score", markdown)


if __name__ == "__main__":
    unittest.main()