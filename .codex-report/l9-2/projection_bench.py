"""Per-cell projection cost on the synthetic 59-pulse v3 calibration.

Synthetic bytes only (tests/b5_analysis/support_s10/calibration.py). Times the
production rederive_detection_from_artifacts under a selectable observer mode:
  plain    - nothing installed
  observer - the joined harness's sys.monitoring layout (PY_RETURN local events
             on a few unrelated code objects, PY_UNWIND as a global event)
  unwind   - PY_UNWIND global event only
  return   - PY_RETURN local events only
Prints one JSON line per mode.
"""
import json
import sys
import time

from joulewise import powermetrics_fiducial as pf
from tests.b5_analysis.support_s10 import calibration as cal


def build():
    # Generate the synthetic raw/event bytes once; the builder itself runs the
    # projection, which is timed separately below.
    evidence, raw, events = cal.self_consistent_calibration(protocol_id=pf.PROTOCOL_ID)
    return evidence, raw, events


def observed(mode):
    if mode == 'plain':
        return None
    tool = next(n for n in range(6) if sys.monitoring.get_tool(n) is None)
    sys.monitoring.use_tool_id(tool, 'bench')
    if mode in ('observer', 'return'):
        sys.monitoring.register_callback(tool, sys.monitoring.events.PY_RETURN, lambda *a: None)
        for code in (json.dumps.__code__, build.__code__):
            sys.monitoring.set_local_events(tool, code, sys.monitoring.events.PY_RETURN)
    if mode in ('observer', 'unwind'):
        def unwound(code, offset, exc):
            if code is not build.__code__:
                return
        sys.monitoring.register_callback(tool, sys.monitoring.events.PY_UNWIND, unwound)
        sys.monitoring.set_events(tool, sys.monitoring.events.PY_UNWIND)
    return tool


def release(tool):
    if tool is None:
        return
    sys.monitoring.set_events(tool, 0)
    for code in (json.dumps.__code__, build.__code__):
        sys.monitoring.set_local_events(tool, code, 0)
    sys.monitoring.register_callback(tool, sys.monitoring.events.PY_RETURN, None)
    sys.monitoring.register_callback(tool, sys.monitoring.events.PY_UNWIND, None)
    sys.monitoring.free_tool_id(tool)


def main(modes):
    evidence, raw, events = build()
    for mode in modes:
        tool = observed(mode)
        try:
            started = time.perf_counter()
            cpu = time.process_time()
            detection = pf.rederive_detection_from_artifacts(raw, events, evidence['clock_anchor'],
                                                             protocol_id=pf.PROTOCOL_ID)
            wall = time.perf_counter() - started
            cpu = time.process_time() - cpu
        finally:
            release(tool)
        cells = detection.projection_evaluated_cell_count
        print(json.dumps(dict(mode=mode, cells=cells, wall_s=round(wall, 3), cpu_s=round(cpu, 3),
                              ms_per_cell=round(1000 * wall / max(cells, 1), 4),
                              disposition=detection.projection_disposition,
                              trigger=detection.projection_budget_trigger,
                              reasons=list(detection.reasons))), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:] or ['plain', 'observer', 'plain'])
