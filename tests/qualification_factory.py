"""Create synthetic qualification records for reader fixtures only."""
from __future__ import annotations
import os
from pathlib import Path
from joulewise import receipt_readers as readiness
from joulewise.qualification_readers import safe_path, require, reference, attempt_record

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(readiness.render_json(value))



def create_record(path, value):
    path = safe_path(path, exists=False)
    require(path.parent.is_dir(), "output.parent_missing")
    raw = readiness.render_json(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return reference(path)

