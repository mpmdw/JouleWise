import contextlib, hashlib, io, json, sys
from pathlib import Path
from joulewise import cli, whole_window as ww
A = Path(sys.argv[1]); key = hashlib.sha256((A/'instrument_calibration/instrument_evidence.json').read_bytes()).hexdigest()
R = {}
for label, val in (('poison_0', 0.0), ('poison_big', 5.0), ('poison_neg', -1.0)):
    out = Path(f'/tmp/jwtmp/{label}.json'); out.unlink(missing_ok=True)
    with ww.shared_instrument_calibration_physics_cache({key: val}), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try: v = cli.main(['validate-bundle', '--strict', str(A)])
        except SystemExit as e: v = e.code
        try: r = cli.main(['reduce', str(A), '--output', str(out)])
        except SystemExit as e: r = e.code
    R[label] = dict(validate=v, reduce=r, reduced=hashlib.sha256(out.read_bytes()).hexdigest() if out.exists() else None)
print(json.dumps(R, indent=1))
