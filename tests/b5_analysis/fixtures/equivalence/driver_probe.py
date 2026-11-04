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

Review 3 of PR #640 (these run the drivers' REAL step functions, with stub programs):
  step6-plain       d.step_6; the closeout stub prints a tooling StepRecord and
                    raises (raw same_unregistered_closeout_code on both).
  step6-badbytes    the same, after a non-UTF-8 byte written to fd 1 on both
                    variants: step_6's strict read fails, raw None on both.
  step6-badbytes-ref  the byte on ref only (raw None versus the StepRecord code).
  internal-unclassified  d.step_3; prepare_tripwires raises RuntimeError (raw
                    'unclassified' on both, from RunState.guarded).
  internal-code     d.step_3; prepare_tripwires raises the same AnalysisRefusal.
  internal-code-differs  the same with a different code per variant.
  step8-staging-code  d.step_8; the staging helper refuses with the same code.
  step8-after-staging d.step_8; staging succeeds, then the driver refuses before
                    the finalizer runs, with a different code per variant.
  step10-reported-code  d.step_10; the issuer stub succeeds, the guarded
                    _reported_open refuses with the same code (window alpha).
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


def stub_module(name, main):
    # A stub program module: the import in the real step function finds it in
    # sys.modules (the r1 tree is extracted without scripts/).
    import types
    module = types.ModuleType(name)
    module.main = main
    sys.modules[name] = module


def refusal(code):
    from joulewise.b5_analysis.windows import AnalysisRefusal
    return AnalysisRefusal(code)


def prepare_tripwires(self, argv):   # named so RunState.guarded treats it as the real helper
    if scenario == 'internal-unclassified':
        raise RuntimeError('same synthetic helper failure')
    if scenario == 'internal-code-differs':
        raise refusal('helper_code_reference' if variant == 'ref' else 'helper_code_candidate')
    raise refusal('same_unregistered_helper_code')


def closeout_main(argv):
    import os
    if scenario == 'step6-badbytes' or (scenario == 'step6-badbytes-ref' and variant == 'ref'):
        os.write(1, b'\xff progress\n')
    print(json.dumps({'status': 'tooling_refusal', 'refusal': 'same_unregistered_closeout_code'}))
    sys.stdout.flush()
    raise RuntimeError('same synthetic closeout failure')


def finalized_manifest(s, r):
    s.write('finalized_manifest', d.FINALIZATION + '/manifest.json', {'synthetic': True})
    return [s.record('8')]


def prepare_finalization(self, argv):
    if scenario == 'step8-staging-code':
        raise refusal('same_unregistered_staging_code')
    staged = self.restricted / d.FINALIZATION / 'inputs/gamma-pack'
    staged.mkdir(parents=True, exist_ok=True)
    (staged / 'analysis_manifest_v3.json').write_text('{"manifest_id":"synthetic"}\n')
    for role in ('gamma_verdict', 'gamma_binding', 'gamma_ledger', 'final_floor', 'final_sidecar'):
        self.write(role, d.FINALIZATION + '/inputs/' + role + '.json', {'synthetic': role})
    return 0


def step_8(s, r):
    s.archives, s.windows = {'gamma': None}, {'gamma': SimpleNamespace(claim_runs_root=s.restricted)}
    try:
        return d.step_8(s, r)
    finally:
        s.archives, s.windows = {}, {}      # the synthetic record has no window


def primary_context_refused(contexts):
    raise refusal('driver_code_reference' if variant == 'ref' else 'driver_code_candidate')


def issue_main(argv):
    output = Path(argv[argv.index('--output') + 1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('{"synthetic":true}\n')
    return 0


def extraction(s, r):
    s.write('extraction_alpha', 'outputs/extraction-alpha.json', {'synthetic': True})
    return [s.record('9b')]


def reported_open(s, pack):
    raise refusal('same_unregistered_reported_code')


patches = []
if scenario.startswith('internal-'):
    special = {'3': d.step_3}
    patches.append(mock.patch.object(d.RunState, 'prepare_tripwires', prepare_tripwires))
elif scenario.startswith('step6-'):
    special = {'8': finalized_manifest, '6': d.step_6}
    stub_module('scripts.run_d165_closeout_from_custody', closeout_main)
elif scenario.startswith('step8-'):
    special = {'8': step_8}
    stub_module('scripts.finalize_analysis_manifest', lambda argv: 0)
    patches.append(mock.patch.object(d.RunState, 'prepare_finalization', prepare_finalization))
    patches.append(mock.patch.object(d, 'require_primary_context', primary_context_refused))
elif scenario.startswith('step10-'):
    special = {'9b': extraction, '10': d.step_10}
    stub_module('scripts.issue_reported_energy', issue_main)
    patches.append(mock.patch.object(d, 'require_step10_admission', lambda *args: None))
    patches.append(mock.patch.object(d, '_reported_open', reported_open))
else:
    special = {'5': probe}
special.setdefault('0', initial)
steps = [(step, special.get(step) or noop(step)) for step in d.STEP_IDS]
raw = []
original_record = d.RunState.record


def record(self, *args, **kwargs):
    row = original_record(self, *args, **kwargs)
    if row.status not in ('ok', 'not_run'):
        raw.append({'step': row.step, 'code': kwargs.get('code')})
    return row


with contextlib.ExitStack() as stack:
    for patch in (mock.patch.object(d, 'STEPS', steps), mock.patch.object(d.RunState, 'record', record), *patches):
        stack.enter_context(patch)
    stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
    stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
    rc = d.run('blind-dry-run', index, target / 'custody', workers=1, _test_repo_root=repo, _git=lambda root: commit)
print(json.dumps({'driver': str(Path(d.__file__).resolve()), 'rc': rc, 'raw_refusals': raw}))
