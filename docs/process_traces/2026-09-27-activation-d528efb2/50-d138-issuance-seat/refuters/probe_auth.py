import sys, json, hashlib, copy, builtins, os, io
from pathlib import Path
from unittest.mock import patch
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-final-d528efb2")
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
import joulewise.calibration_bracketing as B
import joulewise.calibration_dispositions as D
from scripts.issue_calibration_acceptance_generation import derivation_input_sha256, derivation_sha256
S = Path("/tmp/d138-contract-refuter/scratch"); S.mkdir(exist_ok=True)
NEW = B.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH; R7 = B.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH
raw = NEW.read_bytes(); issued = json.loads(raw)
def ser(v): return (json.dumps(v, indent=2, ensure_ascii=True) + "\n").encode()
def load_bytes(b, name):
    p = S / name; p.write_bytes(b); r = B.load_calibration_acceptance_bound(p)
    return None if r is None else r["acceptance_id"]
print("A0 sha256(new file)", hashlib.sha256(raw).hexdigest(), "== pin", hashlib.sha256(raw).hexdigest() == B.EPOCH_25G83_R1_ACCEPTANCE_BOUND_SHA256)
print("A1 default loads ->", B.load_calibration_acceptance_bound()["acceptance_id"], "| ACTIVE", B.ACTIVE_ACCEPTANCE_ID)
print("A1 R7 by path ->", B.load_calibration_acceptance_bound(R7)["acceptance_id"])
print("A2 byte-identical copy elsewhere ->", load_bytes(raw, "copy.json"))
print("A3 trailing space ->", load_bytes(raw + b" ", "ws.json"))
print("A4 reserialized indent=1 ->", load_bytes((json.dumps(issued, indent=1)+"\n").encode(), "indent1.json"))
t = copy.deepcopy(issued); t["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.030000000000000000"
t["derivation_input_sha256"] = derivation_input_sha256(t); t["derivation_sha256"] = derivation_sha256(t); tb = ser(t)
print("A5 member altered+resealed ->", load_bytes(tb, "member.json"))
with patch.dict(B.ISSUED_ACCEPTANCE_REGISTRY, {B.EPOCH_25G83_R1_ACCEPTANCE_ID: dict(B.ISSUED_ACCEPTANCE_REGISTRY[B.EPOCH_25G83_R1_ACCEPTANCE_ID], file_sha256=hashlib.sha256(tb).hexdigest())}):
    print("A5b same, with pin swapped to tampered digest (validator alone) ->", load_bytes(tb, "member2.json"))
t = copy.deepcopy(issued); t["derivation_notes"]["issuance_record"]["disclosures"] = t["derivation_notes"]["issuance_record"]["disclosures"][:7]
t["derivation_notes"]["issuance_record"]["holds"] = []; t["derivation_sha256"] = derivation_sha256(t); tb = ser(t)
print("A6 D8+holds dropped+resealed ->", load_bytes(tb, "d8.json"))
with patch.dict(B.ISSUED_ACCEPTANCE_REGISTRY, {B.EPOCH_25G83_R1_ACCEPTANCE_ID: dict(B.ISSUED_ACCEPTANCE_REGISTRY[B.EPOCH_25G83_R1_ACCEPTANCE_ID], file_sha256=hashlib.sha256(tb).hexdigest())}):
    print("A6b same with pin swapped (validator alone; disclosures unguarded by validator) ->", load_bytes(tb, "d82.json"))
r7 = json.loads(R7.read_bytes()); r7["acceptance_id"] = B.EPOCH_25G83_R1_ACCEPTANCE_ID; r7["derivation_sha256"] = derivation_sha256(r7)
print("A7 R7 content relabelled as new id ->", load_bytes(ser(r7), "r7as.json"))
cand = ROOT / "docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json"
print("A8 candidate dbad7cc7 ->", load_bytes(cand.read_bytes(), "cand.json"), hashlib.sha256(cand.read_bytes()).hexdigest()[:8])
t = copy.deepcopy(issued); t["acceptance_id"] = B.ANCHOR_V3_R7_ACCEPTANCE_ID; t["derivation_sha256"] = derivation_sha256(t)
print("A9 new content relabelled as R7 id ->", load_bytes(ser(t), "newasr7.json"))
t = copy.deepcopy(issued); t["derivation_notes"]["x"] = 1
print("A10 explicit in-memory route, one extra note ->", B._authenticated_explicit_acceptance_bound(t))
print("A10b explicit in-memory route, exact ->", (B._authenticated_explicit_acceptance_bound(copy.deepcopy(issued)) or {}).get("acceptance_id"))
# A11 no load-time IO on the disposition file (new file included)
target = str(D.DISPOSITION_REGISTRY_PATH.resolve()); hits = []
ro, rb, oo = builtins.open, Path.read_bytes, os.open
def g_open(f, *a, **k):
    if str(Path(str(f)).resolve()) == target if isinstance(f,(str,Path)) else False: hits.append("open"); raise AssertionError
    return ro(f, *a, **k)
def g_rb(p):
    if str(p.resolve()) == target: hits.append("read_bytes"); raise AssertionError
    return rb(p)
def g_os(f, *a, **k):
    if isinstance(f,(str,Path)) and str(Path(str(f)).resolve()) == target: hits.append("os.open"); raise AssertionError
    return oo(f, *a, **k)
with patch.object(builtins, "open", g_open), patch.object(Path, "read_bytes", g_rb), patch.object(os, "open", g_os):
    ok = B.load_calibration_acceptance_bound(NEW)
print("A11 new file loads with disposition-file IO guarded ->", ok is not None, "hits", hits)
