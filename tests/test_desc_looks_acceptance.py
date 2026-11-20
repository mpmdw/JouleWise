"""Black-box description look contract, disposable invented observations only."""
import csv
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache, partial
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


# RL-192 / RL-192a. Seconds, GPU watts and total rail watts at scale one.
HAND_TABLE_LEGS = ("f2-inst-01/L001", "f2-inst-02/L001")
HAND_TABLE_STEPS = tuple(tuple(map(Decimal, row)) for row in (
    ("600", "12", "24"),
    ("602.50", "12.4", "24.6"),
    ("602.75", "14", "27"),
    ("603.00", "15.6", "29.4"),
    ("603.25", "16", "30"),
    ("606", "20", "36"),
    ("610.25", "14", "36"),
    ("610.50", "14", "27"),
))


def hand_table_watts(t, scale, ordinal):
    if t < 0:
        extra = 100 if ordinal == 1 and t < -10 else 0
        return scale * Decimal(12 + extra), scale * Decimal(24 + extra)
    if t < 600:
        gpu = 12 + (t - 300) / 64
        return scale * gpu, scale * 2 * gpu
    _, gpu, total = next(row for row in reversed(HAND_TABLE_STEPS) if row[0] <= t)
    return scale * gpu, scale * total


def traces(where, v, ordinal, delta=1, *, hand_table=False):
    """Native interval-row format and decoded point format. Identity mapping plus nonzero clock offset."""
    # Split the DC grid at both integration boundaries and straddle the tail cut.
    ticks = list(range(-20, 603)) + [602 + i / 20 for i in range(1, 181)]
    ticks = [t for t in ticks if t != 611] + [611.025, 611.075]
    cuts = list(range(-20, 603)) + [602+i/4 for i in range(1, 37)]
    bound = [("interval_start_s", "interval_end_s", "timestamp_s", "source", "rail", "power_w")]
    for left, right in zip(cuts, cuts[1:]):
        if hand_table:
            # The integer and quarter-second cut points convert exactly.
            t = (Decimal(left) + Decimal(right)) / 2
            gpu, total = hand_table_watts(t, v * delta, ordinal)
            fifth = (total - gpu) / 5
            powers = ((COLS[2], 2 * fifth), (COLS[0], 3 * fifth), (COLS[1], gpu))
        else:
            t = (left + right) / 2
            g, s = (watts(t, c, v*delta, first_low=ordinal != 1) for c in (0, 1))
            powers = ((COLS[2], (s-g)/3), (COLS[0], 2*(s-g)/3), (COLS[1], g))
        for rail, power in powers:
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
        # RL-192b: keep the authenticated row and all its tempting synthetic traces.
        disposition = "not_qualified:loaded" if doc["loaded_flag"] else status
        self.records[key]=(doc,receipt,leg,disposition)
        self.rows.append(refs)
        if status=="qualified":
            if not doc["loaded_flag"]:  # RL-192b: only contributors enter any print or date.
                self.good[key]=(v,ordinal)
            traces(self.copy/key,v,ordinal,hand_table=key in HAND_TABLE_LEGS)
        else:
            traces(self.copy/key,v,ordinal)  # excluded legs also have tempting synthetic samples
        return refs

    def bind(self):
        self.row.update(status="stage1_committed",stage1_path=str(self.stage.relative_to(self.repo)),
                        stage1_sha256=sha(self.stage.read_bytes()))
        self.save_row()
        self.targets["stage1"]=self.stage
        self.stage1_commit=self.book.seal("bind stage one")

    def qualified_dates(self):
        # RL-192b: a date counts only when at least one qualified member supplies it.
        return {datetime.fromtimestamp(self.records[key][1]["t0_epoch_s"], LA).date()
                for key in self.good}

    def public_truth(self):
        counts={"n_legs":len(self.good)}
        if not self.inst:
            counts["n_local_dates"]=len(self.qualified_dates())
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
# The one sanctioned descriptor setup in the pinned final-validator child.
import stat
def validator_stderr(path, flags, frame):
    module = os.environ["DESC_VALIDATOR_SOURCE"]
    reserve = os.environ["DESC_RESERVATION"]
    caller = frame.f_back
    return (path=="/dev/null" and flags & os.O_ACCMODE==os.O_RDWR
            and not flags & ~(os.O_RDWR | getattr(os,"O_CLOEXEC",0))
            and stat.S_ISCHR(os.stat(path, follow_symlinks=False).st_mode)
            and not os.path.lexists(reserve)
            and frame.f_code.co_filename==module and frame.f_code.co_name=="redirect_to_devnull"
            and frame.f_locals.get("fd")==2 and caller is not None
            and caller.f_code.co_filename==module and caller.f_code.co_name=="main"
            and sys.argv[0]==module and sys.argv[1:2]==["validate"] and sys.argv[-1:]==["--final"]
            and ["-m","joulewise.cadence_looks.manifest_dispatch"] in
                [sys.orig_argv[i:i+2] for i in range(len(sys.orig_argv)-1)])
def audit(event,args):
    if event=="open" and isinstance(args[0],(str,bytes)):
        path=os.path.abspath(os.fsdecode(args[0]))
        flags=args[2] or 0
        if path.startswith(copy):
            log("open",path)
        if flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC):
            if validator_stderr(path,flags,sys._getframe(1)): log("descriptor",path)
            else: log("write",path)
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
             DESC_VALUE_ROOT=str(w.copy),DESC_INJECT=fault,DESC_RESERVATION=str(w.private),
             DESC_VALIDATOR_SOURCE=str(ROOT/"joulewise/cadence_looks/manifest_dispatch.py"),
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
            self.assertEqual(doc["counts"]["n_local_dates"],len(w.qualified_dates()))
            table=doc["token_table"]
            self.assertEqual(len(table),len(w.records))
            self.assertEqual([r["kit_id"]+"/"+r["leg_id"] for r in table],sorted(w.records))
            # RL-192b: even the matching-pairs fixture lacks kit 01's loaded position.
            self.assertEqual(doc["paper_wording"],"the same cell of work")
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
                     missing_count_reason="loaded" if op["loaded_flag"] else
                         "g0_unreleased" if op["prefill_tokens"] is None else None))
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
                    "recovery_s","rail_return_censor_s","resolution_s","rise_s","onset_lag_s","decode_end_lag_s",
                    "recovery_resolution_s","recovery_skipped_windows")))
                self.match(e["recovery_resolution_s"],dict.fromkeys(CHANNEL,10.0))
                self.match(e["recovery_skipped_windows"],dict.fromkeys(CHANNEL,0))
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
    # RL-192b: the signed hand table still describes all three source legs.
    loaded = "f2-inst-01/L001"
    self.assertEqual(set(table["legs"]),set(w.good) | {loaded})
    self.assertEqual(set(edges),set(table["legs"]) - {loaded})
    for key in w.good:
        expected = table["legs"][key]
        self.assertEqual(set(expected),{"onset_lag_s","decode_end_lag_s","recovery_s"})
        self.match({k:edges[key][k] for k in expected},expected)


# SHA-256 of power_trace.csv in leg order. RL-192 §2 and RL-192a.
HAND_TABLE_SHA = (
    "50870a0857f8abf305188c6e2c628e83bf94c42b63078069bf01670da98fc0e6",
    "2bbdc841b77111e94932c3ddabee4148173f4af9db3c0bb98d536a301fa9d345",
)
NEAR_MISS_SHA = (
    "a62793646f990e2df0932982765ed00af8c46de88f23eb205a7913575973829d",
    "4603571162f73e7f145b5241a32ef1a8d59735354e082872b9e0c488444f0add",
)


def hand_table_guard(test):
    world = test.world(IDS[0])
    for i, key in enumerate(HAND_TABLE_LEGS):
        with test.subTest(leg=key):
            scale = i + 1
            folder = world.copy / key
            payload = (folder / "power_trace.csv").read_bytes()
            meta = json.loads((folder / "support.json").read_bytes(), parse_float=Decimal)
            intervals = [tuple(pair) for pair in meta["rail_intervals"]]
            rows = {}
            for row in csv.DictReader(io.StringIO(payload.decode())):
                if row["source"] == "powermetrics":
                    pair = Decimal(row["interval_start_s"]), Decimal(row["interval_end_s"])
                    group = rows.setdefault(pair, {})
                    test.assertNotIn(row["rail"], group)
                    group[row["rail"]] = Fraction(row["power_w"])
            test.assertEqual(list(rows), intervals)
            totals = {}
            for (a, b), group in rows.items():
                test.assertEqual(set(group), set(COLS))
                cpu, gpu, ane = (group[name] for name in COLS)
                planted_gpu, planted_sum = hand_table_watts((a + b) / 2, scale, i)
                totals[a] = cpu + ane + gpu
                test.assertEqual(totals[a], Fraction(planted_sum), (key, a))
                test.assertEqual(2 * cpu, 3 * ane, (key, a))
                test.assertEqual(gpu, Fraction(planted_gpu), (key, a))

            def mean_between(lo, hi):
                return sum(totals[a] * Fraction(b - a) for a, b in intervals
                           if lo <= a and b <= hi) / (hi - lo)

            hold = mean_between(0, 600)
            level = mean_between(604, 606) - hold
            test.assertEqual(hold, 24 * scale)
            test.assertEqual(level, 6 * scale)
            for start, fraction, cpu_w, ane_w in (
                ("602.50", "0.1", "7.32", "4.88"),
                ("602.75", "0.5", "7.8", "5.2"),
                ("603.00", "0.9", "8.28", "5.52"),
            ):
                a = Decimal(start)
                test.assertEqual(totals[a] - (hold + Fraction(fraction) * level), 0, start)
                group = rows[a, a + Decimal("0.25")]
                test.assertEqual(group["cpu_power"], scale * Fraction(cpu_w))
                test.assertEqual(group["ane_power"], scale * Fraction(ane_w))
            test.assertEqual(sha(payload), HAND_TABLE_SHA[i])


def hand_table_near_miss(test, i):
    # Score the frozen CSV via the normal per-leg print with its own DC clock.
    folder = test.base / HAND_TABLE_LEGS[i]
    traces(folder, i + 1, i)
    test.assertEqual(sha((folder / "power_trace.csv").read_bytes()), NEAR_MISS_SHA[i])
    paths = {name: folder / name for name in (RAIL_FILE, DC_FILE)}
    signal = executor().Signals(read(folder / "support.json"), paths, lambda: None, fixture_step3())
    kit, leg = HAND_TABLE_LEGS[i].split("/")
    plan = json.loads(design()[f"kits/{kit}.json"])["legs"][0]
    test.assertEqual(plan["leg_id"], leg)
    detail = ({"quiet_spans_ns": [(0, 600_000_000_000)]}, None, None, None,
              {"nominal_prefill_tokens": plan["prefill_tokens"], "realised_decode_tokens": plan["decode_tokens"]})
    edges = executor().print_leg(signal, detail, True)["edges"]
    for field, rail_sum in (("rise_s", 0.75), ("onset_lag_s", 0.25)):
        with test.subTest(field=field):
            test.assertEqual(edges[field]["rail_sum"], rail_sum)
            test.assertEqual(edges[field]["gpu_rail"], 0.5)


