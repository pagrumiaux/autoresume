"""Fail if any given file resolves to a path under AUTORESUME_DATA_DIR."""

import os
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    """Return 1 and name each file under the data dir; 0 otherwise or if the var is unset."""
    raw = os.environ.get("AUTORESUME_DATA_DIR")
    if not raw:
        return 0
    data_dir = Path(raw).expanduser().resolve()
    bad = [f for f in argv if Path(f).resolve().is_relative_to(data_dir)]
    for f in bad:
        print(f"Refusing: {f} is under AUTORESUME_DATA_DIR ({data_dir})", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
