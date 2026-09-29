import sys, subprocess
sys.path.insert(0, sys.argv[1])
from unittest import mock
from scripts import run_night as d
real_run = subprocess.run
def make(ps_real):
    def fake(argv, **kw):
        if argv[0] == "/usr/bin/pgrep":
            return subprocess.CompletedProcess(argv, 1 if "," not in argv[3] else 0, "", "")
        return real_run(argv, **kw) if ps_real else subprocess.CompletedProcess(argv, 1, "", "ps: Invalid process id")
    return fake
for ps_real in (True, False):
    with mock.patch.object(d.subprocess, "run", side_effect=make(ps_real)), \
         mock.patch.object(d, "_capture_sweep", return_value=(True, {"check": "P3", "matches": []})):
        print(f"R2 pass: P1 exit1/empty, P2 batch exit0/empty, P3 clear, ps {'REAL' if ps_real else 'injected exit1/empty'} ->",
              d._capture_proof_pass({}, 99989, {99990, 99991}, 1.0))
