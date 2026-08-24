from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import smoke_test
import unit_test


def main() -> int:
    unit_test.main()
    smoke_test.main()
    print("test_suite=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
