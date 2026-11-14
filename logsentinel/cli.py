from __future__ import annotations
import argparse
from .analyzer import analyze_events
from .parser import parse_path
from .report import write_reports
def build_parser():
    parser = argparse.ArgumentParser(description="Analyze .log and .txt files for suspicious patterns."); parser.add_argument("--path", required=True, help="log file or directory to analyze"); parser.add_argument("--output", default="logsentinel_report", help="output path without extension"); parser.add_argument("--window", type=int, default=60, help="error-burst window in seconds (default: 60)"); return parser
def main(argv=None):
    args = build_parser().parse_args(argv); parsed = parse_path(args.path); report = analyze_events(parsed, window_seconds=args.window); json_path, markdown_path = write_reports(report, args.output); print(f"JSON report: {json_path}"); print(f"Markdown report: {markdown_path}"); print(f"Anomaly score: {report["score"]["value"]}/100"); return 0
