"""Reader-only access to the one named RL-123 cross-temp denied fixture."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import tempfile

from b6_r12_chain_fixture import PIN
from b6_r12_verify import safe_root, sha

DENIED_OUTER = Path("/Volumes/JW-EXT/jwsol/squeeze/p1-b6-r12c/tmp/r12-r3-denied-air-26")


def reader_root(value):
    try:
        return safe_root(value)
    except ValueError:
        path = Path(value).absolute()
        if ".." in path.parts or not path.is_relative_to(DENIED_OUTER) or DENIED_OUTER.is_symlink():
            raise ValueError("unlisted cross-temp reader root") from None
        declaration = DENIED_OUTER / "declaration.json"
        data = json.loads(declaration.read_bytes())
        parent = json.loads((DENIED_OUTER / "parent.json").read_bytes())
        if (str(path) != data["main"] or data.get("pin") != PIN
                or data.get("synthetic_only") is not True
                or (data.get("mode"), data.get("schedule")) != ("denied", "reduced")
                or parent.get("status") != "done" or parent.get("exit_code") != 0
                or parent.get("declaration_sha256") != sha(declaration)
                or path != path.resolve()
                or (path / "generator-parent-exit.txt").read_text().strip() != "0"):
            raise ValueError("completed authenticated denied-26 reader root required")
        return path


@contextmanager
def denied_reader_environment(root):
    """Preserve strict child TMPDIR checks for an explicitly admitted read.

    This changes only this reader process's environment/cache, never a host
    setting or another process. Generation's safe_root remains untouched.
    """
    root = reader_root(root)
    if not root.is_relative_to(DENIED_OUTER):
        yield
        return
    previous, cached = os.environ.get("TMPDIR"), tempfile.tempdir
    os.environ["TMPDIR"] = str(DENIED_OUTER.parent)
    tempfile.tempdir = str(DENIED_OUTER.parent)
    try:
        yield
    finally:
        tempfile.tempdir = cached
        if previous is None:
            os.environ.pop("TMPDIR", None)
        else:
            os.environ["TMPDIR"] = previous
