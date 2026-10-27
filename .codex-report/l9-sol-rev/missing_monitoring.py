"""Isolate the missing sys.monitoring API (Python 3.11 is allowed by pyproject).

Python 3.11 is not installed on this seat. Delete only the added API on 3.13;
run exactly the BASE_HEAD and reviewed run() functions with identical empty
synthetic dispatch steps. This is an availability probe, not a hardware test.
"""
import ast
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock

from joulewise.b5_analysis import dry_run as d


def original_run():
    tree = ast.parse(subprocess.check_output(['git', 'show', '0576a734d:joulewise/b5_analysis/dry_run.py']))
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
    namespace = dict(vars(d))
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<baseline-run>', 'exec'), namespace)
    return namespace['run'], namespace


def main():
    steps = tuple((step, lambda s, r, step=step: [s.record(step)]) for step in d.STEP_IDS)
    old, namespace = original_run()
    namespace['STEPS'] = steps
    for label, function in [('0576a734d', old), ('f059286bc', d.run)]:
        with tempfile.TemporaryDirectory(prefix='sol-no-monitoring-') as tmp:
            root = Path(tmp)
            (root / 'repo').mkdir()
            index = root / 'index.json'
            index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
            with mock.patch.object(d, 'STEPS', steps), mock.patch.dict(sys.__dict__, clear=False), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                del sys.monitoring
                try:
                    status = function('blind-dry-run', index, root / 'custody',
                                      _test_repo_root=root / 'repo', _git=lambda _: 'b' * 40)
                    result = {'return': status}
                except Exception as exc:
                    result = {'exception': type(exc).__name__, 'message': str(exc)}
            result['record_exists'] = (root / 'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').is_file()
            print(label, json.dumps(result, sort_keys=True))

    mon = sys.monitoring
    original_get = mon.get_tool
    occupied = []

    def competing_registration(number):
        value = original_get(number)
        if value is None and not occupied:
            # Deterministically schedule another real registration between
            # the driver's availability read and its use_tool_id operation.
            mon.use_tool_id(number, 'independent-review-competing-tool')
            occupied.append(number)
            return None
        return value

    try:
        with tempfile.TemporaryDirectory(prefix='sol-tool-race-') as tmp:
            root = Path(tmp)
            (root / 'repo').mkdir()
            index = root / 'index.json'
            index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
            with mock.patch.object(d, 'STEPS', steps), \
                    mock.patch.object(mon, 'get_tool', competing_registration), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                try:
                    status = d.run('blind-dry-run', index, root / 'custody',
                                   _test_repo_root=root / 'repo', _git=lambda _: 'b' * 40)
                    result = {'return': status}
                except Exception as exc:
                    result = {'exception': type(exc).__name__, 'message': str(exc)}
            result['record_exists'] = (root / 'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').is_file()
            result['competing_tool_preserved'] = mon.get_tool(occupied[0]) == 'independent-review-competing-tool'
            print('f059286bc tool-id race', json.dumps(result, sort_keys=True))
    finally:
        for number in occupied:
            mon.free_tool_id(number)


if __name__ == '__main__':
    main()
