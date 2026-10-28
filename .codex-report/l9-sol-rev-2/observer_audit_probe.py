"""Real CPython audit-policy denial, no monitoring mocks."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

from joulewise.b5_analysis import dry_run as d


def audit(event, args):
    if event == 'sys.monitoring.register_callback':
        raise RuntimeError('review fixture audit policy denies monitoring callbacks')


sys.addaudithook(audit)
with tempfile.TemporaryDirectory(prefix='sol-observer-audit-') as tmp:
    root=Path(tmp)
    (root/'repo').mkdir()
    index=root/'index.json'
    index.write_bytes(d._canonical({'schema':'joulewise.b5_window_index.v1','attempts':[]}))
    steps=tuple((step,lambda s,r,step=step:[s.record(step)]) for step in d.STEP_IDS)
    result={}
    with mock.patch.object(d,'STEPS',steps), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            result['return']=d.run('blind-dry-run',index,root/'custody',_test_repo_root=root/'repo',_git=lambda _: 'b'*40)
        except Exception as exc:
            result['exception']=type(exc).__name__
            result['message']=str(exc)
    record=json.loads((root/'custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
    result['first_step']={key:record['steps'][0][key] for key in ('status','refusal')}
    result['later']=sorted({row['status'] for row in record['steps'][1:]})
    result['tools_after']=[sys.monitoring.get_tool(n) for n in range(6)]
    print(json.dumps(result,sort_keys=True))
