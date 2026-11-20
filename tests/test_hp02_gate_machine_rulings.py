"""Executable Q1–Q3 histories. All observations, custody and published authority are synthetic."""
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
from unittest.mock import patch
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hp02_matrix", HERE / "test_hp02_gate_machine.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
wire = m.records
rules = m.M["protocol"]
T = m.BASE
UNKNOWN = "HOLD_UNKNOWN"


def publish(d, tag, payload, when, *, role="lead", include=True, trusted=True):
    """Replace only the reachable-main byte lookup. Let the gate verify the item and payload."""
    number = payload["authority"]["run_state_item"]
    item = dict(schema="joulewise.run_state_item.v1", number=number,
                issued_epoch_s=when, owner=role, status="ISSUED")
    fence = chr(96) * 3
    doc = f"{number}. **Synthetic authority**\n\n{fence}item\n{json.dumps(item)}\n{fence}\n"
    if include:
        doc += f"{fence}{tag}\n{json.dumps(payload)}\n{fence}\n"
    commit = m.digest(doc.encode())[:40]
    if trusted:
        d.authorities[commit] = doc
    return {**payload, "authority": {**payload["authority"], "commit": commit}}


def correction(d, hold, kind, at):
    role = "magistrate" if kind == "non-lead" else "lead"
    evidence = {"record": "synthetic reconciliation of mistaken look attestation",
                "sha256": m.digest(b"fixture execution register shows mistaken association")}
    payload = dict(schema="hp-02.attestation-correction.v1", action="ATTESTATION-CORRECTION",
                   look_id="lm-hp-01", original_source_digest=hold["source_digest"],
                   evidence=evidence, ledger_sequence=hold["ledger_sequence"]+1,
                   authority=dict(role=role, run_state_item=902))
    if kind == "wrong-digest":
        payload["original_source_digest"] = "0"*64
    if kind == "missing-evidence":
        del payload["evidence"]
    if kind == "wrong-look":
        payload["look_id"] = "other-look"
    return publish(d, "hp-02-attestation-correction", payload, at, role=role,
                   include=kind != "unpublished", trusted=kind != "forged")


def execution(d, origin, kind, results):
    fact = next(f for f in m.M["facts"] if f["id"] == "ran")
    # Supply an independently known original source, including for post-claim reads.
    original_sha = m.digest(b"synthetic lm-hp-01 execution register entry at fixture look 91")
    fact = {**fact, "edit": {"set": {**fact["edit"]["set"], "look.receipt_sha256": original_sha}}}
    first = m.first(d, fact, origin)
    holds = d.ledger()[0]
    execution_holds = [h for h in holds.values() if h["decision"] in {"NOT_ADMITTED","SELECT_RANK_4"}]
    exact_source = any(h["source_digest"] == original_sha for h in execution_holds)
    if kind == "ordinary":
        results.check("Q1 original execution digest", origin, exact_source)
    key = [origin, kind]
    if not execution_holds:
        results.check("Q1 execution authority", key, False, reason="missing execution hold", first=first)
        return
    at = T+10
    d.publish("ISSUED", fresh=True)
    row = d.row("Start", at)
    row["hold_dispositions"] = m.proof_rows(d, holds, at, "valid")
    ordinary_refused = True
    if kind == "valid":
        # The same verified ordinary clearance, alone, must leave the execution bar in force.
        control = d.call("Start", at, row)
        ordinary_refused = m.refused(control) and not d.calls
        at += 1
        d.publish("ISSUED", fresh=True)
        row = d.row("Start", at)
        # A verifier may either retain or close the ordinary hold while retaining the global bar.
        still = d.ledger()[0]
        row["hold_dispositions"] = m.proof_rows(d, still, at, "valid") if still else []
    if kind != "ordinary":
        row["attestation_corrections"] = [correction(d, {**execution_holds[0], "source_digest": original_sha}, kind, at)]
    if kind == "still-ran":
        row["look"]["status"] = "ran"
    start = d.call("Start", at, row)
    later = d.row("Run", at+1)
    if kind == "still-ran":
        later["look"]["status"] = "ran"
    run = d.call("Run", at+1, later)
    calls = len(d.calls)
    if kind == "valid":
        ok = ordinary_refused and m.acceptable(start) and m.acceptable(run) and calls == 1
    else:
        ok = m.refused(start) and m.refused(run) and calls == 0
        # The current positive execution in still-ran is a new attestation with its own digest.
        # The historical bar must persist when a later, newly named issue reports clear.
        d.issue["record"] += " replacement identity"
        d.publish("ISSUED")
        again = d.call("Start",at+3)
        another = d.call("Run",at+4)
        ok = ok and m.refused(again) and m.refused(another) and not d.calls
    results.check("Q1 execution authority", key, ok and exact_source and m.refused(first),
                  first=first["decision"], start=start["decision"], run=run["decision"], launches=len(d.calls))


