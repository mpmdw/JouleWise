"""Frozen hp-02 class acceptance. Standard-library only; see DELTA.md for replay."""
import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack, redirect_stdout
from copy import copy, deepcopy
from datetime import datetime, timedelta
from hashlib import sha256
from itertools import product
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zipfile import ZipFile
from zoneinfo import ZoneInfo
import gzip
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import unittest

DATA = Path(__file__).resolve().with_name("hp02_gate_machine")
M = json.loads((DATA / "GATE-MACHINE.json").read_bytes())
spec_records = importlib.util.spec_from_file_location("hp02_fixture_records", DATA / "records.py")
records = importlib.util.module_from_spec(spec_records)
spec_records.loader.exec_module(records)
SEED = json.loads((DATA / "clear.json").read_bytes())
REL = Path("docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203")
ZONE = ZoneInfo("America/Los_Angeles")
DAY = datetime(2026, 11, 21, tzinfo=ZONE)
BASE = int(DAY.timestamp()) + 14 * 3600
PASS = {"ELIGIBLE", "ELIGIBLE_WITH_COPY_DEBT"}
SECTIONS = "look hp01_dates latest_close history safety stops copy priority calendar timing".split()
BINDINGS = "span piece attempt legs pin kit_sha queue predecessor".split()
NATIVE = []


def digest(value):
    return sha256(value).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True))


def native_guard(event, args):
    if event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.fork", "socket.connect"}:
        NATIVE.append(event)
        raise AssertionError(f"unexpected external operation {event}")


class Results:
    def __init__(self, stream):
        self.stream = stream
        self.count = defaultdict(Counter)

    def check(self, group, key, ok, **details):
        self.count[group]["pass" if ok else "fail"] += 1
        if self.stream:
            self.stream.write(json.dumps(dict(group=group, key=key, passed=bool(ok), **details)) + "\n")


def day_at(epoch):
    return datetime.fromtimestamp(epoch, ZONE).date()


def midnight(day):
    return int(datetime.combine(day, datetime.min.time(), ZONE).timestamp())


def close(row, name, end, sha):
    row["latest_close"].update(record=name, ended_epoch_s=end, receipt_sha256=sha)
    row["safety"].update(close_record=name, close_sha256=sha)
    row["copy"]["predecessor"] = name


def ranked(obs, rung):
    return next(entry for entry in obs["priority"]["entries"] if entry["rung"] == rung)


class Desk:
    """Disk is real temporary custody. Stub only machine, source-provenance and launcher I/O."""
    def __init__(self, root, span=1, anchor=BASE):
        self.root, self.anchor = root, anchor
        self.items = deepcopy(ITEMS)
        self.item = self.items[span - 1]
        self.now = anchor
        kit = DRAFTS / "hp-02/cl-hp-02.json"
        self.queue = (kit.parent / "queue-b.json").read_bytes()
        self.args = SimpleNamespace(repo=PIN, kit=kit, span=self.item["span"], phase="Start",
            queue=root / "queue", issue=root / "issue", observation=root / "obs",
            output=root / "synthetic-output", custody=root / "custody", magistrate_pid=1000)
        self.args.queue_hold_root = self.args.custody / "hp02-holds"
        self.issue = deepcopy(SEED["issue"])
        self.issue.update(issued_epoch_s=anchor-86400, check_deadline_epoch_s=anchor+86400)
        self.reset_binding()
        self.calls = []
        self.after_claim = False
        self.receipt_section = None
        self.effect = lambda *args: 0
        self.during_claim = None
        self.authorities = {}
        self.args.queue.write_bytes(self.queue)
        self.io = ExitStack()

    def reset_binding(self):
        self.item["queue"]["sha256"] = digest(self.queue)
        self.issue["binding"] = {k: deepcopy(self.item[k]) for k in BINDINGS}
        self.publish(self.issue["status"])
        write(self.root / "items.json", self.items)
        self.args.queue.write_bytes(self.queue)

    def publish(self, status, *, fresh=False):
        self.issue["status"] = status
        if fresh:
            self.issue["check_target"] += " (republished)"
        write(self.args.issue, self.issue)
        self.args.issue_sha = digest(self.args.issue.read_bytes())

    def __enter__(self):
        from joulewise.align.apple import powermode
        for obj, name, replacement in [
            (hp, "HP", self.root), (hp, "assert_source_bindings", lambda *a: self.queue),
            (hp, "runtime_files", lambda *a, **k: None), (hp, "check_agent_census", lambda *a: None),
            (powermode, "observe_ac_powermode", lambda: 0), (hp.time, "time", lambda: self.now),
            (hp.subprocess, "call", self.launched), (hp, "trusted_run_state", self.trusted),
        ]:
            self.io.enter_context(patch.object(obj, name, replacement))
        original = hp.write_exclusive
        def write_claim(path, row):
            original(path, row)
            self.after_claim = True
            if self.during_claim:
                self.during_claim()
        self.io.enter_context(patch.object(hp, "write_exclusive", write_claim))
        return self

    def __exit__(self, *exc):
        self.io.close()

    def launched(self, argv, **kwargs):
        assert self.args.phase=="Run", "launcher side effect outside Run"
        assert argv[2:4] == ["scripts/launch_cadence_span.py", "launch"]
        self.calls.append((self.now, self.args.issue_sha))
        return self.effect()

    def trusted(self, repo, commit):
        if commit not in self.authorities:
            raise ValueError("unknown synthetic published-main commit")
        return self.authorities[commit]

    def row(self, phase, sampled, variant="resampled-same-source"):
        obs = deepcopy(SEED["observation"])
        obs["issue_record"] = self.issue["record"]
        day = day_at(sampled)
        obs.update(phase=phase, observed_epoch_s=sampled, valid_through_epoch_s=sampled+7200,
                   binding=deepcopy(self.issue["binding"]))
        obs["priority"]["date"] = day.isoformat()
        for section in SECTIONS:
            obs[section]["sampled_at"] = sampled
        for entry in obs["priority"]["entries"]:
            entry["start_windows"] = []
        ranked(obs, "first-stability")["completion"]["t0_date"] = day.isoformat()
        obs["look"]["checked_through"] = sampled
        end = self.anchor - 1200
        close(obs, "fixture-close-17", end, "a"*64)
        if self.item["predecessor"]:
            prior = self.items[self.item["piece"]-2]
            for earlier in self.items[:self.item["piece"]-1]:
                obs["history"]["legs"].update(dict.fromkeys(earlier["legs"], "spent"))
            obs["history"]["prior_check"] = dict(record="preceding HP Check", by="fixture",
                span=prior["span"], kit_sha256=prior["kit_sha"], attempt=1, legs=prior["legs"],
                host=obs["host"], ended_epoch_s=end-100, status="clean", receipt_sha256="b"*64,
                fence_gone=True, restore_proven=True)
        obs["timing"]["post_last_cap_max_s"] = 100-10-12*(len(self.item["legs"])+2)
        if variant == "replacement-source":
            for section in SECTIONS:
                if section != "latest_close":
                    obs[section]["record"] += " renewed"
            # Use a newer genuine close at Start/Run. Issue still names the issued close.
            if phase != "Issue" or self.issue["latest_close_at_issue"]=="fixture-close-19":
                close(obs, "fixture-close-19", end+5, "f"*64)
            if self.item["predecessor"]:
                prior=obs["history"]["prior_check"]
                prior.update(record="independent successor Check", receipt_sha256="d"*64)
        if self.receipt_section and variant in ("same-receipt-flap","replacement-source"):
            source=obs[self.receipt_section]
            if self.receipt_section!="latest_close":
                source["receipt_sha256"]=("c" if variant=="same-receipt-flap" else "e")*64
        if variant == "clear-with-copy-debt":
            obs["copy"].update(status="unverified", debt_record="synthetic debt")
        return obs

    def call(self, phase, at, row=None):
        self.now, self.args.phase, self.after_claim = at, phase, False
        write(self.args.observation, self.row(phase, at) if row is None else row)
        out = io.StringIO()
        with redirect_stdout(out):
            try:
                rc = hp.run_gate(self.args)
            except Exception as exc:
                return {"decision":"ESCAPED_EXCEPTION", "detail":repr(exc), "rc":None}
        try:
            return {**json.loads(out.getvalue()), "rc":rc}
        except (TypeError, ValueError):
            return {"decision":"INVALID_RESPONSE", "detail":out.getvalue(), "rc":rc}

    def ledger(self):
        return records.read_custody(self)


