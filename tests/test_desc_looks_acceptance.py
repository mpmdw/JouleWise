"""Black-box description look contract, disposable invented observations only."""
import csv
from datetime import date, datetime, timedelta
from functools import lru_cache
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo
import zipfile
import zlib

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("DESC_CODE_ROOT", Path.cwd())).resolve()
DESIGN_SHA = "09e8cacb56706ebb7f18a83281e6590b76741f29c127b4defea853add881aa8d"
IDS = ("lm-inst-01", "lm-stab-01", "lm-stab-02")
CONTROL = "docs/process/cadence/looks"
CHANNEL = ("gpu_rail", "rail_sum", "dc_in")
COLS = ["cpu_power", "gpu_power", "ane_power"]
WIDTH = (10, 40, 128)
MEASURES = ("mean_w", "sd10_w", "sd40_w", "sd128_w", "turn_j")
LA = ZoneInfo("America/Los_Angeles")
TOL = 1e-8


def sha(data):
    return hashlib.sha256(data).hexdigest()


def wire(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def read(path):
    return json.loads(path.read_bytes())


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else wire(value))


@lru_cache
def design():
    archive = (HERE / "description-design.zip").read_bytes()
    if sha(archive) != DESIGN_SHA:
        raise ValueError("public design fixture digest changed")
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        return {k: z.read(k) for k in z.namelist()}


def command():
    return shlex.split(os.environ["DESC_CLI"]) if "DESC_CLI" in os.environ else [
        sys.executable, "-B", str(ROOT / "scripts/cadence_description_run.py")]


