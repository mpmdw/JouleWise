"""Opus contract-lens refuter probes for cold gate A2. Usage: python3 -B probe_p1.py <tree>
Every subprocess whose argv names a forbidden program raises before it starts."""
import sys, os, json, tempfile, subprocess, time
TREE = sys.argv[1]
sys.path.insert(0, TREE)
FORBID = ("sudo", "powermetrics", "systemsetup", "sntp", "/usr/bin/log", "ioreg", "pmset")
def _hook(event, args):
    if event == "subprocess.Popen":
        text = " ".join(map(str, args[1] if isinstance(args[1], (list, tuple)) else [args[1]]))
        if any(f in text for f in FORBID):
            raise RuntimeError("p1 guard blocked: " + text)
sys.addaudithook(_hook)
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from scripts import run_night as d
from joulewise import network_time_window as ntw
from joulewise import quiet_predicate_campaign as q

SCR = Path(os.environ.get("P1_TMP", "/tmp"))
PLAN = SimpleNamespace(plan_id="p1-probe", receipt_class="DIAGNOSTIC_NO_PACK", quiet_admission=None)
which = sys.argv[2] if len(sys.argv) > 2 else "all"

def refusals(night):
    return [(p.name, json.loads(p.read_text())["refusal"]["reason"]) for p in d._refusal_paths(night)]

def idle_night(root):
    night = root / "night"; night.mkdir()
    (night / "chain.started").write_text(json.dumps({"pid": 4242, "pgid": 4242, "epoch_s": 0}))
    (night / "evidence_processes.jsonl").write_text("")
    (night / "receipt.json").write_text(json.dumps({"plan_id": PLAN.plan_id, "conditions": [
        {"condition_id": "C5", "status": "PASS", "measured": {"payload_kind": "quiet_predicate_evidence"}}]}))
    return night

P3_FAIL = {"check": "P3", "matches": [{"pid": 999999, "command": "/x/collector.py"}]}

def driver_tail(root, night, abort, proof_ok, termination_proven=True):
    """The production order of run_night.py:3345-3361 then prepare_result :3411-3458,
    with [K] and the proof's answer injected; helpers are the production ones."""
    if proof_ok is False:
        abort = d._capture_unproved_abort(night, PLAN, root, abort,
                                          "capture process absence could not be proved", P3_FAIL)
    if abort is not None:
        if "document" not in abort:
            d._write_driver_refusal(night / "refusal.json", PLAN, abort["reason"], abort["detail"], abort.get("evidence"))
        refused = abort["reason"] in {d._CODES["chain_launch_failed"], d._CODES["chain_alive"]} or not termination_proven
        verdict = "REFUSED" if refused else "ABORTED"
        res = d._write_result(root, night, PLAN, verdict, 1, abort["reason"], 0, 0, None, 0)
    else:
        res = d._write_result(root, night, PLAN, "GO", 0, None, 0, 0, None, 0)
    return res

if which in ("all", "R3"):
    print("== R3 / E2-signature: pre-existing refusal documents at a failed proof ==")
    cases = {}
    with mock.patch.object(d.night_gate, "validate_receipt", return_value=[]):
        # (a) [K] writes refusal.json (idle chain left no outcome), then the proof fails
        for proven in (True, False):
            with tempfile.TemporaryDirectory(dir=SCR) as td:
                root = Path(td); night = idle_night(root)
                with mock.patch.object(q, "cleanup_record", return_value={"cleanup_proven": proven}):
                    k = d._evidence_cleanup_error(PLAN, night)     # the call at run_night.py:3347
                res = driver_tail(root, night, None, False)
                print(f"R3a [K] cleanup_proven={proven}: K_return={k!r}")
                print("    refusals:", refusals(night), "| result:", res["verdict"], res["aborted_reason"], res["refusal_documents"])
        # (b) the chain itself wrote refusal.json (quiet_predicate_campaign.py:1804, 'final evidence cleanup unproven'), then proof fails
        with tempfile.TemporaryDirectory(dir=SCR) as td:
            root = Path(td); night = idle_night(root)
            q.write_refusal(night, PLAN, "final evidence cleanup unproven")
            (night / "evidence_outcome.json").write_text(json.dumps({"outcome": "refused", "error": "final evidence cleanup unproven", "cleanup_proven": False}))
            with mock.patch.object(q, "cleanup_record", return_value={"cleanup_proven": False}):
                k = d._evidence_cleanup_error(PLAN, night)
            res = driver_tail(root, night, None, False)
            print("R3b chain-authored refusal (qpc.py:1804) then proof fails:")
            print("    refusals:", refusals(night), "| result:", res["verdict"], res["aborted_reason"], res["refusal_documents"])
            doc01 = json.loads((night / "refusal-01.json").read_text())["refusal"]["evidence"]
            print("    chain_alive doc names the earlier document?", "prior_abort" in doc01, sorted(doc01))
        # (c) proof PASSES, agent-census stop (abort without document), killed idle chain left no outcome
        with tempfile.TemporaryDirectory(dir=SCR) as td:
            root = Path(td); night = idle_night(root)
            with mock.patch.object(q, "cleanup_record", return_value={"cleanup_proven": True}):
                d._evidence_cleanup_error(PLAN, night)
            abort = d._refusal_mapping(d._CODES["aborted_agent_present"],
                                       "agent session present", {})
            res = driver_tail(root, night, abort, True)
            print("R3c head order ([K] :3347 before result), proof passes, agent-census stop:")
            print("    refusals:", refusals(night), "| result:", res["verdict"], res["aborted_reason"])
    # (d) watchdog control (2b's fix): document on disk -> superseded, one document
    with tempfile.TemporaryDirectory(dir=SCR) as td:
        root = Path(td); night = idle_night(root)
        d._write_driver_refusal(night / "refusal.json", PLAN, "night_window_exceeded", "deadline", {})
        prior = dict(d._refusal_mapping("night_window_exceeded", "deadline", {}), document="refusal.json")
        res = driver_tail(root, night, prior, False)
        print("R3d watchdog control (E2 as fixed):", refusals(night), "| result:", res["verdict"], res["aborted_reason"])

