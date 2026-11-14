# LogSentinel

LogSentinel analyses technical `.log` and `.txt` files, including simple timestamped lines and JSON Lines, then produces actionable JSON and Markdown reports.

This repository is being built through a remote-first TDD workflow. The acceptance tests define the parser, anomaly analysis, reports and CLI contract before the implementation is added.

## Planned CLI

```text
python -m logsentinel --path examples/sample.log --output reports/sample --window 60
```

The final implementation will use only the Python standard library. It will not claim to replace a SIEM, parser for every vendor format, or a security investigation.