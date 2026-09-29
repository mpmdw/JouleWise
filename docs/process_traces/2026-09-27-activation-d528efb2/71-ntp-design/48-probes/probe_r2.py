import sys, subprocess, collections
sys.path.insert(0, sys.argv[1])
from unittest import mock
from scripts import run_night as d
real_run = subprocess.run
def fake(argv, **kw):
    if argv[0] == "/usr/bin/pgrep":
        return subprocess.CompletedProcess(argv, 0, "", "")
    assert argv[0] == "/bin/ps", argv
    return real_run(argv, **kw)
tally = collections.Counter()
with mock.patch.object(d.subprocess, "run", side_effect=fake):
    for _ in range(200):
        try:
            tally["chunk=" + repr(d._census_chunk([99990, 99991], 1.0))] += 1
        except Exception as e:
            tally["raised " + type(e).__name__] += 1
    for _ in range(50):
        try:
            tally["proofpass=" + repr(d._capture_proof_pass({"_x":1}, 99989, {99990, 99991}, 1.0)[1].get("check"))] += 1
        except Exception as e:
            tally["pass raised " + type(e).__name__] += 1
    print("R2 single-group path:", d._group_census(99990, 1.0))
for k, v in tally.items(): print(v, k)
r = real_run(["/usr/bin/pgrep", "-lf", "-g", "99990,99991", "."], capture_output=True, text=True)
print("real pgrep, two absent groups: exit", r.returncode, "stdout", repr(r.stdout))