def set_field(obj, dotted, value):
    fields = dotted.split(".")
    for part in fields[:-1]:
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    obj[fields[-1]] = deepcopy(value)


def counted(name, windows, trans=0):
    return dict(record=name, by="fixture desk", span=name, pin="synthetic counted pin",
                date=day_at(windows[0][0]).isoformat(), windows=windows, through_transition_s=trans)


def stamp(epoch):
    return datetime.fromtimestamp(epoch, ZONE).isoformat()


def scenario(d, fact, phase, at, stack):
    """Produce the adverse input. Return a callable for final-read-only changes."""
    from joulewise.align.apple import powermode
    from scripts import launch_cadence_span as launcher
    from joulewise.cadence.legs import PlanError
    edit = fact["edit"]
    ep = "Run" if phase == "FinalRun" else phase
    row = d.row(ep, at)
    name = fact["id"]
    for key, value in edit.get("set", {}).items():
        set_field(row, key, value)
    if "rank" in edit:
        entry = ranked(row, edit["rank"])
        entry.update(status="eligible", start_windows=[[midnight(day_at(at)),midnight(day_at(at)+timedelta(days=1))-1]])
        if edit["rank"] == "first-stability":
            entry.pop("basis")
            entry.pop("completion")
    if name == "ran-further":
        row["look"]["status"] = "ran"
        ranked(row,"further-stability")["status"] = "eligible"
    if name == "failed-recovery":
        cl = row["latest_close"]
        cl.update(restore_status="unproven",recovery=dict(record="failed recovery", by="fixture",
            same_close=cl["record"], safe_route_proven=True, result="failed", residual_refusal="open"))
    if name == "dated":
        row["calendar"]["starts"] = [counted("A", [[at+600, at+900]])]
    if name == "fence-budget":
        row["timing"]["outer_clear_max_s"] = 3000
    if name == "unsafe-predecessor":
        row["history"]["prior_check"]["status"] = "dirty"
    if name == "receipt-flap":
        # Same digest, changed immutable receipt bytes, both snapshots individually pass.
        row["latest_close"]["groups"][0]["group_id"] += "-changed"
    if name in {"watcher-runway","admission-runway"}:
        if name.startswith("watcher"):
            row["watcher"] = dict(record="synthetic watcher",by="fixture",sampled_at=at,expires_epoch_s=at+350)
        else:
            row["valid_through_epoch_s"] = at+350
    if name == "run-prepublication-sample":
        row["safety"]["sampled_at"] = d.anchor
    if d.receipt_section and isinstance(row.get(d.receipt_section),dict) and d.receipt_section!="latest_close":
        row[d.receipt_section]["receipt_sha256"]="c"*64
    def install():
        if name in {"existing-claim","later-claim"}:
            ledger=d.args.custody/"hp-02-arms"
            ledger.mkdir(parents=True,exist_ok=True)
            span="hp-02-s02" if name=="later-claim" else d.item["span"]
            marker=ledger/f"{d.item['kit_sha']}-{span}-a1.json"
            assert not marker.exists()
            write(marker,{"record":"synthetic competing claim"})
            stack.callback(marker.unlink,missing_ok=True)
        if name=="source-io":
            stack.enter_context(patch.object(hp,"assert_source_bindings",side_effect=OSError("synthetic source I/O")))
        if name=="missing-issue-bytes":
            read_issue=Path.read_bytes
            def missing_issue(path):
                if path==d.args.issue:
                    raise FileNotFoundError("synthetic missing issue file")
                return read_issue(path)
            stack.enter_context(patch.object(Path,"read_bytes",missing_issue))
        if name=="missing-start":
            stack.enter_context(patch.object(hp,"read_published_start",side_effect=FileNotFoundError("missing Start")))
        if name in {"mode", "mode-error"}:
            def mode():
                if name == "mode-error":
                    raise OSError("synthetic unavailable AC read")
                return 2
            stack.enter_context(patch.object(powermode, "observe_ac_powermode",mode))
        if name == "census-error":
            stack.enter_context(patch.object(hp,"check_agent_census",side_effect=ValueError("synthetic census error")))
        if name == "binding":
            d.args.queue.write_bytes(d.queue+b" ")
        if name in {"input-io","bad-json"}:
            read = Path.read_bytes
            def observation_bytes(p):
                if p == d.args.observation:
                    if name == "input-io":
                        raise OSError("synthetic observation I/O error")
                    return b"{invalid"
                return read(p)
            stack.enter_context(patch.object(Path,"read_bytes",observation_bytes))
        if name == "pin-refusal":
            stack.enter_context(patch.object(launcher,"cadence_plan",side_effect=PlanError(["span meets a batch blackout"])))
        if name == "invalid-start-seal":
            read = hp.read_receipt_file
            def bad_seal(path):
                data = read(path)
                return b"{}" if path.name.endswith(".published.json") else data
            stack.enter_context(patch.object(hp,"read_receipt_file",bad_seal))
        if phase == "FinalRun":
            write(d.args.observation,row)
    return row, install


def set_limit(d, name, epoch):
    if name in {"queue-expired", "queue-runway"}:
        q = json.loads(d.queue)
        q["expires_at"] = stamp(epoch)
        d.queue = json.dumps(q).encode()
    if name == "item-runway":
        d.item["expires_epoch_s"] = epoch
    if name == "issue-runway":
        d.issue["expires_epoch_s"] = epoch
    d.reset_binding()


def proof_rows(d, holds, at, variant, role="lead", *, sequence_delta=1, authority_at=None):
    rows, blocks = [], []
    number = 901
    # Sequence is part of the exact payload published in the synthetic authority item.
    last_sequence = max(h["ledger_sequence"] for h in holds.values())
    for hold in holds.values():
        row = dict(schema="hp-02.hold-disposition.v1",action="clear",
                   source_digest=hold["source_digest"],hold_id=hold["id"],
                   authority=dict(role=role,run_state_item=number))
        if "issue_id" in hold:
            row["issue_id"] = hold["issue_id"]
        for v, k in [("wrong-hold","hold_id"),("wrong-issue","issue_id"),("wrong-source","source_digest")]:
            if v == variant:
                row[k] = "0"*64
        if variant != "missing-sequence" and sequence_delta is not None:
            if variant in {"older-sequence", "equal-sequence"}:
                row["ledger_sequence"] = hold["ledger_sequence"] - int(variant == "older-sequence")
            else:
                row["ledger_sequence"] = last_sequence + sequence_delta
        if "queue_sha" in hold:
            row.update(queue_sha=hold["queue_sha"], queue_seq=hold["queue_seq"])
        blocks.append(deepcopy(row))
        rows.append(row)
    when = at if authority_at is None else authority_at
    owner = "builder" if variant=="wrong-role" else role
    item = dict(schema="joulewise.run_state_item.v1",number=number,issued_epoch_s=when,owner=owner,status="ISSUED")
    fence = chr(96)*3
    def fenced(kind,data):
        return f"{fence}{kind}\n{json.dumps(data)}\n{fence}\n"
    doc = f"{number}. **Synthetic disposition**\n\n"+fenced("item",item)
    if variant!="unpublished-payload":
        doc+="".join(fenced("hp-02-hold-disposition",r) for r in blocks)
    commit = digest(doc.encode())[:40]
    if variant!="fabricated-authority":
        d.authorities[commit] = doc
    for row in rows:
        row["authority"]["commit"] = commit
    return rows


