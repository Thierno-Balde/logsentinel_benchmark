import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from logsentinel.analyzer import analyze_events
from logsentinel.cli import main
from logsentinel.parser import parse_path
from logsentinel.report import render_markdown


class LogSentinelRegressionTests(unittest.TestCase):
    def test_space_separated_timestamp_is_parsed_as_one_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.log"
            path.write_text("2026-11-14 10:00:00 ERROR database unavailable\n", encoding="utf-8")
            parsed = parse_path(path)
            self.assertEqual(parsed.events[0].level, "ERROR")
            self.assertEqual(parsed.events[0].message, "database unavailable")
            self.assertEqual(parsed.invalid_lines, 0)

    def test_burst_detection_handles_mixed_timezone_offsets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.log"
            path.write_text(
                "2026-11-14T10:00:00+02:00 ERROR one\n"
                "2026-11-14T08:00:01Z ERROR two\n"
                "2026-11-14T08:00:02Z ERROR three\n",
                encoding="utf-8",
            )
            report = analyze_events(parse_path(path), window_seconds=5, burst_threshold=3)
            self.assertEqual(len(report["anomalies"]["error_bursts"]), 1)

    def test_cli_turns_missing_path_into_argparse_error(self):
        with self.assertRaises(SystemExit) as raised:
            main(["--path", "/definitely/missing/logsentinel", "--output", "ignored"])
        self.assertEqual(raised.exception.code, 2)

    def test_markdown_escapes_backticks_in_log_messages(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.log"
            path.write_text("2026-11-14T10:00:00Z WARNING retry `database`\n" * 3, encoding="utf-8")
            markdown = render_markdown(analyze_events(parse_path(path)))
            self.assertIn("retry \\`database\\`", markdown)


if __name__ == "__main__":
    unittest.main()