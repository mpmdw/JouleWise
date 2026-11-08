"""Optional stdlib/cc accelerator. Build artifacts contain code, never evidence.

An unavailable compiler leaves the ordinary plistlib route usable. The build is
local, content-addressed and atomic. No installation, network or model access.
"""
import ctypes
import hashlib
import os
from pathlib import Path
import platform
import subprocess
import tempfile


class Span(ctypes.Structure):
    _fields_ = [('start', ctypes.c_size_t), ('end', ctypes.c_size_t)]


def load_scanner():
    source = Path(__file__).with_name('_reduce_scan.c').read_bytes()
    flags = ['-O3', '-std=c99', '-shared', '-fPIC']
    identity = hashlib.sha256(source + repr((flags, platform.system(), platform.machine())).encode()).hexdigest()
    root = Path(tempfile.gettempdir()) / 'joulewise-reduce-native' / identity
    library = root / 'scanner.so'
    root.mkdir(parents=True, exist_ok=True)
    if not library.exists():
        with tempfile.TemporaryDirectory(dir=root) as work:
            path = Path(work)
            (path/'scanner.c').write_bytes(source)
            subprocess.run(['/usr/bin/cc', *flags, str(path/'scanner.c'), '-o', str(path/'scanner.so')],
                           check=True, capture_output=True, timeout=60)
            os.replace(path/'scanner.so', library)
    loaded_bytes = library.read_bytes()
    lib = ctypes.CDLL(str(library))
    fn = lib.jw_scan
    fn.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(Span)]
    fn.restype = ctypes.c_int
    return fn, hashlib.sha256(source + loaded_bytes).hexdigest()


try:
    SCAN, LOADED_SHA256 = load_scanner()
except (OSError, subprocess.SubprocessError):
    SCAN, LOADED_SHA256 = None, 'plistlib-only'
