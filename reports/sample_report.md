# LogSentinel report

**Anomaly score:** 40/100

## Summary

- Files: 1
- Total lines: 7
- Parsed events: 7
- Invalid lines: 1

## Severity statistics

- DEBUG: 1
- INFO: 1
- WARNING: 1
- ERROR: 2
- CRITICAL: 1
- UNKNOWN: 1

## Error bursts

- 3 severe events from `2026-11-14T10:01:00+00:00` to `2026-11-14T10:01:02+00:00`

## Repeated messages

- `connection reset by peer` — 3 occurrences

## Score method

- 0-20 invalid-line ratio + 0-40 ERROR/CRITICAL ratio + 0-20 bursts + 0-20 repeated-message groups, capped at 100.

## File errors

- None

## Limits

This is a deterministic triage aid, not a complete SIEM, parser for every vendor format, or security investigation.