def refused(result):
    return result["rc"] not in (0,None) and result["decision"] not in PASS|{"INVALID_RESPONSE","ESCAPED_EXCEPTION"}


def acceptable(result):
    return result["rc"] == 0 and result["decision"] in PASS


def at_stage_time(name):
    # For the selected default plan, whole-work end just precedes 02:00 tomorrow.
    if name == "replan":
        return midnight(day_at(BASE)+timedelta(days=1))+7200-16650-30
    return BASE


def first(d, fact, origin):
    name = fact["id"]
    at = d.anchor+2
    if origin == "Issue":
        d.publish("PROPOSED")
    if name in {"queue-expired","queue-runway","issue-runway","item-runway"}:
        set_limit(d,name,at+(0 if name=="queue-expired" else 350))
    if origin in {"Run","FinalRun"}:
        # Start itself does not apply the 600-second Run margin.
        res = d.call("Start",d.anchor)
        if not acceptable(res):
            raise AssertionError(("Start setup",name,origin,res))
    with ExitStack() as stack:
        row, install = scenario(d,fact,origin,at,stack)
        if origin=="FinalRun":
            d.during_claim = install
            initial = d.row("Run",at)
            result = d.call("Run",at,initial)
            d.during_claim = None
        else:
            install()
            result = d.call(origin,at,row)
    d.args.queue.write_bytes(d.queue)
    return result


def retry(d, fact, origin, variant, path, at):
    ep = "Run" if origin=="FinalRun" else origin
    rows = []
    sampled = d.anchor+1 if variant=="saved-clear" else at
    def visit(phase):
        nonlocal sampled
        reading = d.row(phase,sampled,variant)
        rows.append(d.call(phase,at,reading))
    if fact["id"] in {"queue-expired","queue-runway","issue-runway","item-runway"}:
        set_limit(d,fact["id"],at+7200)
    if path=="same-issue" and ep=="Issue":
        visit("Issue")
        # Exercise Start/Run even when the proposal was refused.
    if path=="fresh-Start" or d.issue["status"]=="PROPOSED":
        d.publish("ISSUED",fresh=path=="fresh-Start")
    started = d.args.custody/"hp-02-arms"/f"start-{d.args.issue_sha}.v4.json"
    if path=="fresh-Start" or not started.exists() or (path=="same-issue" and ep=="Start"):
        visit("Start")
        at+=1
        # Give Run an independently fresh sample after a newly published Start.
        sampled=at
    if path=="fresh-Run":
        # Reload the actual module and rebuild a new invocation from durable bytes.
        # This makes process-local hold caches insufficient for acceptance.
        global hp
        old=hp
        hp=load_gate()
        fresh=copy(d)
        fresh.io=ExitStack()
        fresh.args=copy(d.args)
        fresh.args.issue_sha=digest(fresh.args.issue.read_bytes())
        try:
            with fresh:
                rows.append(fresh.call("Run",at,fresh.row("Run",sampled,variant)))
        finally:
            hp=old
    else:
        visit("Run")
    return rows


def history_case(d, fact, origin, variant, route, result):
    name = fact["id"]
    key = [name,origin,variant,route]
    if variant=="same-receipt-flap":
        mapped={"ran-further":"look","dated":"calendar","fence-budget":"timing",
                "unsafe-predecessor":"history","failed-recovery":"latest_close"}
        fields=fact["edit"].get("set",{})
        section=next(iter(fields),"").split(".")[0]
        if "rank" in fact["edit"]:
            section="priority"
        d.receipt_section=section if section in SECTIONS else mapped.get(name)
    bad = first(d,fact,origin)
    hits = len(d.calls)
    opened,_,orig_bytes = d.ledger()
    valid_ids = bool(opened) and all(
        re.fullmatch("[0-9a-f]{64}",h["source_digest"]) and h["id"] and h["fact"]
        and h["observed_at"] == d.anchor+2 for h in opened.values())
    # Preserve the distinction between the refusal on the command and the semantic hold.
    expected_decisions={fact["wire"]}
    if name=="ran-further":
        expected_decisions.add("NOT_ADMITTED")
    # An alias may surface on the command while the ledger classifies a failed read.
    if fact["wire"] in {"WAIT_BINDING","WAIT_EVIDENCE"}:
        expected_decisions.add("HOLD_UNKNOWN")
    unknown_ok=any(h["decision"] in expected_decisions for h in opened.values())
    result.check("observable hold",key,refused(bad) and hits==0 and valid_ids and unknown_ok,
                 first=bad["decision"],detail=bad.get("detail"),holds=[h["decision"] for h in opened.values()])
    if fact["wire"] == "HOLD_UNKNOWN":
        failures = [h for h in opened.values() if h.get("decision") == "HOLD_UNKNOWN"]
        def authenticated_error(hold):
            record = hold.get("failed_read")
            return (isinstance(record, dict) and bool(record.get("source")) and bool(record.get("error_class"))
                    and record.get("attempt_time") == d.anchor+2 and type(record.get("ledger_sequence")) is int
                    and record["ledger_sequence"] == hold.get("ledger_sequence")
                    and digest(records.canonical(record)) == hold["source_digest"])
        result.check("Q3 canonical record across unknown inputs", key,
                     bool(failures) and all(authenticated_error(h) for h in failures))
    if origin!="FinalRun" and fact["wire"]!="HOLD_UNKNOWN":
        allowed = {fact["wire"]}
        if name=="ran-further":
            allowed.add("NOT_ADMITTED")
        if name=="receipt-flap":
            allowed.add("WAIT_EVIDENCE")
        result.check("initial refusal",key,bad["decision"] in allowed and refused(bad),got=bad["decision"])
    after = retry(d,fact,origin,variant,route,d.anchor+(240 if name=="replan" else 5))
    tail,_,new_bytes = d.ledger()
    target=next(row["to"] for row in M["transitions"] if row["from"]=="held" and row["event"]=="clear_read")
    result.check("retry inhibits launch",key,target=="held" and hits==len(d.calls)==0 and all(refused(r) for r in after),
                 first=bad["decision"],retry=[r["decision"] for r in after],launches=len(d.calls))
    result.check("append-only retention",key,bool(opened) and opened.keys()<=tail.keys() and
                 orig_bytes.items()<=new_bytes.items(),open_before=len(opened),open_after=len(tail))
    # On each path also prove that authority is checked and closes exactly the retained IDs.
    if not opened or not tail or d.calls:
        result.check("clearance after retry",key,False,reason="no reachable held precondition")
        return
    at=d.anchor+1000
    d.publish("ISSUED",fresh=True)
    clean=d.row("Start",at,"replacement-source")
    clean["hold_dispositions"]=proof_rows(d,tail,at,"valid")
    step=d.call("Start",at,clean)
    left,closed,kept=d.ledger()
    ok=tail.keys()<=closed.keys() and new_bytes.items()<=kept.items() and not d.calls
    if fact.get("execution_bar"):
        follow = d.call("Run",at+1,d.row("Run",at+1,"replacement-source"))
        ok = refused(step) and refused(follow) and not d.calls and new_bytes.items()<=kept.items()
    elif not fact.get("sticky"):
        follow=d.call("Run",at+1,d.row("Run",at+1,"replacement-source"))
        ok=ok and acceptable(step) and acceptable(follow) and len(d.calls)==1
    elif fact.get("sticky"):
        ok=ok and refused(step)
    result.check("clearance after retry",key,ok,got=step["decision"],remaining=len(left))


