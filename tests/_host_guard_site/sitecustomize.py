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

# Preserve an unrelated environment's sitecustomize, including its normal name.
_paths = [p for p in sys.path if os.path.realpath(p or '.') != _site_dir]
_spec = importlib.machinery.PathFinder.find_spec('sitecustomize', _paths)
if _spec is not None and _spec.loader is not None:
    _module = importlib.util.module_from_spec(_spec)
    sys.modules['sitecustomize'] = _module
    _spec.loader.exec_module(_module)
