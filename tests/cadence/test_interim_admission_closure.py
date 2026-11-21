"""Frozen RL-184 §3.3 black-box admission tests. Run with unittest or execute --report.

Each generated test has its own stable identifier and expected outcome. The historical
runner corpus is input to the suite. Production admission code never supplies an oracle.
"""
from __future__ import annotations

from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import dataclass
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
DATA = HERE.with_name("interim_admission")
RECEIPT = "runner_receipt.json"
EVENTS = "legs/L001/runtime/runs/cadence-leg/events.jsonl"
SOAK = "soak/soak_reference.json"
LOOK = "lm-interim-01"
PINS = ("b4b6aeb19", "2d347f721", "6e9d42f1d")
BUNDLE = EVENTS.rsplit("/", 1)[0]
SALVAGE = BUNDLE + "/outputs/align_runtime_events.jsonl"
ROOT_ALIAS = BUNDLE + "/align_runtime_events.jsonl"
TIMESTAMP_READER = "joulewise/cadence_looks/time_fields.py"


def wire(doc):
    return json.dumps(doc, separators=(",", ":"), ensure_ascii=True).encode() + b"\n"

def actor(repo):
    # Isolated child. Its only repository on sys.path is the pinned disposable mini-repo.
    sys.path.insert(0, str(repo))
    from scripts import cadence_look_run as cli
    # Only the immutable code/manifest/input-commit checks are memoized in the large matrix.
    # Every cache entry comes from the real function; audit-3 and the full positive controls run uncached.
    if "--fixed-auth" in sys.argv:
        def memo(fn):
            saved={}
            def checked(*args, **kwargs):
                key=repr((args, sorted(kwargs.items())))
                if key not in saved: saved[key]=fn(*args, **kwargs)
                return saved[key]
            return checked
        for name in ("verify_pins","require_inputs_committed","ledger_gate"):
            setattr(cli.M,name,memo(getattr(cli.M,name)))
        # The copied Python sources are immutable. Refresh their real digest inventory
        # whenever an import changes the module/file list, including lazy CLI imports.
        real_hashes = cli.code_hashes
        source_cache = {}
        def fixed_source_hashes():
            imports = tuple((name, getattr(mod, "__file__", None)) for name, mod in sys.modules.copy().items())
            if imports not in source_cache:
                source_cache[imports] = real_hashes()
            return source_cache[imports].copy()
        cli.code_hashes = fixed_source_hashes
    observations = None
    preflight = cli.validate_runtime_bundles
    def observe_preflight(*args, **kwargs):
        observations["admission_complete"] = False
        result = preflight(*args, **kwargs)
        observations["admission_complete"] = True
        return result
    cli.validate_runtime_bundles = observe_preflight

    def observe(event, args):
        if observations is None or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = os.fsdecode(args[0])
        base = os.path.basename(path)
        if event in ("os.rename","os.link","os.symlink") and isinstance(args[1],(str,bytes,os.PathLike)):
            destination=os.path.basename(os.fsdecode(args[1]))
            if destination=="PUBLIC.json": observations["public_attempt"]=True
            if destination in ("RESTRICTED","synthetic-reservation"): observations["reservation_attempt"]=True
        if event == "os.mkdir" and base in ("RESTRICTED", "synthetic-reservation"):
            observations["reservation_attempt"] = True
        if event != "open":
            return
        if base == "PUBLIC.json":
            observations["public_attempt"] = True
        if path in observations["expected_paths"]:
            observations["before"].add(path)
        if path == observations["target"]:
            observations["target_read"] = True
        if base == RECEIPT:
            observations["receipt_read"] = True
        private="/RESTRICTED/" in path or "/synthetic-reservation/" in path
        if (private or base in ("power_trace.csv", "rich_telemetry.jsonl", "powermetrics.plist",
                     "segment_energy.json", "energy.json", "responses.json", "response.json", "twin.json")
                or "/hazards/meter/" in path.replace(os.sep, "/")):
            if not observations["opens"]:
                observations["not_checked_before_trace"] = len(observations["expected_paths"]-observations["before"])
            observations["opens"].add(base)
            if private or base in ("energy.json", "responses.json", "response.json", "segment_energy.json", "twin.json"):
                observations["responses"].add(base)
            if not observations["admission_complete"]:
                observations["early_opens"].add(base)
            meter = "/hazards/meter/stream-" in path
            if meter or base == "power_trace.csv":
                frame = sys._getframe(1)
                while frame and not frame.f_code.co_filename.startswith(str(repo) + os.sep):
                    frame = frame.f_back
                caller = os.path.relpath(frame.f_code.co_filename, repo) if frame else "unknown"
                source = "meter" if meter else "power"
                observations["timestamp_readers"].add(source + "=" + caller)
    sys.addaudithook(observe)
    for line in sys.stdin:
        req = json.loads(line)
        observations = dict(admission_complete=False, early_opens=set(), timestamp_readers=set(), target=req["target"], target_read=False, receipt_read=False,
                            expected_paths=set(req["expected"]),before=set(),not_checked_before_trace=0,
                            opens=set(), responses=set(), public_attempt=False, reservation_attempt=False)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
            rc = cli.main(req["args"])
        row, observations = observations, None
        del row["expected_paths"],row["before"]
        row.update(early_opens=sorted(row["early_opens"]), timestamp_readers=sorted(row["timestamp_readers"]), opens=sorted(row["opens"]), responses=sorted(row["responses"]), rc=rc, err=err.getvalue()[:400])
        print(json.dumps(row), flush=True)