def exact_rail_rows(self):
    # Fixture-only builder adapter uses the two real row readers. It constructs
    # its input from the byte-attested synthetic file and reports no live rows.
    w=self.world(IDS[0])
    # RL-192b: this raw-reader equivalence check still uses the first input CSV.
    key=HAND_TABLE_LEGS[0]
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
    # RL-192b: the first qualified scoring witness has a different planted amplitude.
    scale = w.good[key][0]
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
                row["power_w"]=scale*(12 if mode=="zero_denominator" else 11)
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
        self.match(hold["gpu_rail"]["mean_w"],12.*scale)
        self.match(hold["dc_in"]["mean_w"],40.*scale)
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
                self.match(h[MEASURES[j+1]],scale*(2/64)*width*math.sqrt(n*(n+1)/12))
    elif mode=="sidecar_gap":
        self.match(hold["gpu_rail"]["mean_w"],12.*scale)
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
add("lm_inst_01_hand_table_exact_zero_guard", hand_table_guard)
for i, key in enumerate(HAND_TABLE_LEGS):
    add(key.lower().replace("-", "_").replace("/", "_") + "_near_miss", hand_table_near_miss, i)
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
    # RL-192b: 23 pair members qualify. Another member still supplies date zero.
    self.assertEqual(read(w.stage)["counts"],{"n_legs":23,"n_local_dates":14})

def split(self):
    w=self.world(IDS[0],"split")
    self.stage1(w)
    self.success(w)
    self.assertEqual(len(w.good),4)  # RL-192b: two qualified siblings still supply the split span.
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



# ---------------- Frozen v2 additions (inherited scenarios above) ----------------
from bisect import bisect_left, bisect_right
from collections.abc import Mapping
from contextlib import contextmanager
from itertools import combinations, permutations, product


RAW_CHANNEL = dict(zip(COLS, ("cpu_rail", "gpu_rail", "ane_rail")))
PRINT_INPUTS = {"gpu_rail": ("gpu_power",), "rail_sum": tuple(COLS), "dc_in": ("dc_in",)}
RAW_INPUTS = (*COLS, "dc_in", "sidecar")
STRIDE_S = 10  # RL-188 §4.2. Keep the fixture's clock independent of the executor.


def depends(channel, raw):
    return raw == "sidecar" or raw in PRINT_INPUTS[channel]
RAIL_HEADER = ("interval_start_s", "interval_end_s", "timestamp_s", "source", "rail", "power_w")
# [start, end), split in cadence at the turn. The origin is arbitrary.
INTERVAL = {
    "hold": (0, 600), "sd10": (0, 10), "sd40": (0, 40), "sd128": (0, 128),
    "recovery": (-20, -10), "turn": (602, 611), "prefill": (602, 606),
    "level": (604, 606), "decode": (606, 610), "tail": (610, 611),
    "mixed": (600, 606),
}
RAIL_FILE = "power_trace.csv"
DC_FILE = "dc_points.csv"
POSITION = ("first", "middle", "last")


def executor():
    from joulewise.cadence_looks import description
    return description


@lru_cache
def fixture_step3():
    return executor().step3_reader()


def nominal(raw, a, b):
    # Independent integer oracle. Every endpoint used here is on its nominal grid.
    fast_hz = 1 if raw == "sidecar" else 20 if raw == "dc_in" else 4
    split = max(a, min(602, b))
    return (split - a) + (b - split) * fast_hz


def grid(raw, a, b):
    split = max(a, min(602, b))
    n = nominal(raw, split, b)
    return [float(i) for i in range(a, split)] + [split + (b - split) * i / n for i in range(n)]


def count_floor(raw, a, b):
    return nominal(raw, a, b) * 99 // 100


