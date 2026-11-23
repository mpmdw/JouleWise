"""Source-identity and named-band cases for the frozen hp-02 gate machine."""
import argparse
from contextlib import ExitStack
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hp02_machine", HERE / "test_hp02_gate_machine.py")
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)


def receipt(desk, section, results):
    t = machine.BASE
    sha = "a" * 64 if section == "latest_close" else "c" * 64

    def observation(phase, at):
        row = desk.row(phase, at)
        if section == "watcher":
            row["watcher"] = {"record":"finite watcher", "by":"fixture", "sampled_at":at,
                              "expires_epoch_s":t + 8000}
        row[section]["receipt_sha256"] = sha
        return row

    start = observation("Start", t)
    first = desk.call("Start", t, start)
    assert machine.acceptable(first), first
    row = observation("Run", t + 1)
    # Vary an actual predicate input without changing its claimed receipt identity.
    # Some changes remain individually admissible, others carry another adverse fact.
    edits = {
        "look": ("look.status","reserved"),
        "hp01_dates": ("hp01_dates.t0_dates",["2026-11-15","2026-11-16"]),
        "latest_close": ("latest_close.groups.0.group_id","different group"),
        "history": ("history.legs.L001","ambiguous"),
        "safety": ("safety.mode_verify",{"record":"fixture", "by":"magistrate","rc":1,
                                      "exceptions":["own-agent-tree-or-permitted-jobs"]}),
        "stops": ("stops.open",[{"scope":"other-kit","code":"synthetic other-kit stop"}]),
        "copy": ("copy.ciphertext_size_bytes",750),
        "priority": ("priority.entries.5.status","eligible"),
        "calendar": ("calendar.post_fence_transfer_s",12),
        "timing": ("timing.selector_sample_max_s",1101),
        "watcher": ("watcher.expires_epoch_s",t+8200),
    }
    machine.set_field(row, *edits[section])
    blocked = desk.call("Run", t + 1, row)
    holds, _, immutable = desk.ledger()
    matching = {key for key, value in holds.items() if value["source_digest"] == sha}
    # A changed receipt and its independently adverse content each need clearance.
    required = 2 if section in {"look","history"} else 1
    replay = desk.call("Run", t + 2, observation("Run",t + 2))
    still, _, after = desk.ledger()
    results.check("receipt content under same digest",section,
                  machine.refused(blocked) and len(matching)>=required and machine.refused(replay)
                  and matching<=still.keys() and immutable.items()<=after.items() and not desk.calls,
                  first=blocked["decision"], ids=len(matching), retry=replay["decision"])


def bands(desk, results):
    # Published one-leg pin-A intervals in item 463. Keep argument switches even
    # where adjacent eligible intervals touch. Each row is an inclusive interval.
    ranges = [("00:00:00","02:34:59"),("02:35:00","10:50:00"),
              ("13:15:00","23:48:10"),("23:48:11","23:59:59")]
    def epoch(day, text):
        h,m,s=map(int,text.split(":"))
        return machine.midnight(day) + 3600*h + 60*m + s
    def obs(at):
        row=desk.row("Run",at)
        machine.close(row,"fixture-close-17",at-1800,"a"*64)
        if row["history"]["prior_check"]:
            row["history"]["prior_check"]["ended_epoch_s"]=at-2000
        day=machine.day_at(at)
        entry=machine.ranked(row,"f2-inst-03")
        entry["start_windows"]=[[epoch(day,lo),epoch(day,hi)] for lo,hi in ranges]
        entry["status"]="eligible" if any(lo<=at<=hi for lo,hi in entry["start_windows"]) else "unavailable"
        return row
    base_day=machine.day_at(machine.BASE)
    edges=set()
    for lo,hi in ranges:
        edges.update([epoch(base_day,lo)-1,epoch(base_day,lo),epoch(base_day,hi),epoch(base_day,hi)+1])
    for edge in sorted(edges):
        for offset in range(-121,2):
            at=edge+offset
            row=obs(at)
            _, guards, raw=machine.oracle(desk,row,at)
            wire=machine.eval_run(desk,row,at)
            results.check("item 463 clock bands",[desk.item["span"],edge,offset],
                          machine.compare(wire,guards,raw),want="WAIT" if guards else raw,got=wire)


def all_controls(desk, origin, variant, route, results):
    at=desk.anchor
    if origin=="Issue":
        desk.publish("PROPOSED")
    if origin in {"Run","FinalRun"}:
        assert machine.acceptable(desk.call("Start",at))
    # The counterfactual retains the phase's entry prerequisites and omits only the
    # adverse read. A successful Start/Run would already publish/consume the attempt,
    # so leave the original adverse invocation out of this branch.
    steps=machine.retry(desk,{"id":"control"},origin,variant,route,at+5)
    expect="ELIGIBLE_WITH_COPY_DEBT" if variant=="clear-with-copy-debt" else "ELIGIBLE"
    results.check("route counterfactual",[origin,variant,route],
                  all(step["decision"]==expect and machine.acceptable(step) for step in steps)
                  and len(desk.calls)==1 and not desk.ledger()[0],steps=[s["decision"] for s in steps])