def load_corpus():
    return {pin:json.loads(gzip.decompress((DATA / (pin+".json.gz")).read_bytes())) for pin in PINS}

JOURNAL_PROFILES=("empty-stream","endpoint-error","hold","controller")

def journals(pin, profile="journals"):
    prefix=EVENTS.rsplit("/",1)[0]+"/"
    docs=json.loads(gzip.decompress((DATA/(pin+"-"+profile+".json.gz")).read_bytes()))
    return {prefix+k:v for k,v in docs.items()}

def soak():
    return dict(schema="joulewise.align.r1_soak_reference.v1", source_segment="idle_soak", source_output="span/soak/idle_soak",
                attempt=0,window_s=1200,sensors_c={"TV0h":58.,"TV1h":58.},
                detrended={s:dict(mean_c=58.,detrended_sd_c=0.,slope_c_per_min=0.,settled=True,window_s=1200,window_reads=1200) for s in ("TV0h","TV1h")},
                sensor_roles=None)

@dataclass(frozen=True)
class Case:
    family: str
    writer: str
    branch: str
    file: str = RECEIPT
    path: tuple = ()
    op: str = "control"
    value: object = None
    label: str = ""
    @property
    def name(self):
        parts=(self.family,self.writer,self.branch,self.file,*self.path,self.op,self.label)
        return "/".join(map(str,parts)).rstrip("/")

def doc_bytes(file, doc):
    return b"".join(map(wire,doc)) if file.endswith(".jsonl") else wire(doc)

def mutate(c, docs):
    doc=deepcopy(docs[c.file])
    if c.op == "control":
        return doc_bytes(c.file,doc)
    if c.op == "absent-file":
        return None
    if c.op == "reencode":
        def reverse_members(value):
            if isinstance(value, dict):
                return {k: reverse_members(value[k]) for k in reversed(value)}
            if isinstance(value, list):
                return [reverse_members(item) for item in value]
            return value
        doc = reverse_members(doc)
        if c.file.endswith(".jsonl"):
            return b"".join(("  " + json.dumps(row, separators=(", ", ": ")) + " \r\n").encode() for row in doc)
        return (json.dumps(doc, indent=3) + " \r\n").encode()
    if c.op == "tool-pair":
        # workload.py:582–611, with a plausible generic call id and start/end pair.
        # Only the registered StepTask/backend makes the entire pair unreachable.
        for kind in ("phase_start", "phase_end"):
            doc.append(dict(timestamp_s=doc[-1]["timestamp_s"], event_type=kind, phase="align_tool_0_0",
                            message="fixture_tool", metadata={"align_turn_index": 0, "tool_call_id": "call-0"}))
        return doc_bytes(c.file, doc)
    if c.op == "partial-line":
        head, _, tail = doc_bytes(c.file, doc).rstrip(b"\n").rpartition(b"\n")
        return (head + b"\n" if head else b"") + tail[:-1]
    if c.op == "raw":
        raw=doc_bytes(c.file,doc)
        first, *rest=raw.splitlines(keepends=True)
        if c.value in ("utf16","bom","utf8"):
            if c.value=="utf16": return raw.decode().encode("utf-16")
            return (b"\xef\xbb\xbf" if c.value=="bom" else b"\xff")+raw
        if c.value == "concat": return raw+raw
        if c.value == "blank": return b"\n"+raw
        if c.value == "trailing": return first.rstrip()+b",\n"+b"".join(rest)
        key=next(iter(doc[0] if c.file.endswith(".jsonl") else doc))
        member=json.dumps(key).encode()
        token={"duplicate":b"null","NaN":b"NaN","Infinity":b"Infinity","-Infinity":b"-Infinity",
               "overflow":b"1e999","comment":b"/*abc*/0"}[c.value]
        if c.value != "duplicate":
            # Replace an existing value rather than smuggling in a second defect.
            from json import JSONDecoder
            text=first.decode()
            start=text.index(":", text.index(member.decode()))+1
            _,end=JSONDecoder().raw_decode(text[start:])
            return text[:start].encode()+token+text[start+end:].encode()+b"".join(rest)
        duplicate=wire((doc[0] if c.file.endswith(".jsonl") else doc)[key]).strip()
        return b"{"+member+b":"+duplicate+b","+first[1:]+b"".join(rest)
    node=doc
    for k in c.path[:-1]: node=node[k]
    k=c.path[-1] if c.path else None
    if c.op=="replace": node[k]=c.value
    elif c.op=="remove": del node[k]
    elif c.op=="rename": node["unissued_"+str(k)]=node.pop(k)
    elif c.op=="add": (doc if k is None else node[k])["unissued_member"]=True
    elif c.op=="copy": node.insert(k,deepcopy(node[k]))
    elif c.op=="swap": node[k],node[k+1]=node[k+1],node[k]
    elif c.op=="insert-null": (doc if k is None else node[k])["error"]=None
    else: raise ValueError(c)
    return doc_bytes(c.file,doc)