def clearance_case(d, fact, origin, variant, result):
    key = [fact["id"],origin]
    bad = first(d,fact,origin)
    holds,_,orig_bytes = d.ledger()
    if not holds or not refused(bad) or d.calls:
        result.check("typed disposition",key+[variant],False,reason="no usable initial hold",
                     first=bad["decision"])
        return
    name = fact["id"]
    verify_phase="Run" if origin in {"Run","FinalRun"} else origin
    if name in {"queue-expired","queue-runway","issue-runway","item-runway"}:
        verify_phase="Start" if origin!="Issue" else "Issue"
    if verify_phase=="Issue":
        d.issue["latest_close_at_issue"]="fixture-close-19"
        d.publish("PROPOSED")
    if verify_phase=="Start":
        d.publish("ISSUED",fresh=True)
    at = d.anchor+(240 if name=="replan" else 10)
    if name in {"queue-expired","queue-runway","issue-runway","item-runway"}:
        set_limit(d,name,at+7200)
    row = d.row(verify_phase,at,"replacement-source")
    # Observe a separately bound, genuinely new clean close after an adverse one.
    row["hold_dispositions"] = proof_rows(d,holds,at,variant)
    res = d.call(verify_phase,at,row)
    remaining,closed,new_bytes = d.ledger()
    if variant!="valid":
        ok = refused(res) and holds.keys()<=remaining.keys() and orig_bytes.items()<=new_bytes.items() and not d.calls
    else:
        ok = holds.keys()<=closed.keys() and orig_bytes.items()<=new_bytes.items()
        if fact.get("execution_bar"):
            ok=refused(res) and not d.calls and orig_bytes.items()<=new_bytes.items()
            steps=retry(d,fact,origin,"replacement-source","fresh-Run",at+5)
            ok=ok and all(refused(step) for step in steps) and not d.calls
        elif fact.get("sticky"):
            # Positive spent/halt facts have an independent cross-issue bar.
            ok = ok and refused(res) and not d.calls
        else:
            ok=ok and acceptable(res)
            if verify_phase=="Issue":
                d.publish("ISSUED")
                start=d.call("Start",at+1,d.row("Start",at+1,"replacement-source"))
                ok=ok and acceptable(start)
            if verify_phase!="Run":
                run=d.call("Run",at+2,d.row("Run",at+2,"replacement-source"))
                ok=ok and acceptable(run)
            ok=ok and len(d.calls)==1
    result.check("typed disposition",key+[variant],ok,got=res["decision"],first=bad["decision"],
                 open=len(remaining),closed=len(closed),launches=len(d.calls))


def dated_edges(calendar, fence, lag):
    """Backward feasible sets, including split windows and every remaining row."""
    limit = None
    edges = []
    for row in reversed(calendar["starts"]):
        cap = midnight(datetime.fromisoformat(row["date"]).date()+timedelta(days=1))-1
        if limit is not None:
            cap = min(cap, math.floor(limit-row["through_transition_s"]))
        choices = [min(cap,hi) for lo,hi in row["windows"] if lo<=cap]
        if not choices:
            return edges, None
        limit = max(choices)
        raw = limit-fence-calendar["post_fence_transfer_s"]
        edges.extend([(raw,"dated raw "+row["span"]), (raw-lag,"dated startup "+row["span"])])
    return edges, limit


def pin_clock(item, obs, t):
    """Independent forward schedule for the addendum's cap-paced operating profile."""
    day = day_at(t)
    slots = {}
    profile=M["guard"]["operating_profile"]
    def minutes(text):
        hh,mm=map(int,text.split(":"))
        return 60*hh+mm
    specs=dict(zip(("default","alternate"),profile["plan_arguments"]))
    specs["os"]=profile["implicit_soak_window"]
    for key,window in specs.items():
        lo,hi=map(minutes,window.split("-"))
        slots[key] = [(midnight(day+timedelta(days=shift))+60*lo,
                       midnight(day+timedelta(days=shift))+60*hi) for shift in (-1,0,1,2)]
    timing = obs["timing"]
    lag = timing["runner_start_max_s"]
    attempts = len(item["legs"])+profile["redo_quota"]
    work = profile["fixed_s"]+profile["soak_s"]+attempts*profile["leg_s"]
    fence = work+profile["fence_extra_s"]
    edges = []
    def window_edges(names,offset,duration,kind):
        for name in names:
            for lo,hi in slots[name]:
                begin = lo-offset-duration
                edges.append((begin,kind))
                if duration:
                    edges.append((math.nextafter(begin,math.inf),kind))
                edges.append((hi-offset,kind))
    def overlap(at, duration, pairs):
        return any(at<hi and at+duration>lo for lo,hi in pairs)
    def release(at,duration,pairs):
        for lo,hi in sorted(pairs):
            if (at<hi and at+duration>lo) if duration else (lo<=at<hi):
                at=hi
        return at
    window_edges(slots,0,0,"pin raw")
    window_edges(["default","alternate"],0,work,"plan")
    window_edges(["default","alternate"],0,work+lag,"handoff")
    arg = next((a for a in ("default","alternate") if not overlap(t,work,slots[a])),None)
    if arg is None:
        return edges,"WAIT_PIN"
    if overlap(t,work+lag,slots[arg]):
        return edges,"WITHHOLD_REPLAN"
    sel = timing["selector_sample_max_s"]
    window_edges([arg,"os"],sel,1950,"soak")
    planned = t+sel
    start = release(planned,1950,slots[arg]+slots["os"])
    waited = start>planned
    cursor=start+timing["soak_dispatch_max_s"]+1950
    for attempt in range(attempts):
        cursor+=timing["pre_leg_max_s"]
        if not waited:
            window_edges([arg],cursor-t,0,f"leg {attempt+1}")
        begin=release(cursor,0,slots[arg])
        waited |= begin>cursor
        cursor=begin+timing["leg_wait_overshoot_max_s"]+2700
    end=cursor+timing["post_last_cap_max_s"]
    closed=end+timing["restore_and_close_max_s"]
    clear=closed+timing["outer_clear_max_s"]
    checks=[(end,fence-370,"work cutoff"),(closed,fence-190,"close cutoff"),(clear,fence,"clearance cutoff")]
    if waited:
        edges.extend((stage-budget,label) for stage,budget,label in checks)
    return edges,"ELIGIBLE" if all(stage<=t+budget for stage,budget,_ in checks) else "CEDE_FENCE"


