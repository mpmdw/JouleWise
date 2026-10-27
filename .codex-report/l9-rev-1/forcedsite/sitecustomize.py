# Spawn-worker fault injection for L9-REV-1 P3: jump powermetrics_fiducial's clock in every process.
import os
if os.environ.get('REV1_FORCE_DEADLINE') == '1':
    import time, types, importlib
    class _J(types.ModuleType):
        def __init__(self):
            super().__init__('time'); self._now = time.monotonic()
        def monotonic(self):
            self._now += 1000.0; return self._now
        def __getattr__(self, n):
            return getattr(time, n)
    import joulewise.powermetrics_fiducial as _pf
    _pf.time = _J()
