"""Synthetic custody is the DEFAULT for the harvest-off tests: no test probes a home-directory locator.

The shared B5 window fixture (``tests.test_harvest_b5_window``) is real-shaped. Two of its paths
reach outside the checkout:

* at import, its optional native decorators stat a historical archive unless
  ``JW_B5_SYNTHETIC_ONLY=1`` is already set;
* the harvest's historical calibration-custody pass probes the absolute custody locators that
  the copied acceptance configuration names (``/Users/edr/night-custody/...``, iCloud backups).

Import this module BEFORE that fixture (it sets ``JW_B5_SYNTHETIC_ONLY=1`` for the process), and
run the module's tests inside :func:`fence` (``setUpModule = synthetic_custody.setUpModule`` and
``tearDownModule`` chain it). Inside the fence every custody probe of a path below the user's
home directory, outside this checkout and outside the temporary directory, returns "no candidate
paths" BEFORE any filesystem call, so the custody code treats it as absent; the refused locators
are recorded in :data:`REFUSED` (text only, never opened). ``JOULEWISE_BACKUP_ROOTS=''`` is also
exported so spawned workers inherit the absent shortcut for the backup roots.
"""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import tempfile
from unittest import mock

os.environ['JW_B5_SYNTHETIC_ONLY'] = '1'

REPO = Path(__file__).absolute().parents[2]
HOME = Path(os.path.expanduser('~')).absolute()
TEMP = Path(os.path.realpath(tempfile.gettempdir()))
REFUSED: list[str] = []


def outside_synthetic_custody(path) -> bool:
    absolute = Path(os.path.abspath(path))
    return (absolute.is_relative_to(HOME) and not absolute.is_relative_to(REPO)
            and not absolute.is_relative_to(TEMP))


@contextlib.contextmanager
def fence():
    from joulewise import calibration_ledger as ledger
    original = ledger._custody_probe_paths

    def paths(path, **kwargs):
        if outside_synthetic_custody(path):
            REFUSED.append(str(path))
            return ()
        return original(path, **kwargs)

    with mock.patch.dict(os.environ, {'JW_B5_SYNTHETIC_ONLY': '1', 'JOULEWISE_BACKUP_ROOTS': '',
                                      'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}), \
            mock.patch.object(ledger, '_custody_probe_paths', side_effect=paths):
        yield


_STACK = contextlib.ExitStack()
OPENED: list[str] = []      # in-process open() of a home path outside the checkout/temp while fenced
_AUDITING = [False]


def _audit(event, args):
    if _AUDITING[0] and event in ('open', 'os.listdir', 'os.scandir') and args and isinstance(args[0], (str, Path)):
        if outside_synthetic_custody(args[0]):
            OPENED.append(f'{event}:{args[0]}')


def setUpModule():  # noqa: N802 (unittest hook)
    import sys
    if not getattr(sys, '_jw_synthetic_custody_audit', False):
        sys.addaudithook(_audit)
        sys._jw_synthetic_custody_audit = True
    _AUDITING[0] = True
    _STACK.callback(_AUDITING.__setitem__, 0, False)
    _STACK.enter_context(fence())


def tearDownModule():  # noqa: N802 (unittest hook)
    import sys
    _STACK.close()
    print(f'synthetic_custody: {len(REFUSED)} home custody probes fenced to absent; '
          f'{len(OPENED)} home opens outside checkout/temp' + (': ' + ', '.join(sorted(set(OPENED))[:10]) if OPENED else ''),
          file=sys.stderr)
