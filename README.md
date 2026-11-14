# LogSentinel

LogSentinel is a standard-library Python tool for triaging technical logs. It reads `.log` and `.txt` files recursively, accepts simple timestamped lines and JSON Lines, detects suspicious error bursts and repeated messages, then writes JSON and Markdown reports.

> This is an indicative triage tool. It is not a SIEM, a universal vendor parser, or a complete security investigation.

## Usage

```bash
python -m logsentinel --help
python -m logsentinel --path examples/sample.log --output reports/sample --window 60
python -m logsentinel --path examples/sample_jsonl.txt --output reports/jsonl --window 120
```

The output base path receives `.json` and `.md` files. `--window` is the error-burst window in seconds. The analyzer uses a burst threshold of three severe events and a repeated-message threshold of three occurrences.

## Supported inputs

Simple lines:

```text
2026-11-14T10:00:00Z ERROR connection reset by peer
```

JSON Lines objects with `timestamp`/`time`/`ts`/`date`, `level`/`severity`, and `message`/`msg`/`text` fields are accepted. Naive timestamps are interpreted as UTC. Invalid dates and malformed lines are counted without stopping analysis; invalid UTF-8 files are recorded as file errors.

## Score

The score is deterministic and indicative, from 0 to 100:

- 0–20 points: ratio of invalid lines;
- 0–40 points: ratio of `ERROR` and `CRITICAL` events;
- 0–20 points: detected error-burst groups;
- 0–20 points: repeated-message groups;
- the result is capped at 100.

The report exposes the score components so a reviewer can challenge the result instead of treating it as a black box.

## Development and verification

The project is developed remote-first. The VPS is used only to operate GitHub; application code and tests run in GitHub Actions. The CI workflow runs the standard-library `unittest` suite on Python 3.12, generates reports from the synthetic fixtures, verifies they are non-empty and uploads them as an artifact.

## Sources consulted

- Python `datetime.fromisoformat`: https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
- Python `json` module: https://docs.python.org/3/library/json.html
- JSON Lines specification: https://jsonlines.org/
- NIST SP 800-92, Guide to Computer Security Log Management: https://csrc.nist.gov/pubs/sp/800/92/final

These sources informed strict timestamp handling, line-oriented JSON parsing, invalid-record tolerance and the distinction between log triage and a full security monitoring system.
