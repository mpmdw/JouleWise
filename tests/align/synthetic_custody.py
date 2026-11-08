"""Synthetic custody is the DEFAULT for the harvest-off tests: no test probes a home-directory locator.

The shared B5 window fixture (``tests.test_harvest_b5_window``) is real-shaped. Two of its paths
reach outside the checkout:

* at import, its optional native decorators stat a historical archive unless
  ``JW_B5_SYNTHETIC_ONLY=1`` is already set;
* the harvest's historical calibration-custody pass may probe absolute custody locators that the
  copied, digest-pinned acceptance configuration names as text.

Import this module BEFORE that fixture (it sets ``JW_B5_SYNTHETIC_ONLY=1`` for the process), and
run the module's tests inside :func:`fence` (``setUpModule``/``tearDownModule`` here).

Inside the fence (R17 delta D7/D8):

* every custody probe of a path below the home directory, outside this checkout and the temporary
  directory, returns "no candidate paths" BEFORE any filesystem call, in this process AND in every
  fresh interpreter a test starts (``synthetic_custody_child/sitecustomize.py`` is first on
  PYTHONPATH); fenced probes are recorded in :data:`REFUSED` (text only, never opened);
* an audit hook plus ``os.stat``/``os.lstat`` wrappers record any open, listdir, scandir or stat of a
  forbidden custody path (``jw-b5-*``, ``night-*``, ``restricted``, iCloud backups), str or bytes,
  in :data:`OPENED`. A child process refuses such an access outright;
* ``tearDownModule`` FAILS the module if :data:`OPENED` is not empty.

``JOULEWISE_BACKUP_ROOTS=''`` is exported as well, the production absent shortcut for backup roots.
"""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import sys
import tempfile
from unittest import mock

os.environ['JW_B5_SYNTHETIC_ONLY'] = '1'

REPO = Path(__file__).absolute().parents[2]
HOME = Path(os.path.expanduser('~')).absolute()
TEMP = Path(os.path.realpath(tempfile.gettempdir()))
CHILD_FENCE = Path(__file__).absolute().parent / 'synthetic_custody_child'
REFUSED: list[str] = []
OPENED: list[str] = []      # violations: an access to a forbidden custody path while fenced
_AUDITING = [False]


def _text(path) -> str | None:
    try:
        return os.path.abspath(os.fsdecode(path))
    except TypeError:
        return None


def outside_synthetic_custody(path) -> bool:
    text = _text(path)
    if text is None:
        return False
    absolute = Path(text)
    return (absolute.is_relative_to(HOME) and not absolute.is_relative_to(REPO)
            and not absolute.is_relative_to(TEMP))


def forbidden_custody(path) -> bool:
    """The restricted custody namespaces no test may touch (the lane's hard rule)."""
    text = _text(path)
    if text is None or not outside_synthetic_custody(text):
        return False
    parts = Path(text).relative_to(HOME).parts
    return bool(parts) and (parts[0].startswith(('jw-b5-', 'night-')) or 'restricted' in parts
                            or Path(text).is_relative_to(HOME / 'Library/Mobile Documents'))


def _audit(event, args):
    if _AUDITING[0] and event in ('open', 'os.listdir', 'os.scandir') and args:
        if isinstance(args[0], (str, bytes, os.PathLike)) and forbidden_custody(args[0]):
            OPENED.append(f'{event}:{_text(args[0])}')


def _stat_wrapper(original, event):
    def wrapped(path, *args, **kwargs):
        if _AUDITING[0] and isinstance(path, (str, bytes, os.PathLike)) and forbidden_custody(path):
            OPENED.append(f'{event}:{_text(path)}')
        return original(path, *args, **kwargs)
    return wrapped


@contextlib.contextmanager
def fence():
    from joulewise import calibration_ledger as ledger
    original = ledger._custody_probe_paths

    def paths(path, **kwargs):
        if outside_synthetic_custody(path):
            REFUSED.append(str(path))
            return ()
        return original(path, **kwargs)

    python_path = os.pathsep.join(p for p in (str(CHILD_FENCE), os.environ.get('PYTHONPATH', '')) if p)
    with mock.patch.dict(os.environ, {'JW_B5_SYNTHETIC_ONLY': '1', 'JOULEWISE_BACKUP_ROOTS': '',
                                      'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1',
                                      'JW_SYNTHETIC_CUSTODY_FENCE': '1', 'JW_SYNTHETIC_CUSTODY_REPO': str(REPO),
                                      'JW_SYNTHETIC_CUSTODY_TEMP': str(TEMP), 'PYTHONPATH': python_path}), \
            mock.patch.object(ledger, '_custody_probe_paths', side_effect=paths):
        yield


_STACK = contextlib.ExitStack()


def setUpModule():  # noqa: N802 (unittest hook)
    if not getattr(sys, '_jw_synthetic_custody_audit', False):
        sys.addaudithook(_audit)
        sys._jw_synthetic_custody_audit = True
    _AUDITING[0] = True
    _STACK.callback(_AUDITING.__setitem__, 0, False)
    _STACK.enter_context(mock.patch.object(os, 'stat', _stat_wrapper(os.stat, 'os.stat')))
    _STACK.enter_context(mock.patch.object(os, 'lstat', _stat_wrapper(os.lstat, 'os.lstat')))
    _STACK.enter_context(fence())


def tearDownModule():  # noqa: N802 (unittest hook)
    _STACK.close()
    violations = sorted(set(OPENED))
    print(f'synthetic_custody: {len(REFUSED)} home custody probes fenced to absent; '
          f'{len(violations)} forbidden custody accesses' + (': ' + ', '.join(violations[:10]) if violations else ''),
          file=sys.stderr)
    if violations:
        raise AssertionError('synthetic custody fence violated: ' + ', '.join(violations[:10]))
