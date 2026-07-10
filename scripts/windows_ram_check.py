#!/usr/bin/env python3
"""Regression guard for Windows capability detection, run against an INSTALLED Wira.

`system_ram_gb()` originally read RAM via `os.sysconf`, which does not exist on
Windows. Every Windows machine therefore reported 0 GB and was pushed into the
limited local-AI tier. See STATUS.md 2026-06-07.

Usage: python windows_ram_check.py <install-root>
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    root = Path(sys.argv[1])
    sys.path.insert(0, str(root / "app"))
    sys.path.insert(0, str(root / "app_lib"))

    import platform_support as ps

    ram = ps.system_ram_gb()
    print(f"detected_ram_gb={ram!r}")

    if not isinstance(ram, int):
        print(f"FAIL: system_ram_gb() returned {type(ram).__name__}, expected int", file=sys.stderr)
        return 1
    if ram <= 0:
        print(
            f"FAIL: Windows RAM detection regressed to {ram} GB — this is the os.sysconf bug",
            file=sys.stderr,
        )
        return 1

    assessment = ps.assess()
    print(f"assessment={assessment!r}")
    print("OK: RAM detection healthy on Windows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
