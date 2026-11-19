"""Frozen qualification CLI acceptance. Stdlib only. All observation bytes are invented.

Run from the builder checkout, with the five independent expectations next to this
file. QUAL_SOURCE can select its public source tree. QUAL_TEST_COMMAND is a JSON
argv override for offline mutation checks only. The shipped test never imports a
scorer. Its audit observer lives in the child interpreter, outside scorer code.
"""
import collections
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get("QUAL_SOURCE", Path.cwd())).resolve()
LOOK = "lm-qual-01"
INTERIM = "lm-interim-01"
DOC = "docs/process/cadence/looks/"
MAN = "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-qual-01.manifest.json"
RLD = "docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md"
LEDGER = DOC + "LOOKS.json"
REG = "59557d6e8e00fcba6a2bdb2bfa4189bd6d7aee98"
REG_HASH = "d6fde6918023ea69051da45a6b0e3c06ffcfdafd8975a1773989324fa7c9bdab"
AUDIT = "refs/remotes/origin/audit/2026-11-10-fable"
MAIN = "refs/remotes/origin/main"
SPANS = tuple(f"qual-0{b}-s0{s}" for b in range(1, 4) for s in (1, 2))
CHANNELS = ("gpu_rail", "dc_in")
PREFIX = (3724, 3151, 2981)
HOST_UUID = "00000000-0000-4000-8000-000000000001"
RULES = ("ran_to_cap", "g0_released", "sidecar_coverage", "km003c_clean",
         "not_a_contaminated_attempt", "block_power_mode")
PRIVATE = os.environ.get("QUAL_SELF_CHECK_DIRECTORY", "RESTRICTED")
if PRIVATE != "RESTRICTED" and not os.environ.get("QUAL_TEST_COMMAND"):
    raise ValueError("Synthetic directory alias is confined to the offline self-check")
if PRIVATE not in ("RESTRICTED", "synthetic-reservation"):
    raise ValueError("Unexpected synthetic reservation name")
ORACLES = ("interval_containment", "equal_day_unequal_counts", "fewer_than_three_pair_days",
           "undefined_interval", "l_partial_blocks_same_scorer")


def wire(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw if isinstance(raw, bytes) else wire(raw))


def obj(path):
    return json.loads(path.read_bytes())


def registration():
    # Read the registration commit, even when the checkout now contains a final.
    raw = subprocess.check_output(["git", "-C", str(SOURCE), "show", REG + ":" + MAN])
    if sha(raw) != REG_HASH:
        raise AssertionError("published registration digest")
    return raw


def slots(doc):
    return [rule["code"] for rule in doc["inclusion"]["rules"] if "code" in rule] + [
        doc["pins"]["scorer"], *doc["pins"]["code"], *doc["pins"]["schemas"].values()]


def history(repo, ref, files, parent=None, time=1700000000, main=False):
    """Content-addressed, deterministic disposable Git evidence. No real index or ref."""
    data = [f"commit {ref}\ncommitter Fixture <example@invalid.test> {time} +0000\ndata 5\nplant\n".encode()]
    if parent:
        data.append(f"from {parent}\n".encode())
    for name, raw in sorted(files.items()):
        raw = raw if isinstance(raw, bytes) else wire(raw)
        data += [f"M 100644 inline {name}\ndata {len(raw)}\n".encode(), raw, b"\n"]
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    subprocess.run(["git", "-C", str(repo), "fast-import", "--quiet"], input=b"".join(data)+b"\ndone\n",
                   env=env, check=True, stdout=subprocess.PIPE)
    head = git(repo, "rev-parse", ref).strip().decode()
    if main:
        git(repo, "update-ref", MAIN, head)
    return head


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def host():
    return "hw1:" + sha(("joulewise.execution_host.v1:" + HOST_UUID).encode())


def edge_world(sign=1, big=18):
    # Shared residuals ±big and ±5. The other leg on each date has opposite
    # residuals; at big=18 both sample variances are exactly 100 in binary64.
    return [(s, lo, hi) for s, large in zip((0, 2, 4, 5), (big, -big, 5, -5))
            for lo, hi in ((-sign, sign), (large, large))]


def design(name):
    # Tuples are (zero-based span, GPU own-prefix residual J, whole residual J).
    if name.startswith("edge"):
        _, sign, big = name.split("/")
        return edge_world(int(sign), float(big))
    if name == "noisy":
        return [(s, 3*(s-2)+i, 3*(s-2)+i+(i-1.5)/256)
                for s in range(6) for i in range(4)]
    if name in ("floor_short","floor_long","above_floor"):
        unit=1e-12
        short,long={"floor_short":([2,3,4],[4,6,8]),"floor_long":([.25,1.5,2.75],[2,3,4]),
                    "above_floor":([4,6,8],[4,6,8])}[name]
        return [(s,a*unit,b*unit) for s,a,b in zip((0,2,4),short,long)]
    if name == "zero_days":
        return []
    if name == "one_day":
        return [(0,1,1),(0,2,2),(0,3,3)]
    if name == "two_narrow_days":
        return [(0,1,1),(0,2,2),(2,3,3),(2,4,4)]
    if name == "two_legs":
        return [(0, 2, 1), (4, 4, 5)]
    if name == "two_days":
        return [(0, 2, 1), (0, 4, 5), (2, 6, 7)]
    if name in ("flat_short", "flat_long"):
        return [(s, 1 if name=="flat_short" else s, 1 if name=="flat_long" else s)
                for s in (0, 2, 4)]
    if name == "cross":
        return [(0, -5, -5), (2, 0, 1), (4, 5, 5)]
    if name == "interval_containment":
        return [(0, -8, -8.25), (2, 2, 2.5), (4, 7, 7.125)]
    if name == "equal_day_unequal_counts":
        ds = [0, 0, .06, .12]
        a = math.sqrt((3 - sum((d-.045)**2 for d in ds)/4)/2)
        return [(s, u-d/2, u+d/2) for s, u, d in zip((0, 0, 2, 4), (a,-a,0,0), ds)]
    if name == "fewer_than_three_pair_days":
        return [(0,-9,-8), (1,2,2), (2,8,7)]
    if name == "undefined_interval":
        return [(0,1,3), (2,1,4), (4,1,5)]
    if name == "l_partial_blocks_same_scorer":
        return [(0,-3,-2), (2,2,4), (4,7,7)]
    raise ValueError(name)


def coefficient_set():
    axes = ["p1","p2","a0","a1","a2"]
    return {"schema":"joulewise.cadence_look_coefficients.v1", "look_id":INTERIM, "synthetic":True,
            "stage1_sha256":sha(b"invented development stage 1"),"fit_sha256":sha(b"invented development fit"),
            "manifest_sha256":sha(b"invented interim manifest"),"code_sha256":{},"numpy_version":"2.2.6",
            "qualified_interim_half":{"statistic":"gpu_rail.lodo.hot.max_abs","threshold":.02,
                                      "value":None,"verdict":"not_evaluable"},
            "block_tokens":256, "prefix":dict(zip(("1.10","1.30","1.374"),PREFIX)),
            "centring":{"tf08_c":30,"fan_rpm":1000,"tv0h_excess_c":0},
            "active_readings":dict.fromkeys(("tf08_c","fan_rpm","tv0h_excess_c"),False),
            "calibrated_range":{"tf08_c":[29,31],"fan_rpm":[900,1100],"tv0h_excess_c":[-1,1]},
            "delta_column":"dropped_onset_not_estimable",
            "onset":{"status":"not_estimable","predictors":["intercept","t_p_s"],"folds":{},
                     "coefficients":None,"sigma_s":None,"lodo_rms_s":None,
                     "count_only_cut":{"form":"fixed_116_s","offset_s":None,"fixed_s":116.0}},
            "rates":{"r_p":256,"r_d":128},
            "channels":{ch:{"columns":axes,"coefficients":dict(zip(axes,(k/8,0,k,k/4096,0))),
                            "fold_coefficients":{},"hot_rms_over_legs":None,
                            "covariance":[[0]*5 for _ in axes],"model_sha256":sha(wire([k,k/4096]))} for k,ch in enumerate(CHANNELS,1)}}