def oracle(d, obs, t):
    item,issue,q=d.item,d.issue,json.loads(d.queue)
    lag=obs["timing"]["runner_start_max_s"]
    day=day_at(t)
    edges,expected=pin_clock(item,obs,t)
    edges.extend([(midnight(day),"midnight"),(midnight(day+timedelta(days=1)),"midnight"),
                  (issue["issued_epoch_s"],"issue time"),(obs["observed_epoch_s"],"sample time")])
    lo=midnight(datetime.fromisoformat(next(ent["not_before"] for ent in q["spans"]
                 if ent["span_id"]==item["span"])).date())
    edges.append((lo,"queue opening"))
    limits=[("queue",datetime.fromisoformat(q["expires_at"]).timestamp(),"NEED_FRESH_QUEUE"),
            ("admission",obs["valid_through_epoch_s"],"WAIT_EVIDENCE")]
    for name,obj,w in [("item",item,"WAIT_BINDING"),("issue",issue,"WAIT_BINDING"),
                       ("watcher",obs.get("watcher",{}),"WAIT_EVIDENCE")]:
        if obj.get("expires_epoch_s") is not None:
            limits.append((name,obj["expires_epoch_s"],w))
    for name,limit,_ in limits:
        edges.extend([(limit,name+" expiry"),(limit-600,name+" runway")])
        if lag:
            edges.extend([(limit-lag,name+" startup"),(math.nextafter(limit-600,math.inf),name+" runway")])
    def endpoints(windows,kind):
        for first,last in windows:
            edges.extend((e,kind) for e in (first-1,first,last,last+1))
    for entry in obs["priority"]["entries"]:
        if entry["rung"]!="further-stability":
            endpoints(entry["start_windows"],"competitor "+entry["rung"])
    for row in obs["calendar"]["starts"]:
        endpoints(row["windows"],"counted window "+row["span"])
    date_edges,latest=dated_edges(obs["calendar"],item["deadline_s"],lag)
    edges.extend(date_edges)
    if obs["copy"]["status"]!="verified":
        threshold=obs["latest_close"]["ended_epoch_s"]+600
        edges.append((threshold,"copy wait"))
        if t<threshold:
            expected="WAIT_COPY"
        elif expected=="ELIGIBLE":
            expected="ELIGIBLE_WITH_COPY_DEBT"
    if latest is not None and t+lag+item["deadline_s"]+obs["calendar"]["post_fence_transfer_s"]>latest:
        expected="CEDE_DATED"
    for entry,wire in zip(("ready-session","counted","first-stability","f2-inst-01","f2-inst-02","f2-inst-03"),
                          ("CEDE_READY","CEDE_COUNTED","CEDE_RANK_1","CEDE_INST_01","CEDE_INST_02","CEDE_INST_03")):
        if ranked(obs,entry)["status"]=="eligible":
            expected=wire
            break
    for _,limit,wire in reversed(limits):
        if limit-t<600 or t+lag>=limit:
            expected=wire
    if t<lo:
        expected="BEFORE_QUEUE"
    guards={label for edge,label in edges if t<edge<=t+120}
    return edges,guards,expected


def eval_run(d,obs,t):
    """Production Run assessment followed by its final dated-start check at bounded t0."""
    try:
        result,_,_ = hp.run_decision(d.args,d.item,d.issue,obs,d.queue,t)
        hp.check_dated(obs["calendar"],t+obs["timing"]["runner_start_max_s"],result["fence_s"])
        return result["decision"]
    except hp.Refusal as ex:
        if ex.decision=="WAIT_EVIDENCE" and str(ex).startswith("launch guard at "):
            return "CLOCK_WAIT"
        return ex.decision


def compare(wire,guards,underlying):
    if guards:
        return wire in {"CLOCK_WAIT","WAIT"}
    if underlying=="BEFORE_QUEUE":
        return wire in {"NEED_FRESH_QUEUE","WAIT","CLOCK_WAIT"}
    return wire==underlying


def timing_fixture(d, family, t, lag):
    row=d.row("Run",t)
    row["timing"]["runner_start_max_s"]=lag
    # Keep an identified, already completed close even for clocks before the anchor.
    finish=min(t-1200,d.anchor-1200)
    close(row,"fixture-close-17",finish,"a"*64)
    if row["history"]["prior_check"]:
        row["history"]["prior_check"]["ended_epoch_s"]=finish-100
    end=BASE+4800
    if family in {"queue","issue","item","watcher","admission"}:
        if family=="watcher":
            row["watcher"]=dict(record="finite watcher",by="fixture",sampled_at=t,expires_epoch_s=end)
        if family=="admission":
            row["valid_through_epoch_s"]=end
    if family=="calendar":
        # Three outstanding starts, split A window, positive transfer and distinct constraints.
        # Reverse placement must pick the earlier window after B and C bind the upper bound.
        first=BASE+d.item["deadline_s"]+3600
        row["calendar"].update(post_fence_transfer_s=83,starts=[
            counted("A",[[first-500,first],[first+1600,first+1800]],300),
            counted("B",[[first+100,first+321],[first+800,first+1200]],500),
            counted("C",[[first+600,first+1433]],0)])
    if family=="calendar-two-dates":
        today=BASE+d.item["deadline_s"]+1800
        tomorrow=today+86400
        row["calendar"].update(post_fence_transfer_s=71,starts=[
            counted("A",[[today-301,today]],1700),
            counted("B",[[tomorrow-300,tomorrow]],0)])
    if family=="one-start" or family=="remaining-half":
        last=BASE+d.item["deadline_s"]+4000
        name="A" if family=="one-start" else "B"
        row["calendar"].update(post_fence_transfer_s=0 if name=="A" else 600,
                               starts=[counted(name,[[last-300,last]],0)])
    if family.startswith("competitor "):
        rung=family.split()[1]
        entry=ranked(row,rung)
        datestr=day_at(t).isoformat()
        entry["start_windows"]=[[end,end+600],[end+1200,end+1500]]
        entry["status"]="eligible" if any(lo<=t<=hi for lo,hi in entry["start_windows"]) else "unavailable"
        if rung=="first-stability":
            entry.pop("completion",None)
            if entry["status"]=="eligible":
                entry.pop("basis",None)
            else:
                entry.update(basis="no-eligible-kit",entry_id="f2-stab-01..14",
                             eligibility_census=dict(record="pool",by="fixture",date=datestr,
                             pool="f2-stab-01..14",complete=True,eligible_kits=[]))
    if family=="copy":
        row["copy"].update(status="unverified",debt_record="bounded debt")
        close(row,"fixture-close-17",end-600,"a"*64)
    return row