def sequence(d, case, results):
    label, delta, wall_offset, want = case
    assert m.acceptable(d.call("Start",T))
    at = T+2
    row = d.row("Run",at)
    row["look"]["status"] = "reserved"
    blocked = d.call("Run",at,row)
    holds = d.ledger()[0]
    if not holds:
        results.check("Q3 sequence order",label,False,reason="missing reservation hold")
        return
    before = set(holds)
    now = at+10
    row = d.row("Run",now)
    row["hold_dispositions"] = m.proof_rows(d,holds,now,"valid",sequence_delta=delta,
                                             authority_at=at+wall_offset)
    res = d.call("Run",now,row)
    open_after, closed, _ = d.ledger()
    ok = (m.acceptable(res) and len(d.calls)==1 and before<=closed.keys() if want else
          m.refused(res) and not d.calls and before<=open_after.keys())
    results.check("Q3 sequence order",label,ok and m.refused(blocked),want=want,got=res["decision"],
                  hold_seq=next(iter(holds.values()))["ledger_sequence"],delta=delta,
                  wall_offset=wall_offset,launches=len(d.calls))


def prepare(d, origin):
    # Every position starts with an actual issue-ledger event so a read fault is observable.
    d.publish("PROPOSED")
    assert m.acceptable(d.call("Issue",T))
    if origin != "Issue":
        d.publish("ISSUED")
    if origin in {"Run","FinalRun"}:
        assert m.acceptable(d.call("Start",T+1))


def inject_fault(d, origin, name):
    """One attempt loses the specified input. All later gate calls use working I/O."""
    at = T+3
    phase = "Run" if origin == "FinalRun" else origin
    row = d.row(phase,at)
    issue_dir, = (d.args.custody/"hp-02-arms").glob("holds-*")
    hit = []
    with ExitStack() as scopes:
        def install():
            if name in {"missing-identity","wrong-identity-digest","observation-io"}:
                original = Path.read_bytes
                path = d.args.observation if name == "observation-io" else d.args.issue
                def read(p):
                    if p == path:
                        hit.append(name)
                        if name == "wrong-identity-digest":
                            return original(p) + b" "
                        if name == "missing-identity":
                            raise FileNotFoundError("synthetic issue absent")
                        raise OSError("synthetic observation I/O")
                    return original(p)
                scopes.enter_context(patch.object(Path,"read_bytes",read))
            elif name == "ledger-read":
                original = m.hp.read_receipt_file
                def read(p):
                    if p.parent == issue_dir:
                        hit.append(name)
                        raise OSError("synthetic issue ledger unavailable")
                    return original(p)
                scopes.enter_context(patch.object(m.hp,"read_receipt_file",read))
            elif name == "ledger-write":
                original = m.hp.publish_new_file
                def write(p,data):
                    if p.parent == issue_dir:
                        hit.append(name)
                        raise OSError("synthetic issue ledger rejected append")
                    return original(p,data)
                scopes.enter_context(patch.object(m.hp,"publish_new_file",write))
                row["calendar"]["receipt_sha256"] = "f"*64
                if origin == "FinalRun":
                    m.write(d.args.observation,row)
            elif name == "in-flight":
                marker = issue_dir.parent / (issue_dir.name.replace("holds-","reading-",1)+".json")
                m.write(marker,{"issue_id":issue_dir.name.removeprefix("holds-")})
                hit.append(name)
            elif name == "ac-error":
                from joulewise.align.apple import powermode
                def fail():
                    hit.append(name)
                    raise ValueError("synthetic AC read failure")
                scopes.enter_context(patch.object(powermode,"observe_ac_powermode",fail))
            else:
                raise AssertionError(name)
        if origin == "FinalRun":
            d.during_claim = install
        else:
            install()
        try:
            first = d.call(phase,at,row)
        finally:
            d.during_claim = None
    assert hit, (origin,name,first)
    return first


