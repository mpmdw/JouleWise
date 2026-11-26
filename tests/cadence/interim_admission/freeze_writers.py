"""Developer-only corpus freezer. Run three separate interpreters, each with its pin's sources first.
The acceptance tests themselves consume the immutable corpus and need no historical checkout or network.
Arguments: pin, source tree, destination directory, then the corresponding registered kit.
Outside processes, hardware probes, real custody, telemetry and production jobs are never used.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

pin, source, dest, kit_file = sys.argv[1:]
source, dest, kit_file = map(lambda p: Path(p).resolve(), (source, dest, kit_file))
sys.path.insert(0, str(source))
from scripts import cadence_legs_runner as w

kit_raw = kit_file.read_bytes()
kit = json.loads(kit_raw)
assert kit["frozen"]["commit"].startswith(pin)
epoch = 1794718800
ids = [kit["legs"][0]["leg_id"], next((leg["leg_id"] for leg in kit["legs"][1:]
                                       if leg.get("g0_shape") == "span"), next(leg["leg_id"] for leg in kit["legs"][1:] if leg["prefill_tokens"] in (2000,10000,19458)))]
latest = pin == "6e9d42f1d"

def raising(exc):
    def fail(*args, **kwargs):
        raise exc
    return fail

def generate(case):
    clock = w.FakeClock(epoch)
    if case.startswith("builtin-mock"):
        with tempfile.TemporaryDirectory() as tmp:
            prev=Path.cwd()
            os.chdir(tmp)
            try:
                output=Path("span")
                args=dict(contaminate=ids[:1] if case=="builtin-mock-redo" else (),
                          g0_timeout=ids[:1] if case=="builtin-mock-timeout" else ())
                if latest and case=="builtin-mock-retry": args["soak_refusals"]=1
                deps=w.mock_deps(output,clock,**args)
                w.run_span(kit=kit,kit_sha256=hashlib.sha256(kit_raw).hexdigest(),output=output,
                           deadline=float(epoch+26000),windows=[],deps=deps,leg_ids=ids)
                paths=[output/w.RECEIPT_NAME,*sorted(output.glob("legs/*/leg_record.json")),
                       *sorted(output.glob("legs/*/leg_summary.json")),*sorted(output.glob("soak/soak_reference.json"))]
                return {p.relative_to(output).as_posix():json.loads(p.read_bytes()) for p in paths}
            finally:
                os.chdir(prev)
    meter_error = case == "meter-health"
    def feed(name):
        stop = dict(rc=0, proven_stopped=True)
        obj = SimpleNamespace(name=name, start=lambda: {"rc": 0}, poll=lambda: None,
                              stop=lambda: dict(stop), files=lambda: [])
        if case=="files":
            def start():
                path=Path("span")/("hazards/meter/stream-0001.jsonl" if name=="meter" else
                                   ("censuses.jsonl" if name=="agents" else "volume_censuses.jsonl"))
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(b'{"k":"h","status":"streaming"}\n{"k":"t","bad":0,"polls":1,"usb_errors":0,"elapsed_s":1.0}\n'
                                 if name=="meter" else b'{"synthetic":true}\n')
                obj.files=lambda:[path]
                return {"rc":0}
            obj.start=start
        if name == "volumes":
            obj.before_part = obj.close = lambda: {"rc": 0}
        if case == "stop-" + name:
            obj.stop = raising(ValueError("generated stop failure"))
        if case == "close-" + name:
            obj.close = raising(ValueError("generated close failure"))
        if case == "hash-" + name:
            obj.files = raising(OSError("generated hash failure"))
        if case.startswith("supervisor-") and name=="meter":
            from joulewise.b5 import driver
            def supervisor_stop():
                sv=driver.MonitorSupervisor(["fixture-monitor"],night_dir=Path("span"),popen=raising(AssertionError("process forbidden")))
                sv.argv=["fixture-monitor"]
                sv.starts=1
                sv.process=SimpleNamespace(pid=41,poll=lambda:0)
                now={"wall_s":clock.time(),"monotonic_ns":round(clock.monotonic()*1e9),"monotonic_raw_ns":round(clock.monotonic()*1e9)}
                with patch.object(driver,"stamp",return_value=now):
                    summary=sv.stop()
                proof={"reaped":True,"group_census":[] if case=="supervisor-proven" else ["synthetic process"]}
                result={"rc":0 if not proof["group_census"] else 2,"proven_stopped":not proof["group_census"],
                        "supervisor":summary,"group":proof}
                return result
            obj.stop=supervisor_stop
        return obj

    host = SimpleNamespace(night_agents=lambda: {"rc": 0, "stdout": "generated"},
                           ac_power=lambda: {"rc": 0, "stdout": "Now drawing from 'AC Power'"},
                           condition13=lambda: {"rc": 0, "executed_commit": kit["frozen"]["commit"]},
                           read_power=lambda: {"rc": 0, "ac_powermode": 0, "automatic": True},
                           display=lambda: {"rc": 1 if case == "display" else 0,
                                            "exit_code": 1 if case == "display" else 0,
                                            "argv": ["/usr/bin/pmset", "displaysleepnow"],
                                            "epoch_s": clock.time(), "stderr": ""},
                           dwell_s=lambda: 300., restore_power=lambda read: {
                               "rc": 0, "action": "foreign_marker_left" if read else "no_power_read"})
    if case.startswith("restore") or case == "signal-and-restore":
        host.restore_power = raising(ValueError("generated cleanup failure"))
    if case in ("restore-return","restore-verified"):
        from joulewise.align.apple import powermode
        def restore(read):
            def command(argv):
                reading="AC Power:\n powermode 0\n" if case=="restore-verified" else ""
                return SimpleNamespace(returncode=0 if case=="restore-verified" else 1,stdout=reading,stderr="")
            result=powermode.restore_automatic(runner=command)
            return dict(result,rc=0 if result["ok"] else 2)
        host.restore_power=restore
    if case=="display-exception":
        host.display=lambda:dict(rc=2,argv=["/usr/bin/pmset","displaysleepnow"],epoch_s=clock.time(),
                                 exit_code=None,stderr="OSError: generated")
    if case == "work-error":
        host.night_agents = raising(ValueError("loaded night agent or unreadable launchctl list"))
    soak_count = 0
    def soak(path, *args):
        nonlocal soak_count
        if case.startswith("signal-"):
            code = 130 if case == "signal-and-restore" else int(case.removeprefix("signal-"))
            raise SystemExit(code)
        if case in ("cap-not-fit", "cap-expired"):
            message = ("soak not started: its 1950 s cap cannot fit before the work deadline"
                       if case == "cap-not-fit" else "soak exceeded its 1950 s cap")
            raise w.SpanRefusal(message, 3)
        path.mkdir()
        soak_count += 1
        if case in ("retry", "retry-exhausted", "retry-no-budget") and (soak_count == 1 or case == "retry-exhausted"):
            if case == "retry-no-budget":
                clock.sleep(9900)
            raise w.SoakRefusal("soak exit 5: the idle soak failed its settle or quiet check")
        clock.sleep(1800.)
        return path / "soak_reference.json"

    def leg(path, spec_path, reference, cap, feeds, remaining, **kwargs):
        if case == "leg-error":
            raise w.LegRuntimeError(f"{path.parent.name}: leg runtime exit 2")
        spec = json.loads(spec_path.read_text())
        path.mkdir()
        status = case if case in ("g0_unreleased", "incomplete") else "complete"
        turn = status != "g0_unreleased"
        t = int(clock.time() * 1e9)
        clock.sleep(900. if case != "leg-wall-overtime" else 2600.)
        result = dict(leg_id=spec["leg_id"], leg_status=status, bundle="runs/cadence-leg",
                      member_status="succeeded", g0_outcome="released" if turn else "timeout",
                      g0_released=turn, g0_wait_s=100. if turn else 1200., g0_timeout_s=1200.,
                      quiet_s=spec["quiet_s"], prefill_chars=spec["prefill_chars"],
                      prefill_tokens=spec["prefill_tokens"] if turn else None, decode_cap=spec["decode_tokens"],
                      decode_tokens=spec["decode_tokens"] if status == "complete" else (500 if turn else None),
                      decode_cap_reached=status == "complete", os_level_max=0, pm_nominal=True,
                      incomplete_reasons=[] if status == "complete" else (["turns:0","episode.g0_unreleased:0","thermal.start_gate_timeout"] if not turn else ["episode.deadman:0"]),
                      ac_powermode={"value": 0,"observed_at":"episode_start","source":"pmset -g custom (AC Power block, exact powermode key)"}, quiet_spans_ns=([[t-spec["quiet_s"]*10**9,t]] if turn and spec["quiet_s"] else []), config_sha256="a"*64)
        if turn:
            result.update(turn_start_ns=t, turn_end_ns=t+900_000_000_000, first_token_ns=t+20_000_000_000)
        if pin != "b4b6aeb19":
            result.update(g0_shape=spec.get("g0_shape", "own"), g0_role=spec.get("g0_role","capture"),
                          g0_reference_source=f"cadence-{spec['campaign_id']}-{ids[0] if kwargs else spec['leg_id']}", g0_reference_record_sha256="e"*64 if kwargs else None)
        return result
    verdict_count = 0
    def verdict(name, result, wall):
        nonlocal verdict_count
        verdict_count += 1
        return dict(redo=case == "redo" and verdict_count == 1, seconds=round(wall), max_busy_cores=0.9
                    if case == "redo" and verdict_count == 1 else 0.1, max_gap_s=1.)
    deps = w.Deps(clock=clock, feeds=list(map(feed, ("agents","meter","volumes"))), host=host,
                  run_soak=soak, run_leg=leg, verify_frozen=lambda k: dict(rc=0, head=k["frozen"]["commit"],
                  paths=len(k["frozen"]["paths"])), load_verdict=verdict, soak_cap_s=1950., max_span_s=43200)
    flags = {}
    if case.startswith("authority") or case == "span-id":
        if case != "span-id":
            flags.update(authorized_t0_date="2026-11-14", t0_not_before=epoch-1, t0_before=epoch+1,
                         t0_anchor=(int(epoch*1e9),10**12,10**12))
        if case.endswith("-ns"):
            flags["t0_not_before_ns"] = (epoch-1)*10**9
        if case != "authority":
            flags["span_id"] = "dev-03-s01"
    # Synthetic files exist only to exercise the runner's file enumeration, hashing and desk serialization.
    with tempfile.TemporaryDirectory() as tmp:
        cwd=Path.cwd()
        os.chdir(tmp)
        try:
            with patch.object(w.legsmod, "meter_health", raising(ValueError("generated health error"))
                              if meter_error else w.legsmod.meter_health), patch.object(
                     w.legsmod, "write_desk_bundle", raising(OSError("generated desk failure"))
                     if case == "desk" else w.legsmod.write_desk_bundle):
                def interrupt(frame, event, arg):
                    if event == "line" and frame.f_code.co_filename == w.__file__:
                        # Interruptions after append/before step, before operation, and after completion.
                        target = {"interrupt-attempt": "try:", "interrupt-step": "started = stages.start(",
                                  "interrupt-post": 'record["soak_reference"] ='}
                        line = src_lines[frame.f_lineno - 1].strip()
                        if case.startswith("work-signal@"):
                            match=frame.f_code.co_name=="step" and frame.f_locals.get("name")==case.split("@")[1] and line.startswith("result = operation()")
                        elif case == "interrupt-attempt":
                            match = frame.f_code.co_name == "run_soak" and line == "try:"
                        elif case == "interrupt-after-result":
                            match = frame.f_locals.get("name") == "soak" and line.startswith("if fatal and")
                        elif case == "interrupt-step":
                            match = frame.f_locals.get("name") == "soak" and line.startswith(target[case])
                        else:
                            match = case == "interrupt-post" and line.startswith(target[case])
                        if match:
                            raise SystemExit(130)
                    return interrupt
                if case.startswith(("interrupt-","work-signal@")):
                    sys.settrace(interrupt)
                try:
                    rc=w.run_span(kit=kit,kit_sha256=hashlib.sha256(kit_raw).hexdigest(), output="span",
                                  deadline=float(epoch if case=="deadline" else epoch+15000), windows=([w.legsmod.parse_window("21:08-21:10")] if case=="blackout" else []),
                                  deps=deps,leg_ids=ids[:1] if case=="support" else ids,**flags)
                finally:
                    sys.settrace(None)
            paths = [Path("span/runner_receipt.json"),*sorted(Path("span/legs").glob("*/leg_*.json"))]
            docs={p.relative_to("span").as_posix():json.loads(p.read_bytes()) for p in paths
                  if p.name != "leg_spec.json"}
            assert docs["runner_receipt.json"]["rc"] == rc
            return docs
        finally:
            os.chdir(cwd)

src_lines=Path(w.__file__).read_text().splitlines()
cases="normal support files restore-verified restore-return display-exception restore stop-agents stop-meter stop-volumes close-volumes hash-agents hash-meter hash-volumes meter-health desk work-error display signal-129 signal-130 signal-143 signal-and-restore cap-not-fit cap-expired leg-error interrupt-after-result leg-wall-overtime deadline g0_unreleased incomplete redo interrupt-step".split()
if latest:
    cases += "builtin-mock-retry retry retry-exhausted retry-no-budget interrupt-attempt interrupt-post authority authority-ns span-id".split()
cases += "builtin-mock builtin-mock-redo builtin-mock-timeout supervisor-proven supervisor-refused blackout".split()
normal=generate("normal")[Path(w.RECEIPT_NAME).name]
work=[step["name"] for step in normal["steps"]]
cases.extend("work-signal@"+name for name in work[:work.index("restore")])
all_docs={case:generate(case) for case in cases}
dest.mkdir(parents=True,exist_ok=True)
import gzip
(dest/(pin+".json.gz")).write_bytes(gzip.compress(json.dumps(all_docs,sort_keys=True,separators=(",",":")).encode(),
                                                  mtime=0))
for case,docs in all_docs.items():
    r=docs["runner_receipt.json"];print(pin,case,r["rc"],r.get("error"),r["legs_finished"])