if which in ("all", "R1"):
    print("== R1: never-launched claim with missing keys ==")
    for label, started in [("missing_both", {"popen_attempted": False, "launch_error": "x"}),
                           ("missing_pid", {"pgid": None, "popen_attempted": False}),
                           ("explicit_nulls", {"pid": None, "pgid": None, "popen_attempted": False, "launch_error": "x"}),
                           ("pid_present", {"pid": 4242, "pgid": None, "popen_attempted": False})]:
        with tempfile.TemporaryDirectory(dir=SCR) as td:
            root = Path(td); night = root / "night"; night.mkdir()
            (night / "chain.started").write_text(json.dumps(started))
            (night / "chain.exited").write_text(json.dumps({"launch_failed": True}))
            marker = root / "marker.json"
            marker.write_text(json.dumps({"custody_root": str(root), "plan_id": "p1-probe"}))
            calls = []
            def proof(m, pgid):
                calls.append(pgid); return False, {}
            with mock.patch.object(ntw, "set_network_time_on", side_effect=lambda *a, **k: (calls.append("ON"), {"exit_code": 0})[1]):
                out = ntw.recover_network_time(marker_path=marker, capture_proof=proof)
            print(f"R1 {label}: driver _chain_never_launched={d._chain_never_launched(night)} recovery={out} calls={calls}")

if which in ("all", "R2"):
    print("== R2: batch census exit 0 with empty output ==")
    real_run = subprocess.run
    def fake(argv, **kw):
        if argv[0] == "/usr/bin/pgrep":
            return subprocess.CompletedProcess(argv, 0, "", "")
        return real_run(argv, **kw)   # the attribution `ps -p ""` runs for real
    with mock.patch.object(d.subprocess, "run", side_effect=fake):
        print("R2 _census_chunk([99990,99991]) exit0/empty ->", d._census_chunk([99990, 99991], 1.0))
        print("R2 _group_census(99990) exit0/empty (single-group path) ->", d._group_census(99990, 1.0))
    r = real_run(["/usr/bin/pgrep", "-lf", "-g", "99990,99991", "."], capture_output=True, text=True)
    print("R2 real pgrep on two absent groups: exit", r.returncode, "stdout", repr(r.stdout))
    r = real_run(["/bin/ps", "-o", "pgid=,pid=,command=", "-p", ""], capture_output=True, text=True)
    print("R2 real attribution `ps -p ''`: exit", r.returncode, "stderr", repr(r.stderr[:60]))

if which in ("all", "R4"):
    print("== R4 / NIT-1: pass budget and horizon ==")
    for n in (0, 1, 2, 12, 113, 256, 257, 769):
        g = set(range(2, 2 + n)) if n else set()
        b = d.CAPTURE_CHECK_TIMEOUT_S * d._capture_pass_calls(g)
        print(f"groups={n:4d} calls={d._capture_pass_calls(g)} budget={b:.0f}s last-retry-start<= {d.GROUP_CENSUS_WINDOW_S - d.GROUP_CENSUS_INTERVAL_S - b:.1f}s")
    clock = [1000.0]
    def slow_pass(marker, pgid, groups, t):
        clock[0] += 5.4; return True, {"checks": ["P1", "P2", "P3"]}
    with tempfile.TemporaryDirectory(dir=SCR) as td, \
         mock.patch.object(d.time, "monotonic", side_effect=lambda: clock[0]), \
         mock.patch.object(d, "_capture_proof_pass", side_effect=slow_pass):
        print("R4 first pass succeeding at +5.4 s ->", d._prove_capture_absent({"x": 1}, 4242, Path(td)))

if which in ("all", "R5"):
    print("== R5: C7 path exit status ==")
    with tempfile.TemporaryDirectory(dir=SCR) as td:
        root = Path(td); night = root / "night"; night.mkdir()
        with mock.patch.object(d, "_durable_record"), mock.patch.object(d, "_write_courier_outcome"):
            print("R5 _finish_reporting(EXIT_REFUSED, allow_courier=False) ->",
                  d._finish_reporting(root, night, PLAN, d.EXIT_REFUSED, None, allow_courier=False,
                                      courier_error="chain termination was not proven"))

if which in ("all", "NIT2"):
    print("== NIT-2: path signature prefix ==")
    paths = {"/Users/edr/code/JouleWise"}
    for c in ("/bin/zsh /Users/edr/code/JouleWise-wt-other/run.sh", "/bin/zsh /Users/edr/code/JouleWise/scripts/x.sh",
              "log stream --predicate powermetrics", "vim /Users/edr/code/JouleWiseNotes.txt"):
        print(f"NIT2 {d._capture_signature(c, paths)!s:5} {c}")