def failed_record(hold, at, name):
    """Verify the stored failure independently, including what bytes the authority names."""
    rec = hold.get("failed_read")
    if not isinstance(rec,dict):
        return False
    sources = {"ac-error":("ac","powermode"), "observation-io":("observation", "obs"),
               "ledger-write":("ledger","journal","hold"), "ledger-read":("ledger","journal","hold"),
               "in-flight":("flight","reading"), "missing-identity":("issue","identity"),
               "wrong-identity-digest":("issue","identity")}
    classes = {"ac-error":"ValueError","observation-io":"OSError","missing-identity":"FileNotFoundError",
               "ledger-read":"OSError","ledger-write":"OSError"}
    return (isinstance(rec.get("source"),str) and
            any(token in rec["source"].lower() for token in sources[name]) and
            isinstance(rec.get("error_class"),str) and bool(rec["error_class"]) and
            (name not in classes or rec["error_class"].split(".")[-1] == classes[name]) and
            rec.get("attempt_time") == at and type(rec.get("ledger_sequence")) is int and
            rec["ledger_sequence"] == hold.get("ledger_sequence") and
            m.digest(wire.canonical(rec)) == hold.get("source_digest") and bool(hold.get("id")))


def recovery(d, holds, at):
    d.publish("ISSUED",fresh=True)
    row = d.row("Start",at)
    row["hold_dispositions"] = m.proof_rows(d,holds,at,"valid") if holds else []
    start = d.call("Start",at,row)
    run = d.call("Run",at+1)
    return start, run


def failure_history(d, origin, name, variant, route, results):
    prepare(d,origin)
    first = inject_fault(d,origin,name)
    queue_fault = name in rules["Q2"]["faults"]
    group = "Q2" if queue_fault else "Q3"
    key = [name,origin,variant,route]
    holds = {i:h for i,h in d.ledger()[0].items() if h.get("decision") == UNKNOWN}
    if queue_fault:
        holds = {i:h for i,h in holds.items() if (h.get("queue_sha"),h.get("queue_seq")) == wire.position(d)}
    provenance = bool(holds) and all(failed_record(h,T+3,name) for h in holds.values())
    results.check(group+" failure record",key,provenance and m.refused(first) and not d.calls,
                  first=first["decision"],ids=list(holds),position=wire.position(d))
    if queue_fault and variant=="replacement-source":
        # Model restoration of the failed volume to its last clean snapshot.
        # The separately mounted fallback custody is intentionally preserved.
        for marker in (d.args.custody/"hp-02-arms").glob("reading-*.json"):
            marker.unlink()
    if queue_fault and route=="fresh-Start":
        # Unlike re-publication, this renames the authenticated issue at the same queue position.
        d.issue["record"] += " successor identity"
    steps = m.retry(d,{"id":"fault"},origin,variant,route,T+8)
    retained = d.ledger()[0]
    inhibited = m.refused(first) and all(m.refused(r) for r in steps) and not d.calls
    results.check(group+" retry inhibits launch",key,inhibited,first=first["decision"],
                  retry=[s["decision"] for s in steps],launches=len(d.calls))
    if holds and all(i in retained for i in holds):
        before = len(d.calls)
        start,run = recovery(d,holds,T+20)
        opened,closed,_ = d.ledger()
        ok = (inhibited and provenance and m.acceptable(start) and m.acceptable(run) and
              set(holds)<=closed.keys() and not set(holds)&opened.keys() and len(d.calls)==before+1)
        results.check(group+" end-to-end recovery",key,ok,start=start["decision"],run=run["decision"])
    else:
        results.check(group+" end-to-end recovery",key,False,reason="no retained disposition target")