class Book:
    """Build a real loose Git object graph from *fixture bytes* without invoking git commit."""
    def __init__(self, path):
        self.path = path
        self.git = path / ".git"
        self.head = None
        put(self.git / "HEAD", b"ref: refs/heads/main\n")
        put(self.git / "config", b"[core]\nrepositoryformatversion=0\nbare=false\n")
        put(self.git / "info/exclude", b"/public/\n")

    def obj(self, kind, payload):
        raw = kind.encode() + b" " + str(len(payload)).encode() + b"\0" + payload
        oid = hashlib.sha1(raw).hexdigest()
        objpath = self.git / "objects" / oid[:2] / oid[2:]
        if not objpath.exists():
            put(objpath, zlib.compress(raw))
        return oid

    def tree(self, path):
        entries = []
        for child in path.iterdir():
            if child.name in (".git", "public"):
                continue
            if child.is_dir():
                mode, key, oid = "40000", child.name + "/", self.tree(child)
            else:
                mode, key, oid = "100644", child.name, self.obj("blob", child.read_bytes())
            entries.append((key, f"{mode} {child.name}".encode() + b"\0" + bytes.fromhex(oid)))
        return self.obj("tree", b"".join(data for _, data in sorted(entries)))

    def seal(self, label):
        parent = "" if self.head is None else f"parent {self.head}\n"
        person = "Fixture <test@invalid.example> 1800000000 +0000"
        data = f"tree {self.tree(self.path)}\n{parent}author {person}\ncommitter {person}\n\n{label}\n"
        self.head = self.obj("commit", data.encode())
        for ref in ("heads/main", "remotes/origin/main"):
            put(self.git / "refs" / ref, (self.head + "\n").encode())
        subprocess.run(["git","-C",str(self.path),"read-tree",self.head],check=True,
                       stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
        return self.head


def layout(look):
    if look == IDS[0]:
        return [(1, 1, 1, 0), (2, 1, 2, 1), (3, 2, 3, 2)]
    rows = [(1, 1, 1, 0), (2, 1, 3, 0), (3, 1, 5, 0),
            (4, 1, 2, 1), (5, 1, 6, 1), (6, 1, 4, 2)]
    rows.extend((day, 2 if day % 2 else 3, day - 2, day) for day in range(3, 14))
    if look == IDS[2]:
        rows.append((15, 1, 8, 2))
    return rows


def template(look):
    base = IDS[1] if look == IDS[2] else look
    m = json.loads(design()[f"manifests/{base}.json"])
    m.update(look_id=look, status="committed")
    if look == IDS[2]:
        m["kit_index_path"] = "f2-stab/KITS.json"
    return m


def csvbytes(rows):
    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\n").writerows(rows)
    return output.getvalue().encode()


def pulse(t, c, cutoff=False):
    p = (4, 6, 10)[c]
    if c == 2:
        if t < 4:
            return p * max(0, min(1, t - .75))
        if t < 8:
            return p * (1 + min(1, 2 * (t - 4)))
        return p * (2 - .4*(t-8)) if cutoff else 2 * p * max(0, min(1, (8.75 - t) * 2))
    if t < .5:
        return 0
    if t < 1.25:
        return p * (.1 if t < .75 else .5 if t < 1 else .9)
    if t < 4:
        return p
    return 2 * p if t < (8.25 if c == 0 else 8.5) else .5*p


def watts(t, c, v, dc=False, cutoff=False, first_low=True):
    base = (12, 24, 40)[c]
    if t < 0:
        offset = 0 if first_low or t >= -10 else 100
    elif t < 600 or (dc and t == 600):
        offset = (1/64, 2/64, 3/64)[c] * (t - 300)
    elif t < 602:
        offset = 0
    else:
        offset = pulse(t - 602, c, cutoff)
    return v * (base + offset)


def traces(where, v, ordinal, delta=1):
    """Native interval-row format and decoded point format. Identity mapping plus nonzero clock offset."""
    # Split the DC grid at both integration boundaries and straddle the tail cut.
    ticks = list(range(-20, 603)) + [602 + i / 20 for i in range(1, 181)]
    ticks = [t for t in ticks if t != 611] + [611.025, 611.075]
    cuts = list(range(-20, 603)) + [602+i/4 for i in range(1, 37)]
    bound = [("interval_start_s", "interval_end_s", "timestamp_s", "source", "rail", "power_w")]
    for left, right in zip(cuts, cuts[1:]):
        t = (left + right) / 2
        g, s = (watts(t, c, v*delta, first_low=ordinal != 1) for c in (0, 1))
        for rail, power in ((COLS[2], (s-g)/3), (COLS[0], 2*(s-g)/3), (COLS[1], g)):
            bound.append((left, right, right, "powermetrics", rail, power))
        bound.append((left, right, right, "unrelated", "gpu_power", 900*v*delta))
    put(where / "power_trace.csv", csvbytes(bound))
    dcrows = [(t, round(watts(t, 2, v*delta, dc=True, cutoff=ordinal==2, first_low=ordinal!=1),10)) for t in ticks]
    put(where / "dc_points.csv", csvbytes([("epoch_s", "watts"), *dcrows]))
    gap = (5, 6, None)[ordinal % 3]
    put(where / "support.json", dict(rail_manifest=COLS, rail_intervals=list(zip(cuts, cuts[1:])),
        meter_times=ticks, meter_present=True, meter_clean=True,
        meter_counts={"decoded":len(ticks),"bad":0,"usb_errors":0},
        sidecar_times=ticks, sample_period_s={"hold":1, "rail_edge":.25, "dc_edge":.05},
        clock={"raw_anchor_s":1000, "trace_anchor_s":0}, sampling_started_raw_s=980,
        completion_log_raw_s=None if gap is None else 971, warmup_stage_raw_s=971+(gap or 5),
        turn_start_s=602, first_token_s=606, last_token_s=610,
        host_fan_keys=["left","right"], sensors=[{"fan_keys":{"left":900, "right":1100},"TV0h":35,"Tf08":40},
                 {"fan_keys":{"left":1100, "right":1300},"TV0h":39,"Tf08":42}]))


class World:
    def __init__(self, base, look, change=None):
        self.base, self.look, self.change = base, look, change
        self.repo = base / "book"
        self.book = Book(self.repo)
        self.copy = base / "verified-copy"
        self.private = base / "private" / look / "RESTRICTED"
        self.public = self.repo / "public" / look / "PUBLIC.json"
        self.stage = self.repo / "stage1" / (look+".json")
        self.private.parent.mkdir(parents=True)
        self.public.parent.mkdir(parents=True)
        self.stage.parent.mkdir(parents=True)
        self.man = self.repo / "manifests" / (look+".json")
        self.ledger = self.repo / "LOOKS.json"
        self.rows, self.good, self.targets = [], {}, {}
        self.inst = look == IDS[0]
        self.family = "inst" if self.inst else "stab"
        self.records = {}
        self.day_uses = {}
        self.predecessors = {}
        self.freeze = dict(look_id="lm-interim-01", freeze2_sha256=sha(b"invented coefficient identity"),
                           twin_agrees="yes")
        self.named("freeze", "authority/freeze.json", self.freeze)
        self.named("piece1", "authority/piece1.json", {"gate":"piece1","passed":True})
        self.named("first_native", "authority/native.json", {"gate":"native","passed":True})
        for path,data in design().items():
            if not path.startswith("manifests/"):
                put(self.repo/path, data)
        self.targets["registry"] = self.repo / CONTROL / "filler-kit-registry.json"
        self.targets["commitments"] = self.repo / CONTROL / "look-kit-commitments.v2.json"
        for k in ((look,) if self.inst else IDS[1:]):
            m = template(k)
            for name, pin in m["code_pins"].items():
                path = self.repo / pin["path"]
                if not path.exists():
                    # The executing build supplies its actual code and schemas. No placeholder on the builder path.
                    put(path, (ROOT / pin["path"]).read_bytes())
                pin["sha256"] = sha(path.read_bytes())
                if k == look:
                    self.targets["pin_"+name] = path
            put(self.repo / "manifests" / (k+".json"), m)
        self.targets["manifest"] = self.man
        if not self.inst:
            other = IDS[2] if look == IDS[1] else IDS[1]
            self.targets["peer_manifest"] = self.repo/"manifests"/(other+".json")
        kit15 = "kits/f2-stab-15.json"
        if change=="position_swap":
            k=read(self.repo/kit15)
            a,b=k["legs"][:2]
            a["prefill_tokens"],b["prefill_tokens"]=b["prefill_tokens"],a["prefill_tokens"]
            put(self.repo/kit15,k)
        self.index = [{"kit_id":"f2-stab-15","sha256":sha((self.repo/kit15).read_bytes())}]
        if change=="bad_index_digest": self.index[0]["sha256"]="7"*64
        if look == IDS[2] and change not in ("late_index","same_index","absent_index"):
            self.named("kit_index", "f2-stab/KITS.json", self.index)
        if change=="missing_peer":
            self.targets["peer_manifest"].unlink()
        if change in ("kit_omit","kit_duplicate","kit_alias","kit_foreign","kit_digest","rail_list","draft","placeholder","other_kind","index_path","missing_columns","gpu_only","bad_names","bad_counts","unknown_id","missing_reader"):
            m=read(self.man)
            if change=="kit_omit": m["kits"].pop()
            if change=="kit_duplicate": m["kits"].append(m["kits"][0])
            if change=="kit_alias": m["kits"][0]["kit_id"]="cl-invented-alias"
            if change=="kit_foreign": m["kits"][0]=template(IDS[1] if self.inst else IDS[0])["kits"][0]
            if change=="kit_digest": m["kits"][0]["sha256"]=m["kits"][1]["sha256"]
            if change=="rail_list": m["rail_sum_columns"]=COLS[::-1]
            if change=="draft": m["status"]="draft"
            if change=="placeholder": m["stage2"]="OPEN-4"
            if change=="other_kind": m["look_kind"]="qualification"
            if change=="index_path": m.pop("kit_index_path")
            if change=="missing_columns": m.pop("rail_sum_columns")
            if change=="gpu_only": m["rail_sum_columns"]=["gpu_power"]
            if change=="bad_names": m["outputs"]["custody_names"][-1]="extra.json"
            if change=="bad_counts": m["outputs"]["counts"].append("n_energy")
            if change=="unknown_id": m["look_id"]="lm-stab-03"
            if change=="missing_reader": m["code_pins"].pop("reader")
            put(self.man,m)
        self.reg = self.book.seal("register public designs and identifiers before any close")
        self.specimens = layout(look)
        if change in ("same_work","different_work"):
            self.specimens=[(kit,pos,1,(12*(kit-1)+pos-1)%14) for kit in (1,2) for pos in range(1,13)]
        if change=="all_terminal":
            self.specimens=[]
        if change=="extension_on_01":
            self.specimens.append((15,1,8,2))
        if change == "split":
            self.specimens += [(1,2,4,0),(1,3,5,0)]
        if change == "lock_first":
            self.specimens = self.specimens[:3]
        if change == "thirteen":
            self.specimens = [r for r in self.specimens if r[3] < 13]
        for i,(kit,pos,v,day) in enumerate(self.specimens):
            self.leg(kit,pos,v,day,i,"qualified")
        excluded_kit=14 if change in ("same_work","different_work") else 1
        self.leg(excluded_kit,11,1,0,97,"short")
        self.leg(excluded_kit,12,1,0,98,"unreleased")
        if change == "foreign":
            family=self.family
            self.family="stab" if self.inst else "inst"
            self.leg(2,4,7,3,80,"qualified")
            self.family=family
        if self.inst:
            present = {r["key"] for r in self.rows}
            for kit in range(1,4):
                for pos in range(1,13):
                    key = f"f2-inst-{kit:02}/L{pos:03}"
                    if key not in present:
                        path = "drops/"+key+".json"
                        self.named("drop" if "drop" not in self.targets else None, path,
                                   {"key":key,"status":"dropped","authority":"fixture desk decision"})
                        self.rows.append({"key":key,"drop":path})
        if change == "incomplete":
            self.rows.pop()
        if change == "duplicate":
            self.rows.append(self.rows[0])
        if change in ("bad_receipt","wrong_attempt","runner","multileg","no_soak","hand_disagrees","q1_failed","desk_failed"):
            target={"hand_disagrees":"hand_table","q1_failed":"q1","desk_failed":"desk_final"}.get(change,"receipt")
            path=self.targets[target]
            obj=read(path)
            if change=="bad_receipt": obj["closed"]=False
            if change=="wrong_attempt": obj["attempt"]=2
            if change=="runner": obj["runner_pin"]="9"*40
            if change=="multileg": obj["legs"].append("L002")
            if change=="no_soak": obj["fresh_soak"]=False
            if target!="receipt": obj["passed"]=False
            put(path,obj)
        if change and change.startswith("op_"):
            field=change[3:]
            refs=self.rows[1]
            key=refs["key"]
            doc,rc,plan,_=self.records[key]
            if field=="quiet_short": doc["quiet_spans_ns"]=[[0,599999999999]]
            if field=="g0": doc["g0_outcome"]="timeout"
            if field=="cap_flag": doc["decode_cap_reached"]=False
            if field=="mode": rc["power_mode"]="High Power"
            if field=="short_count": doc["decode_tokens"]-=1
            put(self.repo/refs["receipt"],rc)
            put(self.repo/refs["leg_record"],doc)
            self.records[key]=(doc,rc,plan,{"quiet_short":"short_hold","g0":"unreleased","cap_flag":"cap_not_reached",
                                            "mode":"wrong_mode","short_count":"short"}[field])
            self.good.pop(key)
            self.specimens.pop(1)
        if change=="split":
            first=self.rows[0]
            span=self.records[first["key"]][1]
            span["legs"]=["L001","L002","L003"]
            put(self.repo/first["receipt"],span)
            put(self.repo/first["issue"],{k:span[k] for k in ("kit_id","kit_sha256","span_id","attempt","runner_pin","legs")})
            for index in (3,4):
                refs=self.rows[index]
                key=refs["key"]
                op,_,leg,status=self.records[key]
                self.records[key]=(op,span,leg,status)
                for name in ("issue","receipt","hand_table","q1","desk_final"):
                    refs[name]=first[name]
                old=self.repo/refs["leg_record"]
                refs["leg_record"]=first["leg_record"].replace("/L001/","/"+op["leg_id"]+"/")
                put(self.repo/refs["leg_record"],op)
                shutil.rmtree(old.parents[2])
        if change=="same_index":
            self.named("kit_index","f2-stab/KITS.json",self.index)
        self.named("host_chain","ops/host-closes.json",self.predecessors)
        self.receipts = self.book.seal("close snapshot")
        if look == IDS[2] and change == "late_index":
            self.named("kit_index", "f2-stab/KITS.json", self.index)
        self.roster = {"rows":self.rows,"receipt_commit":self.receipts}
        self.named("roster","roster.json",self.roster)
        self.named("cold","authority/cold.json",
                   {"look_id":look,"manifest_sha256":sha(self.man.read_bytes()),"passed":True})
        self.named("copy","authority/copy.json",{"root":str(self.copy),"execution_host":socket.gethostname(),
                  "receipt_commit":self.receipts,"verified":True,
                  "files":{str(p.relative_to(self.copy)):sha(p.read_bytes()) for p in self.copy.rglob("*") if p.is_file()}})
        event = {"first_proven_close":self.receipts,"previous_read":IDS[1] if look==IDS[2] else None,
                 "previous_status":"completed" if look==IDS[2] else None,
                 "paper1_data_lock":look==IDS[2] or change=="lock_first",
                 "coalesced":[IDS[2]] if change=="lock_first" else []}
        if change=="no_lock": event["paper1_data_lock"]=False
        if change=="coalesced": event["coalesced"]=[IDS[2]]
        if change=="no_prior": event["previous_status"]=None
        if change=="no_close_event": event["first_proven_close"]=None
        if not self.inst:
            self.named("event","authority/events.json",event)
        if change in ("freeze_no","freeze_unevaluable","freeze_ruling"):
            obj=read(self.targets["freeze"])
            obj["twin_agrees"]="not_evaluable" if change=="freeze_unevaluable" else "no"
            if change=="freeze_ruling": obj["ruling"]={"id":"RL-fixture","effective_sha256":obj["freeze2_sha256"]}
            put(self.targets["freeze"],obj)
        if change in ("cold_denied","cold_wrong_hash","copy_failed","piece1_failed","native_failed"):
            key={"cold_denied":"cold","cold_wrong_hash":"cold","copy_failed":"copy","piece1_failed":"piece1","native_failed":"first_native"}[change]
            obj=read(self.targets[key])
            if change=="cold_wrong_hash": obj["manifest_sha256"]="8"*64
            else: obj["verified" if key=="copy" else "passed"]=False
            put(self.targets[key],obj)
        self.events_ledger=[{"event":"paper1_data_lock","receipt_commit":self.receipts}] if event["paper1_data_lock"] else []
        if look==IDS[2]:
            self.events_ledger.append({"look_id":IDS[1],"status":event["previous_status"]})
        if change=="lock_first":
            self.events_ledger.append({"look_id":IDS[2],"status":"coalesced"})
        self.row = dict(look_id=look, status="committed", manifest_path=str(self.man.relative_to(self.repo)),
            sha256=sha(self.man.read_bytes()), execution_host=socket.gethostname(),
            public_root="public", custody_root=str(base/"private"), registration_commit=self.reg,
            input_hashes={str(p.relative_to(self.repo)):sha(p.read_bytes()) for p in self.repo.rglob("*")
                          if p.is_file() and ".git" not in p.parts})
        self.save_row()
        self.book.seal("blind prerequisites")

    def named(self, name, rel, doc):
        p = self.repo/rel
        put(p,doc)
        if name:
            self.targets[name] = p

    def save_row(self):
        put(self.ledger, {"schema":"joulewise.cadence_look_ledger.v1","looks":[self.row,*self.events_ledger]})
        self.targets["ledger"] = self.ledger

    def leg(self, kit, pos, v, day, ordinal, status):
        kid=f"f2-{self.family}-{kit:02}"
        lid=f"L{pos:03}"
        key=kid+"/"+lid
        span=f"span-{kid}-{lid}"
        rel="ops/"+span+"/"
        kitpath=self.repo/"kits"/(kid+".json")
        k=read(kitpath)
        leg=k["legs"][pos-1]
        cap=leg["decode_tokens"]
        # Two local 01 hours on the fall-back date, with different UTC offsets.
        d=date(2026,11,1)+timedelta(days=day)
        visit=self.day_uses.get(day,0)
        self.day_uses[day]=visit+1
        hour=(1 if visit<2 else visit+3) if day==0 else 2*visit
        t=datetime(d.year,d.month,d.day,hour,10,tzinfo=LA,fold=int(day==0 and visit==1))
        epoch=t.timestamp()
        prior=None if ordinal==2 else {"kind":("other","qualification")[ordinal%2],
                    "close_epoch_s":epoch-(-4 if ordinal==3 else 23+ordinal)}
        if prior:
            prior["entry_id"]="previous-to-"+span
            self.predecessors[prior["entry_id"]]=dict(prior,host=socket.gethostname(),proven=True)
        ident=dict(kit_id=kid, kit_sha256=sha(kitpath.read_bytes()),span_id=span,attempt=1,
                   runner_pin=k["frozen"]["commit"],legs=[lid])
        doc=dict(leg_id=lid,leg_status="g0_unreleased" if status=="unreleased" else "complete",
                 g0_outcome="timeout" if status=="unreleased" else "released",
                 quiet_spans_ns=[] if status=="unreleased" else [[0,600_000_000_000]],
                 prefill_tokens=None if status=="unreleased" else leg["prefill_tokens"]+ordinal%3,
                 decode_tokens=0 if status=="unreleased" else cap-int(status=="short"),
                 decode_cap_reached=status=="qualified",loaded_flag=ordinal==0)
        if self.change in ("same_work","different_work") and status=="qualified":
            doc["prefill_tokens"]=leg["prefill_tokens"] + int(self.change=="different_work" and kit==2 and pos==7)
        receipt=dict(ident, closed=True,power_mode="Automatic",t0_epoch_s=epoch,
                     predecessor=prior,fresh_soak=True)
        refs={"key":key}
        files={"issue":("issue.json",ident),"receipt":("runner_receipt.json",receipt),
               "leg_record":("legs/"+lid+"/leg_record.json",doc)}
        files.update({n:(n+".json",dict(span_id=span,attempt=1,record=n,passed=True))
                      for n in ("hand_table","q1","desk_final")})
        for n,(suffix,obj) in files.items():
            refs[n]=rel+suffix
            self.named(n if ordinal==0 else None,refs[n],obj)
        if ordinal==0:
            self.targets["kit"]=kitpath
        self.records[key]=(doc,receipt,leg,status)
        self.rows.append(refs)
        if status=="qualified":
            self.good[key]=(v,ordinal)
            traces(self.copy/key,v,ordinal)
        else:
            traces(self.copy/key,v,ordinal)  # excluded legs also have tempting synthetic samples
        return refs

    def bind(self):
        self.row.update(status="stage1_committed",stage1_path=str(self.stage.relative_to(self.repo)),
                        stage1_sha256=sha(self.stage.read_bytes()))
        self.save_row()
        self.targets["stage1"]=self.stage
        self.stage1_commit=self.book.seal("bind stage one")

    def public_truth(self):
        counts={"n_legs":len(self.good)}
        if not self.inst:
            counts["n_local_dates"]=len({day for *_,day in self.specimens})
        return dict(look_id=self.look, manifest_sha256=sha(self.man.read_bytes()),
                    commit=self.stage1_commit,stage1_sha256=sha(self.stage.read_bytes()),**counts)


# This observer lives only in the test parent/child environment. No executor fault switch.
PROBE = r'''
import builtins, csv, io, json, os, sys
fd=os.open(os.environ["DESC_AUDIT_LOG"],os.O_WRONLY|os.O_APPEND)
copy=os.environ["DESC_VALUE_ROOT"]+os.sep
injection=os.environ.get("DESC_INJECT","")
class Leak_123_456(Exception): pass
def log(*args):
    os.write(fd,(json.dumps(args)+"\n").encode())
def audit(event,args):
    if event=="open" and isinstance(args[0],(str,bytes)):
        path=os.path.abspath(os.fsdecode(args[0]))
        flags=args[2] or 0
        if path.startswith(copy):
            log("open",path)
        if flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC): log("write",path)
    if event in ("os.rename","os.link","os.symlink","os.mkdir","os.remove","os.rmdir"):
        for arg in args[:2 if event in ("os.rename","os.link","os.symlink") else 1]:
            if isinstance(arg,(str,bytes)): log("write",os.path.abspath(os.fsdecode(arg)))
sys.addaudithook(audit)
log("alive",os.getpid())
def decorate(original):
    def opened(path,*args,**kw):
        stream=original(path,*args,**kw)
        if os.environ.get("DESC_SCALE_DIR") and isinstance(path,(str,bytes,os.PathLike)):
            name=os.path.abspath(os.fsdecode(path))
            if os.path.dirname(name)==os.environ["DESC_SCALE_DIR"] and os.path.basename(name) in ("power_trace.csv","dc_points.csv"):
                data=stream.read()
                stream.close()
                binary=isinstance(data,bytes)
                rows=list(csv.reader(io.StringIO(data.decode() if binary else data)))
                out=io.StringIO(newline="")
                writer=csv.writer(out,lineterminator="\n")
                writer.writerow(rows[0])
                for row in rows[1:]:
                    row[-1]=str(float(row[-1])*1.005)
                    writer.writerow(row)
                log("scaled",name)
                return io.BytesIO(out.getvalue().encode()) if binary else io.StringIO(out.getvalue())
        if injection and isinstance(path,(str,bytes,os.PathLike)):
            name=os.path.abspath(os.fsdecode(path))
            if name.startswith(copy) and name.endswith(("power_trace.csv","dc_points.csv")):
                byte=stream.read(1)
                if not byte: raise AssertionError("empty fault fixture")
                log("read_then_fault",name)
                stream.close()
                os.write(1,b"fixture parent out\n"); os.write(2,b"fixture parent err\n")
                pid=os.fork()
                if pid==0:
                    os.write(1,b"fixture child out\n"); os.write(2,b"fixture child err\n"); os._exit(0)
                os.waitpid(pid,0)
                if injection=="RuntimeError": raise RuntimeError("fixture private 314")
                raise Leak_123_456("fixture private 271")
        return stream
    return opened
builtins.open=decorate(builtins.open)
io.open=decorate(io.open)
'''


def invoke(w, stage, *extra, fault="", wait=True):
    probe=w.base/"observer"
    put(probe/"sitecustomize.py",PROBE.encode())
    log=tempfile.NamedTemporaryFile(dir=w.base)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",DESC_AUDIT_LOG=log.name,
             DESC_VALUE_ROOT=str(w.copy),DESC_INJECT=fault,
             PYTHONPATH=os.pathsep.join([str(probe),str(ROOT),os.environ.get("PYTHONPATH","")]))
    proc=subprocess.Popen([*command(),stage,"--repo",str(w.repo),"--look-id",w.look,*extra],
        cwd=w.base,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        close_fds=True)
    def finish():
        out,err=proc.communicate()
        log.seek(0)
        events=[json.loads(line) for line in log]
        log.close()
        if not any(r[0]=="alive" for r in events):
            raise AssertionError("Python I/O observer was not installed")
        return proc.returncode,out,err,events
    return finish() if wait else finish


