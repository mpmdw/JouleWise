"""Read-mode compatibility for immutable, archived campaign generators.

Their source bytes retain the old reader import spelling. Bind that spelling
to the extracted reader object only while executing the archived source; no
retired implementation is imported or installed on disk.
"""
from contextlib import contextmanager
import sys
from threading import RLock

import joulewise
from joulewise import receipt_readers

_IMPORT_LOCK = RLock()
_ABSENT = object()


@contextmanager
def historical_reader_imports():
    name = "joulewise.arm_readiness"
    # Import bindings are process-global. Serialize concurrent replays and
    # restore both import tables, including nested use by the same caller.
    with _IMPORT_LOCK:
        previous = sys.modules.get(name, _ABSENT)
        attribute = vars(joulewise).get("arm_readiness", _ABSENT)
        sys.modules[name] = receipt_readers
        try:
            yield
        finally:
            if previous is _ABSENT:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous
            if attribute is _ABSENT:
                vars(joulewise).pop("arm_readiness", None)
            else:
                joulewise.arm_readiness = attribute
