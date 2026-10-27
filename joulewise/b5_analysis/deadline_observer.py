"""Run-scoped observer: a calibration wall-deadline firing is a tooling refusal.

The governed pulse projection (``powermetrics_fiducial.detect_pulses``) keeps
its frozen 120 s host-safety wall deadline (ED-RULING item 6, option c). A
firing is host-dependent, so the dry run must stop on it, whichever caller
refitted: the strict reducer, the bracket authentication or the NEG-8 replay's
strict-invalid callback, some of which would otherwise turn it into a
not-estimable reduction or a lost reference. Every refit returns through
``detect_pulses``; this observer only reads its return value with a CPython
``sys.monitoring`` PY_RETURN event on that one code object. No callable is
replaced and no governed byte changes.
"""
from __future__ import annotations

from contextlib import contextmanager
import sys

CALIBRATION_WALL_DEADLINE = 'calibration_wall_deadline_in_analysis'
OBSERVER_UNAVAILABLE = 'calibration_deadline_observer_unavailable'
WALL_DEADLINE_TRIGGER = 'wall_deadline'


class DeadlineObserver:
    def __init__(self):
        self.firings = 0


def _projection_code():
    from joulewise import powermetrics_fiducial as pf
    function = pf.detect_pulses
    # A test that wraps detect_pulses names the original as __wrapped__.
    return getattr(function, '__wrapped__', function).__code__


@contextmanager
def observe_wall_deadline():
    """Count wall-deadline dispositions in this process; None if no tool id is free."""
    monitoring = sys.monitoring
    tool = next((n for n in range(6) if monitoring.get_tool(n) is None), None)
    if tool is None:
        yield None
        return
    observer = DeadlineObserver()
    code = _projection_code()
    event = monitoring.events.PY_RETURN

    def returned(_code, _offset, value):
        if getattr(value, 'projection_budget_trigger', None) == WALL_DEADLINE_TRIGGER:
            observer.firings += 1

    monitoring.use_tool_id(tool, 'joulewise-b5-wall-deadline-observer')
    try:
        monitoring.register_callback(tool, event, returned)
        monitoring.set_local_events(tool, code, event)
        yield observer
    finally:
        monitoring.set_local_events(tool, code, 0)
        monitoring.register_callback(tool, event, None)
        monitoring.free_tool_id(tool)