def seed_failure(d, scope):
    """Independent input for the consumer tests, even on a head that fails to produce records."""
    ledger = d.args.custody/"hp-02-arms"
    directory, = ledger.glob("holds-*")
    previous = sorted(directory.glob("*.json"))[-1]
    seq = 1 if scope=="queue" else int(previous.name.split("-")[0])+1
    rec = dict(source="observation",error_class="OSError",attempt_time=T+2,ledger_sequence=seq)
    digest = m.digest(wire.canonical(rec))
    hold = dict(id=m.digest(wire.canonical([scope,wire.position(d),seq,digest])),decision=UNKNOWN,
                fact="failed-read",detail="synthetic missing evidence",observed_at=T+2,
                source_digest=digest,ledger_sequence=seq,failed_read=rec)
    if scope=="queue":
        queue_sha,queue_seq = wire.position(d)
        hold.update(queue_sha=queue_sha,queue_seq=queue_seq)
        path=wire.queue_file(d)
        path.parent.mkdir(parents=True,exist_ok=True)
        event=dict(queue_sha=queue_sha,queue_seq=queue_seq,holds=[hold],clears=[])
    else:
        issue_id=directory.name.removeprefix("holds-")
        event=dict(schema="hp-02.hold-event.v1",issue_id=issue_id,previous=m.digest(previous.read_bytes()),
                   recorded_at=T+2,sources={},holds=[hold],clears=[])
        data=wire.canonical(event)+b"\n"
        path=directory/f"{seq:08d}-{m.digest(data)}.json"
    path.write_bytes(wire.canonical(event)+b"\n")
    return hold["id"]


def reader_trial(d, scope, action, results):
    prepare(d,"Run")
    hid = seed_failure(d,scope)
    hold = d.ledger()[0][hid]
    assert failed_record(hold,T+2,"observation-io")
    now=T+4
    row=d.row("Run",now)
    want=action in {"valid","same-tick"}
    if action != "no-proof":
        variant={"wrong-id":"wrong-hold","wrong-digest":"wrong-source"}.get(action,action)
        row["hold_dispositions"]=m.proof_rows(d,{hid:hold},now,variant,
                                               authority_at=T+2 if action=="same-tick" else now)
        if action in {"wrong-queue","wrong-position","wrong-error-digest"}:
            bound=dict(row["hold_dispositions"][0])
            bound["authority"]={k:v for k,v in bound["authority"].items() if k!="commit"}
            if action=="wrong-error-digest":
                changed={**hold["failed_read"],"error_class":"ValueError"}
                bound["source_digest"]=m.digest(wire.canonical(changed))
            else:
                bound["queue_sha" if action=="wrong-queue" else "queue_seq"]=("0"*64 if action=="wrong-queue" else 3)
            row["hold_dispositions"]=[publish(d,"hp-02-hold-disposition",bound,now)]
    step=d.call("Run",now,row)
    opened,closed,_=d.ledger()
    ok=(m.acceptable(step) and len(d.calls)==1 and hid in closed and hid not in opened if want
        else m.refused(step) and not d.calls and hid in opened)
    if not want:
        replay = d.call("Run",now+1)
        ok = ok and m.refused(replay) and not d.calls and hid in d.ledger()[0]
    results.check(("Q2 queue" if scope=="queue" else "Q3 issue")+" seeded consumer",
                  action,ok,want="clear" if want else "hold",got=step["decision"],launches=len(d.calls),
                  retained=hid in opened,cleared=hid in closed)


