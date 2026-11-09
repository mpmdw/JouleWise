"""Child-process half of tests/align/synthetic_custody.py (R17 delta D7). Test-only; never imported in production.

``synthetic_custody.fence()`` puts this directory first on PYTHONPATH and sets
``JW_SYNTHETIC_CUSTODY_FENCE=1``, so every fresh interpreter a fenced test starts (subprocess,
multiprocessing spawn worker) runs this at startup:

* ``joulewise.calibration_ledger._custody_probe_paths`` answers "no candidate paths" for any path
  below the home directory that is outside the checkout and the temporary directory, BEFORE any
  filesystem call (patched the moment the module is imported);
* an audit hook refuses (PermissionError) any open/listdir/scandir of a forbidden custody path.

Then it runs the interpreter's own sitecustomize, if there is one (Homebrew ships one).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _install():
    import importlib.abc
    home = os.path.abspath(os.path.expanduser('~'))
    repo = os.path.abspath(os.environ.get('JW_SYNTHETIC_CUSTODY_REPO', ''))
    temp = os.path.abspath(os.environ.get('JW_SYNTHETIC_CUSTODY_TEMP', '/private/tmp'))

    def under(path, root):
        return bool(root) and (path == root or path.startswith(root.rstrip('/') + '/'))

    def outside(path):
        path = os.path.abspath(os.fsdecode(path))
        return under(path, home) and not under(path, repo) and not under(path, temp)

    def forbidden(path):
        path = os.path.abspath(os.fsdecode(path))
        if not under(path, home) or under(path, repo) or under(path, temp):
            return False
        parts = path[len(home):].strip('/').split('/')
        return (parts[0].startswith(('jw-b5-', 'night-')) or 'restricted' in parts
                or path.startswith(os.path.join(home, 'Library/Mobile Documents')))

    def audit(event, args):
        if event in ('open', 'os.listdir', 'os.scandir') and args and isinstance(args[0], (str, bytes, os.PathLike)):
            if forbidden(args[0]):
                raise PermissionError(f'synthetic custody fence: {event} of a forbidden path')
    sys.addaudithook(audit)

    def patch(module):
        original = module._custody_probe_paths

        def paths(path, **kwargs):
            return () if outside(path) else original(path, **kwargs)
        module._custody_probe_paths = paths

    class Finder(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name != 'joulewise.calibration_ledger':
                return None
            for finder in sys.meta_path:
                if finder is self or not hasattr(finder, 'find_spec'):
                    continue
                spec = finder.find_spec(name, path, target)
                if spec is not None and spec.loader is not None:
                    execute = spec.loader.exec_module

                    def exec_module(module, execute=execute):
                        execute(module)
                        patch(module)
                    spec.loader.exec_module = exec_module
                    return spec
            return None
    sys.meta_path.insert(0, Finder())


if os.environ.get('JW_SYNTHETIC_CUSTODY_FENCE') == '1':
    _install()

for _entry in list(sys.path):
    if os.path.abspath(_entry or os.curdir) == _HERE:
        continue
    _candidate = os.path.join(_entry or os.curdir, 'sitecustomize.py')
    if os.path.isfile(_candidate):
        import importlib.util as _util
        _spec = _util.spec_from_file_location('_jw_chained_sitecustomize', _candidate)
        _module = _util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
        break