# An enum or cross-record equality restricts these strings. Free writer error text, stdout and paths
# may themselves contain digits; a string-to-string change is never generically a type mutation.
ENUMS={"runner_kind","schema","name","event_type","phase","leg_status","g0_shape","g0_role","start_band",
       "chain_outcome","outcome","redo_reason","message","leg_id","campaign_id","frozen_commit","sha256",
       "output_dir","phase_boundary_method"}
NULLABLE={"redo_reason","refused","exit_code","observed","marker","g0_outcome","g0_wait_s","os_level_max",
          "pm_nominal","span_reference","g0_reference_record_sha256","g0_reference_source","prefill_tokens",
          "decode_tokens","first_token_ns","elapsed_s","bad_polls","usb_errors","polls","sensor_roles",
          "original_eos_token_ids"}
def document_set(pin,branch,corpus):
    if branch in ("journals","salvage",*JOURNAL_PROFILES):
        docs=dict(corpus[pin]["incomplete"])
        docs.update(journals(pin,branch if branch in JOURNAL_PROFILES else "journals"))
        if branch=="salvage":
            for suffix in ("outputs/align_runtime_events.jsonl",):
                docs[EVENTS.rsplit("/",1)[0]+"/"+suffix]=docs[EVENTS]
    elif branch == "salvaged-failure":
        docs = dict(corpus[pin]["incomplete"])
        docs.update(journals(pin, "salvaged-failure"))
    elif branch == "interrupted-journals":
        # The on-disk incomplete result names episode.deadman:0 and still locates the journal.
        docs = dict(corpus[pin]["incomplete"])
        docs.update(journals(pin))
    else:
        docs=dict(corpus[pin][branch])
    if "soak_reference" in docs[RECEIPT] and SOAK not in docs:
        docs[SOAK]=soak()
    return docs

def leaf_config_name(file,path):
    return file.endswith("/config.json") and bool(path)

