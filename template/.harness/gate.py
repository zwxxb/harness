#!/usr/bin/env python3
"""Severity gate for the HARNESS.md review loop.

Parses .harness/ledger.md and exits nonzero while any critical, high, or
medium finding is still `open` or `confirmed`. Stdlib only.

Exit codes: 0 clean, 1 blocking findings (or, with --done, fewer than two
round reports), 2 ledger missing or malformed.
"""

import argparse
import json
import re
import sys
from pathlib import Path

BLOCKING_SEVERITIES = ("critical", "high", "medium")
SEVERITIES = ("critical", "high", "medium", "low", "info")
STATUSES = ("open", "confirmed", "fixed", "wontfix", "waived")

RECORD_RE = re.compile(
    r"^###\s+(F-\d{3,})\s+\[(open|confirmed|fixed|wontfix|waived)\]\s+"
    r"(critical|high|medium|low|info)\s*$"
)

LEDGER_TEMPLATE = """# Review Ledger

Append-only findings ledger for the HARNESS.md review loop. Never delete or
renumber records. Retire a finding by flipping its status, never by removing
it. Section headings use `##`; the `###` heading is reserved for records.

## Status meanings

- open      found by a hunt pass; triage not done yet
- confirmed triage verified a true positive; awaiting fix
- fixed     patched and proven (passes/prove-post-patch-validation.md)
- wontfix   triage verified FALSE POSITIVE; one-line evidence required
- waived    waived by the user; reason required

## Record format

The gate parses the heading line only; keep it exact:

    ### F-NNN [open] medium
    - lens: review
    - title: short title
    - location: path/to/file.py:12
    - evidence: why this is real and what breaks

For fixed records add `- commit: <sha>` and `- proof: <evidence line>`.

## Records
"""


def parse_ledger(text: str):
    records = []
    seen = {}
    errors = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if not line.startswith("### "):
            continue
        m = RECORD_RE.match(line)
        if not m:
            errors.append(f"line {lineno}: malformed record heading: {line!r}")
            continue
        fid, status, severity = m.group(1), m.group(2), m.group(3)
        if fid in seen:
            errors.append(
                f"line {lineno}: duplicate record id {fid} (first on line {seen[fid]})"
            )
            continue
        seen[fid] = lineno
        records.append({"id": fid, "status": status, "severity": severity, "line": lineno})
    return records, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Severity gate for the HARNESS.md loop.")
    ap.add_argument("--ledger", type=Path, default=Path(".harness/ledger.md"))
    ap.add_argument("--init", action="store_true", help="create the ledger if missing")
    ap.add_argument("--json", action="store_true", help="print counts as JSON")
    ap.add_argument("--done", action="store_true",
                    help="final check: also require two round reports (a round plus the confirmation round)")
    args = ap.parse_args()

    if args.init and not args.ledger.exists():
        args.ledger.parent.mkdir(parents=True, exist_ok=True)
        args.ledger.write_text(LEDGER_TEMPLATE, encoding="utf-8")
        print(f"created {args.ledger}")

    if not args.ledger.exists():
        print(
            f"no ledger at {args.ledger}; run: python3 {sys.argv[0]} --init",
            file=sys.stderr,
        )
        return 2

    records, errors = parse_ledger(args.ledger.read_text(encoding="utf-8"))
    if errors:
        for e in errors:
            print(f"ledger error: {e}", file=sys.stderr)
        print(
            "fix the record headings (format is at the top of the ledger).",
            file=sys.stderr,
        )
        return 2

    counts = {s: {st: 0 for st in STATUSES} for s in SEVERITIES}
    for r in records:
        counts[r["severity"]][r["status"]] += 1

    blocking = [
        r
        for r in records
        if r["severity"] in BLOCKING_SEVERITIES and r["status"] in ("open", "confirmed")
    ]

    if args.json:
        print(json.dumps({
            "records": len(records),
            "blocking": len(blocking),
            "blocking_ids": [r["id"] for r in blocking],
            "counts": counts,
        }))
    else:
        n = len(records)
        print(f"ledger: {args.ledger} ({n} record{'s' if n != 1 else ''})")
        for s in SEVERITIES:
            openish = counts[s]["open"] + counts[s]["confirmed"]
            tail = (
                f"{counts[s]['fixed']} fixed, "
                f"{counts[s]['wontfix']} wontfix, {counts[s]['waived']} waived"
            )
            marker = "  <-- blocking" if s in BLOCKING_SEVERITIES and openish else ""
            print(f"{s:8} {openish} open/confirmed, {tail}{marker}")

    if blocking:
        print(f"BLOCKED: {len(blocking)} critical/high/medium finding(s) still open or confirmed:")
        for r in blocking:
            print(f"  {r['id']} [{r['status']}] {r['severity']} (line {r['line']})")
        print("Next: triage and fix per HARNESS.md, then re-run this gate.")
        return 1

    rounds = len(list(args.ledger.parent.glob("rounds/round-*.md")))
    if args.done and rounds < 2:
        print(f"NOT DONE: {rounds} round report(s) in .harness/rounds/; need a round plus a confirmation round.")
        return 1

    print("PASS: no open or confirmed critical/high/medium findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
