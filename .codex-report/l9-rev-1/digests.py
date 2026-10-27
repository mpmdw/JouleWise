"""Uncached step-1/step-2 digests for members given on argv; code tree chosen by PYTHONPATH."""
import contextlib, hashlib, io, json, sys
from pathlib import Path
from joulewise import cli

out_dir = Path(sys.argv[1])
res = {}
for m in sys.argv[2:]:
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        try:
            c1 = cli.main(['validate-bundle', '--strict', m])
        except SystemExit as x:
            c1 = x.code
    t = out_dir / (Path(m).name + '.reduced.json')
    o2, e2 = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o2), contextlib.redirect_stderr(e2):
        try:
            c2 = cli.main(['reduce', m, '--output', str(t)])
        except SystemExit as x:
            c2 = x.code
    h = lambda b: hashlib.sha256(b).hexdigest()
    res[Path(m).name] = dict(validate_exit=c1, validate_stdout=h(o.getvalue().encode()),
                             reduce_exit=c2, reduce_stdout=h(o2.getvalue().encode()),
                             reduced_json=(h(t.read_bytes()) if t.exists() else None))
print(json.dumps(res, indent=1, sort_keys=True))
