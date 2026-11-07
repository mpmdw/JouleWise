import contextlib, hashlib, json, os, subprocess, sys, time
from pathlib import Path
ROOT=Path.cwd()
LEAD=ROOT.parents[1]
OUT=Path(os.environ["TMPDIR"])
sys.path.insert(0,str(ROOT))
from tests.b5_analysis.fixtures_s10 import chain_fixture
from tests.b5_analysis.joined_s10 import JoinedHarness, capture_driver_streams
from joulewise.b5_analysis import dry_run as d

def emit(event, **fields):
    with (OUT/"progress.jsonl").open("a") as f:
        f.write(json.dumps(dict(event=event,elapsed_s=round(time.monotonic()-start,2),**fields))+"\n")
start=time.monotonic()
emit("restore_start")
fixture=chain_fixture()
assert set(fixture.windows)=={"alpha","beta","gamma"}
assert fixture.root.is_relative_to(ROOT/".scratch-s10f/tmp")
emit("restore_done",index=str(fixture.index))
harness=JoinedHarness(fixture.index)
(OUT/"index.json").write_bytes(harness.index.read_bytes())
# Read-only event observer: no program function or arithmetic is replaced.
tool=next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
sys.monitoring.use_tool_id(tool,"r2-synthetic-progress")
def returned(code, offset, value):
    frame=sys._getframe(1)
    emit("program_done",step=frame.f_locals["step"],window=frame.f_locals["window"])
sys.monitoring.register_callback(tool,sys.monitoring.events.PY_RETURN,returned)
sys.monitoring.set_local_events(tool,d.StepRunner.run.__code__,sys.monitoring.events.PY_RETURN)
custody=OUT/"synthetic-custody"
with harness.git_seams() as checkout, capture_driver_streams() as streams:
    rc=d.run("blind-dry-run",harness.index,custody,workers=1,_test_seal_pins=harness.pins,
             _test_repo_root=harness.repo,_runner=None,_git=checkout)
sys.monitoring.set_local_events(tool,d.StepRunner.run.__code__,0)
sys.monitoring.free_tool_id(tool)
(OUT/"driver.stdout").write_text(streams["stdout"])
(OUT/"driver.stderr").write_text(streams["stderr"])
record=custody/"dry-run/B5-BLIND-DRY-RUN-RECORD.json"
r=json.loads(record.read_bytes())
summary=dict(driver_rc=rc,driver_wall_s=round(time.monotonic()-start,2),
             r2_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
             record_sha256=hashlib.sha256(record.read_bytes()).hexdigest(),
             steps=[{k:v for k,v in row.items() if k in ("step","window","status","flags")} for row in r["steps"]],
             completed_without_tooling_refusal=r["completed_without_tooling_refusal"],
             index=str(OUT/"index.json"),custody=str(custody))
(OUT/"driver-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
emit("driver_done",rc=rc)
argv=[sys.executable,"-B",str(LEAD/"scripts/independent_recompute_b5.py"),"--member-detail","--out",str(OUT/"recompute.json")]
for pack,w in fixture.windows.items():
    argv += ["--"+pack,str(w.archive),"--claim-runs-"+pack,str(w.claim),"--bound-runs-"+pack,str(w.bound)]
(OUT/"recompute-command.json").write_text(json.dumps(argv,indent=2)+"\n")
with (OUT/"recompute.stdout").open("w") as stdout,(OUT/"recompute.stderr").open("w") as stderr:
    result=subprocess.run(argv,stdout=stdout,stderr=stderr)
emit("recompute_done",rc=result.returncode)
argv=[sys.executable,"-B",str(LEAD/"scripts/compare_b5_recompute.py"),"--l9-custody",str(custody),"--recompute",str(OUT/"recompute.json"),"--window-index",str(OUT/"index.json"),"--restricted-out",str(OUT/"comparison-initial.json")]
(OUT/"comparator-command.json").write_text(json.dumps(argv,indent=2)+"\n")
with (OUT/"comparison-initial.stdout").open("w") as stdout,(OUT/"comparison-initial.stderr").open("w") as stderr:
    result=subprocess.run(argv,stdout=stdout,stderr=stderr)
emit("comparison_done",rc=result.returncode)
print(json.dumps(summary))
