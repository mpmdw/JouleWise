"""Feasibility: can a non-governed observer see a wall-deadline firing from rederive's return value?"""
import json, sys, time, types
from pathlib import Path
from unittest import mock


class JumpingClock(types.ModuleType):
    def __init__(self):
        super().__init__('time'); self._now = time.monotonic()
    def monotonic(self):
        self._now += 1000.0; return self._now
    def __getattr__(self, n):
        return getattr(time, n)


def main():
    from joulewise import cli, powermetrics_fiducial as pf
    seen = []; orig = pf.rederive_detection_from_artifacts
    def observe(*a, **k):
        d = orig(*a, **k); seen.append(getattr(d, 'projection_budget_trigger', 'NO_ATTR')); return d
    pf.rederive_detection_from_artifacts = observe
    m = Path(sys.argv[1])
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try: cli.main(['validate-bundle', '--strict', str(m)])
        except SystemExit: pass
        with mock.patch.object(pf, 'time', JumpingClock()):
            try: cli.main(['validate-bundle', '--strict', str(m)])
            except SystemExit: pass
    print(json.dumps({'triggers_control_then_forced': seen, 'return_type': type(orig).__name__}))


if __name__ == '__main__':
    main()
