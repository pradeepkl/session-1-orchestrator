#!/usr/bin/env python3
"""Generate structural test modules from case_map.py (run once during suite setup)."""

from __future__ import annotations

from pathlib import Path

from tests.structural.case_map import FILE_GROUPS, make_case

HEADER = '''"""Structural tests — auto-generated case wiring; do not edit by hand."""

from __future__ import annotations

from tests.structural.case_map import make_case
from tests.structural.conftest import Case, run_pair

'''


def main() -> None:
    root = Path(__file__).resolve().parent / "structural"
    for filename, requirement_ids in FILE_GROUPS.items():
        lines = [HEADER]
        for req_id in requirement_ids:
            func = "test_" + req_id.replace(".", "_")
            lines.append(
                f"def {func}() -> None:\n"
                f'    """Covers: {req_id}"""\n'
                f"    run_pair(make_case({req_id!r}))\n\n"
            )
        (root / filename).write_text("".join(lines), encoding="utf-8")
        print(f"wrote {filename} ({len(requirement_ids)} tests)")


if __name__ == "__main__":
    main()
