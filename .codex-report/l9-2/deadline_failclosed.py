"""Fail-closed probe for a wall-deadline firing (diagnostic process only; synthetic member copy).

usage: deadline_failclosed.py <member-bundle-copy> <scratch-dir>

1. Times one detection of the member's own instrument calibration bytes, unforced.
2. Forces the wall deadline by giving powermetrics_fiducial a clock that jumps
   past 120 s at the first budget check (nothing else is replaced), then runs the
   two consuming CLI programs the driver dispatches on a member:
   `validate-bundle --strict` (step 1) and `reduce` (step 2), and reports exit
   status, problems and the reduction's anchor/bound fields.
"""
import contextlib, hashlib, io, json, sys, time, types
from pathlib import Path

from joulewise import powermetrics_fiducial as pf
from joulewise import cli

member, scratch = Path(sys.argv[1]), Path(sys.argv[2])
scratch.mkdir(parents=True, exist_ok=True)
cal = member / 'instrument_calibration'
raw, events = (cal / 'raw/powermetrics.plist').read_bytes(), (cal / 'events.jsonl').read_bytes()
evidence = json.loads((cal / 'instrument_evidence.json').read_bytes())
out = dict(raw_sha256=hashlib.sha256(raw).hexdigest(),
           evidence_sha256=hashlib.sha256((cal / 'instrument_evidence.json').read_bytes()).hexdigest())

t = time.perf_counter()
d = pf.rederive_detection_from_artifacts(raw, events, evidence['clock_anchor'], protocol_id=evidence.get('protocol_id', pf.PROTOCOL_ID))
out['unforced'] = dict(wall_s=round(time.perf_counter() - t, 3), cells=d.projection_evaluated_cell_count,
                       disposition=d.projection_disposition, reasons=list(d.reasons), b_fiducial_s=d.b_fiducial_s)


class JumpingClock(types.ModuleType):
    """time stand-in for powermetrics_fiducial only: monotonic() jumps 1000 s per call."""
    def __init__(self):
        super().__init__('time'); self._t = time.monotonic()
    def monotonic(self):
        self._t += 1000.0; return self._t
    def __getattr__(self, name):
        return getattr(time, name)


def run(argv):
    stream_out, stream_err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stream_out), contextlib.redirect_stderr(stream_err):
        try:
            code = cli.main(argv)
        except SystemExit as exc:
            code = exc.code
    return dict(exit=code, stdout=stream_out.getvalue()[-1500:], stderr=stream_err.getvalue()[-1500:])


for label, clock in (('control', None), ('forced', JumpingClock())):
    original = pf.time
    if clock is not None:
        pf.time = clock
    try:
        forced_check = pf.rederive_detection_from_artifacts(raw, events, evidence['clock_anchor'],
            protocol_id=evidence.get('protocol_id', pf.PROTOCOL_ID))
        validate = run(['validate-bundle', '--strict', str(member)])
        target = scratch / f'{label}.reduced.json'
        reduce_ = run(['reduce', str(member), '--output', str(target)])
        reduced = json.loads(target.read_bytes()) if target.exists() else None
    finally:
        pf.time = original
    keep = {}
    if isinstance(reduced, dict):
        for key, value in reduced.items():
            if any(word in key for word in ('anchor', 'bound', 'status', 'calibration', 'reason', 'energy')):
                keep[key] = value
    out[label] = dict(detection=dict(disposition=forced_check.projection_disposition,
                                     trigger=forced_check.projection_budget_trigger,
                                     reasons=list(forced_check.reasons)),
                      validate=validate, reduce=dict(reduce_, output_written=reduced is not None,
                      output_sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None,
                      selected_fields=keep))
print(json.dumps(out, indent=1, default=str))