def establish_count(stamps, count, a, b):
    # Spread omissions so that count loss alone does not synthesize a >2 s gap.
    # Preserve the first point, including the left DC bracket when possible.
    if count > len(stamps):
        return sorted([*stamps, (stamps[-1] + b) / 2])
    if count == 0:
        return []
    return [stamps[i * len(stamps) // count] for i in range(count)]


def gap_grid(stamps, a, b, gap):
    # Preserve the requested count, both end brackets, and the nominal header.
    # Pack each half on its side of an internal hole of exactly 'gap' seconds.
    mid = len(stamps) // 2
    left, right = (a+b-gap)/2, (a+b+gap)/2
    return ([a + (left-a)*i/max(1, mid-1) for i in range(mid)]
            + [right + (b-right)*i/(len(stamps)-mid) for i in range(len(stamps)-mid)])


def raw_fixture(folder, rails, dc, sidecar, **metadata):
    pairs = sorted({(a, b) for rows in rails.values() for a, b, _ in rows})
    meta = dict(turn_start_s=602, sample_period_s={"hold": 1, "rail_edge": .25, "dc_edge": .05},
                rail_manifest=list(COLS), rail_intervals=pairs, meter_times=[t for t, _ in dc],
                sidecar_times=sidecar, meter_present=True, meter_clean=True,
                meter_counts={"decoded": len(dc), "bad": 0, "usb_errors": 0},
                sensors=[{"fan_keys": {"left": 700}, "TV0h": 42}])
    meta.update(metadata)
    paths = {name:folder/name for name in (RAIL_FILE, DC_FILE)}
    rows = sorted((a, b, b, "powermetrics", rail, watts)
                  for rail, series in rails.items() for a, b, watts in series)
    put(paths[RAIL_FILE], csvbytes([RAIL_HEADER, *rows]))
    put(paths[DC_FILE], csvbytes([("epoch_s","watts"), *dc]))
    return executor().Signals(meta, paths, lambda: None, fixture_step3()), meta


def assert_scalar(test, value, reason):
    if reason:
        test.assertEqual(value, null(reason))
    else:
        test.assertIn(type(value), (int, float))
        test.assertTrue(math.isfinite(value))


def boundary(test, phase, channel, raw, offset, gap):
    a, b = INTERVAL[phase]
    base = {key: grid(key, a, b) for key in RAW_INPUTS}
    n = count_floor(raw, a, b) + offset
    chosen = establish_count(base[raw], n, a, b)
    bad = n * 100 < 99 * nominal(raw, a, b)
    rail_grid = sorted(set(base[COLS[0]]) | (set(chosen) if raw in COLS else set()))
    ends = dict(zip(rail_grid, rail_grid[1:] + [b]))
    rails = {key: [(s, ends[s], i+1) for s in (chosen if key == raw else base[key])]
             for i, key in enumerate(COLS)}
    points = {}
    for key in ("dc_in", "sidecar"):
        stamps = chosen if raw == key else base[key]
        points[key] = [a-1, *stamps, b]
        if gap in (key, "both"):
            if b-a >= 4 and len(stamps) >= 3:
                points[key] = [a-1, *gap_grid(stamps, a, b, 3), b]
            else:
                # A short span can have a gap in its enclosing observations.
                # Move the boundary bracket and preserve the number *inside*.
                inner = [a + (i + 1) * (b-a) / (len(stamps)+1) for i in range(len(stamps))]
                points[key] = [a-3, *inner, b]
            test.assertGreater(max(y-x for x,y in zip(points[key], points[key][1:])), 2)
    signal, _ = raw_fixture(test.base, rails, [(t, 7) for t in points["dc_in"]], points["sidecar"])
    starts = [r[0] for r in rails[raw]] if raw in COLS else points[raw]
    test.assertEqual(sum(a <= stamp < b for stamp in starts), n)
    if bad:
        reason = "coverage"
    elif gap in ("sidecar", "both") or (channel == "dc_in" and gap == "dc_in"):
        reason = "meter_gap"
    else:
        reason = None
    assert_scalar(test, signal.average(channel, a, b), reason)


class TraceLeg:
    """One ordinary invented leg, editable before the production print entry point."""
    def __init__(self, folder):
        self.folder = folder
        traces(folder, 1, 0)
        self.meta = read(folder/"support.json")
        self.rows = {}
        for name in (RAIL_FILE, DC_FILE):
            with (folder/name).open(newline="") as stream:
                self.rows[name] = list(csv.DictReader(stream))

    def omit(self, raw, stamps):
        stamps = set(stamps)
        if raw == "sidecar":
            self.meta["sidecar_times"] = [s for s in self.meta["sidecar_times"] if s not in stamps]
        elif raw == "dc_in":
            self.rows[DC_FILE] = [row for row in self.rows[DC_FILE] if float(row["epoch_s"]) not in stamps]
            self.meta["meter_times"] = [float(row["epoch_s"]) for row in self.rows[DC_FILE]]
            self.meta["meter_counts"]["decoded"] = len(self.rows[DC_FILE])
        else:
            self.rows[RAIL_FILE] = [row for row in self.rows[RAIL_FILE]
                                    if row["source"] != "powermetrics" or row["rail"] != raw
                                    or float(row["interval_start_s"]) not in stamps]

    def signal(self):
        for name, rows in self.rows.items():
            put(self.folder/name, csvbytes([list(rows[0]), *(row.values() for row in rows)]))
        return executor().Signals(self.meta, {n:self.folder/n for n in self.rows},
                                  lambda: None, fixture_step3())


def print_one(signal, look):
    detail = ({"quiet_spans_ns":[(0, 600_000_000_000)]}, None, None, None,
              {"nominal_prefill_tokens":19458, "realised_decode_tokens":512})
    return executor().print_leg(signal, detail, look == IDS[0])


def omit_at(leg, raw, a, b, position, n):
    starts = grid(raw, a, b)
    # The left endpoint is eligible; the right endpoint belongs to the next interval.
    begin = {"first":0, "middle":(len(starts)-n)//2, "last":len(starts)-n}[position]
    stamps = starts[begin:begin+n]
    leg.omit(raw, stamps)
    return stamps


def look_counts(test, look, raw, position, gap, offset):
    leg = TraceLeg(test.base)
    n = 594 + offset
    # Keep holes isolated so channel coverage and the auxiliary gap are independent.
    first = {"first":1, "middle":294, "last":585}[position]
    leg.omit(raw, (first+2*i for i in range(600-n)))
    if gap in ("sidecar","both"):
        leg.omit("sidecar", [100,101])
    if gap in ("dc_in","both"):
        # Relocate two points to create a 3 s hole without changing the tested count.
        for row in leg.rows[DC_FILE]:
            stamp = float(row["epoch_s"])
            if stamp in (200,201):
                row["epoch_s"] = stamp - 1.75 if stamp==200 else stamp+1.25
        leg.rows[DC_FILE].sort(key=lambda row:float(row["epoch_s"]))
        leg.meta["meter_times"] = [float(row["epoch_s"]) for row in leg.rows[DC_FILE]]
    report = print_one(leg.signal(), look)
    for name in CHANNEL:
        affected = depends(name, raw)
        reason = ("coverage" if n<594 and affected else
                  "meter_gap" if gap in ("sidecar","both") or (name=="dc_in" and gap=="dc_in")
                  else None)
        with test.subTest(print=name):
            assert_scalar(test, report["hold"][name]["mean_w"], reason)


def turn_projection(test, look, raw, position):
    leg = TraceLeg(test.base)
    # Defeat both count gates with loss inside decode, on its own faster cadence.
    n = 2 if raw == "dc_in" else 1
    omit_at(leg, raw, 606, 610, position, n)
    report = print_one(leg.signal(), look)
    for name in CHANNEL:
        affected = depends(name, raw)
        reason = "coverage" if affected else None
        assert_scalar(test, report["hold"][name]["mean_w"], None)
        assert_scalar(test, report["turn"]["energy_j"][name], reason)
        if look == IDS[0]:
            assert_scalar(test, report["gain"]["decode_w"][name], reason)


class WatchedToken(str):
    # Also detect interpretation of a previously cached raw field under a later request.
    def __new__(cls, value, row, spy):
        token = super().__new__(cls, value)
        token.row, token.spy = row, spy
        return token

    def __float__(self):
        self.spy(self.row)
        return float(str.__str__(self))

    def __str__(self):
        self.spy(self.row)
        return str.__str__(self)


class WatchedRow(Mapping):
    """Tag field *retrieval*, including get/items/values/dict copies, before float conversion."""
    def __init__(self, row, spy):
        self._row = row
        self.spy = spy

    def __len__(self):
        return len(self._row)

    def __iter__(self):
        return iter(self._row)

    def __getitem__(self, key):
        if key in ("watts","power_w"):
            self.spy(self._row)
            return WatchedToken(self._row[key], self._row, self.spy)
        return self._row[key]


@contextmanager
def observe_fields(folder, spy):
    real = csv.DictReader
    watched = {str(folder/n) for n in (RAIL_FILE,DC_FILE)}
    class FieldReader(real):
        def __init__(self, stream, *args, **kwargs):
            self.watched = getattr(stream, "name", None) in watched
            super().__init__(stream, *args, **kwargs)

        def __next__(self):
            row = super().__next__()
            return WatchedRow(row, spy) if self.watched else row

    with patch.object(csv, "DictReader", FieldReader):
        yield


def rail_selections(leg):
    rows = {rail: set() for rail in COLS}
    for row in leg.rows[RAIL_FILE]:
        if row["source"] == "powermetrics":
            rows[row["rail"]].add((float(row["interval_start_s"]), float(row["interval_end_s"])))
    return {**{RAW_CHANNEL[k]: sorted(v) for k,v in rows.items()},
            "rail_sum": sorted(set.intersection(*rows.values()))}


def read_order(test, look, target, raw, phase, position):
    # The oracle sees only fixture identities/stamps. No scorer state or refusal helper is used.
    leg = TraceLeg(test.base)
    if phase == "tiles":
        lo = {"first":0, "middle":300, "last":590}[position]
        hi = lo + 10
    else:
        lo, hi = INTERVAL[phase]
    if phase == "recovery":
        # Keep window zero and every channel's first stamp intact even for
        # a leading omission. A conforming common anchor will visit this tile.
        leg, start, _ = recovery_fixture(test.base, 4, STRIDE_S)
        lo, hi = start+STRIDE_S, start+2*STRIDE_S
    n = nominal(raw, lo, hi)
    omit_at(leg, raw, lo, hi, position, n - ((99*n-1)//100))
    rails = rail_selections(leg)
    joint_pairs = set(rails["rail_sum"])
    dc = leg.meta["meter_times"]
    active = None
    seen_good = set()
    violations = {}
    checked = []
    # A first- or last-row omission may also make a DC gap. Counts always win.
    @lru_cache(None)
    def allowed(channel, a, b):
        if channel == "sidecar":
            return False, 0, -1
        if channel == "dc_in":
            left, right = bisect_right(dc,a)-1, bisect_left(dc,b)
            count = bisect_left(dc,b) - bisect_left(dc,a)
            ok = (100*count >= 99*nominal("dc_in",a,b) and left >= 0 and right < len(dc)
                  and all(dc[i+1]-dc[i] <= 2 for i in range(left,right)))
            return ok, dc[max(0,left)], dc[min(right,len(dc)-1)]
        bounds = rails[channel]
        count = sum(a <= start < b for start,_ in bounds)
        edge, longest = a, 0
        for start, stop in bounds:
            if start < b and stop > a:
                longest = max(longest, start-edge)
                edge = max(edge, stop)
        period = .25 if a >= 602 else 1
        return (100*count >= 99*nominal("gpu_power",a,b)
                and max(longest,b-edge) <= max(1,5*period)), a, b

    def spy(row):
        if "epoch_s" in row:
            channel, stamp = "dc_in", float(row["epoch_s"])
        elif row["source"] == "powermetrics":
            channel, stamp = row["rail"], float(row["interval_start_s"])
        else:
            return
        if channel != raw:
            return
        if active is None:
            violations.setdefault("outside any interval", stamp)
            return
        name, a, b = active
        admitted, left, right = allowed(name, a, b)
        dependent = depends(name, raw)
        inside = left <= stamp <= right if raw=="dc_in" else stamp < right and float(row["interval_end_s"]) > left
        if name == "rail_sum" and raw in COLS:
            inside = inside and (stamp, float(row["interval_end_s"])) in joint_pairs
        if dependent and admitted and inside:
            seen_good.add(stamp)
        else:
            label = "failed fixture interval" if lo <= stamp < hi else "other unadmitted field"
            violations.setdefault(label, (raw,stamp,active))

    def access(channel, span):
        nonlocal active
        previous = active
        active = (channel, *span)
        try:
            result = original(channel, span)
            if channel == target and span == (lo,hi):
                checked.append(result)
            return result
        finally:
            active = previous

    with observe_fields(leg.folder, spy):
        signal = leg.signal()
        original = signal.interval_values
        with patch.object(signal, "interval_values", access):
            print_one(signal, look)
            # Re-query after cache warmup. A broad print cannot admit this subwindow.
            value = signal.interval_values(target, (lo,hi))
    test.assertEqual(value, null("coverage"))
    test.assertGreaterEqual(len(checked), 2, "normal print did not exercise the failed interval")
    test.assertFalse(violations, violations)
    test.assertTrue(seen_good, "reader spy did not intercept any admitted raw field")


def recovery_fixture(folder, winner, stride_s):
    # The fixture supplies its grid. The implementation supplies its own search.
    # All starts coincide here, so staggered-start or crossing choices cannot mask coverage.
    leg = TraceLeg(folder)
    origin, start = -69, -60
    turn_low = start + winner*stride_s
    leg.meta.update(sampling_started_raw_s=1000+start, completion_log_raw_s=1000+origin,
                    warmup_stage_raw_s=1005+origin)
    negative = range(start, 0)
    rail_rows = []
    for a in negative:
        for key, base in zip(COLS, (8,12,4)):
            rail_rows.append(dict(zip(RAIL_HEADER, (a,a+1,a+1,"powermetrics",key,
                                                     base + (40 if a < turn_low else 0)))))
    leg.rows[RAIL_FILE] = rail_rows + [r for r in leg.rows[RAIL_FILE] if float(r["interval_start_s"])>=0]
    leg.rows[DC_FILE] = [dict(epoch_s=a,watts=40 + (100 if a < turn_low else 0)) for a in negative] + [
        r for r in leg.rows[DC_FILE] if float(r["epoch_s"])>=0]
    leg.meta["rail_intervals"] = [[a,a+1] for a in negative] + [r for r in leg.meta["rail_intervals"] if r[0]>=0]
    leg.meta["meter_times"] = [float(r["epoch_s"]) for r in leg.rows[DC_FILE]]
    leg.meta["meter_counts"]["decoded"] = len(leg.rows[DC_FILE])
    leg.meta["sidecar_times"] = list(negative) + [t for t in leg.meta["sidecar_times"] if t>=0]
    return leg, start, origin


def shift_points(leg, raw, a):
    # Relocate (never delete) two samples. The common clock and nominal rate stay fixed.
    moved = {a+2: a+1.25, a+3: a+4.25}
    if raw == "sidecar":
        leg.meta["sidecar_times"] = sorted(moved.get(t, t) for t in leg.meta["sidecar_times"])
    else:
        for row in leg.rows[DC_FILE]:
            stamp = float(row["epoch_s"])
            row["epoch_s"] = moved.get(stamp, stamp)
        leg.rows[DC_FILE].sort(key=lambda row: float(row["epoch_s"]))
        leg.meta["meter_times"] = [float(row["epoch_s"]) for row in leg.rows[DC_FILE]]


def plant_rail_gap(leg, raw, a):
    # Add six complete triples on equal endpoints, then omit six consecutive
    # 1 s intervals of just one component. Count still passes; its 6 s gap fails.
    rows = []
    bounds = set()
    for row in leg.rows[RAIL_FILE]:
        lo, hi = float(row["interval_start_s"]), float(row["interval_end_s"])
        if a+2 <= lo < a+8 and row["source"] == "powermetrics" and row["rail"] == raw:
            continue
        steps = 4 if a <= lo < a+2 else 1
        for i in range(steps):
            x, y = lo+(hi-lo)*i/steps, lo+(hi-lo)*(i+1)/steps
            bounds.add((x, y))
            rows.append(dict(row, interval_start_s=x, interval_end_s=y, timestamp_s=y))
    leg.rows[RAIL_FILE] = rows
    leg.meta["rail_intervals"] = sorted(bounds)


def window_fault(leg, raw, a, width, fault):
    if fault == "gap":
        if raw in COLS:
            plant_rail_gap(leg, raw, a)
        else:
            shift_points(leg, raw, a)
    else:
        if fault == "mixed":
            shift_points(leg, "sidecar", a)
        # Keeping ceil(.99 W)-1 eligible starts fails the count, without
        # creating an independent time gap in the single-cause case.
        missing = width - ((99*width-1)//100)
        leg.omit(raw, [a+5+2*i for i in range(missing)])


def window_reason(channel, raw, fault):
    if depends(channel, raw):
        return "meter_gap" if fault == "gap" else "coverage"
    if fault == "mixed":
        return "meter_gap"  # The common sidecar gap still vetoes the sibling.
    return None


def assert_recovery(test, edges, values, reasons):
    # Independent assertions keep a correct late value visible when bookkeeping is absent.
    for channel in CHANNEL:
        with test.subTest(channel=channel, field="recovery_s"):
            test.match(edges["recovery_s"][channel], values[channel])
        with test.subTest(channel=channel, field="recovery_skipped_windows"):
            counts = edges.get("recovery_skipped_windows", {})
            test.assertEqual(set(counts), set(CHANNEL))
            test.match(counts[channel], len(reasons[channel]))
        with test.subTest(channel=channel, field="skip reasons"):
            # A clean legacy row has no reason document. On a drop we need
            # an observation in the print itself, independent of fixture metadata.
            test.match(edges.get("recovery_skip_reasons", {}).get(channel, []), reasons[channel])
        with test.subTest(channel=channel, field="recovery_resolution_s"):
            resolution = edges.get("recovery_resolution_s", {})
            test.assertEqual(set(resolution), set(CHANNEL))
            test.assertIn(type(resolution[channel]), (int, float))
            test.assertEqual(resolution[channel], 10)


def recovery_prefix(test, raw, faults, winner, stride_s, window_reason=window_reason):
    leg, start, origin = recovery_fixture(test.base, winner, stride_s)
    for index, fault in faults:
        window_fault(leg, raw, start+stride_s*index, 10, fault)
    values, reasons = {}, {}
    for ch in CHANNEL:
        reasons[ch] = []
        for index in range(6):
            reason = next((window_reason(ch, raw, fault) for i, fault in faults if i == index), None)
            if reason:
                reasons[ch].append(reason)
            elif index >= winner:
                values[ch] = float(start+index*stride_s-origin) if index else null("under", bound_s=float(start-origin))
                break
        test.assertIn(ch, values, "fixture must contain a complete qualifying successor")
    assert_recovery(test, print_one(leg.signal(), IDS[0])["edges"], values, reasons)


def audit5_window_zero(test):
    leg = TraceLeg(test.base)
    leg.omit("sidecar", [-18])
    leg.omit("gpu_power", [610.25])
    leg.meta["rail_missing"] = {"gpu_power": [[610.25, 610.5]]}
    test.assertEqual(sum(-20 <= t < -10 for t in leg.meta["sidecar_times"]), 9)
    test.assertEqual(sum(-10 <= t < 0 for t in leg.meta["sidecar_times"]), 10)
    edges = print_one(leg.signal(), IDS[0])["edges"]
    assert_recovery(test, edges, dict.fromkeys(CHANNEL, 19.0),
                    {ch: ["coverage"] for ch in CHANNEL})


def window_sd(test, look, channel, raw, width, position, fault):
    leg = TraceLeg(test.base)
    total = 600 // width
    index = {"first": 0, "middle": total//2, "last": total-1}[position]
    window_fault(leg, raw, index*width, width, fault)
    report = print_one(leg.signal(), look)["hold"]
    tested = CHANNEL if raw == "sidecar" else (channel, *(ch for ch in CHANNEL if not depends(ch, raw)))
    for ch in tested:
        reason = window_reason(ch, raw, fault)
        kept = [i for i in range(total) if not reason or i != index]
        c = CHANNEL.index(ch)
        means = [(12,24,40)[c] + (c+1)/64 * ((i+.5)*width-300) for i in kept]
        with test.subTest(channel=ch, field="SD and counts"):
            test.match(report[ch]["kept"][WIDTH.index(width)], len(kept))
            test.match(report[ch]["dropped"][WIDTH.index(width)], total-len(kept))
            test.match(report[ch][f"sd{width}_w"], statistics.stdev(means))
        with test.subTest(channel=ch, field="drop reasons"):
            test.match(report[ch].get("drop_reasons", {}).get(str(width), []), [reason] if reason else [])


def staggered_grid(test, late, mode, stride_s, raw=None, placement=None):
    leg = TraceLeg(test.base)
    # Earliest stamp -20, latest channel start -15, origin -29.
    # Remove leading intervals from ONE component, or leading points only from DC.
    leg.omit(late, range(-20, -15))
    if mode == "nonreturn":
        # Tile k has equal positive and negative impulses, so every hold mean
        # is 300 W (900 W for the sum), SD=0. Moving the grid by 5 s pairs the
        # old negative impulse with the next, strictly larger positive one.
        def level(t):
            if t < 0:
                return 400
            k, offset = divmod(t, 10)
            return 300 + (k+1) * ((offset == 2) - (offset == 7))
        for row in leg.rows[RAIL_FILE]:
            t = float(row["interval_start_s"])
            if t < 600 and row["source"] == "powermetrics":
                row["power_w"] = level(t)
        for row in leg.rows[DC_FILE]:
            t = float(row["epoch_s"])
            if t <= 600:
                row["watts"] = level(t)
    # From -15 the final complete tile is [585,595); [595,600) has no vote.
    # Keep omissions away from the hand fixture's impulses and interpolation knots.
    if placement in ("complete", "both"):
        leg.omit(raw, [589])
    if placement in ("incomplete", "both"):
        leg.omit(raw, [599])
    reasons = {ch: ["coverage"] if placement in ("complete","both") and depends(ch,raw) else []
               for ch in CHANNEL}
    expected = null("under", bound_s=14.) if mode == "under" else null("not returned", bound_s=624.)
    signal = leg.signal()
    calls = []
    original = signal.interval_values
    def observe(ch, span):
        calls.append((ch, span))
        return original(ch, span)
    with patch.object(signal, "interval_values", observe):
        e = print_one(signal, IDS[0])["edges"]
    for ch in CHANNEL:
        with test.subTest(channel=ch):
            test.assertIn((ch, (-15, -15+stride_s)), calls)
            if mode == "nonreturn":
                test.assertIn((ch, (585,595)), calls)
                test.assertFalse(any(name == ch and lo == 595 and hi > lo for name,(lo,hi) in calls))
    assert_recovery(test, e, dict.fromkeys(CHANNEL, expected), reasons)


def tail_reason(test, raw, position, null=null):
    leg = TraceLeg(test.base)
    if raw=="sidecar":
        # The ordinary sidecar is oversampled after the turn. Remove the whole
        # half-open tail, retaining its two brackets and a sub-2 s gap.
        leg.omit(raw, [s for s in leg.meta["sidecar_times"] if 610 <= s < 611])
    else:
        omit_at(leg, raw, 610, 611, position, 1)
    edges = print_one(leg.signal(), IDS[0])["edges"]
    for channel in ("gpu_rail","rail_sum"):
        affected = (channel=="rail_sum" and raw in COLS) or raw in ("sidecar","gpu_power")
        with test.subTest(channel=channel, print="rail return"):
            test.assertEqual(edges["rail_return_censor_s"][channel],
                             null("coverage") if affected else null("stream_end",bound_s=1))
        with test.subTest(channel=channel, print="decode end"):
            assert_scalar(test, edges["decode_end_lag_s"][channel],
                          "coverage" if affected or raw=="dc_in" else None)


def gap_limit_v2(test, channel, raw, period, delta, phase):
    # Decouple counts from gaps by dividing the covered duration into N rows.
    a = 602 if phase == "turn" else 0
    duration = 32
    b = a+duration
    n = int(duration/period)
    rail = raw in COLS
    limit = max(1,5*period) if rail else 2
    width = limit + delta
    span = (duration-width)/2
    bounds = [(start+i*span/(n//2), start+(i+1)*span/(n//2))
              for start in (a,a+span+width) for i in range(n//2)]
    regular = [(a+i*period, a+(i+1)*period) for i in range(n)]
    rows = {r:[(lo,hi,1) for lo,hi in (bounds if rail else regular)] for r in COLS}
    common = [s for s,_ in regular]
    stamps = gap_grid(common,a,b,width)
    meter = stamps if raw=="dc_in" else common
    sidecar = stamps if raw=="sidecar" else common
    hold = period if phase=="hold" or not rail else 1
    signal,_ = raw_fixture(test.base, rows, [(t,7) for t in [*meter,b]], [*sidecar,b],
                            sample_period_s={"hold":hold,"rail_edge":period,"dc_edge":period})
    result = signal.interval_values(channel,(a,b))
    if delta>0:
        test.assertEqual(result,null("meter_gap"))
    else:
        test.assertIsInstance(result,list)
        test.assertTrue(result)


def sum_intersection(test, raw_pair, offset):
    # Every component passes 594 individually; staggered absences decide the join.
    missing = 600-(594+offset)
    rails = {r:[(i,i+1,1) for i in range(600)
                if not (r==raw_pair[0] and i in {10,20,30})
                and not (r==raw_pair[1] and i in set(range(100,100+10*(missing-3),10)))]
             for r in COLS}
    signal,_ = raw_fixture(test.base,rails,[(i,7) for i in range(601)],list(range(601)))
    test.assertTrue(all(len(rail) >= 594 for rail in rails.values()))
    assert_scalar(test,signal.average("gpu_rail",0,600),None)
    assert_scalar(test,signal.average("rail_sum",0,600),"coverage" if offset<0 else None)


def manifest_order(test, look, order):
    leg = TraceLeg(test.base)
    leg.meta["rail_manifest"] = list(order)
    report = print_one(leg.signal(), look)
    good = list(order)==COLS
    for name in CHANNEL:
        reason = "rail_manifest" if name=="rail_sum" and not good else None
        assert_scalar(test, report["hold"][name]["mean_w"], reason)
        assert_scalar(test, report["turn"]["energy_j"][name], reason)


def public_order(test, look):
    world = test.world(look)
    test.stage1(world)
    truth = world.public_truth()
    # A profile hook records the actual validated byte return. The I/O hook uses
    # the child process's real file descriptors and writes at its first scoring open.
    extra = r"""
def profile(frame, event, result):
    if event=="return" and frame.f_code.co_name=="validate_public" and isinstance(result,bytes):
        log("public_bytes",result.hex())
sys.setprofile(profile)
sent=False
def echo_at_stream(event,args):
    global sent
    if event=="open" and not sent and isinstance(args[0],str) and args[0].startswith(copy) and args[0].endswith(("power_trace.csv","dc_points.csv")):
        sent=True
        os.write(1,b"fixture-v2 parent stdout\n")
        os.write(2,b"fixture-v2 parent stderr\n")
        pid=os.fork()
        if pid==0:
            os.write(1,b"fixture-v2 child stdout\n")
            os.write(2,b"fixture-v2 child stderr\n")
            os._exit(0)
        os.waitpid(pid,0)
sys.addaudithook(echo_at_stream)
"""
    with patch.dict(invoke.__globals__,PROBE=PROBE+extra):
        rc,out,err,events=invoke(world,"stage2")
    test.assertEqual((rc,out,err),(0,b"",b""))
    first_open=next(i for i,(kind,_) in enumerate(events) if kind=="open")
    test.assertIn(["public_bytes",wire(truth).hex()],events[:first_open])
    test.assertEqual(world.public.read_bytes(),wire(truth))
    for pipe in ("stdout","stderr"):
        payload=(world.private/pipe).read_bytes()
        for sender in ("parent","child"):
            test.assertIn(f"fixture-v2 {sender} {pipe}\n".encode(),payload)


def native_preflight(test, look, mutation, stage):
    # Native ledger placement is essential. A normalized Book intentionally
    # permits a pinned Git fallback and cannot serve as this refusal oracle.
    reader = executor()
    w = test.world(look)
    root = test.base/"native"
    native = Book(root)
    def path(name):
        if name.startswith("manifests/"):
            return reader.CAMPAIGN+"/looks/"+Path(name).stem+".manifest.json"
        if name.startswith("kits/"):
            return reader.CAMPAIGN+"/"+name
        return name

    def project(commit):
        names = subprocess.check_output(["git","-C",str(w.repo),"ls-tree","-rz","--name-only",commit])
        for entry in names.split(b"\0"):
            if not entry or entry==b"LOOKS.json":
                continue
            name = entry.decode()
            data = (w.repo/name).read_bytes()
            if name=="manifests/lm-stab-02.json":
                data = wire(dict(json.loads(data),kit_index_path=reader.CAMPAIGN+"/f2-stab/KITS.json"))
            put(root/path(name),data)

    project(w.reg)
    reg = native.seal("invented native registration")
    project(w.receipts)
    rec = native.seal("invented native receipts")
    project(w.book.head)
    bindings = [("authority/copy.json","receipt_commit"),("roster.json","receipt_commit")]
    if not w.inst:
        bindings.append(("authority/events.json","first_proven_close"))
    for name, field in bindings:
        item = read(root/name)
        item[field] = rec
        put(root/name,item)
    hashes = {path(k):sha((root/path(k)).read_bytes()) for k in w.row["input_hashes"]}
    pub = test.base/"native-public"
    (pub/look).mkdir(parents=True)
    row = dict(w.row,manifest_path=path(w.row["manifest_path"]),registration_commit=reg,
               public_root=str(pub),input_hashes=hashes)
    ledger = root/CONTROL/"LOOKS.json"
    put(ledger,{"schema":reader.LEDGER_SCHEMA,"looks":[row]})
    native.seal("invented admission")
    loader = test.base/"fixture-loader.py"
    source = b"fixture_reader = True\n"
    put(loader,source)
    original_git = subprocess.check_output
    fallback = []
    def object_read(cmd,*args,**kwargs):
        if cmd[-2:] == ["show",f"{reader.STEP3_COMMIT}:{loader}"]:
            fallback.append(True)
            return source
        return original_git(cmd,*args,**kwargs)
    with patch.multiple(reader,STEP3_PATH=str(loader),STEP3_SHA256=sha(source)), \
         patch.object(subprocess,"check_output",side_effect=object_read):
        snap = reader.Snapshot(root,look,"stage1")
        test.assertTrue(snap.native)
        census,qualified = reader.census(snap)
        test.assertGreater(len(qualified),0)
        if stage == "stage2":
            stage_name=f"{CONTROL}/stage1/{look}.json"
            put(root/stage_name,wire(census))
            row.update(status="stage1_committed",stage1_path=stage_name,stage1_sha256=sha(wire(census)))
            put(ledger,{"schema":reader.LEDGER_SCHEMA,"looks":[row]})
            native.seal("invented bound native stage one")
            reader.Snapshot(root,look,stage).check_stage1(census)
        loader.unlink()
        if mutation=="symlink":
            backing = test.base/"invented-source"
            put(backing,source)
            loader.symlink_to(backing)
        elif mutation=="drift":
            put(loader,source+b"# different\n")
        with test.assertRaises((FileNotFoundError,reader.Refusal)):
            reader.Snapshot(root,look,stage)
        test.assertEqual(fallback,[])
        test.assertFalse(w.private.exists())
        test.assertFalse((pub/look/"PUBLIC.json").exists())


def sidecar_read(test, look, position, sparse):
    # Sibling energy rows are complete. Only the common interval dependency changes.
    leg = TraceLeg(test.base)
    a = {"first":0,"middle":300,"last":590}[position]
    if sparse:
        leg.omit("sidecar", [a+4])
    signal = leg.signal()
    seen, denied = set(), set()
    active = None
    original = signal.interval_values
    def access(name, pair):
        nonlocal active
        old = active
        active = (name, *pair)
        try:
            return original(name,pair)
        finally:
            active = old
    def record(row):
        if active is None:
            denied.add("outside request")
        elif active[1:]==(a,a+10):
            seen.add(active[0])
            if sparse:
                denied.add(active)
    with patch.object(signal,"interval_values",access),observe_fields(leg.folder,record):
        # Exercise this interval before the full per-leg path can populate any cache.
        for name in CHANNEL:
            assert_scalar(test, signal.average(name,a,a+10), "coverage" if sparse else None)
        report=print_one(signal,look)
    test.assertFalse(denied,denied)
    if not sparse:
        test.assertTrue(seen, "synthetic value reader spy was silent")
    for name in CHANNEL:
        test.assertEqual(report["hold"][name]["kept"][0],59 if sparse else 60)


def public_inventory(test,look):
    world=test.world(look)
    test.stage1(world)
    truth=world.public_truth()
    fields={"look_id","commit","manifest_sha256","stage1_sha256","n_legs"}
    if look==IDS[1]:
        fields.add("n_local_dates")
    test.assertEqual(set(truth),fields)
    candidate=world.base/"v2-candidate.json"
    for doc,code in [(truth,0),(dict(truth,extra="fixture-marker"),2),
                     *( (dict(truth,**{k:True}),2) for k in fields if k.startswith("n_") )]:
        put(candidate,doc)
        rc,out,err,events=invoke(world,"validate-public","--candidate",str(candidate))
        test.assertEqual((rc,out),(code,b""),err)
        test.assertFalse(any(kind=="open" for kind,_ in events))
        test.assertFalse(world.private.exists())
        test.assertFalse(world.public.exists())


def check_before_value(test, name, raw, phase, loss):
    # This is the white-box seam for temporal order on *passing* as well as
    # failing gates. An all-valid fixture alone cannot expose parse-then-check by output.
    leg = TraceLeg(test.base)
    a,b = INTERVAL[phase]
    if loss:
        n = nominal(raw,a,b)
        omit_at(leg,raw,a,b,"last", n-((99*n-1)//100))
    adjudicated = []
    reads = []
    actual = rail_selections(leg).get(name, [])
    def adjudicate(channel,lo,hi,rail_support):
        result = original(channel,lo,hi,rail_support)
        if channel==name and (lo,hi)==(a,b) and result is None:
            # The optimistic interval ledger is not proof of missing raw identities.
            if raw=="dc_in" or any([p for p in bounds if p[0]<b and p[1]>a]
                                   == [p for p in actual if p[0]<b and p[1]>a]
                                   for _,bounds in rail_support):
                adjudicated.append((lo,hi))
        return result
    def spy(row):
        if raw=="dc_in":
            if "epoch_s" not in row or not a<=float(row["epoch_s"])<b:
                return
        elif row.get("source")!="powermetrics" or row.get("rail")!=raw or not a<=float(row["interval_start_s"])<b:
            return
        test.assertTrue(adjudicated,"raw field retrieved before a passing interval check")
        test.assertFalse(loss,"a failed interval exposed a raw field")
        reads.append(1)
    with observe_fields(leg.folder,spy):
        signal = leg.signal()
        original = signal._interval_refusal
        with patch.object(signal,"_interval_refusal",adjudicate):
            value=signal.average(name,a,b)
    assert_scalar(test,value,"coverage" if loss else None)
    test.assertEqual(bool(reads),not loss,"spy missed the admitted value path")


def binding_before_reservation(test,look):
    world=test.world(look)
    test.stage1(world)
    # The synthetic refusal makes this order test independent of filesystem
    # permission to create the one-use directory. The real-pipe case uses the worker unchanged.
    extra = r"""
def record_binding(frame,event,result):
    if event=="return" and frame.f_code.co_name=="validate_public" and isinstance(result,bytes):
        log("public_bytes",result.hex())
sys.setprofile(record_binding)
def refuse_reservation(event,args):
    if event=="os.mkdir" and args[0]==os.environ["DESC_RESERVATION"]:
        log("reservation_attempt",args[0])
        raise PermissionError("invented refusal")
sys.addaudithook(refuse_reservation)
"""
    with patch.dict(invoke.__globals__,PROBE=PROBE+extra):
        rc,out,err,events=invoke(world,"stage2")
    test.assertEqual((rc,out),(2,b""),err)
    before=events.index(["reservation_attempt",str(world.private)])
    test.assertIn(["public_bytes",wire(world.public_truth()).hex()],events[:before])
    test.assertFalse(any(kind=="open" for kind,_ in events))
    test.assertFalse(world.public.exists())
    test.assertFalse(world.private.exists())


def gap_per_look(test, look, raw, ticks):
    leg = TraceLeg(test.base)
    # Subdivide six clean rows, so losing five or six consecutive 250 ms
    # intervals cannot trip the 99% count first. Keep the header cadence fixed.
    bounds = []
    rows = []
    for lo,hi in leg.meta["rail_intervals"]:
        if not 606 <= lo < 610:
            bounds.append((lo,hi))
            continue
        mids = [lo,(lo+hi)/2,hi] if lo<607.5 else [lo,hi]
        for x,y in zip(mids,mids[1:]):
            bounds.append((x,y))
            for key,val in zip(COLS,(12,20,4)):
                if key!=raw or not 608 <= x < 608+.25*ticks:
                    rows.append(dict(zip(RAIL_HEADER,(x,y,y,"powermetrics",key,val))))
    leg.meta["rail_intervals"]=bounds
    leg.rows[RAIL_FILE]=[r for r in leg.rows[RAIL_FILE] if not 606<=float(r["interval_start_s"])<610]+rows
    leg.rows[RAIL_FILE].sort(key=lambda r:float(r["interval_start_s"]))
    test.assertGreaterEqual(sum(r["rail"]==raw for r in rows),16)
    report=print_one(leg.signal(),look)
    for name in CHANNEL:
        affected = depends(name, raw)
        reason = "meter_gap" if affected and ticks>5 else None
        assert_scalar(test,report["turn"]["energy_j"][name],reason)
        if look==IDS[0]:
            assert_scalar(test,report["gain"]["decode_w"][name],reason)


def dc_bracket(test, edge):
    # Preserve all nominal starts even when the first/last interpolation bracket is absent.
    a,b=602,606
    legs={r:[(s,s+.25,1) for s in grid(r,a,b)] for r in COLS}
    times=grid("dc_in",a,b)
    if edge=="left":
        times[0] += .005
    if edge!="right":
        times.append(b)
    signal,_=raw_fixture(test.base,legs,[(s,7) for s in times],list(range(a,b+1)))
    test.assertEqual(sum(a<=s<b for s in times),80)
    assert_scalar(test,signal.average("dc_in",a,b),None if edge=="both_present" else "meter_gap")
    assert_scalar(test,signal.average("gpu_rail",a,b),None)


def manifest_first(test, variant, fault):
    leg = TraceLeg(test.base)
    manifests = {"order": list(reversed(COLS)), "short": COLS[:-1],
                 "extra": [*COLS, "unknown"], "duplicate": [COLS[0], COLS[1], COLS[1]]}
    leg.meta["rail_manifest"] = manifests[variant]
    if fault in ("count", "mixed"):
        leg.omit("ane_power", range(40, 47))
    if fault in ("gap", "mixed"):
        shift_points(leg, "sidecar", 100)
    events = []
    class OrderedManifest(list):
        def __eq__(self, other):
            events.append("manifest")
            return super().__eq__(other)
        def __ne__(self, other):
            return not self == other
        def __iter__(self):
            events.append("manifest")
            return super().__iter__()
        def __len__(self):
            events.append("manifest")
            return super().__len__()

    class ObservedSupport(dict):
        def __getitem__(self, key):
            if key in ("rail_intervals", "rail_missing", "meter_times", "meter_counts", "sidecar_times"):
                events.append("coverage")
            return super().__getitem__(key)
        def get(self, key, default=None):
            return self[key] if key in self else default

    leg.meta["rail_manifest"] = OrderedManifest(leg.meta["rail_manifest"])
    leg.meta = ObservedSupport(leg.meta)
    def raw(row):
        events.append("raw")
    with observe_fields(leg.folder, raw):
        signal = leg.signal()
        with patch.object(signal, "_interval_refusal", wraps=signal._interval_refusal) as gate:
            assert_scalar(test, signal.average("rail_sum", 0, 600), "rail_manifest")
            gate.assert_not_called()
    test.assertIn("manifest", events)
    test.assertEqual(events[0], "manifest", events)
    test.assertNotIn("raw", events)


def bad_tail_gap(test, raw, null=null):
    leg = TraceLeg(test.base)
    # The right bracket is available, but too far from the last in-span stamp.
    if raw == "sidecar":
        leg.meta["sidecar_times"] = [t for t in leg.meta["sidecar_times"] if t < 611] + [614.]
    else:
        rows = [r for r in leg.rows[DC_FILE] if float(r["epoch_s"]) < 611]
        leg.rows[DC_FILE] = rows + [dict(epoch_s=614., watts=40.)]
        leg.meta["meter_times"] = [float(r["epoch_s"]) for r in leg.rows[DC_FILE]]
        leg.meta["meter_counts"]["decoded"] = len(leg.rows[DC_FILE])
    edges = print_one(leg.signal(), IDS[0])["edges"]
    for rail in CHANNEL[:2]:
        with test.subTest(print="lag", rail=rail):
            assert_scalar(test, edges["decode_end_lag_s"][rail], "meter_gap")
        with test.subTest(print="return", rail=rail):
            test.assertEqual(edges["rail_return_censor_s"][rail], null("meter_gap")
                             if raw == "sidecar" else null("stream_end", bound_s=1.))


def already_crossed(test, channel, direction):
    leg = TraceLeg(test.base)
    a, b = INTERVAL["prefill" if direction == "rise" else "tail"]
    value = 120 if direction == "rise" else 0
    if channel == "dc_in":
        for row in leg.rows[DC_FILE]:
            if a <= float(row["epoch_s"]) < b:
                row["watts"] = value
    else:
        for row in leg.rows[RAIL_FILE]:
            if (row["source"] == "powermetrics" and row["rail"] in PRINT_INPUTS[channel]
                    and a <= float(row["interval_start_s"]) < b):
                row["power_w"] = value
    e = print_one(leg.signal(), IDS[0])["edges"]
    if direction == "rise":
        test.assertEqual(e["rise_s"][channel], null("crossed_before_span"))
    lags = e["onset_lag_s" if direction == "rise" else "decode_end_lag_s"]
    for rail in CHANNEL[:2] if channel == "dc_in" else (channel,):
        test.assertEqual(lags[rail], null("crossed_before_span"))


def decisive_rail_row(test, channel, last_rail, present):
    # Both tapes have the same nominal ledger, file length in rows, stamps and
    # sidecar. Only the final row's source decides whether 98 or 99 qualify.
    # Even a correct final scalar cannot excuse an earlier field projection.
    leg = TraceLeg(test.base)
    final = []
    rows = []
    for row in leg.rows[RAIL_FILE]:
        stamp = float(row["interval_start_s"])
        if not 0 <= stamp < 100 or row["source"] != "powermetrics":
            continue
        if row["rail"] == last_rail:
            if stamp == 19:
                row = dict(row, source="unrelated")
            if stamp == 99:
                final.append(dict(row, source="powermetrics" if present else "unrelated"))
                continue
        rows.append(row)
    test.assertEqual(len(final), 1)
    leg.rows[RAIL_FILE] = rows + final
    leg.meta["rail_intervals"] = [(i, i+1) for i in range(100)]
    leg.meta["sidecar_times"] = list(range(101))
    decisive_seen = False
    projected = []

    def project(row):
        if "power_w" in row:
            test.assertTrue(decisive_seen, "raw field projected before the decisive row arrived")
            test.assertTrue(present, "failed interval exposed a raw field")
            projected.append(row["rail"])

    original = WatchedRow.__init__
    def observe_arrival(mapping, row, spy):
        nonlocal decisive_seen
        original(mapping, row, spy)
        if row.get("rail") == last_rail and float(row["interval_start_s"]) == 99:
            decisive_seen = True

    with observe_fields(leg.folder, project), patch.object(WatchedRow, "__init__", observe_arrival):
        signal = leg.signal()
        value = signal.average(channel, 0, 100)
    assert_scalar(test, value, None if present else "coverage")
    test.assertEqual(bool(projected), present, "spy did not see the admitted rail path")


def retained_rows(test, channel, raw, direction):
    # Catch a cache of whole raw row mappings even if it never calls row["power_w"]
    # until a later request. Weak references keep the observer from retaining a row.
    import weakref
    leg = TraceLeg(test.base)
    permitted, refused = (INTERVAL["hold"], INTERVAL["tail"]) if direction == "forward" else (
        INTERVAL["tail"], INTERVAL["hold"])
    a, b = refused
    count = nominal(raw, a, b)
    omit_at(leg, raw, a, b, "middle", count-((99*count-1)//100))
    candidates, touched, positive = [], [], []
    def watch(row):
        if raw == "dc_in":
            return float(row["epoch_s"]) if "epoch_s" in row else None
        if row.get("source") == "powermetrics" and row.get("rail") == raw:
            return float(row["interval_start_s"])
        return None
    def project(row):
        stamp = watch(row)
        if stamp is not None:
            if a <= stamp < b:
                touched.append(stamp)
            elif permitted[0] <= stamp < permitted[1]:
                positive.append(stamp)
    original = WatchedRow.__init__
    def register(self, row, spy):
        original(self, row, spy)
        stamp = watch(row)
        if stamp is not None and a <= stamp < b:
            candidates.append(weakref.ref(self))
    with observe_fields(leg.folder, project), patch.object(WatchedRow, "__init__", register):
        signal = leg.signal()
        assert_scalar(test, signal.average(channel, *permitted), None)
        test.assertTrue(positive, "no admitted raw field reached the observation seam")
        test.assertFalse(touched, f"outside field read before failed interval check: {touched[:2]}")
        test.assertFalse(any(ref() is not None for ref in candidates), "whole raw row cached across requests")
        assert_scalar(test, signal.average(channel, *refused), "coverage")
        test.assertFalse(touched, f"raw value retrieved on the failed request: {touched[:2]}")
        test.assertFalse(any(ref() is not None for ref in candidates), "failed request retained a raw row")


# Separately discoverable cases; no expected failures, skips or baseline edits.

# RL-190 3.8. All return times below are read from the instrument print.
def recovery_gap_reason(channel, raw, fault):
    reason = window_reason(channel, raw, fault)
    return "gap_over_u1" if reason == "meter_gap" else reason


def tail_with_end(reason, **fields):
    # RL-190 3.8. The rail-return field's bound is the elapsed stream end.
    if reason in ("coverage", "meter_gap"):
        fields["bound_s"] = 1.0
    return null(reason, **fields)


def prefix_edges(folder, winner, faults=(), unobserved=12.0):
    leg, start, _ = recovery_fixture(folder, winner, STRIDE_S)
    origin = start - unobserved
    leg.meta.update(completion_log_raw_s=1000 + origin, warmup_stage_raw_s=1005 + origin)
    for index, fault in faults:
        window_fault(leg, "sidecar", start + 10*index, 10, fault)
    return print_one(leg.signal(), IDS[0])["edges"]


def hand_prefix(test, winner, faults, value, reasons):
    edges = prefix_edges(test.base, winner, faults)
    assert_recovery(test, edges, dict.fromkeys(CHANNEL, value),
                    {channel: list(reasons) for channel in CHANNEL})


def terminal_leg(folder, anchor):
    # Quiet tiles average 300 per rail and 300 on DC, with zero between-tile SD.
    # Moving the window grid by 5 or 6 s pairs a negative impulse with the
    # next tile's larger positive impulse. Every judged recovery window fails.
    leg = TraceLeg(folder)
    for raw in RAW_INPUTS:
        leg.omit(raw, range(-20, anchor))
    leg.meta["rail_intervals"] = [r for r in leg.meta["rail_intervals"] if r[0] >= anchor]
    leg.meta.update(sampling_started_raw_s=1000+anchor, completion_log_raw_s=988+anchor,
                    warmup_stage_raw_s=993+anchor)
    def level(t):
        if t < 0:
            return 400.0
        tile, offset = divmod(t, 10)
        return 300 + (tile+1) * ((offset == 2) - (offset == 7))
    for row in leg.rows[RAIL_FILE]:
        t = float(row["interval_start_s"])
        if t < 600 and row["source"] == "powermetrics":
            row["power_w"] = level(t)
    for row in leg.rows[DC_FILE]:
        t = float(row["epoch_s"])
        if t <= 600:
            row["watts"] = level(t)
    return leg


def terminal_edges(folder, vector):
    anchor = -15
    leg = terminal_leg(folder, anchor)
    if vector == "F":
        leg.omit("sidecar", [anchor+15])
    else:
        # All 61 complete recovery tiles have nine points. Alternate which
        # half loses a point so the independently aligned quiet SD is defined.
        starts = range(anchor, 595, 10)
        lost = [a + (2 if j % 2 == 0 else 7) for j, a in enumerate(starts)]
        leg.omit("sidecar", lost)
        # Preserve 600 s hold coverage with extra distinct points in the
        # unsearched final fragment. No inter-stamp gap exceeds two seconds.
        leg.meta["sidecar_times"] = sorted(leg.meta["sidecar_times"] +
                                          [596 + i/128 for i in range(1, 62)])
    printed = print_one(leg.signal(), IDS[0])
    return printed


def hand_terminal(test, vector):
    printed = terminal_edges(test.base, vector)
    for ch in CHANNEL:
        for field in ("mean_w", "sd10_w"):
            test.assertIsInstance(printed["hold"][ch][field], (float, int))
    # Last complete window ends at 595; origin is -27. [595,600) has no vote.
    count = 1 if vector == "F" else 61
    assert_recovery(test, printed["edges"], dict.fromkeys(CHANNEL, null("not returned", bound_s=622.)),
                    {ch: ["coverage"]*count for ch in CHANNEL})


def hand_stream_end(test, final_loss):
    # Rail stream stops inside [586,596). DC and sidecar continue. The whole
    # hold remains count- and gap-admissible on both rails at this cutoff.
    leg = terminal_leg(test.base, -14)
    if final_loss:
        leg.omit("gpu_power", [580])
    end = 595.75
    rows = [r for r in leg.rows[RAIL_FILE] if float(r["interval_start_s"]) < end]
    for r in rows:
        if float(r["interval_end_s"]) > end:
            r.update(interval_end_s=end, timestamp_s=end)
    leg.rows[RAIL_FILE] = rows
    leg.meta["rail_intervals"] = [(a, min(b, end)) for a, b in leg.meta["rail_intervals"] if a < end]
    signal = leg.signal()
    with patch.object(signal, "average", wraps=signal.average) as observed:
        printed = print_one(signal, IDS[0])
    edges = printed["edges"]
    for ch in CHANNEL[:2]:
        with test.subTest(channel=ch):
            test.assertIsInstance(printed["hold"][ch]["mean_w"], (int, float))
            spans = [call.args[1:] for call in observed.call_args_list if call.args[0] == ch]
            test.assertIn((576, 586), spans)
            test.assertFalse(any(a == 586 and b > a for a, b in spans), spans[-5:])
            test.match(edges["recovery_s"][ch], null("not returned", bound_s=612.))
            test.match(edges["recovery_skipped_windows"][ch], int(final_loss))
            test.match(edges.get("recovery_skip_reasons", {}).get(ch, []),
                       ["coverage"] if final_loss else [])


def maximum_case(test, winner):
    # RL-190 3.8 and RL-187 3.7. The freezing line consumes private per-leg
    # prints. The consumer below checks their sufficiency without adding a
    # design decision to the description executor's output inventory.
    rows = {"ordinary": prefix_edges(test.base/"ordinary", 2),    # 32 s
            "under": prefix_edges(test.base/"under", 0, unobserved=37.25 if winner=="under" else 12.)}
    if winner == "not_returned":
        rows["exhausted"] = terminal_edges(test.base/"exhausted", "G")["edges"]
    leg = TraceLeg(test.base/"no-threshold")
    leg.meta["rail_manifest"] = COLS[::-1]  # Other channels still contribute.
    rows["without_sum"] = print_one(leg.signal(), IDS[0])["edges"]
    # A genuine over-1-s lag from the third invented leg triggers the fallback.
    cut = TraceLeg(test.base/"lag")
    traces(cut.folder, 1, 2)
    for name in cut.rows:
        with (cut.folder/name).open(newline="") as stream:
            cut.rows[name] = list(csv.DictReader(stream))
    cut.meta = read(cut.folder/"support.json")
    rows["cut_lag"] = print_one(cut.signal(), IDS[0])["edges"]
    lag = rows["cut_lag"]["decode_end_lag_s"]
    test.assertTrue(any(isinstance(x, dict) and x["reason"] == "over 1 s" for x in lag.values()))
    contributions, excluded = {}, []
    for key, edges in rows.items():
        for ch in CHANNEL:
            v = edges["recovery_s"][ch]
            if type(v) in (int, float):
                n = v
            else:
                test.assertIsNone(v["value"])
                if v["reason"] == "under":
                    n = v["bound_s"]
                elif v["reason"] == "not returned":
                    n = 600
                else:
                    test.assertTrue(v["reason"])
                    excluded.append((key, ch))
                    continue
            contributions[key, ch] = n
    test.assertEqual(excluded, [("without_sum", "rail_sum")])
    test.assertEqual(len(contributions), 3*len(rows)-1)
    # Check the winning contributor, all three normalized inputs and the
    # unrounded maximum before either clamp can hide an incorrect mapping.
    max_key = {"ordinary":"ordinary", "under":"under", "not_returned":"exhausted"}[winner]
    expected = {"ordinary":32., "under":37.25, "not_returned":600}[winner]
    for ch in CHANNEL:
        test.assertEqual(contributions[max_key, ch], expected)
    largest = max(contributions.values())
    test.assertEqual(largest, expected)
    test.assertEqual(min(600, max(120, 5*largest)),
                     {"ordinary":160, "under":186.25, "not_returned":600}[winner])
    test.assertEqual(min(60, max(10, math.ceil(largest))),
                     {"ordinary":32, "under":38, "not_returned":60}[winner])


def no_thresholds(test):
    # RL-190 3.8 / RL-187 3.7 Amends (3.9). Leave all three leg/channel
    # identities visible. The empty maximum has no observed contributor.
    leg = TraceLeg(test.base)
    leg.omit("sidecar", range(10, 100, 10))
    printed = print_one(leg.signal(), IDS[0])
    edges = printed["edges"]
    test.assertEqual(set(edges["recovery_s"]), set(CHANNEL))
    eligible = []
    for ch in CHANNEL:
        test.assertIsNone(printed["hold"][ch]["mean_w"]["value"])
        result = edges["recovery_s"][ch]
        if type(result) in (int, float):
            eligible.append(result)
        else:
            test.assertIsNone(result["value"])
            test.assertTrue(result["reason"])
            if result["reason"] in ("under", "not returned"):
                eligible.append(result.get("bound_s"))
    test.assertEqual(eligible, [])
    for lag in edges["decode_end_lag_s"].values():
        test.assertIsNone(lag["value"])
    # RL-190 3.9 supplies the recovery duration when there is no contributor.
    rest = min(600, max(120, 5*max(eligible))) if eligible else 600
    test.assertEqual(rest, 600)


def short_rail_tail(test):
    # RL-190 3.8. The observed stream ends 0.75 s after the last token.
    # A count loss inside that tail and the non-unit bound must both survive.
    leg = TraceLeg(test.base)
    leg.omit("gpu_power", [610.25])
    leg.rows[RAIL_FILE] = [r for r in leg.rows[RAIL_FILE] if float(r["interval_end_s"]) <= 610.75]
    leg.meta["rail_intervals"] = [r for r in leg.meta["rail_intervals"] if r[1] <= 610.75]
    printed = print_one(leg.signal(), IDS[0])
    for ch in CHANNEL[:2]:
        with test.subTest(channel=ch):
            test.match(printed["edges"]["rail_return_censor_s"][ch], null("coverage", bound_s=.75))


def git_ok(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def reservation_boundary(test, world):
    # Observe the real mkdir attempt and stop it before creating anything.
    probe = """
def reservation(event,args):
    if event == "os.mkdir" and args[0] == os.environ["DESC_RESERVATION"]:
        log("boundary", args[0])
        raise PermissionError("synthetic boundary")
sys.addaudithook(reservation)
"""
    with patch.dict(invoke.__globals__, PROBE=PROBE+probe):
        rc, out, err, events = invoke(world, "stage2")
    test.assertEqual((rc, out), (2, b""), err)
    test.assertFalse(any(kind == "open" for kind, _ in events))
    test.assertFalse(world.private.exists())
    test.assertFalse(world.public.exists())
    return [p for kind, p in events if kind == "boundary"]


def merge_fixture(book, first, other):
    # Add the second parent without changing the current fixture tree.
    tree = book.tree(book.path)
    env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="test@example.invalid",
               GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="test@example.invalid")
    book.head = subprocess.check_output(
        ["git", "-C", str(book.path), "commit-tree", tree, "-p", first, "-p", other],
        input=b"merge the two invented records\n", env=env).decode().strip()


def graph_case(test, look, placement):
    # RL-190 3.4. All loose objects, receipts and commits are synthetic.
    # Remove the final bytes from early history; a new label on an old
    # identical manifest would not expose a path/history-based age check.
    seal = Book.seal
    manifests, commits = {}, {}
    def snapshot(book, label):
        if label == "register public designs and identifiers before any close":
            for path in (book.path/"manifests").glob("*.json"):
                manifests[path] = path.read_bytes()
                path.unlink()
        if label == "close snapshot" and placement == "same":
            for path, data in manifests.items():
                put(path, data)
        oid = seal(book, label)
        if label == "register public designs and identifiers before any close" and placement == "parallel":
            for path, data in manifests.items():
                put(path, data)
            commits["manifest"] = seal(book, "register final bytes on a separate branch")
            for path in manifests:
                path.unlink()
            book.head = oid
        if label == "close snapshot":
            commits["receipts"] = oid
            if placement == "same":
                commits["manifest"] = oid
            else:
                for path, data in manifests.items():
                    put(path, data)
                if placement == "parallel":
                    merge_fixture(book, oid, commits["manifest"])
                else:
                    commits["manifest"] = seal(book, "register the final manifests after close")
        return oid
    save = World.save_row
    def bind_registration(world):
        world.reg = world.row["registration_commit"] = commits["manifest"]
        save(world)
    with patch.object(Book, "seal", snapshot), patch.object(World, "save_row", bind_registration):
        w = test.world(look)
    name = str(w.man.relative_to(w.repo))
    test.assertEqual(git_ok(w.repo, "cat-file", "-e", f"{w.receipts}:{name}"), placement=="same")
    test.assertEqual(git_ok(w.repo, "merge-base", "--is-ancestor", w.receipts, w.reg), placement != "parallel")
    test.assertEqual(git_ok(w.repo, "merge-base", "--is-ancestor", w.reg, w.receipts), placement == "same")
    test.stage1(w)
    test.assertTrue(git_ok(w.repo, "merge-base", "--is-ancestor", w.reg, w.stage1_commit))
    test.assertEqual(reservation_boundary(test, w), [str(w.private)])


def sibling_manifest(test, look):
    w = test.world(look)
    rc, _, err, _ = invoke(w, "stage1")
    test.assertEqual(rc, 0, err)
    # Registration bytes and the stage-1 projection are valid. The stated
    # final registration is on a sibling of the stage-1 binding.
    parent = w.book.head
    w.book.head = w.reg
    sibling = w.book.seal("register identical final bytes on an unmerged branch")
    w.book.head = parent
    w.row["registration_commit"] = sibling
    w.bind()
    name = str(w.man.relative_to(w.repo))
    test.assertEqual(subprocess.check_output(["git","-C",str(w.repo),"show",f"{sibling}:{name}"]),
                     w.man.read_bytes())
    test.assertFalse(git_ok(w.repo, "merge-base", "--is-ancestor", sibling, w.stage1_commit))
    merge_fixture(w.book, w.stage1_commit, sibling)
    tip = w.book.seal("advance origin/main after stage one")
    test.assertTrue(git_ok(w.repo, "merge-base", "--is-ancestor", sibling, tip))
    test.assertEqual(reservation_boundary(test, w), [])


def unbound_stage(test, look):
    w = test.world(look)
    rc, _, err, _ = invoke(w, "stage1")
    test.assertEqual(rc, 0, err)
    # Consistent census, working ledger and index. No commit contains them.
    w.row.update(status="stage1_committed", stage1_path=str(w.stage.relative_to(w.repo)),
                 stage1_sha256=sha(w.stage.read_bytes()))
    w.save_row()
    subprocess.run(["git","-C",str(w.repo),"add","--","LOOKS.json",w.row["stage1_path"]],check=True)
    test.assertFalse(git_ok(w.repo, "cat-file", "-e", "HEAD:"+w.row["stage1_path"]))
    test.assertEqual(reservation_boundary(test, w), [])
    w.bind()
    test.assertEqual(reservation_boundary(test, w), [str(w.private)])


def receipt_digest(test, look, mutation, member):
    # Rebuild the receipt snapshot and every ledger hash around the mutation.
    # Another kit's genuine digest is a valid SHA; the issue agrees with it.
    seal = Book.seal
    def snapshot(book, label):
        if label == "close snapshot":
            family = "inst" if look == IDS[0] else "stab"
            kit, pos = (2, 1) if member == "qualified" else (1, 11)
            folder = book.path/"ops"/f"span-f2-{family}-{kit:02}-L{pos:03}"
            for filename in ("runner_receipt.json", "issue.json"):
                path = folder/filename
                doc = read(path)
                if mutation in ("missing", "both_missing"):
                    if filename == "issue.json" and mutation == "missing":
                        continue
                    del doc["kit_sha256"]
                else:
                    doc["kit_sha256"] = sha((book.path/"kits"/f"f2-{family}-03.json").read_bytes())
                put(path, doc)
        return seal(book, label)
    with patch.object(Book, "seal", snapshot):
        w = test.world(look)
    test.refused(w, "stage1")
    test.assertFalse(w.stage.exists())


def register_rl190():
    for letter, winner, faults, value, reasons in (
            ("A", 2, ((1,"count"),), 32., ("coverage",)),
            ("B", 2, ((1,"gap"),), 32., ("gap_over_u1",)),
            ("C", 2, ((1,"mixed"),), 32., ("coverage",)),
            ("D", 0, ((0,"count"),), 22., ("coverage",)),
            ("E", 0, (), null("under", bound_s=12.), ())):
        add(f"rl190_38_{letter}", hand_prefix, winner, faults, value, reasons)
    for letter in ("F", "G"):
        add(f"rl190_38_{letter}", hand_terminal, letter)
    for loss in (False, True):
        add("rl190_38_H_"+("last_skipped" if loss else "last_judged"), hand_stream_end, loss)
    add("rl190_38_maximum_no_contributors", no_thresholds)
    add("rl190_38_tail_coverage_bound_075", short_rail_tail)
    for winner in ("ordinary","under","not_returned"):
        add(f"rl190_38_maximum_{winner}", maximum_case, winner)
    for look in IDS:
        prefix = "rl190_34_"+look.replace("-", "_")
        for placement in ("after", "same", "parallel"):
            add(f"{prefix}_manifest_{placement}_receipts", graph_case, look, placement)
        add(f"{prefix}_manifest_off_stage1_line", sibling_manifest, look)
        add(f"{prefix}_stage1_commit_before_reservation", unbound_stage, look)
        for mutation, member in product(("missing","both_missing","different"), ("qualified","excluded")):
            add(f"{prefix}_receipt_{mutation}_kit_sha_{member}", receipt_digest, look, mutation, member)



def register_v2():
    def case(family, fn, *args):
        def identifier(x):
            return str(x).replace("lm-inst-01","inst").replace("lm-stab-01","stab").replace("-", "m").replace("+","p").replace(".","_")
        add("v2_"+family+"_"+"_".join(identifier(x) for x in args),fn,*args)

    for channel, inputs in PRINT_INPUTS.items():
        for phase, (a, b) in INTERVAL.items():
            for raw, offset, gap in product((*inputs, "sidecar"), (-1,0,1), ("none","sidecar","dc_in","both")):
                if count_floor(raw, a, b)+offset >= 0:
                    case("boundary", boundary, phase, channel, raw, offset, gap)
        for look, position in product(IDS[:2], POSITION):
            phases = ("hold","tiles","turn","prefill","level","decode","recovery","tail") if look==IDS[0] else ("hold","tiles","turn")
            for raw, phase in product(inputs, phases):
                case("read", read_order, look, channel, raw, phase, position)
            for raw, width, fault in product(inputs, WIDTH, ("count","gap","mixed")):
                case("sd", window_sd, look, channel, raw, width, position, fault)
            # A common sidecar fault affects every print. One case checks all siblings.
            if channel == CHANNEL[0]:
                for width, fault in product(WIDTH, ("count","gap","mixed")):
                    case("sd", window_sd, look, channel, "sidecar", width, position, fault)
        for raw, phase, loss in product(inputs, INTERVAL, (False,True)):
            case("order", check_before_value, channel, raw, phase, loss)
        for raw, delta in product((*inputs,"sidecar"), (-.03125,0,.03125)):
            for period, phase in ((1,"hold"),(.25,"turn"),(.125,"turn")):
                case("gap", gap_limit_v2, channel, raw, period, delta, phase)
        for raw, direction in product(inputs, ("forward","backward")):
            case("cache", retained_rows, channel, raw, direction)
        for direction in ("rise","fall"):
            case("crossing", already_crossed, channel, direction)
    for channel in ("gpu_rail", "rail_sum"):
        for raw, present in product(PRINT_INPUTS[channel], (False, True)):
            case("decisive", decisive_rail_row, channel, raw, present)
    for edge in ("left","right","both_present"):
        case("bracket",dc_bracket,edge)
    for look,raw,ticks in product(IDS[:2],COLS,(4,5,6)):
        case("period",gap_per_look,look,raw,ticks)
    for look,raw,pos in product(IDS[:2],(*COLS,"dc_in"),POSITION):
        case("turn",turn_projection,look,raw,pos)
        for gap,offset in product(("none","sidecar","dc_in","both"),(-1,0,1)):
            case("hold",look_counts,look,raw,pos,gap,offset)
    for raw in RAW_INPUTS:
        # Before, at, and after the first otherwise-qualifying candidate. Mixed and
        # multiple failures distinguish a per-channel skip list from a leg-wide flag.
        for fault in ("count", "gap", "mixed"):
            for bad,winner in ((0,0),(0,5),(2,5),(4,5),(3,3),(4,1),(4,0)):
                # RL-190 3.8 B/C: update only a gap actually printed before the winner.
                changed = bad <= winner and (fault == "gap" or (fault == "mixed" and raw != "sidecar"))
                fn = partial(recovery_prefix, window_reason=recovery_gap_reason) if changed else recovery_prefix
                add(f"v2_recovery_{raw}_{fault}_bad{bad}_winner{winner}",
                    fn,raw,((bad,fault),),winner,STRIDE_S)
        # RL-190 3.8 B: the second skipped window has a count-passing U1 gap.
        add(f"v2_recovery_{raw}_multiple",partial(recovery_prefix, window_reason=recovery_gap_reason),raw,((0,"count"),(2,"gap"),(4,"mixed")),4,STRIDE_S)
        for pos in POSITION if raw!="sidecar" else ("first",):
            # RL-190 3.8: failed rail-tail admission and the stream-end bound both print.
            fn = partial(tail_reason, null=tail_with_end) if raw != "dc_in" else tail_reason
            case("tail",fn,raw,pos)
    add("v2_recovery_audit5_9_of_10",audit5_window_zero)
    for raw in ("sidecar","dc_in"):
        # RL-190 3.8: only the shared sidecar gap also vetoes the rail return.
        fn = partial(bad_tail_gap, null=tail_with_end) if raw == "sidecar" else bad_tail_gap
        case("tailgap",fn,raw)
    for late, mode in product((*COLS,"dc_in"),("under","nonreturn")):
        case("anchor",staggered_grid,late,mode,STRIDE_S)
    for raw, placement in product(RAW_INPUTS, ("complete","incomplete","both")):
        case("terminal", staggered_grid, "dc_in", "nonreturn", STRIDE_S, raw, placement)
    for pair,offset in product(combinations(COLS,2),(-1,0,1)):
        add("v2_join_"+"_".join(pair)+"_"+str(offset).replace("-","m"),sum_intersection,pair,offset)
    for variant, fault in product(("order","short","extra","duplicate"),("none","count","gap","mixed")):
        case("manifestfirst",manifest_first,variant,fault)
    for look in IDS[:2]:
        for pos,sparse in product(POSITION,(False,True)):
            case("sidecar_read",sidecar_read,look,pos,sparse)
        case("inventory",public_inventory,look)
        case("binding",binding_before_reservation,look)
        for order in permutations(COLS):
            add("v2_manifest_"+look.replace("-","_")+"_"+"_".join(order),manifest_order,look,order)
        for mutation,stage in product(("missing","drift","symlink"),("stage1","stage2")):
            case("native",native_preflight,look,mutation,stage)
        case("publication",public_order,look)


register_v2()
register_rl190()


if __name__=="__main__":
    unittest.main()

