"""Fresh battery-float probe answers built from the real ioreg capture.

`tests/fixtures/battery_float/README.md` documents the capture and its
synthetic byte edits.  A runner here answers only the ruled ioreg argv, with
the capture's `UpdateTime` re-stamped to now so the observation is fresh.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import time

from joulewise import battery_float

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "battery_float"


def fresh_ioreg(name: str = "float.ioreg", *, now_s: float | None = None) -> bytes:
    """The named capture with its top-level `UpdateTime` set to `now_s`."""

    stamp = int(time.time() if now_s is None else now_s)
    raw, count = re.subn(
        rb'(?m)^(\s+"UpdateTime" = )[0-9]+$',
        lambda match: match.group(1) + str(stamp).encode(),
        (FIXTURES / name).read_bytes(), count=1,
    )
    assert count == 1, name
    return raw


def answer(argv, name: str = "float.ioreg"):
    """A text-mode completed ioreg run for the ruled argv, else None.

    For runners shaped like `evidence_night.probe_command` that answer
    several commands: `return battery_float_fixture.answer(argv) or ...`.
    """

    if tuple(map(str, argv)) != battery_float.IOREG_BATTERY_ARGV:
        return None
    return subprocess.CompletedProcess(list(argv), 0, fresh_ioreg(name).decode("utf-8"), "")


def runner(name: str = "float.ioreg"):
    """A `battery_float.observe` runner answering the ioreg argv only."""

    def run(argv):
        assert tuple(argv) == battery_float.IOREG_BATTERY_ARGV, argv
        return subprocess.CompletedProcess(list(argv), 0, fresh_ioreg(name), b"")

    return run


_USERCUSTOMIZE = '''"""Test-only (tests/battery_float_fixture.py): answer the battery probe.

A child Python started with this fake HOME answers every real-probe
`battery_float.observe` call from the real float capture, never the host
battery.  An explicitly injected runner is left untouched.
"""
try:
    from joulewise import battery_float as _battery_float
    from tests import battery_float_fixture as _fixture
except ImportError:
    pass
else:
    _observe = _battery_float.observe

    def _fixture_observe(*, runner=None, **kwargs):
        return _observe(runner=_fixture.runner() if runner is None else runner, **kwargs)

    _battery_float.observe = _fixture_observe
'''


def install_user_site_runner(home: Path, python: str | None = None) -> bool:
    """Make child Pythons run with HOME=`home` answer the probe from the fixture.

    The installer runs as a separate `python -m` process behind its zsh
    wrapper, so an in-process patch cannot reach it.  Python imports
    `usercustomize` from the user site of the child's HOME; the file above is
    written there.  Returns False when the interpreter disables the user site
    (a virtual environment), in which case the child reads the host battery.
    """

    import os
    import sys

    probe = subprocess.run(
        [python or sys.executable, "-c",
         "import site; print(site.ENABLE_USER_SITE); print(site.getusersitepackages())"],
        env={**os.environ, "HOME": str(home)}, capture_output=True, text=True, check=True,
    )
    enabled, site_dir = probe.stdout.splitlines()[-2:]
    if enabled != "True":
        return False
    Path(site_dir).mkdir(parents=True, exist_ok=True)
    (Path(site_dir) / "usercustomize.py").write_text(_USERCUSTOMIZE, encoding="utf-8")
    return True
