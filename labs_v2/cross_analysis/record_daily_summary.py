"""Record a daily summary to the discovery ledger.

Appends a `daily_summary` record to discovery_ledger.jsonl with
the date, a list of accomplishments, and counts of artifacts
changed. Run at the end of each working session.

Usage:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/record_daily_summary.py \\
        "description of what was done"
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_LABS_V2 = Path(__file__).resolve().parent.parent
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"
COMPOSITES_ROOT = _LABS_V2 / "composites"
EQUATIONS_ROOT = _LABS_V2 / "equations"


def count_artifacts() -> dict:
    n_equations = sum(1 for _ in EQUATIONS_ROOT.rglob("equation.yaml"))
    n_composites = sum(1 for _ in COMPOSITES_ROOT.rglob("composite.yaml"))
    n_failure_modes = 0
    for eq_path in EQUATIONS_ROOT.rglob("equation.yaml"):
        with eq_path.open() as f:
            doc = yaml.safe_load(f) or {}
        n_failure_modes += len(doc.get("failure_modes") or [])
    return {
        "n_equations": n_equations,
        "n_composites": n_composites,
        "n_failure_modes": n_failure_modes,
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: record_daily_summary.py <summary text>",
              file=sys.stderr)
        return 2

    summary_text = " ".join(argv[1:])
    counts = count_artifacts()
    now = datetime.now(tz=timezone.utc)

    record = {
        "timestamp_utc": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "kind": "daily_summary",
        "summary": summary_text,
        "artifact_counts": counts,
    }

    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")

    print(f"Daily summary recorded for {record['date']}:")
    print(f"  {summary_text}")
    print(f"  Equations: {counts['n_equations']}, "
          f"Composites: {counts['n_composites']}, "
          f"Failure modes: {counts['n_failure_modes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