def terminal_product(desk, failure, variant, route, results):
    """Separate post-invocation consumption and uncertain-storage recovery."""
    m=machine
    at=desk.anchor
    assert m.acceptable(desk.call("Start",at))
    row=desk.row("Run",at+1)
    if failure=="failed-append":
        row["look"].update(status="reserved",pending_conflict=True)
        put=m.hp.publish_new_file
        def broken(path,data):
            if path.parent.name.startswith("holds-") and json.loads(data).get("holds"):
                raise OSError("fixture volume rejects append")
            return put(path,data)
        with m.patch.object(m.hp,"publish_new_file",broken):
            first=desk.call("Run",at+1,row)
        expected_calls=0
    else:
        def launcher():
            if failure=="ambiguous-invocation":
                raise OSError("fixture ambiguous invocation")
            return 27
        desk.effect=launcher
        first=desk.call("Run",at+1,row)
        expected_calls=1
    desk.effect=lambda:0
    attempts=m.retry(desk,{"id":"terminal"},"Run",variant,route,at+5)
    ok=first["rc"] not in (0,None) and all(m.refused(x) for x in attempts) and len(desk.calls)==expected_calls
    results.check("terminal and custody retry",[failure,variant,route],ok,first=first["decision"],
                  retries=[x["decision"] for x in attempts],additional_calls=len(desk.calls)-expected_calls)


def raised_read(desk,origin,variant,route,results):
    m=machine
    base=m.scenario
    def failing_read(actor,fact,phase,at,stack):
        row,install=base(actor,fact,phase,at,stack)
        def apply():
            install()
            previous=Path.read_bytes
            def read(path):
                if path==actor.args.observation:
                    raise RuntimeError("synthetic observation backend failed")
                return previous(path)
            stack.enter_context(m.patch.object(Path,"read_bytes",read))
        return row,apply
    with m.patch.object(m,"scenario",failing_read):
        fact={"id":"backend-exception","edit":{},"wire":"HOLD_UNKNOWN"}
        m.history_case(desk,fact,origin,variant,route,results)



def run(root, stream):
    m=machine
    results=m.Results(stream)
    m.DRAFTS=root/m.REL
    m.ITEMS=json.loads((m.DRAFTS/"hp-02/items.json").read_bytes())
    with tempfile.TemporaryDirectory(prefix="hp02-receipts-") as work:
        work=Path(work)
        archive=m.DRAFTS/"hp-02/fixtures/hp02-occupancy-fixture.zip"
        assert m.digest(archive.read_bytes())==m.M["fixture_sha256"][archive.name]
        with ZipFile(archive) as bundle:
            bundle.extractall(work/"seat")
        m.PIN=work/"seat/tmp/pin"
        sys.path.insert(0,str(m.PIN))
        m.hp=m.load_gate()
        sys.addaudithook(m.native_guard)
        for section in [*m.SECTIONS,"watcher"]:
            m.isolated(work,1,m.BASE,receipt,section,results)
        for span in (1,2,3):
            m.isolated(work,span,m.BASE,bands,results)
        for origin,variant,route in m.product(m.M["origins"],m.M["clear_reads"],m.M["retry_paths"]):
            m.isolated(work,1,m.BASE,all_controls,origin,variant,route,results)
        for failure,variant,route in m.product(m.M["terminal_cases"],m.M["clear_reads"],m.M["retry_paths"]):
            m.isolated(work,1,m.BASE,terminal_product,failure,variant,route,results)
        for origin,variant,route in m.product(m.M["origins"],m.M["clear_reads"],m.M["retry_paths"]):
            m.isolated(work,1,m.BASE,raised_read,origin,variant,route,results)
        results.check("synthetic isolation","sources",not m.NATIVE,attempts=m.NATIVE)
    return results


class HP02FrozenSourceTests(unittest.TestCase):
    def test_sources_and_bands(self):
        result=subprocess.run([sys.executable,"-IB",__file__],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--checkout",type=Path,default=HERE.parent)
    parser.add_argument("--results",type=Path)
    args=parser.parse_args()
    with ExitStack() as files:
        stream=files.enter_context(gzip.open(args.results,"wt")) if args.results else None
        report=run(args.checkout.resolve(),stream)
    print(json.dumps(report.count,indent=2,sort_keys=True))
    sys.exit(int(any(c["fail"] for c in report.count.values())))
