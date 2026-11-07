"""ALIGN tests.

Lead ruling R6-7 keeps the High Power marker and the night lock at a
host-level path (``joulewise.align.apple.powermode.host_state_dir``). No test
may touch the real one, so every process that imports this package points it
at a private temporary directory unless the caller already chose one.
"""
import os as _os
import tempfile as _tempfile

_os.environ.setdefault("JOULEWISE_HOST_STATE_DIR", _tempfile.mkdtemp(prefix="jw-host-power-"))
