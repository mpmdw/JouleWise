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

CALIBRATION_WALL_DEADLINE = 'calibration_wall_deadline_fired'
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
    """Count wall-deadline dispositions in this process.

    Yields None when no observer can be installed (no ``sys.monitoring``, no
    free tool id, or the reservation lost a race); the driver then refuses
    the run with ``calibration_deadline_observer_unavailable``.
    """
    monitoring = getattr(sys, 'monitoring', None)
    tool = None
    try:
        tool = next((n for n in range(6) if monitoring.get_tool(n) is None), None)
        if tool is not None:
            monitoring.use_tool_id(tool, 'joulewise-b5-wall-deadline-observer')
    except (AttributeError, RuntimeError, ValueError):
        tool = None
    if tool is None:
        yield None
        return
    observer = DeadlineObserver()
    event = monitoring.events.PY_RETURN

    def returned(_code, _offset, value):
        if getattr(value, 'projection_budget_trigger', None) == WALL_DEADLINE_TRIGGER:
            observer.firings += 1

    code = None
    callback_installed = events_installed = False
    try:
        try:
            code = _projection_code()
            monitoring.register_callback(tool, event, returned)
            callback_installed = True
            monitoring.set_local_events(tool, code, event)
            events_installed = True
        except (AttributeError, RuntimeError, ValueError):
            observer = None
        yield observer
    finally:
        # Undo only what was installed: a call the setup could not make (for
        # example one an audit hook rejects) is not repeated during cleanup.
        try:
            if events_installed:
                monitoring.set_local_events(tool, code, 0)
            if callback_installed:
                monitoring.register_callback(tool, event, None)
        finally:
            monitoring.free_tool_id(tool)
