"""Print one reducer observation while importing code from a supplied HEAD tree.

This helper never writes a golden.  The caller controls ``PYTHONPATH`` and
working directory so :mod:`joulewise.reduce` comes from a pristine Git archive;
stdout is the observation that a human transcribes into the frozen golden.
"""

from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path

from joulewise.reduce import reduce_bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument(
        "--version", required=True, choices=("0.4.1", "0.4.2", "0.5.0")
    )
    parser.add_argument("--source-root", required=True, type=Path)
    args = parser.parse_args()

    loaded_module = Path(inspect.getfile(reduce_bundle)).resolve()
    expected_module = (args.source_root / "joulewise" / "reduce.py").resolve()
    if loaded_module != expected_module:
        raise SystemExit(
            f"refusing non-pristine reducer import: {loaded_module} != {expected_module}"
        )
    observed = reduce_bundle(
        args.fixture.resolve(), reducer_version=args.version
    ).to_dict()
    print(json.dumps(observed, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
