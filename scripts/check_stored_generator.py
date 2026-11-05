"""Run an immutable historical generator in its existing --check mode."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.stored_generator import historical_reader_imports


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2 or "--check" not in args[1:]:
        raise ValueError("historical generator replay requires --check")
    previous = sys.argv
    try:
        sys.argv = args
        with historical_reader_imports():
            runpy.run_path(args[0], run_name="__main__")
    finally:
        sys.argv = previous


if __name__ == "__main__":
    main()