def timing(d,family,lag,results):
    edge=BASE+4800
    if family in {"queue","item","issue"}:
        set_limit(d,family+"-runway",edge)
    def row(t):
        return timing_fixture(d,family,t,lag)
    seeds=[]
    if family=="pin":
        # Find all active branches: data-dependent downstream edges are constant in
        # each affine segment. Start at interval endpoints and iterate to closure.
        lo=midnight(day_at(BASE))
        hi=lo+86400
        work=[lo,lo+43200,hi-1]
        seen=set()
        while work:
            t=work.pop()
            if t in seen: continue
            seen.add(t)
            edges,_=pin_clock(d.item,row(t),t)
            for point,kind in edges:
                center=math.floor(point)
                if lo<=center<hi:
                    seeds.append((point,kind))
                    for x in (center-1,center,center+1):
                        if x not in seen: work.append(x)
        seeds.append((hi,"midnight"))
    else:
        edges,_,_=oracle(d,row(BASE),BASE)
        stems={"queue":("queue expiry","queue runway","queue startup"),"one-start":("dated ","counted window"),"remaining-half":("dated ","counted window"),
               "calendar":("dated ","counted window"),"calendar-two-dates":("dated ","counted window"),"copy":("copy wait",),
               "opening":("queue opening",)}.get(family,(family+" ",) if " " not in family else (family,))
        seeds=[(e,k) for e,k in edges if k.startswith(stems)]
    observed={}
    for boundary,kind in sorted(set(seeds)):
        # Preserve fractional half-open touch points. Both adjacent whole seconds
        # and the exact equality are sampled, including the start of the guard.
        for offset in range(-121,2):
            t=boundary+offset
            if t not in observed:
                sample=row(t)
                active,guards,raw=oracle(d,sample,t)
                wire=eval_run(d,sample,t)
                observed[t]=(wire,guards,raw,set(active))
            wire,guards,raw,active=observed[t]
            if family=="pin" and (boundary,kind) not in active:
                continue  # this selector does not move with t0 on this branch
            results.check("clock "+family,[d.item["span"],lag,kind,boundary,offset],
                          compare(wire,guards,raw),want="WAIT" if guards else raw,got=wire)


def controls(d, variant, path, result):
    origin="Issue"
    d.publish("PROPOSED")
    res=d.call("Issue",d.anchor)
    steps=retry(d,{"id":"control"},origin,variant,path,d.anchor+5)
    result.check("clear path controls",[variant,path],acceptable(res) and all(acceptable(s) for s in steps)
                 and len(d.calls)==1 and not d.ledger()[0],steps=[s["decision"] for s in steps])


def multiple(d,result):
    at=d.anchor
    res=d.call("Start",at)
    assert acceptable(res),res
    row=d.row("Run",at+1)
    row["look"].update(status="reserved")
    row["fence_clear"]=False
    bad=d.call("Run",at+1,row)
    held,_,_=d.ledger()
    result.check("multiple holds","two independent facts",refused(bad) and len(held)>=2 and not d.calls)
    if len(held)<2:
        for key in ("partial","reoccurrence","old proof","new proof"):
            result.check("multiple holds",key,False,reason="two usable hold IDs required")
        return
    first_id=next(iter(held))
    row=d.row("Run",at+2)
    old=proof_rows(d,{first_id:held[first_id]},at+2,"valid")
    row["hold_dispositions"]=old
    step=d.call("Run",at+2,row)
    remain,closed,_=d.ledger()
    result.check("multiple holds","partial",refused(step) and bool(remain) and first_id in closed and not d.calls)
    # Bring both facts back. A replay of the old authority cannot dispose a new observation.
    row=d.row("Run",at+3)
    row["look"]["status"]="reserved"
    row["fence_clear"]=False
    step=d.call("Run",at+3,row)
    still,_,_=d.ledger()
    result.check("multiple holds","reoccurrence",refused(step) and bool(set(still)-set(held)) and not d.calls)
    row=d.row("Run",at+4)
    row["hold_dispositions"]=old
    step=d.call("Run",at+4,row)
    result.check("multiple holds","old proof",refused(step) and d.ledger()[0].keys()==still.keys() and not d.calls)
    row=d.row("Run",at+5)
    row["hold_dispositions"]=proof_rows(d,still,at+5,"valid",role="magistrate")
    step=d.call("Run",at+5,row)
    result.check("multiple holds","new proof",acceptable(step) and len(d.calls)==1 and not d.ledger()[0])


def launch_terminal(d,style,result):
    assert acceptable(d.call("Start",BASE))
    def simulated():
        if style=="exception":
            raise OSError("synthetic ambiguous launcher exit")
        return 17
    d.effect=simulated
    first_result=d.call("Run",BASE+1)
    d.effect=lambda:0
    retry_result=d.call("Run",BASE+2)
    claims=list((d.args.custody/"hp-02-arms").glob("*-a1.json"))
    result.check("launcher terminal",style,len(d.calls)==1 and first_result["rc"] not in (0,None)
                 and refused(retry_result) and bool(claims),initial=first_result,retry=retry_result["decision"])


def read_last(d,result):
    from joulewise.align.apple import powermode
    assert acceptable(d.call("Start",BASE))
    active=[False]
    events=[]
    def audit(event,args):
        if active[0] and (event in {"os.rename","os.link","os.remove","os.mkdir","os.rmdir","os.truncate",
                                     "os.chmod","os.utime","os.symlink"} or
                event=="open" and args[2] & (os.O_WRONLY|os.O_RDWR|os.O_TRUNC|os.O_CREAT|os.O_APPEND)):
            events.append(event)
    sys.addaudithook(audit)
    def mode():
        events.append("mode")
        active[0]=True
        return 0
    def launch():
        active[0]=False
        events.append("launcher")
        return 0
    d.effect=launch
    with patch.object(powermode,"observe_ac_powermode",mode),patch.object(hp.time,"sleep",lambda x:events.append("sleep")):
        step=d.call("Run",BASE+1)
    active[0]=False
    result.check("final ordering","write/sleep interval",acceptable(step) and events==["mode","launcher"],trace=events)


def clock_route(d,kind,offset,result):
    # Use a published Start from an earlier clear clock, even for a refused Run.
    boundary=BASE+2400
    t=boundary+offset
    if kind=="opening":
        boundary=midnight(day_at(BASE))
        t=boundary+offset
        d.issue["issued_epoch_s"]=boundary-86400
        d.publish("ISSUED")
        first=d.call("Start",t)
        held=d.ledger()[0]
        if t<boundary:
            d.publish("ISSUED",fresh=True)
            good=d.call("Start",boundary+10)
            run=d.call("Run",boundary+11)
            ok=refused(first) and not held and acceptable(good) and acceptable(run) and len(d.calls)==1
        else:
            ok=acceptable(first) and not held
        result.check("clock retry", [kind,offset],ok,first=first["decision"])
        return
    assert acceptable(d.call("Start",BASE))
    def observed(at):
        row=d.row("Run",at)
        if kind=="calendar":
            last=boundary+d.item["deadline_s"]+60
            row["calendar"]["starts"]=[counted("A",[[last-600,last]],0)]
        elif kind=="guard":
            ranked(row,"f2-inst-03")["start_windows"]=[[boundary,boundary+600]]
            if boundary<=at<=boundary+600:
                ranked(row,"f2-inst-03")["status"]="eligible"
        elif kind=="watcher":
            row["watcher"]=dict(record="watcher",by="fixture",sampled_at=at,expires_epoch_s=boundary+600)
        return row
    row=observed(t)
    _,guards,raw=oracle(d,row,t)
    step=d.call("Run",t,row)
    held=d.ledger()[0]
    wire=clock_word(step)
    ok=compare(wire,guards,raw) and len(d.calls)==int(not guards and raw in PASS)
    if guards:
        # A later independently clear observation can launch with no disposition.
        next_at=boundary+800
        later=d.call("Run",next_at,d.row("Run",next_at))
        ok=ok and not held and acceptable(later) and len(d.calls)==1
    result.check("clock retry",[kind,offset],ok,first=step["decision"],holds=len(held),guards=sorted(guards))


def isolated(root,span,anchor,task,*args):
    with tempfile.TemporaryDirectory(dir=root) as directory, Desk(Path(directory),span,anchor) as d:
        task(d,*args)