def segments(P, N):
    first = P/256
    yield {"seg":0, "kind":"prefill", "n_tokens":P,"edge_lo":None,"edge_hi":None,
           "tok_first":None,"tok_last":None,"first_token_s":None,"wall_start_s":0,"wall_end_s":first}
    for k in range(N//256):
        lo, hi = max(0,256*k-1), 256*k+255
        yield {"seg":k+1,"block":k,"kind":"decode","n_tokens":256,"edge_lo":lo,"edge_hi":hi,
               "tok_first":256*k,"tok_last":hi,"first_token_s":first+256*k/128,
               "wall_start_s":first+lo/128,"wall_end_s":first+hi/128}


def tail(P,N):
    lo, hi = 256*(N//256)-1, N-1
    return {"kind":"prefix_tail","prefix_len":N,"edge_lo":lo,"edge_hi":hi,"tok_first":lo+1,
            "tok_last":hi,"n_tokens":hi-lo,"first_token_s":P/256+(lo+1)/128,
            "wall_start_s":P/256+lo/128,"wall_end_s":P/256+hi/128}


def turn(P,N):
    return {"prefill_tokens":P,"decode_tokens":N,"turn_start_s":0,"first_token_s":P/256,
            "last_token_s":P/256+(N-1)/128,"segments":list(segments(P,N)),
            "prefix_tails":[tail(P,n) for n in PREFIX if n<N],
            "native_pm":[],"journal":[{"t_s":-1,"os_level":0,"pm_state":"Nominal","pm_fresh":True,
                                       "tf08_c":30,"fan_rpm":1000,"tv0h_c":30}]}


def base_j(P, seg, k):
    if seg["kind"]=="prefill":
        return k*P/8
    lo,hi = seg["edge_lo"],seg["edge_hi"]
    return k*(hi-lo)*(1+(P+(lo+1+hi)/2)/4096)


def measurements(P,N,short,long,ordinal):
    response = {}
    for k,ch in enumerate(CHANNELS,1):
        # DC deliberately disagrees with the GPU decision. The non-decision
        # prefixes and L pairs are independently planted.
        a,b = (short,long) if k==1 else (ordinal+3,30-ordinal)
        v=[base_j(P,seg,k) for seg in segments(P,N)]
        t={str(n):base_j(P,tail(P,n),k)+(a if n==3724 else 2*ordinal+1)
           for n in PREFIX if n<N}
        terminal = None
        if N%256:
            terminal=base_j(P,tail(P,N),k)+b
        else:
            v[-1]+=b
        response[ch]={"segments":v,"prefix_tails":t,"terminal":terminal}
    return response


def inputs(name, excluded):
    chosen=collections.defaultdict(list)
    for s,lo,hi in design(name):
        chosen[s].append((lo,hi))
    by_span, responses = {},{}
    for s,span in enumerate(SPANS):
        block=s//2
        ratio = (1 if s%2 else 2) if block<2 else (2 if s%2 else 1)
        full_first=(ratio==1 and block!=2) or (ratio==2 and block!=0)
        bound=PREFIX[ratio-1]
        caps = ([4096,bound] if full_first else [bound,4096])
        rows=[]
        for i,(P,N) in enumerate([(p,4096) for p in (2000,10000,19458,19458)]
                                 +[(2000,c) for c in caps]):
            typ = "A" if i<4 else "L"
            key=f"{span}/{typ}{i+1:03d}"
            ok=(i>=4 or i<len(chosen[s])) and key not in excluded
            lo,hi = chosen[s][i] if i<len(chosen[s]) else (3+s, (9-s if N==4096 else s*s+2))
            row={"leg_key":key,"span_id":span,"leg_type":typ,"P":P,"N":N,
                 "pair":None if i<4 else f"qual-0{block+1}-p{ratio}",
                 "order":i,"rules":{rule:bool(ok or idx!=0) for idx,rule in enumerate(RULES)},
                 "maintenance_job":"fixture-job" if s%2 else None,"turn":turn(P,N)}
            rows.append(row)
            responses[key]=measurements(P,N,lo,hi,6*s+i)
        by_span[span]=rows
    return by_span,responses

FIT = "joulewise/cadence_looks/fit_interim.py"
IPUB = "public/lm-interim-01/PUBLIC.json"
ISCHEMA = DOC+"lm-interim-01.output.schema.json"
IMAN = DOC+"lm-interim-01.json"
NAMING = DOC+"lm-interim-01.freeze2.json"
EQUIV = DOC+"lm-qual-01.equivalence.json"
STAGE = DOC+"lm-qual-01.stage1.json"
CONFIG = "configs/align/v4/r1_runtime.json"
KITS = DOC+"qualification-kit-commitments.json"
BASE_TIME = 1700000000


class World:
    def __init__(self, root):
        self.root=Path(root)
        self.repo=self.root/"repo"
        self.files=self.root/"inputs"
        self.private=self.root/"private"/LOOK/PRIVATE
        self.coef=self.root/"private"/INTERIM/PRIVATE/"coefficients.json"
        self.public=self.repo/"public"/LOOK/"PUBLIC.json"
        self.stage=self.root/"stage1.json"
        self.trace=self.root/"observer.jsonl"

    def refs(self):
        return obj(self.root/"fixture-refs.json")

    def original(self, ref, name):
        return git(self.repo,"show",ref+":"+name)

    def init(self,name="noisy",excluded=(),word="yes",named=False,equivalent=False,late_final=False):
        self.repo.mkdir(parents=True)
        subprocess.run(["git","init","--quiet","--initial-branch=fixture",str(self.repo)],check=True)
        # This mini-repo contains synthetic pins, kit bytes and host ownership only.
        # The published registration has a separate exact-byte integration test.
        rows, responses=inputs(name,excluded)
        raw=registration()
        development=wire({"d_n_chunk_status":"dev-plant"})
        qual=wire({"d_n_chunk_status":"qual-plant"})
        selected={}
        blocks=json.loads(raw)["reads"]["blocks"]
        for b in blocks:
            kit={"block_id":b["block_id"],"config_sha256":sha(qual),
                 "spans":{s:[{k:r[k] for k in ("leg_key","leg_type","pair","P","N","order")}
                             for r in rows[s]] for s in b["spans"]}}
            path="kits/"+b["block_id"]+".json"
            selected[path]=wire(kit)
            raw=raw.replace(b["kit_sha256"].encode(),sha(selected[path]).encode())
        registered=json.loads(raw)
        pins=slots(registered)
        paths=set(p["path"] for p in pins)
        if (len(paths),len(pins))!=(30,32):
            raise AssertionError("registered paths or slots changed")
        # Use the builder's real pinned source if present. The throwaway reference
        # export has placeholders only for then-unbuilt code, never for the validator.
        for path in paths:
            source=SOURCE/path
            if source.is_file():
                selected[path]=source.read_bytes()
            elif os.environ.get("QUAL_TEST_COMMAND"):
                selected[path]=("synthetic pin "+path+"\n").encode()
            else:
                raise AssertionError(f"missing registered source path: {path}")
        selected[KITS]=wire({LOOK:{"kit_sha256_by_block":{
            b["block_id"]:b["kit_sha256"] for b in registered["reads"]["blocks"]}}})
        selected[CONFIG]=qual
        selected["dev/"+CONFIG]=development
        row={"look_id":LOOK,"status":"registered","manifest_path":MAN,"sha256":sha(raw)}
        def ledger(*entries):
            return {"schema":"joulewise.cadence_look_ledger.v1","looks":list(entries)}
        reg=history(self.repo,"refs/heads/records",{**selected,MAN:raw,LEDGER:ledger(row)},
                    time=BASE_TIME,main=True)
        put(self.files/"registration.json",raw)
        numbers=coefficient_set()
        if name in ("floor_short","floor_long","above_floor"):
            vector=numbers["channels"]["gpu_rail"]["coefficients"]
            vector.update(dict.fromkeys(vector,0))
            for s,lo,hi in design(name):
                gpu=responses[SPANS[s]+"/A001"]["gpu_rail"]
                gpu["segments"]=[lo]+[0]*15+[hi-lo]
                gpu["prefix_tails"]=dict.fromkeys(gpu["prefix_tails"],0)
        put(self.coef,numbers)
        old_bytes=selected[FIT]+(b"\n# Previous generated revision with the same A branch.\n" if equivalent else b"")
        old=sha(old_bytes)
        interim=obj(SOURCE/IMAN)
        interim["status"]="committed"
        next(p for p in interim["fit"]["code"] if p["path"]==FIT)["sha256"]=old
        next(p for p in interim["fit"]["dependencies"] if p["path"]==CONFIG)["sha256"]=sha(development)
        ischema=(SOURCE/ISCHEMA).read_bytes()
        interim["outputs"]["schema"]={"path":ISCHEMA,"sha256":sha(ischema)}
        numbers["manifest_sha256"]=sha(wire(interim))
        put(self.coef,numbers)
        priv=str(self.root/"private")
        irow={"look_id":INTERIM,"status":"stage1_committed","manifest_path":IMAN,
              "sha256":sha(wire(interim)),"stage1_sha256":numbers["stage1_sha256"],
              "roster_sha256":sha(b"invented interim roster"),"verdicts_sha256":sha(b"invented interim verdicts"),
              "public_root":"public","custody_root":priv,"execution_host":host()}
        iexec=history(self.repo,"refs/heads/records",{LEDGER:ledger(row,irow),IMAN:interim,ISCHEMA:ischema,FIT:old_bytes},reg,BASE_TIME+1)
        pub={"look_id":INTERIM,"commit":iexec,"manifest_sha256":irow["sha256"],
             "stage1_sha256":irow["stage1_sha256"],"in_energy_fit":36,"qualified_interim":"yes",
             "drift_tripwire":"within","twin_agrees":word,"stage2_error":"no","coefficients_sha256":sha(wire(numbers)),
             **dict.fromkeys(("dev_included_below_45","days_below_4","cell_below_10",
                              "start_reading_invalid_over_10pct","hp01_below_9"),"no")}
        irow.update(status="frozen",output_sha256=sha(wire(pub)),coefficients_sha256=pub["coefficients_sha256"])
        final=re.sub(rb'("path": "([^"]+)",\n\s*"sha256": )"PENDING:CODE"',
                     lambda m:m[1]+b'"'+sha(selected[m[2].decode()]).encode()+b'"',raw)
        if b"PENDING:CODE" in final:
            raise AssertionError("unfilled pin")
        row.update(status="committed",sha256=sha(final),registration_commit=reg,
                   registration_sha256=sha(raw),public_root="public",custody_root=priv)
        files={MAN:final,IPUB:wire(pub),IMAN:wire(interim),ISCHEMA:ischema,FIT:selected[FIT]}
        if equivalent:
            # Public synthetic attestation. These turns and this coefficient set
            # are invented for this record, separate from either look's private fit.
            prompts=(3072,3584,8192)
            turns=[{"leg_key":f"equiv/A{j:03d}","leg_type":"A","turn":turn(P,4096)}
                   for j,P in enumerate(prompts,1)]
            series={}
            for leg,P in zip(turns,prompts):
                sample=series[leg["leg_key"]]={}
                for k,ch in enumerate(CHANNELS,1):
                    blocks=[base_j(P,b,k) for b in segments(P,4096)]
                    sample[ch]={"segments":blocks,"prefixes":{str(n):sum(blocks[:n//256+1])+base_j(P,tail(P,n),k)
                                                              for n in PREFIX}}
            eq={"interim_sha256":old,"qualification_sha256":sha(selected[FIT]),
                "coefficient_set_sha256":sha(wire(coefficient_set())),"generated_turns_sha256":sha(wire(turns)),
                "segments_compared":sum(len(v["segments"])+len(v["prefixes"]) for row in series.values() for v in row.values()),
                "interim_predictions_sha256":sha(wire(series)),"qualification_predictions_sha256":sha(wire(series))}
            for label,payload in (("generated-turns",turns),("synthetic-parameters",coefficient_set()),
                                  ("interim-predictions",series),("qualification-predictions",series)):
                files[DOC+"equivalence-fixture/"+label+".json"]=wire(payload)
            files[EQUIV]=wire(eq)
            row["equivalence_sha256"]=sha(files[EQUIV])
        if named:
            rid="RL-99999"
            stanza=(f"FREEZE-2-NAMING ruling={rid} look={INTERIM} coefficients_sha256={pub['coefficients_sha256']} "
                    f"public_sha256={irow['output_sha256']} designation=freeze-2")
            audit=history(self.repo,AUDIT,{RLD:("# "+rid+". Synthetic ruling\n\n"+stanza+"\n").encode()})
            irow["ruling"]=rid
            files[NAMING]=wire({"schema":"joulewise.cadence_looks.freeze2_naming.v1","ruling":rid,
                "look_id":INTERIM,"public_sha256":irow["output_sha256"],"coefficients_sha256":pub["coefficients_sha256"],
                "designation":"freeze-2","decisions_path":RLD,"decisions_commit":audit,"stanza":stanza})
        days=(0,0,1,1,2,3)
        for s,span in enumerate(SPANS):
            block=span[:7]
            t0=int(dt.datetime(2031,2,4,6,30,tzinfo=dt.timezone.utc).timestamp())+days[s]*86400+s*60
            ident={"span_id":span,"block_id":block,"kit_sha256":sha(selected["kits/"+block+".json"])}
            rec={**ident,"t0_epoch_s":t0,"registration_at_issue":reg}
            # Public evidence is a committed envelope around the delivered files.
            # Stage 1 inventories blind facts only. Level-E fixtures are explicit inputs.
            for k,val in (("receipt",rec),("hand",ident),("desk",ident),("q1",ident),
                          ("roster",{"span_id":span,"legs":rows[span]})):
                rel=f"spans/{span}/{k}.json"
                selected[rel]=wire(val)
                files["evidence/"+rel]=wire(val)
        files[LEDGER]=wire(ledger(row,irow))
        fid=history(self.repo,"refs/heads/records",files,iexec,2100000000 if late_final else BASE_TIME+100,main=True)
        for rel,rawbytes in selected.items():
            put(self.files/rel,rawbytes)
        for rel in ("joulewise/cadence_looks/manifest_dispatch.py",DOC+"look-kit-commitments.v2.json",
                    DOC+"filler-kit-registry.json"):
            put(self.files/rel,(SOURCE/rel).read_bytes())
        for rel in (MAN,IMAN,IPUB,ISCHEMA,LEDGER,NAMING,EQUIV):
            if rel in files:
                put(self.files/rel,files[rel])
        for key,energy in responses.items():
            put(self.files/"observations"/(key+".json"),energy)
        put(self.files/"local-host.json",{"IOPlatformUUID":[HOST_UUID]})
        self.public.parent.mkdir(parents=True)
        self.private.parent.mkdir(parents=True)
        put(self.root/"fixture-refs.json",{"registration":reg,"final":fid})
        return self

    def adm(self):
        st=self.stage.read_bytes()
        old=self.refs()["final"]
        led=json.loads(self.original(old,LEDGER))
        row=led["looks"][0]
        row.update(status="stage1_committed",stage1_sha256=sha(st),stage1_path=STAGE,
                   execution_host=host())
        head=history(self.repo,"refs/heads/records",{STAGE:st,LEDGER:led},old,int(git(self.repo,"show","-s","--format=%ct",old))+100,main=True)
        put(self.files/LEDGER,led)
        git(self.repo,"update-ref","refs/heads/fixture",head)
        return head

    def change(self, changes, ref=MAIN, checkout=True):
        parent=git(self.repo,"rev-parse",ref).strip().decode()
        head=history(self.repo,"refs/heads/variant",changes,parent,BASE_TIME+300)
        git(self.repo,"update-ref",ref,head)
        if checkout and ref==MAIN:
            git(self.repo,"update-ref","refs/heads/fixture",head)
            for key,val in changes.items():
                put(self.files/key,val)
        return head


# Observer wraps __main__ in a fresh Python. Its fd is opened before the CLI.
# The scorer gets no callback, expected word, fixture name or error selector.
BOOT = r"""
import builtins,json,os,runpy,sys
from pathlib import Path
target,root,fault,observe=sys.argv[1:5]
base=Path(root)
log=os.open(base/'observer.jsonl',os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
def note(*item):
    os.write(log,(json.dumps(item)+'\n').encode())
def audit(event,args):
    if event=='open':
        path,mode,flags=args
        if not isinstance(path,(str,bytes)): return
        path=os.fsdecode(path)
        if not os.path.isabs(path): path=os.path.abspath(path)
        if not path.startswith(str(base)+'/'):
            if flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC) and path!=os.devnull:
                note('write',path)
            return
        rel=os.path.relpath(path,base)
        if flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC):
            note('write',rel)
        else:
            note('open',rel)
            if rel.startswith('inputs/observations/'):
                note('reader_pid',str(os.getpid()))
                seen.add(rel)
                if fault and len(seen)==2:
                    os.write(1,b'parent-123.456\n')
                    os.write(2,b'parent-654.321\n')
                    import subprocess
                    subprocess.run([sys.executable,'-I','-B','-c',
                        "import os;os.write(1,b'child-333.444\\n');os.write(2,b'child-555.666\\n')"],check=True)
                    if fault=='custom': raise type('Leak_123_456',(Exception,),{})('secret')
                    if fault=='spoof': raise type('ValueError',(Exception,),{'__module__':'builtins'})('secret')
                    if fault=='json': raise json.JSONDecodeError('secret','',0)
                    if fault=='linalg':
                        from numpy.linalg import LinAlgError
                        raise LinAlgError('secret')
                    raise RuntimeError('secret')
    if event in ('os.mkdir','os.rename','os.link','os.symlink','os.remove'):
        paths=[os.path.abspath(os.fsdecode(x)) for x in args[:2] if isinstance(x,(str,bytes))]
        for p in paths:
            if p.startswith(str(base)+'/'): note(event,os.path.relpath(p,base))
seen=set()
sys.addaudithook(audit)
if observe=="native":
    import hashlib
    def profile(frame,event,arg):
        if event!="call" or frame.f_code.co_name!="predict_frozen": return
        path=Path(frame.f_code.co_filename)
        if path.name!="fit_interim.py": return
        leg=frame.f_locals.get("leg",{})
        note("native",[leg.get("leg_key"),leg.get("leg_type"),hashlib.sha256(path.read_bytes()).hexdigest()])
    sys.setprofile(profile)
sys.argv=[target,*sys.argv[5:]]
runpy.run_path(target,run_name='__main__')
"""


def launch(w,operation,extra=(),fault="",wait=True,native=False):
    path=os.environ.get("QUAL_TEST_COMMAND")
    cmd=json.loads(path) if path else [str(SOURCE/"joulewise/cadence_looks/qual_score.py")]
    args=[sys.executable,"-B","-c",BOOT,cmd[0],str(w.root),fault,"native" if native else "ordinary",*cmd[1:],operation,
          "--repo",str(w.repo),"--inputs",str(w.files),"--stage1",str(w.stage),*extra]
    env={**os.environ,"PYTHONPATH":str(SOURCE),"PYTHONDONTWRITEBYTECODE":"1","GIT_OPTIONAL_LOCKS":"0"}
    child=subprocess.Popen(args,cwd=w.root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    if not wait:
        return child
    out,err=child.communicate()
    return subprocess.CompletedProcess(args,child.returncode,out,err)


def events(w):
    return [json.loads(s) for s in w.trace.read_bytes().splitlines()]


def clear(w):
    w.trace.write_bytes(b"")


def relation(w):
    legs=[leg for span in SPANS for leg in obj(w.files/f"spans/{span}/roster.json")["legs"]
          if all(leg["rules"].values())]
    return legs


def input_commitment(w):
    names=[CONFIG,"dev/"+CONFIG,*["kits/qual-0%d.json"%n for n in (1,2,3)],
           *[f"spans/{span}/{kind}.json" for span in SPANS
             for kind in ("hand","desk","q1","receipt","roster")]]
    return sha(wire({name:sha((w.files/name).read_bytes()) for name in names}))


def bindings(w):
    return {"look_id":LOOK,"manifest_sha256":sha((w.files/MAN).read_bytes()),
            "stage1_sha256":sha(w.stage.read_bytes()),"coefficients_sha256":sha(w.coef.read_bytes()),
            "qualification_config_sha256":sha((w.files/CONFIG).read_bytes()),
            "development_config_sha256":sha((w.files/"dev"/CONFIG).read_bytes()),
            "commit":git(w.repo,"rev-parse","HEAD").strip().decode(),
            "included_legs":len(relation(w)),"type_m_residual":"not_run","stage2_error":"no"}


def records(case,w,word=None):
    raw=w.public.read_bytes()
    rec=json.loads(raw)
    case.assertIn(rec.get("qualified_qualification"),("yes","no","not_evaluable"))
    expected={**bindings(w),"qualified_qualification":word or rec["qualified_qualification"]}
    case.assertEqual(raw,wire(expected)) # validates literal token type, source, closed keys and exact bytes
    case.assertEqual(set(os.listdir(w.private)),{"scores.json","stdout","stderr"})
    return rec


def restricted_writes(case,w):
    inside=str(w.private.relative_to(w.root))
    output=str(w.public.relative_to(w.root))
    audit=events(w)
    for index,(kind,p) in enumerate(audit):
        if kind=="open" and (p.startswith("inputs/observations/") or p==str(w.coef.relative_to(w.root))):
            case.assertIn(["os.mkdir",inside],audit[:index])
        if p==output:
            case.assertIn(kind,("open","os.link","os.rename"),(kind,p))
        if kind not in ("open","native","reader_pid"):
            case.assertTrue(p==inside or p.startswith(inside+"/") or p==output,(kind,p))
    return [p for kind,p in events(w) if kind=="open" and p.startswith("inputs/observations/")]


def read_trace(case,w,allow_coefficient=False):
    observed=events(w)
    case.assertFalse(any(p.startswith("inputs/observations/") for _,p in observed),observed[-5:])
    if not allow_coefficient:
        case.assertFalse(any(p==str(w.coef.relative_to(w.root)) for _,p in observed))


def fresh(case,name="noisy",**options):
    w=World(Path(case.tmp.name)/("w"+str(case.count)))
    case.count+=1
    w.init(name,**options)
    admit(case,w)
    return w


def admit(case,w):
    run=launch(w,"stage1")
    case.assertEqual(run.returncode,0,run.stderr)
    read_trace(case,w)
    st=obj(w.stage)
    case.assertEqual(st["input_sha256"],input_commitment(w))
    case.assertEqual(st["counts"]["included_legs"],len(relation(w)))
    case.assertEqual(st["configs"],{"development_sha256":sha((w.files/"dev"/CONFIG).read_bytes()),
                                   "qualification_sha256":sha((w.files/CONFIG).read_bytes())})
    w.adm()
    clear(w)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template=tempfile.TemporaryDirectory()
        try:
            cls.seed=World(Path(cls.template.name)/"base").init()
            admit(unittest.TestCase(),cls.seed)
            cls.pristine=Path(cls.template.name)/"pristine"
            cls.seed.root.rename(cls.pristine)
        except BaseException:
            cls.template.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.template.cleanup()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.count=0

    def copy(self):
        w=World(self.seed.root)
        if w.root.exists():
            shutil.rmtree(w.root)
        shutil.copytree(self.pristine,w.root,copy_function=shutil.copyfile)
        return w

    def success(self,w,word=None,native=False):
        r=launch(w,"stage2",native=native)
        self.assertEqual((r.returncode,r.stdout,r.stderr),(0,b"",b""),r.stderr)
        reads=restricted_writes(self,w)
        self.assertEqual(set(reads),{"inputs/observations/"+leg["leg_key"]+".json" for leg in relation(w)})
        return records(self,w,word)

    def refuses(self,w,stage="stage2",reserved=False):
        r=launch(w,stage)
        self.assertEqual(r.returncode,2,r.stderr)
        read_trace(self,w)
        self.assertEqual(restricted_writes(self,w),[])
        self.assertEqual(w.private.exists(),reserved)
        self.assertFalse(w.public.exists())


def damage(path,mode):
    raw=path.read_bytes()
    if mode=="missing":
        path.unlink()
    elif mode=="empty":
        path.write_bytes(b"")
    elif mode=="truncate":
        path.write_bytes(raw[:len(raw)//2])
    elif mode=="one_byte":
        path.write_bytes(raw[:-1]+(b" " if raw[-1:]!=b" " else b"\n"))
    elif mode=="substitute":
        path.write_bytes(wire({"span_id":"invented-wrong-source"}))
    elif mode=="gzip_only":
        import gzip
        path.with_suffix(path.suffix+".gz").write_bytes(gzip.compress(raw))
        path.unlink()
    elif mode=="redirect":
        donor=path.with_name("different-fixture")
        donor.write_bytes(b"{}\n")
        path.unlink()
        path.symlink_to(donor)
    else:
        raise ValueError(mode)


class Matrix(Base):
    """Each Cartesian-product member is a separately discovered unittest."""


MUTATIONS=("missing","empty","truncate","one_byte","substitute","gzip_only","redirect")
BLIND=["registration.json",MAN,LEDGER,IPUB,IMAN,ISCHEMA,CONFIG,"dev/"+CONFIG,KITS,STAGE,
       *["kits/qual-0%d.json"%i for i in (1,2,3)],
       *[f"spans/{s}/{k}.json" for s in SPANS for k in ("receipt","hand","desk","q1","roster")]]
# All 30, independent of whatever list the implementation decides to walk.
PIN_PATHS=[p["path"] for p in slots(json.loads(registration()))]
BLIND+=sorted(set(PIN_PATHS))
assert len(set(PIN_PATHS))==30 and len(PIN_PATHS)==32 and len(set(BLIND))==len(BLIND)


def matrix_case(rel,mode):
    def test(self):
        w=self.copy()
        path=w.stage if rel==STAGE else w.files/rel
        damage(path,mode)
        self.refuses(w)
    return test


def add(cls,name,fn):
    assert not hasattr(cls,name),name
    fn.__name__=name
    setattr(cls,name,fn)


for rel in BLIND:
    for mode in MUTATIONS:
        add(Matrix,"test_input_"+re.sub(r"[^a-zA-Z0-9]","_",rel)+"_"+mode,matrix_case(rel,mode))


class Science(Base):
    def test_threshold_crossing_inside_point(self):
        w=fresh(self,"cross")
        self.success(w,"no")
        d=obj(w.private/"scores.json")["decision"]
        self.assertLess(abs(d["estimate"]),.1)
        self.assertLess(d["ci90"][0],-.1)
        self.assertGreater(d["ci90"][1],.1)

    def test_qual_noisy_single_leg_invariance(self):
        w=self.copy()
        base=self.success(w,"yes")
        mask=lambda raw:re.sub(rb'("[a-z0-9_]+_sha256":")[0-9a-f]{64}"',rb'\1' + b'x'*64+b'"',raw)
        baseline=mask(w.public.read_bytes())
        compared=skipped=0
        for row in relation(w):
            with self.subTest(leg=row["leg_key"]):
                trial=self.copy()
                path=trial.files/"observations"/(row["leg_key"]+".json")
                v=obj(path)
                for ch in v.values():
                    ch["segments"]=[j*1.005 for j in ch["segments"]]
                    ch["prefix_tails"]={k:j*1.005 for k,j in ch["prefix_tails"].items()}
                    if ch["terminal"] is not None:
                        ch["terminal"]*=1.005
                put(path,v)
                # Independent decision from the planted differences and analytically
                # known prediction. The equal-day critical value is for FOUR dates.
                by_day=collections.defaultdict(list)
                points=[]
                for leg in relation(trial):
                    if leg["leg_type"]!="A": continue
                    key=leg["leg_key"]
                    span_index=SPANS.index(leg["span_id"])
                    lo,hi=design("noisy")[4*span_index+int(key[-3:])-1][1:]
                    if key==row["leg_key"]:
                        P=leg["P"]
                        measured=obj(path)["gpu_rail"]
                        full=sum(measured["segments"])
                        short=sum(measured["segments"][:15])+measured["prefix_tails"]["3724"]
                        hi+=(1-1/1.005)*full
                        lo+=(1-1/1.005)*short
                    points.append(((0,0,1,1,2,3)[span_index],lo,hi))
                a,b=(statistics.stdev(p[i] for p in points) for i in (1,2))
                for day,lo,hi in points:
                    by_day[day].append(hi/b-lo/a)
                means=list(map(statistics.mean,by_day.values()))
                h=2.353363434801827*statistics.stdev(means)/2
                m=statistics.mean(means)
                expected="yes" if m-h>=-.1 and m+h<=.1 else "no"
                self.success(trial,expected)
                if expected!=base["qualified_qualification"]:
                    skipped+=1
                else:
                    compared+=1
                    self.assertEqual(mask(trial.public.read_bytes()),baseline)
        self.assertEqual(compared+skipped,36)
        self.assertGreater(compared,0)
        print(f"synthetic invariance: attempted=36 compared={compared} word_flip_skips={skipped}")

    def test_private_pair_support_and_singletons(self):
        for ratio in (1,2):
            for n in range(4):
                with self.subTest(ratio=ratio,complete=n):
                    spans=[s for s in range(6) if (1 if (s%2==1)^(s//2==2) else 2)==ratio]
                    missing=[SPANS[s]+"/L005" for s in spans[n:]]
                    w=fresh(self,excluded=missing)
                    self.success(w,"yes")
                    data=obj(w.private/"scores.json")
                    pair=data["pairs"][("1.10","1.30")[ratio-1]]
                    self.assertEqual((pair["complete"],pair["incomplete"],pair["status"]),
                        (n,3-n,("not_evaluable","not_evaluable","pairs_only","described")[n]))
                    self.assertEqual(set(pair["incomplete_ids"]),{x[:7]+"-p"+str(ratio) for x in missing})
                    if n<3:
                        self.assertIsNone(pair["estimate"])
                        self.assertIsNone(pair["ci90"])
                    self.assertEqual(len(pair["contrasts"]),n)
                    self.assertEqual(len(pair["own_prefix"]),n)
                    self.assertEqual(set(data["singletons"]),{key.replace("L005","L006") for key in missing})

    def test_each_of_six_blind_inclusion_rules(self):
        for rule in RULES:
            with self.subTest(rule=rule):
                w=World(Path(self.tmp.name)/rule).init()
                rel=f"spans/{SPANS[0]}/roster.json"
                rows=obj(w.files/rel)
                for i in (0,4):
                    rows["legs"][i]["rules"][rule]=False
                put(w.files/rel,rows)
                head=w.change({"evidence/"+rel:rows})
                put(w.root/"fixture-refs.json",{**w.refs(),"final":head})
                admit(self,w)
                self.success(w,"yes")
                self.assertEqual(obj(w.public)["included_legs"],34)
                self.assertIn(SPANS[0]+"/L006",obj(w.private/"scores.json")["singletons"])

    def test_private_print_inventory(self):
        w=self.copy()
        self.success(w,"yes")
        d=obj(w.private/"scores.json")
        self.assertEqual(set(d["bias"]),set(CHANNELS))
        for ch in CHANNELS:
            for ratio in ("1.10","1.30"):
                b=d["bias"][ch][ratio]
                self.assertEqual(len(b["ci90"]),2)
                self.assertIsInstance(b["estimate"],(int,float))
                self.assertEqual(b["contained"], b["ci90"][0]>=-.1 and b["ci90"][1]<=.1)
            self.assertIsInstance(d["bias"][ch]["1.374"]["estimate"],(int,float))
        self.assertEqual(set(d["load_ratios"]),{"2000","10000","19458"})
        self.assertEqual(set(d["maintenance"]),{"flagged","unflagged"})
        self.assertEqual(set(d["by_cell"]),set(d["load_ratios"]))
        self.assertEqual(set(d["joint"]),{"1/full_first","1/short_first","2/full_first","2/short_first"})
        self.assertEqual([len(d["joint"][k]) for k in sorted(d["joint"])],[1,2,3,0])
        self.assertTrue(d["pooled"])
        self.assertEqual(set(d["legs"]),{l["leg_key"] for l in relation(w)})
        self.assertEqual(obj(w.stage)["dates"],dict(zip(SPANS,("2031-02-03","2031-02-03","2031-02-04","2031-02-04","2031-02-05","2031-02-06"))))
        self.assertEqual(set(d["tails"]),{l["leg_key"] for l in relation(w) if l["N"]!=4096})


def planted(name,word):
    def test(self):
        self.success(fresh(self,name),word)
    return test


for direction,label in ((1,"upper"),(-1,"lower")):
    for big,where,word in ((18,"exact","yes"),(18+2**-15,"inside","yes"),(18-2**-15,"outside","no")):
        add(Science,"test_"+label+"_"+where,planted(f"edge/{direction}/{big}",word))
for cause in ("two_legs","two_days","two_narrow_days","one_day","zero_days","flat_long","flat_short","floor_long","floor_short"):
    add(Science,"test_not_evaluable_"+cause,planted(cause,"not_evaluable"))


add(Science,"test_above_sd_floor",planted("above_floor","yes"))


def excludes_l(key):
    def test(self):
        w=fresh(self,excluded=[key])
        self.success(w,"yes")
        self.assertEqual(obj(w.public)["included_legs"],35)
        self.assertNotIn(key,obj(w.private/"scores.json")["legs"])
    return test


for span in SPANS:
    for leg in ("L005","L006"):
        add(Science,"test_exclude_"+span.replace("-","_")+"_"+leg,excludes_l(span+"/"+leg))


class Provenance(Base):
    def test_published_registration_through_dispatcher(self):
        orig=registration()
        self.assertEqual(sha(orig),REG_HASH)
        self.assertEqual(len(set(PIN_PATHS)),30)
        path=Path(self.tmp.name)
        reg=path/"registration.json"
        file=path/"final.json"
        reg.write_bytes(orig)
        good=orig.replace(b'"PENDING:CODE"',b'"'+b'0'*64+b'"')
        for label,raw,rc in (("pins",good,0),("whitespace",good+b" ",2),
                             ("science",good.replace(b'"min_days": 3',b'"min_days": 2'),2),
                             ("add-path",good.replace(FIT.encode(),(FIT+".other").encode()),2),
                             ("unfilled",orig,2)):
            with self.subTest(label=label):
                file.write_bytes(raw)
                run=subprocess.run([sys.executable,"-B","-m","joulewise.cadence_looks.manifest_dispatch",
                                    "validate",str(file),"--final","--registration",str(reg)],
                    cwd=SOURCE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                self.assertEqual(run.returncode,rc,run.stderr)

    def test_registration_and_final_forged_together(self):
        w=self.copy()
        orig=(w.files/"registration.json").read_bytes()
        final=(w.files/MAN).read_bytes()
        # Both are valid-shaped and compare equal outside their slots. Neither
        # is the trusted registration. Forge even the latest row's registration SHA.
        led=obj(w.files/LEDGER)
        led["looks"][0].update(registration_sha256=sha(orig+b" "),sha256=sha(final+b" "))
        put(w.files/"registration.json",orig+b" ")
        w.change({MAN:final+b" ",LEDGER:led})
        self.refuses(w)

    def test_final_after_receipts_on_main_is_allowed(self):
        w=fresh(self,late_final=True)
        latest=max(obj(w.files/f"spans/{span}/receipt.json")["t0_epoch_s"] for span in SPANS)
        self.assertGreater(int(git(w.repo,"show","-s","--format=%ct",w.refs()["final"])),latest)
        self.success(w,"yes")

    def test_qualified_named_freeze_for_either_non_yes(self):
        for word in ("no","not_evaluable"):
            with self.subTest(word=word):
                w=fresh(self,word=word,named=True)
                self.success(w,"yes")

    def test_equivalent_pins_with_committed_record(self):
        self.success(fresh(self,equivalent=True),"yes")

    def test_wrong_host_before_reservation(self):
        for uuids in ([],[HOST_UUID,HOST_UUID],["invalid"],[HOST_UUID[:-1]+"2"]):
            w=self.copy()
            put(w.files/"local-host.json",{"IOPlatformUUID":uuids})
            self.refuses(w)

    def test_public_or_reservation_spends_id(self):
        w=self.copy()
        w.private.mkdir()
        self.refuses(w,reserved=True)
        w=self.copy()
        w.public.write_bytes(b"existing")
        r=launch(w,"stage2")
        self.assertEqual(r.returncode,2)
        read_trace(self,w)
        self.assertEqual(w.public.read_bytes(),b"existing")
        self.assertFalse(w.private.exists())

    def test_race_and_repeat(self):
        w=self.copy()
        children=[launch(w,"stage2",wait=False) for _ in range(2)]
        result=[(p.communicate(),p.returncode) for p in children]
        self.assertEqual(sorted(rc for _,rc in result),[0,2],result)
        records(self,w,"yes")
        self.assertEqual(len({p for kind,p in events(w) if kind=="reader_pid"}),1)
        prior=w.public.read_bytes()
        before={p.name:p.read_bytes() for p in w.private.iterdir()}
        clear(w)
        self.assertEqual(launch(w,"stage2").returncode,2)
        read_trace(self,w)
        self.assertEqual((prior,before),(w.public.read_bytes(),{p.name:p.read_bytes() for p in w.private.iterdir()}))

    def test_repointed_output_cannot_reset_id(self):
        w=self.copy()
        self.success(w,"yes")
        before=w.public.read_bytes()
        clear(w)
        trial=launch(w,"stage2",["--out",str(w.root/"elsewhere")])
        self.assertEqual(trial.returncode,2)
        read_trace(self,w)
        self.assertEqual(w.public.read_bytes(),before)
        self.assertFalse((w.root/"elsewhere").exists())

    def test_spent_history_survives_reset_row(self):
        for status in ("failed","interrupted","run","frozen"):
            w=self.copy()
            valid=obj(w.files/LEDGER)
            old=json.loads(wire(valid))
            old["looks"][0].update(status=status,error_type="none_recorded" if status=="interrupted" else "ValueError")
            w.change({LEDGER:old})
            w.change({LEDGER:valid})
            self.refuses(w)

    def test_branch_only_publication(self):
        w=self.copy()
        git(w.repo,"update-ref",MAIN,w.refs()["registration"])
        self.refuses(w)

    def test_successor_without_ruling(self):
        w=self.copy()
        changed=(w.files/MAN).read_bytes().replace(LOOK.encode(),b"lm-qual-02")
        w.change({MAN:changed})
        self.refuses(w)


def semantic(kind,mode):
    def test(self):
        w=self.copy()
        if kind in SPANS:
            path=f"spans/{kind}/receipt.json"
            record=obj(w.files/path)
            if mode in ("earlier","tie"):
                record["t0_epoch_s"]=BASE_TIME-(mode=="earlier")
            if mode=="unbound": record["span_id"]=SPANS[(SPANS.index(kind)+1)%6]
            if mode=="kit": record["kit_sha256"]="0"*64
            if mode=="no_order": record.pop("registration_at_issue")
            if mode=="foreign_order": record["registration_at_issue"]="f"*40
            put(w.files/path,record)
            w.change({"evidence/"+path:record})
        elif kind in ("stage1","ledger","interim","equivalence","naming"):
            led=obj(w.files/LEDGER)
            q,i=led["looks"]
            if kind=="stage1":
                st=obj(w.stage)
                if mode=="numpy": st["numpy_version"]="foreign-version"
                if mode=="count": st["counts"]["included_legs"]-=1
                if mode=="config": st["configs"]["development_sha256"]="3"*64
                if mode=="roster": st["roster"]=st["roster"][:-1]
                put(w.stage,st)
                q["stage1_sha256"]=sha(w.stage.read_bytes())
                w.change({STAGE:st,LEDGER:led})
            if kind=="ledger":
                if mode=="registration_hash": q["registration_sha256"]="3"*64
                if mode=="registration_commit": q["registration_commit"]=w.refs()["final"]
                if mode=="final_hash": q["sha256"]="3"*64
                if mode=="exec_host": q["execution_host"]="hw1:"+"3"*64
                if mode=="stage_hash": q["stage1_sha256"]="3"*64
                if mode=="status": q["status"]="registered"
                w.change({LEDGER:led})
            if kind=="interim":
                p=obj(w.files/IPUB)
                if mode in ("no","not_evaluable"): p["twin_agrees"]=mode
                if mode=="no_word": p.pop("twin_agrees")
                if mode=="wrong_id": p["look_id"]=LOOK
                if mode=="coeff_hash": i["coefficients_sha256"]="7"*64
                i["output_sha256"]=sha(wire(p)) if mode!="public_hash" else "7"*64
                w.change({IPUB:p,LEDGER:led})
            if kind=="equivalence":
                w=fresh(self,equivalent=True)
                data=obj(w.files/EQUIV)
                led=obj(w.files/LEDGER)
                if mode=="record_hash": led["looks"][0]["equivalence_sha256"]="0"*64
                elif mode=="absent": led["looks"][0].pop("equivalence_sha256")
                else:
                    if mode=="different_predictions": data["qualification_predictions_sha256"]="3"*64
                    if mode=="wrong_pin": data["qualification_sha256"]="3"*64
                    if mode=="zero_segments": data["segments_compared"]=0
                    led["looks"][0]["equivalence_sha256"]=sha(wire(data))
                w.change({EQUIV:data,LEDGER:led})
            if kind=="naming":
                w=fresh(self,word="no",named=True)
                record=obj(w.files/NAMING)
                if mode in ("coefficients_sha256","public_sha256"): record[mode]="1"*64
                if mode=="designation": record[mode]="other"
                if mode=="ruling": record[mode]="RL-123"
                if mode=="look_id": record[mode]=LOOK
                if mode=="extra": record["extra"]=True
                if mode=="stanza": record[mode]+=" extra"
                if mode=="noncanonical":
                    w.change({NAMING:wire(record)+b" "})
                elif mode in ("nonancestor","duplicate","wrong_heading","missing_line"):
                    old=record["decisions_commit"]
                    line=record["stanza"]
                    text="# RL-99999. Synthetic\n"+line+"\n"
                    if mode=="duplicate": text+=line+"\n"
                    if mode=="wrong_heading": text=text.replace("# RL-99999","# RL-99998")
                    if mode=="missing_line": text=text.replace(line,"held")
                    audit=history(w.repo,"refs/heads/new-audit",{RLD:text.encode()},old)
                    if mode!="nonancestor": git(w.repo,"update-ref",AUDIT,audit)
                    record["decisions_commit"]=audit
                    w.change({NAMING:record})
                else: w.change({NAMING:record})
        self.refuses(w)
    return test


for group,modes in {
    **{s:("earlier","tie","unbound","kit","no_order","foreign_order") for s in SPANS},
    "stage1":("numpy","count","config","roster"),
    "ledger":("registration_hash","registration_commit","final_hash","stage_hash","exec_host","status"),
    "interim":("no","not_evaluable","no_word","wrong_id","coeff_hash","public_hash"),
    "equivalence":("absent","record_hash","different_predictions","wrong_pin","zero_segments"),
    "naming":("coefficients_sha256","public_sha256","designation","ruling","look_id","extra",
              "stanza","noncanonical","nonancestor","duplicate","wrong_heading","missing_line")
}.items():
    for mode in modes:
        add(Provenance,"test_"+group.replace("-","_")+"_"+mode,semantic(group,mode))


def optional_matrix(kind,mutation):
    def test(self):
        w=fresh(self,**({"named":True,"word":"no"} if kind=="naming" else {"equivalent":True}))
        path=NAMING if kind=="naming" else EQUIV
        damage(w.files/path,mutation)
        self.refuses(w)
    return test


for kind in ("naming","equivalence"):
    for mutation in MUTATIONS:
        add(Provenance,"test_input_"+kind+"_"+mutation,optional_matrix(kind,mutation))


def blind_span(kind,span):
    def test(self):
        w=World(Path(self.tmp.name)/"pre").init()
        rel=f"spans/{span}/{kind}.json"
        data=obj(w.files/rel)
        data["span_id"]=next(s for s in SPANS if s!=span)
        put(w.files/rel,data)
        w.change({"evidence/"+rel:data})
        self.refuses(w,stage="stage1")
        self.assertFalse(w.stage.exists())
    return test


for span in SPANS:
    for kind in ("receipt","hand","desk","q1","roster"):
        add(Provenance,"test_stage1_bound_"+span.replace("-","_")+"_"+kind,blind_span(kind,span))


def host_mutation(mode):
    def test(self):
        w=self.copy()
        path=w.files/"local-host.json"
        if mode=="one_byte":
            raw=path.read_bytes()
            path.write_bytes(raw.replace(HOST_UUID.encode(),(HOST_UUID[:-1]+"2").encode()))
        else:
            damage(path,mode)
        self.refuses(w)
    return test


for mode in MUTATIONS:
    add(Provenance,"test_input_host_"+mode,host_mutation(mode))


class Boundary(Base):
    def test_field_type_and_source_binding(self):
        w=self.copy()
        original=self.success(w,"yes")
        valid=wire(original)
        candidate=w.root/"candidate.json"
        put(candidate,valid)
        self.assertEqual(launch(w,"validate-public",["--candidate",str(candidate)]).returncode,0)
        wrong={"commit":"1"*40,"included_legs":original["included_legs"]-1,"look_id":"lm-qual-02",
               "type_m_residual":"some text","stage2_error":"yes","qualified_qualification":"maybe"}
        for key in original:
            changed={**original,key:wrong.get(key,"0"*64)}
            cases=[wire(changed),wire({k:v for k,v in original.items() if k!=key}),
                   wire({**original,key:1.0}),wire({**original,key:True}),wire({**original,key:[]})]
            for raw in cases:
                with self.subTest(key=key,candidate=raw):
                    put(candidate,raw)
                    self.assertEqual(launch(w,"validate-public",["--candidate",str(candidate)]).returncode,2)
        for raw in (wire({**original,"unexpected":1}),wire({**original,"included_legs":"36"}),
                    valid.replace(b'"included_legs":36',b'"included_legs":36e0'),
                    valid.replace(b'"included_legs":36',b'"included_legs":36.0')):
            put(candidate,raw)
            self.assertEqual(launch(w,"validate-public",["--candidate",str(candidate)]).returncode,2)
        self.assertEqual(w.public.read_bytes(),valid)

    def test_failure_after_first_response_read(self):
        for fault,word in (("builtin","RuntimeError"),("custom","OtherError"),("spoof","OtherError"),
                           ("json","JSONDecodeError"),("linalg","LinAlgError")):
            with self.subTest(fault=fault):
                w=self.copy()
                r=launch(w,"stage2",fault=fault)
                self.assertEqual((r.returncode,r.stdout,r.stderr),(1,b"",f"stage2_error\n{word}\n".encode()))
                self.assertFalse(w.public.exists())
                self.assertTrue(restricted_writes(self,w))
                self.assertFalse(any(p==str(w.public.relative_to(w.root)) and kind!="open" for kind,p in events(w)))
                self.assertIn(b"child-333.444", (w.private/"stdout").read_bytes())
                self.assertIn(b"parent-654.321",(w.private/"stderr").read_bytes())
                clear(w)
                self.refuses(w,reserved=True)


# A missing/unusable file detected without an open is pre-read. Once private
# coefficient bytes or a response have been opened the same fixed failure applies.
def private_damage(family,mode):
    def test(self):
        w=self.copy()
        key=SPANS[-1]+"/L006"
        p=w.coef if family=="coefficients" else w.files/"observations"/(key+".json")
        damage(p,mode)
        # A trailing whitespace byte changes a coefficient SHA but is valid JSON.
        # Level E is a generated representation, so the response mutation instead
        # breaks its closed numeric shape without relying on a raw archive hash.
        if family=="response" and mode=="one_byte":
            raw=p.read_bytes()
            p.write_bytes(b"X"+raw[1:])
        r=launch(w,"stage2")
        if family=="coefficients":
            read_trace(self,w,allow_coefficient=True)
        if family=="coefficients" and mode in ("missing","gzip_only","redirect"):
            attempted=any(kind=="open" and file==str(p.relative_to(w.root)) for kind,file in events(w))
            self.assertEqual(r.returncode,1 if attempted else 2)
        else:
            self.assertEqual(r.returncode,1)
        if r.returncode==1:
            self.assertRegex(r.stderr,rb"\Astage2_error\n(?:[A-Za-z]+Error|OtherError)\n\Z")
        self.assertEqual(r.stdout,b"")
        self.assertFalse(w.public.exists())
        self.assertTrue(w.private.is_dir())
        restricted_writes(self,w)
    return test


for family in ("coefficients","response"):
    for mode in MUTATIONS:
        add(Boundary,"test_"+family+"_"+mode,private_damage(family,mode))


def independent_oracle(name):
    def test(self):
        expect_file=HERE/"qual_oracle_expected.json"
        self.assertTrue(expect_file.is_file(),"Independent Opus oracle required")
        expect=obj(expect_file)
        self.assertEqual(set(expect),set(ORACLES))
        w=fresh(self,name)
        rec=self.success(w,native=(name=="l_partial_blocks_same_scorer"))
        if name=="l_partial_blocks_same_scorer":
            pin=json.loads((w.files/MAN).read_bytes())["pins"]["scorer"]["sha256"]
            calls={tuple(value) for kind,value in events(w) if kind=="native"}
            self.assertEqual(calls,{(leg["leg_key"],leg["leg_type"],pin) for leg in relation(w)})
        private=obj(w.private/"scores.json")
        want=expect[name]
        if name=="l_partial_blocks_same_scorer":
            samples={"full":SPANS[0]+"/L006","short3724":SPANS[1]+"/L006","short3151":SPANS[0]+"/L005"}
            self.assertEqual(set(want),set(samples))
            for alias,key in samples.items():
                self.assertEqual(set(want[alias]),set(CHANNELS))
                for ch in CHANNELS:
                    actual=private["legs"][key][ch]
                    exp=want[alias][ch]
                    fields={"predicted","measured"} | ({"tail_predicted","tail_measured"} if alias!="full" else set())
                    self.assertEqual(set(exp),fields)
                    for field in fields:
                        self.number(actual[field],exp[field])
        else:
            self.assertEqual(set(want),{"word","estimate","ci90","n_legs","n_days"})
            self.assertEqual(rec["qualified_qualification"],want["word"])
            for k in ("n_legs","n_days"):
                self.assertIs(type(want[k]),int)
                self.assertEqual(private["decision"][k],want[k])
            self.number(private["decision"]["estimate"],want["estimate"])
            actual=private["decision"]["ci90"]
            if want["ci90"] is None:
                self.assertIsNone(actual)
            else:
                self.assertEqual(len(want["ci90"]),2)
                self.assertEqual(len(actual),2)
                for a,b in zip(actual,want["ci90"]):
                    self.number(a,b)
    return test


class Oracle(Base):
    def number(self,a,b):
        if b is None:
            self.assertIsNone(a)
        else:
            self.assertIs(type(b) in (int,float),True)
            self.assertIs(type(a) in (int,float),True)
            self.assertTrue(math.isclose(a,b,rel_tol=2e-12,abs_tol=2e-12),(a,b))


for name in ORACLES:
    add(Oracle,"test_qual_"+name,independent_oracle(name))

if __name__=="__main__":
    unittest.main()