def catalog(corpus):
    seen=set()
    for pin,branches in corpus.items():
        for branch in ["normal","journals",*sorted(set(branches)-{"normal","support"})]:
            docs=document_set(pin,branch,corpus)
            yield Case("admit",pin,branch)
            if branch=="interrupt-step":
                i=next(i for i,row in enumerate(docs[RECEIPT]["steps"]) if row["name"]=="soak")
                yield Case("admit",pin,branch,path=("steps",i,"rc"),op="remove",label="F03")
            if branch=="journals":
                for j,ev in enumerate(docs[EVENTS]):
                    if ev["event_type"]=="token":
                        for val in (None,):
                            yield Case("admit",pin,branch,EVENTS,(j,"metadata","align_turn_index"),"replace",val,"T05-null")
                        yield Case("admit",pin,branch,EVENTS,(j,"metadata","align_turn_index"),"remove",label="T05-absent")
                        break
            for file,doc in docs.items():
                def produce(family,path,op,value=None,label=""):
                    return Case(family,pin,branch,file,path,op,value,label)
                if (branch=="normal" or (branch=="journals" and "/runtime/" in file)) and pin==PINS[0]:
                    for token in ("duplicate","NaN","Infinity","-Infinity","overflow","comment","utf16","utf8","bom","trailing"):
                        yield produce("wire",(),"raw",token,token)
                    if not file.endswith(".jsonl"): yield produce("wire",(),"raw","concat","concatenated")
                    yield produce("absent-file",(),"absent-file")
                def visit(node,path,role):
                    # Equivalence of production sites, never equality of reader behavior. The step and event
                    # alternatives have different continuation rules even when their JSON keys coincide.
                    if isinstance(node,dict):
                        variant=node.get("name") or node.get("event_type","")+"."+str(node.get("phase",""))
                        if node.get("error") is not None:
                            variant+="!"+node["error"].split(":")[0]
                        sig=(role,variant,tuple((k,type(v).__name__) for k,v in sorted(node.items())))
                        if sig not in seen:
                            seen.add(sig)
                            yield produce("extra-key",path,"add")
                            for key,val in node.items():
                                dest=(*path,key)
                                # A genuine optional span-id, meter-health or end stamp cannot simply be
                                # declared mandatory. Test option-specific correlations separately.
                                optional=key in {"span_id","t0_authority","t0_not_before_ns","meter_health_error",
                                                 "epoch_ns","soak_attempts"} or (key=="rc" and variant in ("soak","soak.a2")) or (key=="align_turn_index" and file==EVENTS and doc[path[0]]["event_type"]=="token")
                                if not optional: yield produce("missing-key",dest,"remove")
                                yield produce("rename-key",dest,"rename")
                                variants=[("null",None),("bool",True),("number-text","2"),("unicode-digit","٢"),
                                          ("fraction",1.5),("integer",2),("object",{}),("array",[]),("NaN",float("nan"))]
                                flexible_numeric=(any(component in ("sensors","readings","reference","release",
                                                                   "entry_sensors","entry_slope_c_per_min","sensors_c")
                                                      for component in path) or key in ("g0_s","g0_wait_s","g0_timeout_s",
                                                      "duration_s","max_busy_cores","max_gap_s","delta_fast_c","delta_slow_c"))
                                for label,bad in variants:
                                    if flexible_numeric and type(val) in (int,float) and type(bad) in (int,float) and label!="NaN":
                                        continue
                                    if type(val) in (int,float) and label=="number-text": bad=str(val)
                                    if type(val) in (int,float) and label=="unicode-digit":
                                        bad=str(val).translate(str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩"))
                                    if type(val) is int and label=="bool" and val in (0,1): bad=bool(val)
                                    if type(bad) is type(val) and label!="NaN": continue
                                    if bad is None and (key in NULLABLE or optional or key=="rc" and variant.startswith("soak")):
                                        continue
                                    if val is None and key in NULLABLE:
                                        # Nullable union. Non-null arm checked at its emitting alternative.
                                        if label not in ("object","array") or key in ("span_reference","original_eos_token_ids","sensor_roles"):
                                            continue
                                    if label=="integer" and isinstance(val,float):
                                        # Only strict floating clock/stamp positions use an int/float swap.
                                        if key not in ("timestamp_s","epoch_s","started_epoch_s","ended_epoch_s","wall_s"):
                                            continue
                                    yield produce("type-"+label,dest,"replace",bad,label)
                                if type(val) is int and not flexible_numeric:
                                    yield produce("type-integral-float",dest,"replace",float(val),"same-value")
                                if ((key in ENUMS|{"schema_version","kind","module","g0_outcome","member_status","observed_at","unit"})
                                        and isinstance(val,str) and not (key=="name" and leaf_config_name(file,path))):
                                    yield produce("schema" if key=="schema" else "enum",dest,"replace","unregistered","outside")
                        for k,v in node.items():
                            yield from visit(v,(*path,k),(*role,variant,k))
                    elif isinstance(node,list):
                        for i,v in enumerate(node):
                            if type(v) not in (dict,list):
                                site=(role,"array-element",type(v).__name__)
                                if site not in seen:
                                    seen.add(site)
                                    for label,bad in (("bool",True),("fraction",1.5),("number-text","3"),("unicode-digit","٣"),
                                                      ("object",{}),("array",[]),("NaN",float("nan"))):
                                        if type(v)!=type(bad) or label=="NaN": yield produce("element-"+label,(*path,i),"replace",bad,label)
                            yield from visit(v,(*path,i),(*role,"[]"))
                # Both pin identity and production site matter. Cross-file copies are mutated independently.
                norm=file.replace(file.split("/")[1],"<leg>") if file.startswith("legs/") else file
                yield from visit(doc,(),(pin,norm))
            if branch in ("normal","retry","redo","restore","desk","cap-expired","signal-130","signal-and-restore",
                          "stop-meter","close-volumes","hash-agents","meter-health","interrupt-attempt"):
                r=docs[RECEIPT]
                yield Case("rc-coupling",pin,branch,path=("rc",),op="replace",value=2 if r["rc"]!=2 else 0,label="span")
                for i,st in enumerate(r["steps"]):
                    if "error" in st:
                        yield Case("rc-coupling",pin,branch,path=("steps",i,"rc"),op="replace",value=0,label="step")
                if "error" not in r:
                    yield Case("explicit-null",pin,branch,op="insert-null")
            if branch=="normal":
                result_file="legs/L001/leg_record.json"
                for label,bundle in (("empty",""),("absolute","/some/path"),("empty-component","runs//leg"),
                                     ("dot","runs/./leg"),("parent","runs/../leg"),("slash","runs/leg/")):
                    yield Case("locator",pin,branch,result_file,("result","bundle"),"replace",bundle,label)
                yield Case("schema",pin,branch,path=("kit","frozen_commit"),op="replace",value="0"*40,label="wrong-pin")
            if branch=="retry-exhausted":
                yield Case("retry-limit",pin,branch,path=("soak_attempts",1),op="copy")
            if branch in ("normal","retry","redo"):
                for key in ("roster","legs","steps","soak_attempts"):
                    for i,item in enumerate(docs[RECEIPT].get(key,[])):
                        for op in ("copy","remove","swap"):
                            if op=="swap" and i+1==len(docs[RECEIPT][key]): continue
                            yield Case("sequence-"+op,pin,branch,path=(key,i),op=op)
        for branch in ("normal","redo"):
            docs=document_set(pin,branch,corpus)
            for filename,doc in docs.items():
                if not filename.endswith("/leg_record.json"): continue
                for i in range(len(doc["attempts"])):
                    for op in ("remove","copy","swap"):
                        if op=="swap" and i+1==len(doc["attempts"]): continue
                        yield Case("leg-attempt-"+op,pin,branch,filename,("attempts",i),op)
                yield Case("cross-copy",pin,branch,filename,("result","leg_status"),"replace","incomplete","result-versus-step")
                yield Case("cross-copy",pin,branch,filename,("spec","seed"),"replace",doc["spec"]["seed"]+1,"spec-versus-summary")
        for branch,rc in (("signal-129",129),("signal-130",130),("signal-143",143)):
            rows=corpus[pin][branch][RECEIPT]["steps"]
            index=next(i for i,row in enumerate(rows) if row["name"]=="soak")
            different=143 if rc!=143 else 129
            for path in (("error",),("steps",index,"error")):
                yield Case("signal-error",pin,branch,RECEIPT,path,"replace","SystemExit: "+str(different),"code-mismatch")
        for suffix in ("outputs/align_turns.jsonl","outputs/align_thermal.jsonl"):
            file=EVENTS.rsplit("/",1)[0]+"/"+suffix
            for i in range(len(journals(pin)[file])):
                for op in ("remove","copy","swap"):
                    if op=="swap" and i+1==len(journals(pin)[file]): continue
                    yield Case("journal-sequence-"+op,pin,"journals",file,(i,),op)
        for profile in JOURNAL_PROFILES:
            yield Case("admit",pin,profile)
            # Reuse each actual emitting row as a base. Keep the pin and alternative in the name.
            for file,rows in journals(pin,profile).items():
                if not file.endswith(".jsonl"): continue
                seen_shapes=set()
                for i,row in enumerate(rows):
                    payload="metadata" if "metadata" in row else "values" if "values" in row else "generation"
                    variant=(row.get("event_type"),row.get("phase"),row.get("kind"),row.get("message"),tuple(row[payload]))
                    if variant in seen_shapes: continue
                    seen_shapes.add(variant)
                    yield Case("journal-extra",pin,profile,file,(i,),"add")
                    for key in row:
                        yield Case("journal-required",pin,profile,file,(i,key),"remove")
                    if file==EVENTS:
                        yield Case("journal-enum",pin,profile,file,(i,"event_type"),"replace","unissued","event")
                        yield Case("journal-payload",pin,profile,file,(i,"metadata"),"replace",None,"null")
        event_count=len(journals(pin)[EVENTS])
        for suffix in ("outputs/align_runtime_events.jsonl",):
            file=EVENTS.rsplit("/",1)[0]+"/"+suffix
            for token in ("duplicate","NaN","utf8","trailing"):
                yield Case("fallback-wire",pin,"salvage",file,(),"raw",token,token)
            for key in ("timestamp_s","event_type","phase","message","metadata"):
                yield Case("fallback-key",pin,"salvage",file,(0,key),"remove")
        for i in range(event_count):
            for op in ("copy","remove","swap"):
                if i==event_count-1 and op=="swap": continue
                yield Case("event-"+op,pin,"journals",EVENTS,(i,),op)
        yield Case("F1", pin, "journals", label="admitted-timestamp-readers")
        for filename in journals(pin):
            if not filename.endswith(".jsonl"):
                continue
            n = len(journals(pin)[filename])
            yield Case("F2", pin, "interrupted-journals", filename, (n - 1,), "remove", label="unattested-prefix")
            yield Case("F2", pin, "interrupted-journals", filename, op="partial-line", label="torn-write")
        last_leg = branches["normal"][RECEIPT]["roster"][-1]
        interrupted = "work-signal@" + last_leg + ".a1"
        first = branches["normal"][RECEIPT]["roster"][0]
        record = f"legs/{first}/leg_record.json"
        summary = f"legs/{first}/leg_summary.json"
        finished = branches[interrupted]
        assert finished[RECEIPT]["legs_finished"] == sum(path.endswith("/leg_record.json") for path in finished) == 1
        n = len(finished[record]["attempts"])
        assert n == finished[summary]["attempts"] == len(finished[RECEIPT]["legs"][0]["attempts"])
        yield Case("F2", pin, interrupted, record, label="attested-completed-prefix")
        yield Case("F2", pin, interrupted, record, ("attempts", n - 1), "remove", label="count-mismatch")
        yield Case("F2", pin, interrupted, record, op="absent-file", label="missing-counted-leg")
        for filename in document_set(pin, "journals", corpus):
            yield Case("F3", pin, "journals", filename, op="reencode", label="equivalent-object")
        yield Case("F4", pin, "journals", EVENTS, op="tool-pair", label="registered-task-has-no-tools")
        yield Case("F4", pin, "salvaged-failure", SALVAGE, op="tool-pair", label="tool-in-salvage")
        salvage_rows = journals(pin, "salvaged-failure")[SALVAGE]
        yield Case("F2", pin, "salvaged-failure", SALVAGE, (len(salvage_rows) - 1,), "remove", label="unattested-salvage-prefix")
        yield Case("F2", pin, "salvaged-failure", SALVAGE, op="partial-line", label="torn-salvage-write")
        yield Case("F5", pin, "salvaged-failure", SALVAGE, label="outputs-location")
        yield Case("F5", pin, "salvaged-failure", SALVAGE, op="relocate", label="root-only")
        yield Case("F5", pin, "salvaged-failure", SALVAGE, op="alias-copy", label="root-and-outputs")
    for name in ("failed_restore_span_zero","wrong_schema","extra_member","explicit_null_error","missing_phase_metadata"):
        yield Case("audit-3",PINS[0],"audit",EVENTS if name=="missing_phase_metadata" else RECEIPT,label=name)

def audit_mutation(name,file,original):
    # Verbatim operations from writer_invariants.py and phase_record.py. Re-encode the same as audit 3.
    if file==EVENTS:
        rows=[json.loads(line) for line in original.splitlines()]
        phase=next(row for row in rows if row["event_type"] == "phase_start")
        assert type(phase["metadata"]) is dict
        phase.setdefault("message", None)
        if name!="phase_control": del phase["metadata"]
        from joulewise.cadence_looks import interim_release as C
        return b"".join(C.dump(row) for row in rows)
    r=json.loads(original)
    assert r["rc"] == 0 and r["steps"] == [{"name": "soak", "rc": 0}]
    if name in ("failed_restore_span_zero","failed_restore_span_two"):
        r["steps"].append({"name": "restore", "rc": 2, "error": "ValueError: generated cleanup failure"})
        r["rc"] = 2 if name=="failed_restore_span_two" else 0
    elif name=="receipt_control": pass
    elif name=="wrong_schema": r["schema"] = "unregistered"
    elif name=="extra_member": r["unissued_member"] = True
    elif name=="explicit_null_error": r["error"] = None
    else: raise ValueError(name)
    return json.dumps(r).encode()

def admits(c):
    return (c.family in {"admit", "F1", "F3"} or c.label in {"attested-completed-prefix", "outputs-location"})

def full_roster(c):
    return c.family == "admit" or c.family in {"F1", "F2", "F3", "F4", "F5"}

class Arena:
    def __init__(self, owner, audit=False, negative=False):
        self.negative=negative
        from tests.cadence import look_minirepo as mr
        from scripts import cadence_look_synth as synth
        if audit:
            from tests.cadence.test_interim_release import TwinThroughCLI
            from joulewise.cadence_looks import interim_release as release
            original=TwinThroughCLI()
            owner.addCleanup(original.doCleanups)
            original.setUp()
            self.mini=original.mini
        else:
            self.mini=mr.mini_repo(owner)
        self.root=Path(owner.enterContext(tempfile.TemporaryDirectory(prefix="admission-"))).resolve()
        self.source=original.source if audit else self.root/"generated"
        self.pub=self.mini/"public"/LOOK/"PUBLIC.json"
        self.reservation=self.source/LOOK/"RESTRICTED"
        self.out=self.root/"stage1.json"
        self.corpus=load_corpus()
        tokens={}
        level,energy,_=synth.build("exact",tokens=tokens)
        if not audit:
            # The committed supporting fit leg supplies timestamps for the positive CLI. It is outside
            # the mutated span; the verifier sees all rostered envelopes before reading either trace.
            level["spans"]=level["spans"][:1]
            level["legs"]=level["legs"][:1]
        loc=({k:self.source/k for k in ("roster.json","rules_3_4.json")} if audit
             else synth.write_custody(self.source,level,energy,tokens))
        self.support=self.source/level["spans"][0]["span_id"]
        if not (audit or negative):
            for file,doc in self.corpus[PINS[0]]["support"].items():
                (self.support/file).write_bytes(wire(doc))
        self.span=self.source/original.spans[0] if audit else self.source/"dev-03-s01"
        roster=Path(loc["roster.json"]);rules=Path(loc["rules_3_4.json"])
        if not audit:
            self.span.mkdir()
            rr=json.loads(roster.read_bytes())
            rr.insert(0,dict(rr[0],span_id=self.span.name,block_id="dev-03"))
            if negative: rr=rr[:1]  # Focus-only roster for the historical mutation sweep.
            roster.write_bytes(wire(rr))
            verdicts=json.loads(rules.read_bytes())
            for branches in self.corpus.values():
                for lid in branches["normal"][RECEIPT]["roster"]:
                    verdicts[self.span.name+"/"+lid]=dict(sidecar_coverage=False,km003c_clean=False)
            rules.write_bytes(wire(verdicts))
        manifest=self.mini/mr.MANIFEST
        # Preserve the executable twin pinned at the revision under test. The shared helper's generic
        # stub is suitable for manifest tests; these trials mimic the audit's committed input row.
        original=json.loads((ROOT/mr.MANIFEST).read_bytes())
        doc=json.loads(manifest.read_bytes())
        doc.update(status="committed")
        doc["fit"]["twin"]=original["fit"]["twin"]
        manifest.write_bytes(release.dump(doc) if audit else wire(doc))
        self.ledger=self.mini/mr.lm.LOOK_LEDGER_PATH
        shared=json.loads(self.ledger.read_bytes())
        row=next(row for row in shared["looks"] if row["look_id"]==LOOK)
        row.update(status="committed",sha256=mr.lm.sha256_file(manifest),roster_sha256=mr.lm.sha256_file(roster),
                   verdicts_sha256=mr.lm.sha256_file(rules))
        self.ledger.write_bytes(release.dump(dict(schema=mr.lm.LOOK_LEDGER_SCHEMA,looks=[row])) if audit else wire(shared))
        mr.git_commit(self.mini,"Register generated stage-one inputs")
        self.ledger_bytes=self.ledger.read_bytes()
        self.args=list(map(str,["stage1","--manifest",manifest,"--roster",roster,"--rules-3-4",rules,
                               "--custody",self.source,"--out",self.out,"--ledger-ref","origin/main"]))
        self.proc=subprocess.Popen([sys.executable,"-I","-B",str(HERE),"--actor",str(self.mini),
                                    *(["--fixed-auth"] if negative else [])],
                                   stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
        owner.addCleanup(self.close)
        self.key=None
        self.paired={}
    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=30)
        self.proc.stdout.close()
    def install(self,c):
        if self.key==(c.writer,c.branch): return
        if c.branch=="audit":
            self.docs={}
        else:
            if self.span.is_dir(): shutil.rmtree(self.span)
            self.docs=document_set(c.writer,c.branch,self.corpus)
            for file,doc in self.docs.items():
                p=self.span/file;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(doc_bytes(file,doc))
            if self.negative:
                # Always materialize a small synthetic timestamp source for the single-span sweep.
                # The observer is passive. Late refusal on this roster (including no fit) fails.
                stream=self.span/"hazards/meter/stream-0001.jsonl"
                stream.parent.mkdir(exist_ok=True,parents=True)
                stream.write_bytes(b'{"k":"h","status":"streaming"}\n{"k":"t","bad":0,"polls":0,"usb_errors":0,"elapsed_s":0.0}\n' )
        self.key=(c.writer,c.branch)
    def invoke(self,path):
        self.out.unlink(missing_ok=True)
        wanted=[str(self.span/name) for name in self.docs if (self.span/name).is_file()]
        req=dict(args=self.args,target=str(path),expected=wanted)
        self.proc.stdin.write(json.dumps(req)+"\n")
        self.proc.stdin.flush()
        msg=self.proc.stdout.readline()
        if not msg: raise RuntimeError(f"stage-one driver exited {self.proc.poll()}")
        return json.loads(msg)

    def run(self,c):
        self.install(c)
        path=self.span/c.file
        original=path.read_bytes()
        if self.negative and self.key not in self.paired:
            control=self.invoke(path)
            self.paired[self.key] = "" if control["opens"] else control["err"] or "control never reached the trace"

        self.out.unlink(missing_ok=True)
        if c.branch=="audit": changed=audit_mutation(c.label,c.file,original)
        elif c.op in ("control", "relocate", "alias-copy"): changed=original
        else: changed=mutate(c,self.docs)
        try:
            if changed is None: path.unlink()
            else: path.write_bytes(changed)
            observed_path = path
            if c.op in ("relocate", "alias-copy"):
                observed_path = self.span/ROOT_ALIAS
                if observed_path.exists():
                    raise AssertionError("unexpected pre-existing alias")
                observed_path.write_bytes(original)
                if c.op == "relocate":
                    path.unlink()
            row=self.invoke(observed_path)
            row["base_refusal"]=self.paired.get(self.key,"")
            row["output"]=self.out.exists()
            row["spent"]=(row["reservation_attempt"] or self.reservation.exists()
                          or (self.reservation.parent/"synthetic-reservation").exists()
                          or self.ledger.read_bytes()!=self.ledger_bytes)
            row["public"]=(row["public_attempt"] or self.pub.exists())
            return row
        finally:
            if c.op in ("relocate", "alias-copy"):
                (self.span/ROOT_ALIAS).unlink(missing_ok=True)
            path.write_bytes(original)

def problems(c,r):
    admitted=admits(c)
    errors=[]
    if r["rc"]!=(0 if admitted else 2): errors.append(f"rc={r['rc']}")
    if r["output"]!=admitted: errors.append("stage1 output="+str(r["output"]))
    if r["spent"]: errors.append("reservation")
    if r["public"]: errors.append("PUBLIC")
    if (r["responses"] if admitted else r["opens"]): errors.append("opened="+",".join(r["opens"]))
    if r["base_refusal"]: errors.append("unchanged control already refused")
    if admitted and r["not_checked_before_trace"]: errors.append("incomplete inventory before trace")
    if r["early_opens"]: errors.append("protected open before admission returned")
    if admitted:
        if not r["admission_complete"]: errors.append("operational preflight did not return")
        if set(r["timestamp_readers"]) != {"power=" + TIMESTAMP_READER, "meter=" + TIMESTAMP_READER}:
            errors.append("timestamp sources or reader differ from RL-173 E.1")
    if admitted and r["rc"] == 2 and r["opens"]:
        errors.append("refusing command opened a protected source")
    if not admitted and r["rc"] == 2 and not r["err"].startswith("REFUSED "):
        errors.append("unexpected exception instead of refusal")
    if admitted and c.family.startswith("F") and not r["target_read"]:
        errors.append("admitted fixture target unread")
    if not r["receipt_read"]: errors.append("fixture never reached")
    return errors

def cases():
    items=list(catalog(load_corpus()))
    names={c.name for c in items}
    if len(names)!=len(items): raise AssertionError("duplicate case identifier")
    return items

class Admission(unittest.TestCase):
    arena=None
    audit=None
    @classmethod
    def setUpClass(cls):
        owner=unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.arena=Arena(owner,negative=True)
        cls.positive=Arena(owner)
    def check_case(self,c):
        if c.family=="audit-3":
            if type(self).audit is None:
                owner=unittest.TestCase()
                type(self).addClassCleanup(owner.doCleanups)
                type(self).audit=Arena(owner,True)
            arena=type(self).audit
        else: arena=type(self).positive if full_roster(c) else type(self).arena
        row=arena.run(c)
        self.assertEqual(problems(c,row),[], f"{c.name}: {row}")

def load_tests(loader,tests,pattern):
    suite=unittest.TestSuite()
    for i,c in enumerate(cases()):
        name=f"test_{i:05}_{c.family.replace('-','_')}"
        def run(self,c=c): self.check_case(c)
        setattr(Admission,name,run)
        suite.addTest(Admission(name))
    return suite

class Rulings(unittest.TestCase):
    """Direct unittest selectors from the original five questions. Default discovery expands each case once."""
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.arena = Arena(owner)
        cls.resolved = [c for c in cases() if c.family in {"F1", "F2", "F3", "F4", "F5"}]

    def check_ruling(self, family):
        selected = [c for c in self.resolved if c.family == family]
        self.assertTrue(selected, family)
        for case in selected:
            with self.subTest(case=case.name):
                row = self.arena.run(case)
                self.assertEqual(problems(case, row), [], row)

    def test_successful_full_cli_zero_trace_opens(self):
        self.check_ruling("F1")

    def test_truncated_record_at_interruption(self):
        self.check_ruling("F2")

    def test_sorted_object_reencoded_in_a_different_order(self):
        self.check_ruling("F3")

    def test_tool_phase_on_a_rostered_one_turn_step_task(self):
        self.check_ruling("F4")

    def test_root_level_salvage_alias(self):
        self.check_ruling("F5")

if __name__=="__main__":
    if sys.argv[1:2]==["--actor"]: actor(Path(sys.argv[2]))
    else:
        sys.path.insert(0,str(ROOT))
        if sys.argv[1:2]==["--list"]:
            print(json.dumps(Counter(c.family for c in cases()),sort_keys=True))
        elif sys.argv[1:2]==["--report"]:
            # Independent shards create their own mini-repos. JSONL is also the replayable per-case ledger.
            audit_only = sys.argv[2] == "audit"
            part,total = (0, 1) if audit_only else map(int, sys.argv[2].split("/"))
            separate_audit = "--separate-audit" in sys.argv[3:]
            owner=unittest.TestCase()
            try:
                regular=None if audit_only else Arena(owner,negative=True)
                positive=audit=None
                for i,c in enumerate(cases()):
                    if c.family=="audit-3":
                        if part != 0 or separate_audit: continue
                    elif audit_only or i%total!=part: continue
                    if c.family=="audit-3" and audit is None: audit=Arena(owner,True)
                    if full_roster(c) and positive is None: positive=Arena(owner)
                    arena=audit if c.family=="audit-3" else positive if full_roster(c) else regular
                    r=arena.run(c)
                    r.pop("target",None)
                    print(json.dumps(dict(index=i,case=c.name,family=c.family,problems=problems(c,r),result=r)),flush=True)
            finally: owner.doCleanups()
        else: unittest.main()