def unrelated_position(d, dimension, results):
    prepare(d,"Run")
    seed_failure(d,"queue")
    own=wire.queue_file(d)
    event=json.loads(own.read_bytes())
    sha, seq=wire.position(d)
    # A synthetic hold only on another key must leave this clear position eligible.
    if dimension=="queue":
        sha="0"*64
    else:
        seq+=1
    event.update(queue_sha=sha,queue_seq=seq)
    event["holds"][0].update(queue_sha=sha,queue_seq=seq)
    own.unlink()
    m.write(own.parent/f"{sha}-{seq}.json",event)
    step=d.call("Run",T+4)
    results.check("Q2 key isolation",dimension,m.acceptable(step) and len(d.calls)==1,got=step["decision"])


def run(checkout, stream):
    results=m.Results(stream)
    m.DRAFTS=checkout/m.REL
    m.ITEMS=json.loads((m.DRAFTS/"hp-02/items.json").read_bytes())
    with tempfile.TemporaryDirectory(prefix="hp02-rulings-") as tmp:
        root=Path(tmp)
        archive=m.DRAFTS/"hp-02/fixtures/hp02-occupancy-fixture.zip"
        assert m.digest(archive.read_bytes())==m.M["fixture_sha256"][archive.name]
        with ZipFile(archive) as bundle:
            bundle.extractall(root/"seat")
        m.PIN=root/"seat/tmp/pin"
        sys.path.insert(0,str(m.PIN))
        m.hp=m.load_gate()
        sys.addaudithook(m.native_guard)
        def check(fn,*args):
            m.isolated(root,1,T,fn,*args,results)
        for origin,kind in m.product(m.M["origins"],("ordinary","wrong-digest","missing-evidence","non-lead",
                                                     "wrong-look","unpublished","forged","still-ran","valid")):
            check(execution,origin,kind)
        for case in rules["Q3"]["order_cases"]:
            check(sequence,case)
        for name,origin,variant,route in m.product([*rules["Q2"]["faults"],"ac-error","observation-io"],
                                                  m.M["origins"],m.M["clear_reads"],m.M["retry_paths"]):
            if name=="ac-error" and origin=="Run":
                continue  # The live AC reader is called at FinalRun on this route.
            check(failure_history,origin,name,variant,route)
        for scope in ("issue","queue"):
            variants=["no-proof","wrong-id","wrong-digest","wrong-error-digest","fabricated-authority",
                      "wrong-role","unpublished-payload","older-sequence","equal-sequence","missing-sequence",
                      "same-tick","valid"]
            if scope=="queue":
                variants+=["wrong-queue","wrong-position"]
            for action in variants:
                check(reader_trial,scope,action)
        for dimension in ("queue","sequence"):
            check(unrelated_position,dimension)
        results.check("synthetic isolation","rulings",not m.NATIVE,attempts=m.NATIVE)
    return results


class FrozenRulings(unittest.TestCase):
    def test_authority_and_recovery(self):
        out=subprocess.run([sys.executable,"-IB",__file__],capture_output=True,text=True)
        self.assertEqual(out.returncode,0,out.stdout+out.stderr)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--checkout",type=Path,default=HERE.parent)
    p.add_argument("--results",type=Path)
    args=p.parse_args()
    with ExitStack() as files:
        out=files.enter_context(gzip.open(args.results,"wt")) if args.results else None
        summary=run(args.checkout.resolve(),out)
    print(json.dumps(summary.count,sort_keys=True,indent=2))
    sys.exit(int(any(row["fail"] for row in summary.count.values())))
