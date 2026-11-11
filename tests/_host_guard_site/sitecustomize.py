"""Carry the test tripwire into ordinary child Python interpreters."""
import importlib.machinery
import importlib.util
import os
import sys

_site_dir = os.path.dirname(os.path.realpath(__file__))
_root = os.path.dirname(os.path.dirname(_site_dir))
_added = _root not in sys.path
if _added:
    sys.path.insert(0, _root)
try:
    from tests.host_command_guard import install
    install()
finally:
    if _added:
        sys.path.remove(_root)

# Preserve an unrelated environment's sitecustomize, including its normal name. Chain only to entries AFTER
# this directory on sys.path, and never to a sitecustomize file already loaded: another chaining
# sitecustomize earlier on the path (e.g. tests/align/synthetic_custody_child) has run this one.
_entries = [os.path.realpath(p or '.') for p in sys.path]
_after = sys.path[_entries.index(_site_dir) + 1:] if _site_dir in _entries else list(sys.path)
_loaded = {os.path.realpath(m.__file__) for m in list(sys.modules.values())
           if isinstance(getattr(m, '__file__', None), str)}
_spec = importlib.machinery.PathFinder.find_spec('sitecustomize', _after)
if (_spec is not None and _spec.loader is not None and _spec.origin
        and os.path.realpath(_spec.origin) not in _loaded):
    _module = importlib.util.module_from_spec(_spec)
    sys.modules['sitecustomize'] = _module
    _spec.loader.exec_module(_module)
