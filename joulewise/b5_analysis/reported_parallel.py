"""Step-10 pack staging. Only the driver publishes files and records, in order."""
from __future__ import annotations

from contextlib import ExitStack
from copy import copy
from pathlib import Path
import shutil
import tempfile

from . import pack_parallel as pp


def reported_pack(state, pack, counter):
    from . import dry_run as d

    runner = d.StepRunner(state.restricted)
    runner._counter = counter
    state._runner = runner
    before = set(state.outputs)
    record = d._reported_one(state, runner, pack)
    _, code, exception_class = state._raw_codes[-1]
    return (record, code, exception_class, runner._counter,
            {role: item for role, item in state.outputs.items() if role not in before})


def staged_state(state, root):
    """A private copy of authenticated inputs; never alias a mutable driver map."""
    staged = copy(state)
    staged.restricted = Path(root)
    staged.outputs = dict(state.outputs)
    staged._raw_codes, staged._runner, staged.vdl_store, staged.deadline = [], None, None, None
    staged.physics_store = {}
    for item in staged.outputs.values():
        source = state.restricted / item['name']
        destination = staged.path(item['name'])
        shutil.copyfile(source, destination)
    return staged


def step_10_parallel(state, runner):
    from . import dry_run as d

    d.require_primary_context(state.contexts)
    state.rehash()
    base = runner._counter
    records = []
    with ExitStack() as staging:
        roots = [Path(staging.enter_context(tempfile.TemporaryDirectory(prefix='b5-reported-')))
                 for _ in range(2)]
        views = [staged_state(state, root) for root in roots]
        calls = [((view, pack, base + 2 * i), {})
                 for i, (view, pack) in enumerate(zip(views, ('alpha', 'beta')))]
        outcomes = pp.pack_map(reported_pack, calls)
        for pack, root, outcome in zip(('alpha', 'beta'), roots, outcomes or [None, None]):
            # Re-authenticate all earlier public commitments at their original
            # serial position, including alpha's newly registered custody.
            d.require_primary_context(state.contexts)
            state.rehash()
            if outcome is None or not outcome.ok:
                # A failed staging computation has no publication authority.
                # The original call owns its exception, logs and partial writes.
                pp.consume(outcome, lambda: None)
                record = d._reported_one(state, runner, pack)
            else:
                record, code, exception_class, counter, outputs = pp.consume(outcome, lambda: None)
                found = []
                for role, item in outputs.items():
                    destination = state.path(item['name'])
                    if destination.exists():
                        raise d.AnalysisRefusal('custody_run_directory_exists')
                    shutil.move(str(root / item['name']), destination)
                    found.append(state.register(role, destination))
                for log in sorted((root / 'logs').iterdir()):
                    destination = runner.logs / log.name
                    if destination.exists():
                        raise d.AnalysisRefusal('custody_run_directory_exists')
                    shutil.move(str(log), destination)
                runner._counter = counter
                runner.last_exception_class = exception_class
                record = state.record('10', window=pack, exit_status=record.exit_status,
                                      code=code, outputs=found)
            records.append(record)
            if record.status != 'ok':
                break
    return records
