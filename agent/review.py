#!/usr/bin/env python3
"""Quick CLI for an operator (you, until the dashboard exists) to review
pending drafts and mark them sent / skipped.

Usage:
    python review.py            # list pending drafts
    python review.py --tail     # follow new drafts as they arrive
"""

import argparse
import os
import time
from datetime import datetime
from pathlib import Path

# Load .env so DRAFTS_DB_PATH matches the running agent
_env = Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

from drafts import Drafts  # noqa: E402


def show(d: dict):
    when = datetime.fromtimestamp(d["created_at"]).strftime("%H:%M:%S")
    print(f"\n[#{d['id']} · {when} · {d['sender_name'] or d['sender']}]")
    print(f"  in:  {d['incoming']}")
    print(f"  out: {d['draft']}")


def main():
    parser = argparse.ArgumentParser(description="Review Wira drafts.")
    parser.add_argument("--tail", action="store_true", help="follow new drafts live")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    drafts = Drafts()

    if not args.tail:
        pending = drafts.pending(args.limit)
        if not pending:
            print("No pending drafts.")
            return
        print(f"{len(pending)} pending drafts:")
        for d in pending:
            show(d)
        print("\nTo mark sent:    python -c \"from drafts import Drafts; Drafts().mark(<id>, 'sent')\"")
        print("To mark skipped: python -c \"from drafts import Drafts; Drafts().mark(<id>, 'skipped')\"")
        return

    print("Following drafts (Ctrl-C to stop)...")
    seen = {d["id"] for d in drafts.pending(args.limit)}
    for d in drafts.pending(args.limit)[::-1]:
        show(d)
    while True:
        time.sleep(2)
        for d in drafts.pending(args.limit)[::-1]:
            if d["id"] not in seen:
                seen.add(d["id"])
                show(d)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
