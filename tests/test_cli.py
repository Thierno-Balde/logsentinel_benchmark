import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from logsentinel.cli import main


class LogSentinelCLITests(unittest.TestCase):
    def test_cli_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "sample.log"
            source.write_text("2026-11-14T10:00:00Z INFO ready\n", encoding="utf-8")
            output = root / "out" / "report"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--path", str(source), "--output", str(output), "--window", "30"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(output.with_suffix(".json").exists())
            self.assertTrue(output.with_suffix(".md").exists())
            payload = json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(payload["configuration"]["window_seconds"], 30)
            self.assertIn("Anomaly score", stdout.getvalue())

    def test_cli_help_is_available(self):
        with self.assertRaises(SystemExit) as raised:
            main(["--help"])
        self.assertEqual(raised.exception.code, 0)


if __name__ == "__main__":
    unittest.main()