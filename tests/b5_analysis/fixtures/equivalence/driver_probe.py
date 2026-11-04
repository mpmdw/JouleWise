"""One bounded synthetic run through a checkout's ACTUAL dry_run driver (review 2 of PR #640, T1/T2).

    python3 -B driver_probe.py CHECKOUT COMMIT TARGET SCENARIO VARIANT

CHECKOUT is a tree holding joulewise/ and configs/analysis/ (this branch, or the
b5/analysis-r1 tree extracted by git archive); COMMIT is bound as the record's
analysis_commit. Every step but 0 and 5 is a no-op; step 5 runs one stub child
program through RunState.invoke, so the driver's own runner, token rules, step-5
record and run() exception handling decide the record. Synthetic data only: an
empty window index, no bundle, no real input. Prints one JSON line: the driver
file, its exit code and every raw (unredacted) code it recorded for a refusing row.

Scenarios (VARIANT is 'ref' or 'cand'):
  no-refusal      the child succeeds; the run completes.
  exception-code  the child prints 'error: hypothetical_refusal'; ref returns 2,
                  cand raises (raw codes hypothetical_refusal versus None).
  exception-audit the child prints a different progress line per variant, then
                  raises the same exception (raw code None on both).
  missing-output  the child prints a different progress line per variant and
                  returns 0 without its promised output (raw code None on both).
  driver-code     the child succeeds; the step function then raises a different
                  AnalysisRefusal per variant (driver-raised raw codes).
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest import mock

checkout, commit, target, scenario, variant = sys.argv[1:]
sys.path.insert(0, checkout)
from joulewise.b5_analysis import dry_run as d  # noqa: E402

if not Path(d.__file__).resolve().is_relative_to(Path(checkout).resolve()):
    raise SystemExit('driver_probe: dry_run was not imported from the checkout')

target = Path(target)
target.mkdir(parents=True, exist_ok=True)
index = target / 'index.json'
index.write_bytes(b'{"schema":"joulewise.b5_window_index.v1","attempts":[]}\n')
repo = target / 'repository'
repo.mkdir(exist_ok=True)


def initial(s, r):
    s.index = SimpleNamespace(entries=(), sha256=hashlib.sha256(index.read_bytes()).hexdigest())
    return [s.record('0')]


def noop(step):
    return lambda s, r: [s.record(step)]


def probe(s, r):
    def child(argv):
        if scenario in ('exception-audit', 'missing-output'):
            print('audit_reference' if variant == 'ref' else 'audit_candidate')
            if scenario == 'exception-audit':
                raise RuntimeError('same synthetic child failure')
            return 0
        if scenario == 'exception-code':
            print('error: hypothetical_refusal')
            if variant == 'cand':
                raise RuntimeError('synthetic child failure')
            return 2
        return 0
    outputs = [('promised', s.path('mint/promised.json'))] if scenario == 'missing-output' else []
    result, found, code, exit_status = s.invoke(r, child, [], step='5', outputs=outputs)
    if scenario == 'driver-code':
        from joulewise.b5_analysis.windows import AnalysisRefusal
        raise AnalysisRefusal('unknown_refusal_a' if variant == 'ref' else 'unknown_refusal_b')
    return [s.record('5', exit_status=exit_status, code=code, outputs=found)]


steps = [(step, initial if step == '0' else probe if step == '5' else noop(step)) for step in d.STEP_IDS]
raw = []
original_record = d.RunState.record


def record(self, *args, **kwargs):
    row = original_record(self, *args, **kwargs)
    if row.status not in ('ok', 'not_run'):
        raw.append({'step': row.step, 'code': kwargs.get('code')})
    return row


with mock.patch.object(d, 'STEPS', steps), mock.patch.object(d.RunState, 'record', record), \
        contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    rc = d.run('blind-dry-run', index, target / 'custody', workers=1, _test_repo_root=repo, _git=lambda root: commit)
print(json.dumps({'driver': str(Path(d.__file__).resolve()), 'rc': rc, 'raw_refusals': raw}))