def r2(d, offsets, result):
    ss,pub,rs,read=(BASE+n for n in offsets)
    # Delay publication by moving only the clock at the write. Store and verify real seals.
    original=hp.publish_new_file
    def delayed(path,data):
        if path.name.startswith("start-") and path.name.endswith(".v4.json"):
            d.now=pub
        return original(path,data)
    if pub<=read:
        with patch.object(hp,"publish_new_file",delayed):
            d.call("Start",min(ss,pub),d.row("Start",ss))
    trace=[]
    read_file=Path.read_bytes
    verify=hp.read_published_start
    def verified(*args):
        r=verify(*args)
        trace.append("Start")
        return r
    def sample(path):
        if path==d.args.observation:
            trace.append("sample")
        return read_file(path)
    with patch.object(Path,"read_bytes",sample), patch.object(hp,"read_published_start",verified):
        step=d.call("Run",read,d.row("Run",rs))
    allowed=ss<=pub<rs<=read
    pairs=(["Start","sample"]*(2 if allowed else 1)) if ss<=pub<=read else []
    ok=(acceptable(step) if allowed else refused(step)) and len(d.calls)==int(allowed) and trace==pairs
    result.check("R2 publication",list(offsets),ok,got=step["decision"],trace=trace)


def r3(d,field,value,result):
    for phase in ("Issue","Start","Run"):
        obs=d.row(phase,BASE)
        d.publish("PROPOSED" if phase=="Issue" else "ISSUED")
        r=ranked(obs,"first-stability")
        ref=r if field=="pool" else r["completion"]
        if value is None:
            ref.pop(field)
        else:
            ref[field]=value
            if field=="kit_id":
                r["entry_id"]=value
        answer=hp.decide(d.item,d.issue,obs,phase,BASE,d.args.kit,d.queue)
        result.check("R3 completion evidence",[field,value,phase],answer["decision"] not in PASS,
                     got=answer["decision"])


def margin(d,scope,remaining,lag,result):
    t=BASE+2
    if scope in {"queue","issue","item"}:
        set_limit(d,scope+"-runway",t+remaining)
    step=d.call("Start",BASE)
    assert acceptable(step),step
    row=d.row("Run",t)
    if scope=="watcher":
        row["watcher"]=dict(record="finite watcher",by="fixture",sampled_at=t,expires_epoch_s=t+remaining)
    if scope=="admission":
        row["valid_through_epoch_s"]=t+remaining
    row["timing"]["runner_start_max_s"]=lag
    launch_times=[]
    def enter():
        launch_times.append(d.now+lag)
        return 0
    d.effect=enter
    answer=d.call("Run",t,row)
    # Raw time is exclusive. R1's equality is inclusive only if the start cannot
    # move into the insufficient-runway branch. G1 independently covers both edges.
    allowed=remaining>=600 and remaining>lag and not (
        600<remaining<=720 or lag>0 and remaining-600<=lag)
    ok=(acceptable(answer) if allowed else refused(answer))
    ok=ok and len(d.calls)==int(allowed) and all(x<t+remaining for x in launch_times)
    result.check("R1 runway",[scope,remaining,lag],ok,got=answer["decision"],t0=launch_times)


def registry(d,lag,alternate,result):
    # Observe (without modifying) the guard sets actually used on the successful final path.
    t=BASE if not alternate else midnight(day_at(BASE))+23*3600
    assert acceptable(d.call("Start",t-1))
    row=d.row("Run",t)
    row["timing"]["runner_start_max_s"]=lag
    if not alternate:
        last=t+d.item["deadline_s"]+2100
        row["calendar"]["starts"]=[counted("A",[[last-500,last]],120),counted("B",[[last,last+300]],0)]
        row["calendar"]["post_fence_transfer_s"]=23
    seen=set()
    original=hp.check_guard_band
    def observe(edges,*args,**kwargs):
        seen.update(edges)
        return original(edges,*args,**kwargs)
    with patch.object(hp,"check_guard_band",observe):
        step=d.call("Run",t,row)
    assert acceptable(step) and len(d.calls)==1,(step,t)
    edges,_,_=oracle(d,row,t)
    edges.append((t+d.item["deadline_s"]-(d.item["worst_case_s"]+560),"launcher deadline"))
    # The pin computes daily epochs locally; only select today's and tomorrow's
    # event instances. The numeric observer never reads a candidate-derived expected edge.
    for edge,kind in sorted(set(edges)):
        if not midnight(day_at(t))<=edge<midnight(day_at(t)+timedelta(days=2)):
            continue
        key=[d.item["span"],lag,alternate,kind,edge]
        # Distinct requirements share a timestamp legitimately.
        result.check("boundary inventory",key,edge in seen)
        table={edge:"independent expected edge"} if edge in seen else {}
        for offset in range(-121,2):
            try:
                original(table,edge+offset)
            except hp.Refusal as ex:
                got=ex.decision
            else:
                got="PASS"
            correct=(got in {"WAIT","WAIT_EVIDENCE"}) if -120<=offset<0 else got=="PASS"
            result.check("isolated boundary guard",key+[offset],correct,
                         registered=edge in seen)
    # Issue time is normally in the past. Confirm its registration separately.
    result.check("boundary inventory",[d.item["span"],lag,alternate,"issue time",d.issue["issued_epoch_s"]],
                 d.issue["issued_epoch_s"] in seen)


def source_drift(d,result):
    code=(DRAFTS/"prepare_hp_items.py").read_text()
    wires=set(re.findall(r'["\']((?:ELIGIBLE|WAIT|CEDE|HOLD|WITHHOLD|NOT_ADMITTED|NEED_FRESH_QUEUE|SKIP_SPENT|SELECT_RANK|HALT_AND_PAGE|INELIGIBLE_DATE)[A-Z_0-9]*)["\']',code))
    result.check("vocabulary","emitted wire tokens",wires<=M["outcomes"].keys(),unclassified=sorted(wires-M["outcomes"].keys()))
    states=set(M["states"])
    result.check("vocabulary","all transition endpoints declared",
                 all(row["from"] in states and row["to"] in states for row in M["transitions"]))
    declared={f["id"] for f in M["facts"]}
    for word,spec in M["outcomes"].items():
        if spec.get("cases"):
            result.check("vocabulary",word,set(spec["cases"])<=declared)
    result.check("vocabulary","unique input classes",len(declared)==len(M["facts"]))


def disk_unavailable(d,result):
    def fail(target,data):
        if target.parent.name.startswith("holds-") and json.loads(data).get("holds"):
            raise OSError("fixture volume rejects hold publication")
        return original(target,data)
    assert acceptable(d.call("Start",BASE))
    row=d.row("Run",BASE+1)
    row["look"]["status"]="reserved"
    original=hp.publish_new_file
    with patch.object(hp,"publish_new_file",fail):
        step=d.call("Run",BASE+1,row)
    next_step=d.call("Run",BASE+2)
    result.check("custody refusal","failed append followed by clean read",refused(step) and refused(next_step)
                 and not d.calls,first=step,next=next_step,open_ids=list(d.ledger()[0]))




