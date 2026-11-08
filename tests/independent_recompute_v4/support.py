"""Shared test helpers: load the recompute script as a module; temporary synthetic series."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPT = ROOT / "scripts" / "independent_recompute_v4.py"
for p in (str(HERE), str(SCRIPT.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

import independent_recompute_v4 as rc  # noqa: E402
import synth  # noqa: E402

SMALL = dict(period_ns=10_000_000_000, n_tasks=0, clusters=0)


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = rc.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


def temp_dir(test):
    tmp = tempfile.TemporaryDirectory()
    test.addCleanup(tmp.cleanup)
    return Path(tmp.name)