def metrics(v, ordinal, c):
    base=float((12,24,40)[c]*v)
    a=(1/64,2/64,3/64)[c]*v
    p=(4,6,10)[c]*v
    sd=[a*w*math.sqrt((600//w)*(600//w+1)/12) for w in WIDTH]
    pre=(3.125 if c<2 else 2.75)*p
    dec=(8 if c<2 else 7.75)*p
    tail=(.875,1.25,(1.8 if ordinal==2 else 1))[c]*p
    return (base,*sd,pre+dec+tail), (pre/4,dec/4),a*600


def null(reason, **extra):
    return {"value":None,"reason":reason,**extra}


def private_names(look):
    return template(look)["outputs"]["custody_names"]


def by_key(w, file):
    return read(w.private/(file+".json"))


def sd1(xs):
    return statistics.stdev(xs) if len(xs)>=2 else null("fewer_than_two")


class Checks(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base=Path(temp.name).resolve()/"world"

    def world(self, look, change=None):
        return World(self.base,look,change)

    def stage1(self,w):
        result=invoke(w,"stage1")
        self.assertEqual(result[0],0,result[2])
        self.assertEqual([p for e,p in result[3] if e=="open"],[])
        doc=read(w.stage)
        self.assertEqual(doc["counts"]["n_legs"],len(w.good))
        rollup={}
        for rr in w.rows:
            key=rr["key"]
            counts=rollup.setdefault(key.split("/")[0],{})
            reason=w.records[key][-1] if key in w.records else "dropped"
            counts[reason]=counts.get(reason,0)+1
        self.assertEqual(doc["by_kit"],rollup)
        self.assertEqual(set(doc["positions"]),{r["key"] for r in w.rows})
        for key,(_,__,___,status) in w.records.items():
            self.assertEqual(doc["positions"][key]["disposition"],status)
            self.assertEqual(doc["positions"][key]["loaded_flag"],w.records[key][0]["loaded_flag"])
        for row in w.rows:
            if "drop" in row:
                self.assertEqual(doc["positions"][row["key"]]["disposition"],"dropped")
        if not w.inst:
            self.assertEqual(doc["counts"]["n_local_dates"],len({r[-1] for r in w.specimens}))
            table=doc["token_table"]
            self.assertEqual(len(table),len(w.records))
            self.assertEqual([r["kit_id"]+"/"+r["leg_id"] for r in table],sorted(w.records))
            self.assertEqual(doc["paper_wording"],"the same work" if w.change=="same_work" else "the same cell of work")
            for r in table:
                k=r["kit_id"]+"/"+r["leg_id"]
                op,rc,plan,disp=w.records[k]
                self.assertEqual(r,dict(kit_id=rc["kit_id"],kit_sha256=rc["kit_sha256"],
                     span_id=rc["span_id"],leg_id=op["leg_id"],position=int(op["leg_id"][1:]),
                     attempt=1,nominal_prefill_tokens=plan["prefill_tokens"],decode_cap=plan["decode_tokens"],
                     realised_prefill_tokens=op["prefill_tokens"],realised_decode_tokens=op["decode_tokens"],
                     local_t0_date=datetime.fromtimestamp(rc["t0_epoch_s"],LA).date().isoformat(),
                     leg_status=op["leg_status"],decode_cap_reached=op["decode_cap_reached"],
                     loaded_flag=op["loaded_flag"],disposition=disp,
                     missing_count_reason="g0_unreleased" if op["prefill_tokens"] is None else None))
        w.bind()

    def match(self,actual,expected):
        if isinstance(expected,dict):
            self.assertIsInstance(actual,dict)
            self.assertEqual(actual.keys(),expected.keys())
            for k,v in expected.items():
                with self.subTest(field=k):
                    self.match(actual[k],v)
        elif isinstance(expected,(tuple,list)):
            self.assertIsInstance(actual,list)
            self.assertEqual(len(actual),len(expected))
            for a,b in zip(actual,expected):
                self.match(a,b)
        elif type(expected) is float:
            self.assertIn(type(actual),(int,float))
            self.assertTrue(math.isclose(actual,expected,rel_tol=TOL,abs_tol=TOL),(actual,expected))
        else:
            self.assertEqual(type(actual),type(expected))
            self.assertEqual(actual,expected)

    def confined(self,w,events):
        for event,path in events:
            if event=="write":
                p=Path(path)
                self.assertTrue(p==w.public or p==w.private or w.private in p.parents,
                                f"unexpected write attempt {p}")

    def refused(self,w,stage="stage2",reserved=False,extra=()):
        before=w.public.read_bytes() if w.public.is_file() else None
        rc,out,err,events=invoke(w,stage,*extra)
        self.assertEqual((rc,out),(2,b""),err)
        self.assertFalse(any(e=="open" for e,p in events),"opened a scoring input before refusal")
        self.assertEqual(w.public.read_bytes() if w.public.is_file() else None,before)
        self.assertEqual(w.private.exists(),reserved)
        self.assertFalse(any(e=="write" for e,p in events),"refusal attempted a write")
        return err

    def success(self,w):
        rc,out,err,events=invoke(w,"stage2")
        self.assertEqual((rc,out,err),(0,b"",b""))
        self.confined(w,events)
        actual=w.public.read_bytes()
        self.assertEqual(actual,wire(w.public_truth()),"source-bound canonical PUBLIC.json")
        self.assertEqual(set(p.name for p in w.private.iterdir()),set(private_names(w.look)))
        self.assertTrue(all(p.is_file() and not p.is_symlink() for p in w.private.iterdir()))
        seen={str(Path(p).parent.relative_to(w.copy)) for e,p in events
              if e=="open" and Path(p).name in ("power_trace.csv","dc_points.csv")}
        self.assertEqual(seen,set(w.good))
        self.last_events=events
        return actual

    def scientific(self,w):
        hold,turn=by_key(w,"hold"),by_key(w,"turn")
        self.assertEqual(set(hold),set(w.good))
        self.assertEqual(set(turn),set(w.good))
        gains=by_key(w,"gain") if w.inst else {}
        edges=by_key(w,"edges") if w.inst else {}
        if w.inst:
            self.assertEqual(gains.keys(),hold.keys())
            self.assertEqual(edges.keys(),hold.keys())
        for key,(v,i) in w.good.items():
            with self.subTest(leg=key):
                op,_,leg,_=w.records[key]
                m=[metrics(v,i,c) for c in range(3)]
                expected_hold={}
                for c,ch in enumerate(CHANNEL):
                    vals,_,drift=m[c]
                    h=dict(zip(MEASURES[:4],vals[:4]))
                    h.update(kept=[60,15,4],dropped=[0,0,0])
                    if w.inst:
                        h.update(drift_w_per_600s=drift)
                    expected_hold[ch]=h
                self.match(hold[key],expected_hold)
                energy={ch:m[c][0][-1] for c,ch in enumerate(CHANNEL)}
                expected_turn={"energy_j":energy,"dc_tail_cut":True}
                def ratios(x):
                    return {ch:{"numerator":x[2],"denominator":x[c],"value":x[2]/x[c]}
                            for c,ch in enumerate(CHANNEL[:2])}
                if w.inst:
                    expected_turn["ratios"]=ratios(list(energy.values()))
                self.match(turn[key],expected_turn)
                if not w.inst:
                    continue
                pre=[item[1][0] for item in m]
                dec=[item[1][1] for item in m]
                long=leg["prefill_tokens"]==19458
                self.match(gains[key],dict(decode_w=dict(zip(CHANNEL,dec)),
                    long_prefill_w=dict(zip(CHANNEL,pre)) if long else null("not_long_prefill"),
                    decode_gain=ratios(dec),long_prefill_gain=ratios(pre) if long else null("not_long_prefill"),
                    idle_dc_minus_sum_w=16.*v,mean_fan_rpm=1100.,mean_start_c={"TV0h":37.,"Tf08":41.},
                    floor_tokens={ch:[s*wlen*op["decode_tokens"]/(4*dec[c]) for s,wlen in
                                   zip(m[c][0][1:4],WIDTH)] for c,ch in enumerate(CHANNEL)}))
                e=edges[key]
                self.assertEqual(set(e),set(("fallback","gap_outside","completion_to_stage_s","unobserved_s",
                    "recovery_s","rail_return_censor_s","resolution_s","rise_s","onset_lag_s","decode_end_lag_s")))
                self.match(e["fallback"],i==2)
                self.match(e["gap_outside"],i==1)
                self.match(e["completion_to_stage_s"],null("no_completion_log") if i==2 else (5.,6.)[i])
                self.match(e["unobserved_s"],9.)
                for ch in CHANNEL:
                    if i!=1:
                        self.match(e["recovery_s"][ch],null("under",bound_s=9.))
                    else:
                        # The first observed window fails and the second passes. The
                        # ruling does not fix the stride for windows after the first.
                        self.assertGreater(e["recovery_s"][ch],9.)
                        self.assertLessEqual(e["recovery_s"][ch],19.)
                self.match(e["rail_return_censor_s"],{ch:null("stream_end",bound_s=1.) for ch in CHANNEL[:2]})
                self.match(e["resolution_s"],dict(zip(CHANNEL,(.25,.25,.05))))
                if leg["prefill_tokens"]==256:
                    self.match(e["rise_s"],{c:null("prefill shorter than the level window") for c in CHANNEL})
                    self.match(e["onset_lag_s"],{c:null("prefill shorter than the level window") for c in CHANNEL[:2]})
                else:
                    for c,expected in zip(CHANNEL,(.5,.5,.8)):
                        self.assertAlmostEqual(e["rise_s"][c],expected,delta=TOL)
                    for c in CHANNEL[:2]:
                        self.assertTrue(any(abs(e["onset_lag_s"][c]-x)<=TOL for x in (.5,.25)))
                for c,fall in zip(CHANNEL[:2],(.25,.5)):
                    if i==2:
                        self.match(e["decode_end_lag_s"][c],null("over 1 s",bound_s=1.))
                    else:
                        self.assertTrue(any(abs(e["decode_end_lag_s"][c]-x)<=TOL
                            for d in (.5078125,.55) for x in (d-fall,d-fall-.25)))
        if not w.inst:
            self.spreads(w)

    def spreads(self,w):
        cells=[f"{p}/{c}/{m}" for p in (256,2000,19458) for c in CHANNEL for m in MEASURES]
        grouped={k:{} for k in cells}
        context={k:{} for k in cells}
        for key,(v,i) in w.good.items():
            _,rc,plan,_=w.records[key]
            instant=datetime.fromtimestamp(rc["t0_epoch_s"],LA)
            d=instant.date().isoformat()
            prev=rc["predecessor"]
            for c,ch in enumerate(CHANNEL):
                for metric,num in zip(MEASURES,metrics(v,i,c)[0]):
                    k=f'{plan["prefill_tokens"]}/{ch}/{metric}'
                    grouped.setdefault(k,{}).setdefault(d,[]).append(num)
                    context.setdefault(k,{})[key]=dict(value=num,date=d,hour=instant.hour,
                        utc_offset_s=int(instant.utcoffset().total_seconds()),
                        predecessor_kind=prev["kind"] if prev else None,
                        gap_s=rc["t0_epoch_s"]-prev["close_epoch_s"] if prev else None,
                        status=("unknown" if not prev else "negative_gap" if rc["t0_epoch_s"]<prev["close_epoch_s"] else "known"))
        expected={}
        for k,days in grouped.items():
            means=[statistics.mean(xs) for xs in days.values()]
            df=sum(len(xs)-1 for xs in days.values())
            ss=sum(sum((x-statistics.mean(xs))**2 for x in xs) for xs in days.values())
            expected[k]=dict(dates={d:dict(n=len(xs),mean=statistics.mean(xs),sd=sd1(xs)) for d,xs in days.items()},
                singleton_dates=sum(len(xs)==1 for xs in days.values()),sd_date_means=sd1(means),
                pooled_within_sd=math.sqrt(ss/df) if df else null("no_within_date_df"))
        self.match(by_key(w,"date_spreads"),expected)
        self.match(by_key(w,"context"),context)


def rebind_inputs(w):
    """A new *synthetic* authorized snapshot for tests that change content intentionally."""
    for rel in w.row["input_hashes"]:
        p=w.repo/rel
        w.row["input_hashes"][rel]=sha(p.read_bytes())
    w.save_row()
    w.book.seal("bind revised fixture authority")


def copy_attestation(w):
    proof=read(w.targets["copy"])
    proof["files"]={str(p.relative_to(w.copy)):sha(p.read_bytes()) for p in w.copy.rglob("*") if p.is_file()}
    put(w.targets["copy"],proof)
    rebind_inputs(w)


def corruption(w, cls, issue):
    path=w.targets[cls]
    if issue=="missing":
        path.unlink()
    elif issue=="bytes":
        put(path,path.read_bytes()+b" ")
    elif issue=="malformed":
        put(path,b"\xff{")
    elif issue=="substitute":
        put(path,wire({"authentic_but_wrong_identity":"neighbour"}))
    elif issue=="duplicate_key":
        put(path,b'{"identity":"fixture","identity":"fixture"}')
    elif issue=="escape":
        other=w.base/"elsewhere"/path.name
        put(other,path.read_bytes())
        path.unlink()
        path.symlink_to(other)


MUTATIONS=("missing","bytes","malformed","substitute","duplicate_key","escape")
COMMON=("manifest","ledger","commitments","registry","kit","roster","issue","receipt","leg_record",
        "hand_table","q1","desk_final","first_native","freeze","cold","copy","stage1",
        *("pin_"+n for n in ("reader","manifest_schema","stage1_schema","output_schema",
                             "restricted_schema","validator","schema_validator","kit_commitments")))
# Registry and the eight code-pin roles are distinct bindings, even where their paths coincide.
def classes(look):
    return COMMON+(("piece1","drop") if look==IDS[0] else ("peer_manifest","event","host_chain"))+(
        ("kit_index",) if look==IDS[2] else ())


def matrix(self,look,cls,issue):
    w=self.world(look)
    self.stage1(w)
    corruption(w,cls,issue)
    self.refused(w)


def happy(self,look):
    w=self.world(look)
    self.stage1(w)
    self.success(w)
    self.scientific(w)


def public_test(self,look):
    w=self.world(look)
    self.stage1(w)
    rc,out,err,events=invoke(w,"stage2")
    self.assertEqual((rc,out,err),(0,b"",b""))
    self.assertTrue(any(e=="open" and p.endswith("power_trace.csv") for e,p in events))
    self.assertEqual(w.public.read_bytes(),wire(w.public_truth()),"source-bound canonical PUBLIC.json")


def foreign(self,look):
    w=self.world(look,"foreign")
    self.refused(w,"stage1")


def invariant(self,look,idx):
    # Reconstitute an independent, pristine simulation at identical registered paths.
    # A transform of file reads below leaves the simulated copy verification and the
    # Git graph byte-identical. Only the responding leg's value bytes change.
    w=self.world(look)
    self.stage1(w)
    all_keys=list(w.records)
    key=all_keys[idx]
    original=dict(w.good)
    before=self.success(w)
    old_turn=by_key(w,"turn").get(key)
    shutil.rmtree(w.base)  # exclusively owned TemporaryDirectory fixture
    w=self.world(look)
    self.stage1(w)
    self.assertEqual(original,w.good)
    # The independent synthetic instrument delivers the perturbed samples after
    # the host's verified copy is staged. Operational sources are byte-identical.
    with patch.dict(os.environ,DESC_SCALE_DIR=str(w.copy/key)):
        after=self.success(w)
    if old_turn is None:
        self.assertNotIn(key,by_key(w,"turn"))
        self.assertFalse(any(e=="scaled" for e,_ in self.last_events))
    else:
        self.assertTrue(any(e=="scaled" for e,_ in self.last_events))
        for ch,value in by_key(w,"turn")[key]["energy_j"].items():
            self.assertAlmostEqual(value,old_turn["energy_j"][ch]*1.005,delta=TOL*abs(value))
    self.assertEqual(before,after)


def fault(self,look,exc):
    w=self.world(look)
    self.stage1(w)
    rc,out,err,events=invoke(w,"stage2",fault=exc)
    self.assertEqual((rc,out,err),(1,b"",b"stage2_error\n"+
                     (exc if exc=="RuntimeError" else "OtherError").encode()+b"\n"))
    self.assertEqual(sum(e=="read_then_fault" for e,_ in events),1)
    self.confined(w,events)
    self.assertFalse(w.public.exists())
    for fd in ("stdout","stderr"):
        log=(w.private/fd).read_bytes()
        for which in ("parent","child"):
            self.assertIn(f"fixture {which} {fd[3:]}\n".encode(),log)
    self.refused(w,reserved=True)


def once(self,look,mode):
    w=self.world(look)
    self.stage1(w)
    if mode in ("race","again"):
        if mode=="race":
            finishes=[invoke(w,"stage2",wait=False) for _ in range(2)]
            results=[f() for f in finishes]
            self.assertEqual(sorted(r[0] for r in results),[0,2])
            self.assertFalse(any(e=="open" for result in results if result[0]==2 for e,_ in result[3]))
            self.assertEqual(w.public.read_bytes(),wire(w.public_truth()))
        else:
            self.success(w)
        old={p:p.read_bytes() for p in w.private.iterdir()}
        self.refused(w,reserved=True)
        self.assertEqual(old,{p:p.read_bytes() for p in w.private.iterdir()})
    elif mode in ("abandoned","other_checkout"):
        w.private.mkdir()
        put(w.private/"stderr",b"existing fixture bytes")
        if mode=="other_checkout":
            alt=w.base/"book2"
            shutil.copytree(w.repo,alt)
            w.repo=alt
        self.refused(w,reserved=True)
        self.assertEqual((w.private/"stderr").read_bytes(),b"existing fixture bytes")
    elif mode=="public":
        put(w.public,b"previous fixture")
        self.refused(w)
    elif mode=="other_root":
        self.refused(w,extra=("--out",str(w.base/"unused"),))
    elif mode=="post_mkdir":
        # Fail fd setup via preinstalled test observer, without signalling any process.
        with patch.dict(invoke.__globals__,PROBE=PROBE+'\ndef fail_fd(event,args):\n'
            '    if event=="open" and str(args[0]).endswith("/RESTRICTED/stderr"): raise OSError("fixture")\n'
            'sys.addaudithook(fail_fd)\n'):
            rc,_,_,events=invoke(w,"stage2")
        self.assertEqual(rc,2)
        self.assertTrue(w.private.is_dir())
        self.assertFalse(any(e=="open" for e,_ in events))
        self.refused(w,reserved=True)
    else:
        if mode=="wrong_host":
            w.row["execution_host"]+=".invalid"
        else:
            w.row["status"]=mode
        w.save_row()
        w.book.seal("independent ledger disposition")
        self.refused(w)


BLIND=("foreign","duplicate","incomplete","bad_receipt","wrong_attempt","runner","multileg","no_soak",
       "hand_disagrees","q1_failed","desk_failed","kit_omit","kit_duplicate","kit_alias","kit_foreign",
       "kit_digest","rail_list","draft","placeholder","other_kind","missing_peer","no_lock","coalesced",
       "no_prior","no_close_event","late_index","index_path","position_swap","thirteen",
       "absent_index","same_index","bad_index_digest","extension_on_01")
BLIND_ALL=("duplicate","bad_receipt","wrong_attempt","runner","hand_disagrees","q1_failed","desk_failed",
           "kit_omit","kit_duplicate","kit_alias","kit_foreign","kit_digest","rail_list","draft","placeholder","other_kind")
FINAL_GATES=("missing_columns","gpu_only","bad_names","bad_counts","unknown_id","missing_reader")
GATES=("freeze_no","freeze_unevaluable","cold_denied","cold_wrong_hash","copy_failed")
def refused_gate(self,look,reason):
    w=self.world(look,reason)
    if reason in BLIND or reason in FINAL_GATES:
        self.refused(w,"stage1")
        return
    # These gates govern reservation. An implementation may also check them at stage 1.
    rc,_,err,events=invoke(w,"stage1")
    self.assertFalse(any(e=="open" for e,p in events))
    if rc==2:
        self.assertFalse(w.stage.exists())
        self.assertFalse(w.private.exists())
        return
    self.assertEqual(rc,0,err)
    w.bind()
    self.refused(w)


def writer(self,look,field,mutation):
    w=self.world(look)
    self.stage1(w)
    p=w.base/"candidate.json"
    truth=w.public_truth()
    put(p,truth)
    rc,_,err,events=invoke(w,"validate-public","--candidate",str(p))
    self.assertEqual(rc,0,err)
    self.assertFalse(any(e=="open" for e,_ in events))
    old=truth[field]
    if mutation=="missing":
        del truth[field]
    elif mutation=="extra":
        truth["extra_"+field]=old
    elif mutation=="same_type":
        truth[field]=old+1 if type(old) is int else (
            "lm-stab-01" if old=="lm-inst-01" else "lm-inst-01" if field=="look_id" else
            ("1" if old[0]!="1" else "2")+old[1:])
    else:
        truth[field]={"bool":True,"float":float(old) if type(old) is int else 1.0,
                      "array":[old],"null":None,"word":"fixture_private_37"}[mutation]
    put(p,truth)
    self.refused(w,"validate-public",extra=("--candidate",str(p)))


def repaired_freeze(self,look):
    w=self.world(look,"freeze_ruling")
    self.stage1(w)
    self.success(w)


def exact_edges(self):
    # Independent ruling attachment, issued by the research lead with the final hand table.
    # A bound or a range alone cannot certify a single audit pass.
    path=HERE/"description-edge-ruling.json"
    self.assertTrue(path.is_file(),"NEEDS_SPEC: signed-off crossing and recovery hand values, FOR-FABLE.md")
    table=read(path)
    self.assertRegex(table["ruling"],r"^RL-[0-9]+[a-z]?$")
    w=self.world(IDS[0])
    self.stage1(w)
    self.success(w)
    edges=by_key(w,"edges")
    self.assertEqual(set(table["legs"]),set(w.good))
    for key,expected in table["legs"].items():
        self.assertEqual(set(expected),{"onset_lag_s","decode_end_lag_s","recovery_s"})
        self.match({k:edges[key][k] for k in expected},expected)


def exact_rail_rows(self):
    # Fixture-only builder adapter uses the two real row readers. It constructs
    # its input from the byte-attested synthetic file and reports no live rows.
    w=self.world(IDS[0])
    key=next(iter(w.good))
    source=w.copy/key/"power_trace.csv"
    expected=[]
    for row in csv.DictReader(io.StringIO(source.read_text())):
        if row["rail"]=="gpu_power" and row["source"]=="powermetrics":
            expected.append([float(row[k]) for k in ("interval_start_s","interval_end_s","power_w","timestamp_s")])
    probe=ROOT/"tests/fixtures/description_gpu_rows.py"
    r=subprocess.run([sys.executable,"-B",str(probe),"--invented-world","first-instrument"],
                     cwd=w.base,capture_output=True)
    self.assertEqual(r.returncode,0,r.stderr)
    self.assertEqual(json.loads(r.stdout),{"description":expected,"pinned_step3":expected})


def coalescence(self):
    w=self.world(IDS[1],"lock_first")
    self.stage1(w)
    self.success(w)
    self.scientific(w)
    self.assertEqual(read(w.targets["event"])["coalesced"],[IDS[2]])


def cut(self,look):
    w=self.world(look)
    self.stage1(w)
    before=w.stage.read_bytes()
    # A later operational close outside the committed snapshot cannot be discovered by rescanning.
    w.leg(2,9,42,15,109,"qualified")
    w.book.seal("another proven close after the bound stage one")
    late=w.rows[-1]["key"]
    w.good.pop(late)
    self.success(w)
    self.assertEqual(w.stage.read_bytes(),before)
    self.assertNotIn(late,by_key(w,"hold"))


def coverage(self,look,mode):
    w=self.world(look)
    key=next(iter(w.good))
    where=w.copy/key
    meta=read(where/"support.json")
    if mode=="rail_manifest":
        meta["rail_manifest"]=COLS[::-1]
        p=where/"power_trace.csv"
        rows=list(csv.DictReader(io.StringIO(p.read_text())))
        for row in rows:
            if row["rail"] in ("cpu_power","ane_power"): row["power_w"]="FORBIDDEN_VALUE"
        put(p,csvbytes([list(rows[0]),*(r.values() for r in rows)]))
    elif mode in ("meter_absent","meter_dirty"):
        meta["meter_present" if mode=="meter_absent" else "meter_clean"]=False
        if mode=="meter_dirty": meta["meter_counts"]["bad"]=1
        else:
            meta["meter_times"]=[]
            meta["meter_counts"]["decoded"]=0
    elif mode=="sidecar_gap":
        meta["sidecar_times"]=[t for t in meta["sidecar_times"] if not 604<t<608]
    elif mode in ("rail_gap","few_windows"):
        # Keep the GPU rows. Removing ANE creates a gap only in the sum.
        limit=590 if mode=="few_windows" else 10
        p=where/"power_trace.csv"
        rows=list(csv.DictReader(io.StringIO(p.read_text())))
        rows=[r for r in rows if not(r["rail"]=="ane_power" and 0<=float(r["interval_start_s"])<limit)]
        put(p,csvbytes([list(rows[0]),*(r.values() for r in rows)]))
        meta["rail_missing"]={"ane_power":[[0,limit]]}
    elif mode in ("zero_denominator","negative_denominator"):
        p=where/"power_trace.csv"
        rows=list(csv.DictReader(io.StringIO(p.read_text())))
        for row in rows:
            if row["source"]=="powermetrics" and row["rail"]=="gpu_power" and float(row["interval_start_s"])>=602:
                row["power_w"]=12 if mode=="zero_denominator" else 11
        put(p,csvbytes([list(rows[0]),*(r.values() for r in rows)]))
    put(where/"support.json",meta)
    copy_attestation(w)
    self.stage1(w)
    self.success(w)
    hold=by_key(w,"hold")[key]
    turn=by_key(w,"turn")[key]
    def undefined(x):
        self.assertIsNone(x["value"])
        self.assertIsInstance(x["reason"],str)
        self.assertTrue(x["reason"])
    if mode=="rail_manifest":
        undefined(hold["rail_sum"]["mean_w"])
        self.match(hold["gpu_rail"]["mean_w"],12.)
        self.match(hold["dc_in"]["mean_w"],40.)
    elif mode in ("rail_gap","few_windows"):
        h=hold["rail_sum"]
        self.assertEqual(h["kept"],[1,0,0] if mode=="few_windows" else [59,14,3])
        self.assertEqual(h["dropped"],[a-b for a,b in zip((60,15,4),h["kept"])])
        undefined(h["mean_w"])
        if mode=="few_windows":
            for name in MEASURES[1:4]:
                undefined(h[name])
        else:
            for j,width in enumerate(WIDTH):
                n=h["kept"][j]
                self.match(h[MEASURES[j+1]],(2/64)*width*math.sqrt(n*(n+1)/12))
    elif mode=="sidecar_gap":
        self.match(hold["gpu_rail"]["mean_w"],12.)
        for value in turn["energy_j"].values():
            undefined(value)
    elif mode.startswith("meter_"):
        self.assertNotIn(["open",str(where/"dc_points.csv")],self.last_events)
        undefined(hold["dc_in"]["mean_w"])
        undefined(turn["energy_j"]["dc_in"])
    else:
        for ratio in (turn["ratios"]["gpu_rail"],by_key(w,"gain")[key]["decode_gain"]["gpu_rail"]):
            self.assertIsNone(ratio["value"])
            self.assertTrue(ratio["reason"])
            self.assertGreater(ratio["numerator"],0)
            self.assertLessEqual(ratio["denominator"],0)
        for value in by_key(w,"gain")[key]["floor_tokens"]["gpu_rail"]:
            undefined(value)


def add(name, fn, *args):
    def test(self):
        fn(self,*args)
    test.__name__="test_"+name
    if hasattr(Checks,test.__name__):
        raise AssertionError("duplicate test name")
    setattr(Checks,test.__name__,test)


for look in IDS:
    prefix=look.replace("-","_")
    add(prefix+"_public_type",public_test,look)
    add(prefix+"_all_prints_and_partial",happy,look)
    add(prefix+"_roster_foreign_series",foreign,look)
    for cls in classes(look):
        for issue in MUTATIONS:
            add(f"{prefix}_auth_{cls}_{issue}",matrix,look,cls,issue)
    for idx,row in enumerate(layout(look)):
        add(f"{prefix}_scale_kit{row[0]:02}_L{row[1]:03}",invariant,look,idx)
    for offset,status in enumerate(("partial","unreleased")):
        add(f"{prefix}_scale_excluded_{status}",invariant,look,len(layout(look))+offset)
    for exc in ("RuntimeError","Leak_123_456"):
        add(f"{prefix}_after_first_read_{exc}",fault,look,exc)
    for mode in ("wrong_host","public","race","again","abandoned","other_checkout","other_root",
                 "failed","completed","coalesced","post_mkdir"):
        add(f"{prefix}_once_{mode}",once,look,mode)
    for field in ("look_id","commit","manifest_sha256","stage1_sha256","n_legs")+(
            ("n_local_dates",) if look!=IDS[0] else ()):
        for mutation in ("missing","extra","same_type","bool","float","array","null","word"):
            add(f"{prefix}_writer_{field}_{mutation}",writer,look,field,mutation)
    gates=GATES+BLIND_ALL+FINAL_GATES
    if look==IDS[0]:
        gates+=("incomplete","piece1_failed","native_failed")
    else:
        gates+=("multileg","missing_peer","no_soak")
        gates+=(("thirteen","no_close_event","extension_on_01") if look==IDS[1] else
                ("no_lock","no_prior","coalesced","late_index","index_path","position_swap","absent_index","same_index","bad_index_digest"))
        add(prefix+"_bound_cut",cut,look)
    for gate in gates:
        add(f"{prefix}_refuse_{gate}",refused_gate,look,gate)
    for mode in ("rail_manifest","meter_absent","meter_dirty","sidecar_gap","rail_gap","few_windows")+(
            ("zero_denominator","negative_denominator") if look==IDS[0] else ()):
        add(f"{prefix}_print_null_{mode}",coverage,look,mode)
    add(prefix+"_named_freeze",repaired_freeze,look)
add("lm_stab_lock_coalesces",coalescence)
add("lm_inst_01_edge_hand_table_exact",exact_edges)
add("lm_inst_01_gpu_rows_equal_step3",exact_rail_rows)



def registry_gate(self,kind,kit,field):
    docs=design()
    name="lm-qual-01" if kind=="qualification" else "lm-transfer-01"
    body=json.loads(docs["manifests/"+name+".json"])
    target=self.base/"candidate.json"
    put(target,body)
    cmd=[sys.executable,"-B","-m","joulewise.cadence_looks.manifest_dispatch","validate",str(target)]
    def run():
        return subprocess.run(cmd,cwd=ROOT,capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
    r=run()
    self.assertEqual(r.returncode,0,r.stderr)
    reg=json.loads(docs[CONTROL+"/filler-kit-registry.json"])["kit_sha256_by_id"]
    row=body["reads"]["blocks" if kind=="qualification" else "kits"][0]
    if field=="id": row["block_id" if kind=="qualification" else "kit_id"]=kit
    else: row["kit_sha256" if kind=="qualification" else "sha256"]=reg[kit]
    put(target,body)
    r=run()
    self.assertEqual((r.returncode,r.stdout),(2,b""))
    self.assertIn(b"filler kit",r.stderr)


def projection(self,look,field):
    w=self.world(look,"op_"+field)
    self.stage1(w)
    self.success(w)
    self.assertNotIn(w.rows[1]["key"],by_key(w,"hold"))


def staged(self,look,part,mut):
    w=self.world(look)
    self.stage1(w)
    # Three independent attestation entries are bound per staged leg. Test each
    # attack on the trusted copy manifest relative to the committed verify result.
    proof=read(w.targets["copy"])
    key=next(iter(w.good))+"/"+part
    if mut=="missing":
        del proof["files"][key]
    elif mut=="bytes":
        proof["files"][key]="0"*64
    elif mut=="malformed":
        proof["files"][key]=False
    elif mut=="substitute":
        other=list(w.good)[1]+"/"+part
        proof["files"][key]=proof["files"][other]
    elif mut=="duplicate_key":
        data=wire(proof)
        quoted=json.dumps(key).encode()
        data=data.replace(quoted+b":",quoted+b':"bad",'+quoted+b":",1)
        put(w.targets["copy"],data)
    else:
        proof["files"]["../unregistered/"+part]=proof["files"].pop(key)
    if mut!="duplicate_key": put(w.targets["copy"],proof)
    self.refused(w)


def gate_binding(self,look,mode):
    w=self.world(look)
    self.stage1(w)
    if mode=="uncommitted_binding":
        put(w.book.git/"refs/remotes/origin/main",(w.receipts+"\n").encode())
    elif mode in ("private_symlink","public_symlink"):
        p=w.private.parent if mode=="private_symlink" else w.public.parent
        displaced=w.base/("displaced_"+mode)
        p.rename(displaced)
        p.symlink_to(displaced,target_is_directory=True)
    elif mode=="foreign_stage":
        doc=read(w.stage)
        key=next(iter(w.good))
        doc["positions"]["f2-"+("stab" if w.inst else "inst")+"-01/L001"]=doc["positions"].pop(key)
        put(w.stage,doc)
        w.bind()  # authentic bytes, inconsistent with the stage-1 source snapshot
    elif mode=="count_substitution":
        doc=read(w.stage)
        doc["counts"]["n_legs"]+=1
        put(w.stage,doc)
        w.bind()
    elif mode=="wrong_copy_host":
        proof=read(w.targets["copy"])
        proof["execution_host"]+=".invalid"
        put(w.targets["copy"],proof)
        rebind_inputs(w)
    self.refused(w)


def empty_roster(self):
    w=self.world(IDS[0],"all_terminal")
    self.stage1(w)
    self.success(w)
    for name in ("hold","turn","gain","edges"):
        self.assertEqual(by_key(w,name),{})

def gap_limit(self,seconds):
    w=self.world(IDS[0])
    key=next(iter(w.good))
    p=w.copy/key/"support.json"
    support=read(p)
    support["warmup_stage_raw_s"]=support["completion_log_raw_s"]+seconds
    put(p,support)
    copy_attestation(w)
    self.stage1(w)
    self.success(w)
    edge=by_key(w,"edges")[key]
    self.match(edge["completion_to_stage_s"],seconds)
    self.match(edge["gap_outside"],seconds<4.5 or seconds>5.5)
    self.match(edge["fallback"],False)

def missing_fan(self):
    w=self.world(IDS[0])
    key=next(iter(w.good))
    p=w.copy/key/"support.json"
    doc=read(p)
    doc["host_fan_keys"]=["left","right"]
    for row in doc["sensors"]: del row["fan_keys"]["right"]
    put(p,doc)
    copy_attestation(w)
    self.stage1(w)
    self.success(w)
    field=by_key(w,"gain")[key]["mean_fan_rpm"]
    self.assertIsNone(field["value"])
    self.assertTrue(field["reason"])

def token_evidence(self,change):
    w=self.world(IDS[1],change)
    self.stage1(w)
    self.assertEqual(read(w.stage)["counts"],{"n_legs":24,"n_local_dates":14})

def split(self):
    w=self.world(IDS[0],"split")
    self.stage1(w)
    self.success(w)
    self.assertEqual(len(w.good),5)
    self.assertEqual(len({rc["span_id"] for _,rc,_,status in w.records.values()
                          if status=="qualified"}),3)


for k in IDS:
    prefix=k.replace("-","_")
    for part in ("support.json","power_trace.csv","dc_points.csv"):
        for mut in MUTATIONS:
            add(prefix+"_copy_binding_"+part.replace(".","_")+"_"+mut,staged,k,part,mut)
    for mode in ("uncommitted_binding","private_symlink","public_symlink","foreign_stage",
                 "count_substitution","wrong_copy_host"):
        add(prefix+"_binding_"+mode,gate_binding,k,mode)
    for field in ("quiet_short","g0","cap_flag","mode","short_count"):
        add(prefix+"_eligibility_"+field,projection,k,field)
add("lm_inst_01_split_receipt",split)
add("lm_inst_01_all_terminal_zero_qualified",empty_roster)
add("lm_inst_01_fan_key_missing",missing_fan)
for gap in (4.499,4.5,5.5,5.501):
    add("lm_inst_01_observed_gap_"+str(gap).replace(".","_"),gap_limit,gap)
for option in ("same_work","different_work"):
    add("lm_stab_01_token_"+option,token_evidence,option)
registry=json.loads(design()[CONTROL+"/filler-kit-registry.json"])
for kind in ("qualification","transfer"):
    for kid in sorted(set(registry["kit_sha256_by_id"])|set(registry["other_ids"])):
        fields=("id","digest") if kid in registry["kit_sha256_by_id"] else ("id",)
        for f in fields:
            add("registry_"+kind+"_"+kid.replace("-","_")+"_"+f,registry_gate,kind,kid,f)



if __name__=="__main__":
    unittest.main()