def command_clock(d, family, lag, offset, result):
    base_row=timing_fixture(d,family,BASE,lag)
    boundaries,_=dated_edges(base_row["calendar"],d.item["deadline_s"],lag)
    # A single remaining half exercises all seconds and the complete dispatch.
    # The chain tests each row (also when an earlier row already cannot fit).
    for edge,kind in boundaries:
        if not kind.startswith("dated startup "):
            continue
        t=edge+offset
        with tempfile.TemporaryDirectory(dir=d.root) as directory, Desk(Path(directory),d.item["piece"],BASE-100) as arm:
            start=arm.call("Start",BASE-100)
            assert acceptable(start),start
            obs=timing_fixture(arm,family,t,lag)
            _,guards,raw=oracle(arm,obs,t)
            step=arm.call("Run",t,obs)
            wire=clock_word(step)
            ok=compare(wire,guards,raw) and len(arm.calls)==int(not guards and raw in PASS)
            if guards and raw in PASS:
                ok=ok and not arm.ledger()[0]
            result.check("command dated sweep",[d.item["span"],family,lag,kind,offset],ok,
                         want="WAIT" if guards else raw,got=wire,launches=len(arm.calls))


def guard_and_fact(d,part,result):
    assert acceptable(d.call("Start",BASE))
    t=BASE+10
    obs=d.row("Run",t)
    ranked(obs,"f2-inst-02")["start_windows"]=[[t+90,t+300]]
    if part=="priority":
        ranked(obs,"f2-inst-01").update(status="eligible",start_windows=[[t-20,t+600]])
    else:
        obs["look"].update(status="reserved",pending_conflict=True)
    step=d.call("Run",t,obs)
    held,_,_=d.ledger()
    later=d.call("Run",t+700)
    result.check("clock and adverse fact",part,refused(step) and bool(held) and refused(later) and not d.calls,
                 first=step["decision"],later=later["decision"],holds=len(held),launches=len(d.calls))


def current_block(d,result):
    assert acceptable(d.call("Start",BASE))
    row=d.row("Run",BASE+1)
    row["look"].update(status="reserved",pending_conflict=True)
    first=d.call("Run",BASE+1,row)
    holds,_,_=d.ledger()
    if not holds:
        result.check("clearance reevaluates","still reserved",False,first=first)
        return
    row=d.row("Run",BASE+2)
    row["look"].update(status="reserved",pending_conflict=True)
    row["look"]["record"]="a distinct second reservation"
    row["hold_dispositions"]=proof_rows(d,holds,BASE+2,"valid")
    step=d.call("Run",BASE+2,row)
    later=d.call("Run",BASE+3)
    result.check("clearance reevaluates","still reserved",refused(step) and refused(later) and not d.calls,
                 same=step["decision"],later=later["decision"],launches=len(d.calls))


def clock_word(step):
    if step["decision"]=="WAIT_EVIDENCE" and step.get("detail","").startswith("launch guard at "):
        return "CLOCK_WAIT"
    return step["decision"]



def load_gate():
    spec=importlib.util.spec_from_file_location("candidate_hp",DRAFTS/"prepare_hp_items.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(checkout,stream,part="all"):
    global DRAFTS,PIN,hp,ITEMS
    DRAFTS=checkout/REL
    ITEMS=json.loads((DRAFTS/"hp-02/items.json").read_bytes())
    result=Results(stream)
    with tempfile.TemporaryDirectory(prefix="hp02-frozen-") as tmp:
        root=Path(tmp)
        archive=DRAFTS/"hp-02/fixtures/hp02-occupancy-fixture.zip"
        if digest(archive.read_bytes())!=M["fixture_sha256"][archive.name]:
            raise AssertionError("frozen pin archive identity changed")
        with ZipFile(archive) as fixture:
            fixture.extractall(root/"seat")
        PIN=root/"seat/tmp/pin"
        sys.path.insert(0,str(PIN))
        hp=load_gate()
        sys.addaudithook(native_guard)
        if part in ("all","protocol"):
            isolated(root,1,BASE,source_drift,result)
            isolated(root,1,BASE,disk_unavailable,result)
            for field,value in ([("pool",None)]+[(f,None) for f in M["protocol"]["R3"]["completion"]]
                                +[("kit_id",v) for v in M["protocol"]["R3"]["excluded"]]):
                isolated(root,1,BASE,r3,field,value,result)
            for offsets in product(M["protocol"]["R2"]["grid_s"],repeat=4):
                isolated(root,1,BASE,r2,offsets,result)
            for scope,rem,latency in product(M["guard"]["expiry_scopes"],(0,1,599,600,601,602,1200),
                                             M["protocol"]["R1"]["startup_latencies_s"]):
                isolated(root,1,BASE,margin,scope,rem,latency,result)
            for span,lag,alt in product((1,2,3),M["guard"]["startup"],(False,True)):
                isolated(root,span,BASE,registry,lag,alt,result)
        if part in ("all","dispatch"):
            for span,lag in product((1,2,3),M["guard"]["startup"]):
                for family in ("one-start","calendar","remaining-half","calendar-two-dates"):
                    for offset in range(-121,2):
                        isolated(root,span,BASE,command_clock,family,lag,offset,result)
        if part in ("all","controls"):
            for fact in ("priority","reservation"):
                isolated(root,1,BASE,guard_and_fact,fact,result)
            isolated(root,1,BASE,current_block,result)
            for name,expected in M["fixture_sha256"].items():
                result.check("fixture identity",name,digest((archive.parent/name).read_bytes())==expected)
            for variant,path in product(M["clear_reads"],M["retry_paths"]):
                isolated(root,1,BASE,controls,variant,path,result)
            isolated(root,1,BASE,multiple,result)
            for style in ("nonzero","exception"):
                isolated(root,1,BASE,launch_terminal,style,result)
            isolated(root,1,BASE,read_last,result)
            for kind,offset in product(("guard","calendar","watcher","opening"),(-121,-120,-90,-1,0,1)):
                anchor=midnight(day_at(BASE))-1800 if kind=="opening" else BASE
                isolated(root,1,anchor,clock_route,kind,offset,result)
        if part in ("all","history","dispositions"):
            for fact in M["facts"]:
                for origin in fact["at"]:
                    args=(fact.get("span",1),at_stage_time(fact["id"]))
                    if part!="dispositions":
                        for variant,path in product(M["clear_reads"],M["retry_paths"]):
                            isolated(root,*args,history_case,fact,origin,variant,path,result)
                    if part!="history":
                        for variant in [*M["invalid_dispositions"],"valid"]:
                            isolated(root,*args,clearance_case,fact,origin,variant,result)
        if part in ("all","clock"):
            families=["pin","one-start","remaining-half","calendar","calendar-two-dates","copy","opening",*M["guard"]["expiry_scopes"],
                      *["competitor "+r for r in ("ready-session","counted","first-stability",
                                                 "f2-inst-01","f2-inst-02","f2-inst-03")]]
            for span,lag,family in product((1,2,3),M["guard"]["startup"],families):
                isolated(root,span,BASE,timing,family,lag,result)
        result.check("synthetic isolation",part,not NATIVE,attempts=NATIVE)
    return result


class HP02FrozenGateMachine(unittest.TestCase):
    def test_gate_machine(self):
        # Keep the frozen pin imports and process audit hooks out of the pytest/unittest host.
        result=subprocess.run([sys.executable,"-IB",__file__,"--checkout",str(Path(__file__).resolve().parents[1])],
                              capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--checkout",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--results",type=Path)
    parser.add_argument("--part",choices=["all","clock","history","dispositions","controls","protocol","dispatch"],default="all")
    options=parser.parse_args()
    with ExitStack() as files:
        stream=files.enter_context(gzip.open(options.results,"wt")) if options.results else None
        summary=run(options.checkout.resolve(),stream,options.part)
    print(json.dumps(summary.count,sort_keys=True,indent=2))
    sys.exit(int(any(row["fail"] for row in summary.count.values())))
