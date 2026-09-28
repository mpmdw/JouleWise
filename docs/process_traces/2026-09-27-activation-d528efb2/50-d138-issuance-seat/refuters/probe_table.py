import sys, json, hashlib, copy
from pathlib import Path
from unittest.mock import patch
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-final-d528efb2"); sys.path.insert(0, str(ROOT)); sys.dont_write_bytecode = True
import joulewise.calibration_bracketing as B
import joulewise.calibration_dispositions as D
import scripts.issue_calibration_acceptance_generation as I
from scripts.issue_calibration_acceptance_generation import derivation_sha256
issued = json.loads(B.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH.read_bytes())
def valid(v): v = copy.deepcopy(v); v["derivation_sha256"] = derivation_sha256(v); return B._valid_acceptance_bound(v)
raw = D.DISPOSITION_REGISTRY_PATH.read_bytes(); rows = json.loads(raw)
table = {c: d for d, r in D.DISPOSITION_DECISIONS.items() for c in r["content_ids"]}
print("T0 file sha == pin", hashlib.sha256(raw).hexdigest() == D.DISPOSITION_REGISTRY_SHA256, "rows", len(rows), "parsed==table", D.parse_disposition_registry(raw, expected_sha256=D.DISPOSITION_REGISTRY_SHA256) == table)
# T1 file edited (drop a row), pin NOT updated
b1 = (json.dumps(rows[:-1], indent=2, ensure_ascii=False) + "\n").encode()
try: D.parse_disposition_registry(b1, expected_sha256=D.DISPOSITION_REGISTRY_SHA256); print("T1 accepted!")
except D.DispositionRegistryError as e: print("T1 file edited, pin unchanged ->", str(e)[:40])
# T2 file edited, module pin updated, table not
with patch.object(D, "DISPOSITION_REGISTRY_SHA256", hashlib.sha256(b1).hexdigest()):
    try: D.parse_disposition_registry(b1, expected_sha256=D.DISPOSITION_REGISTRY_SHA256); print("T2 accepted!")
    except D.DispositionRegistryError as e: print("T2 file+module pin edited, table not ->", e)
# T3 file edited, only the issuer-level pin overridden (caller passes its own expected digest)
out = D.parse_disposition_registry(b1, expected_sha256=hashlib.sha256(b1).hexdigest())
print("T3 caller-supplied digest != module pin -> table equality SKIPPED, returns", len(out), "rows")
with patch.object(I, "DISPOSITION_REGISTRY_SHA256", hashlib.sha256(b1).hexdigest()):
    p = Path("/tmp/d138-contract-refuter/scratch/disp10.json"); p.write_bytes(b1)
    print("T3b issuer _registered_dispositions with patched issuer pin ->", len(I._registered_dispositions(p)), "rows (no table check)")
# T4 mechanism sentence edit
r2 = copy.deepcopy(rows); r2[0]["mechanism"] += "."
b4 = (json.dumps(r2, indent=2, ensure_ascii=False) + "\n").encode()
try: D.parse_disposition_registry(b4, expected_sha256=hashlib.sha256(b4).hexdigest()); print("T4 accepted!")
except D.DispositionRegistryError as e: print("T4 mechanism edit ->", e)
# Loader vs table drift
ids = D.DISPOSITION_DECISIONS[D.DISPOSITION_DECISION_ID]["content_ids"]
prior = issued["prior_observation_set"]["observations"]
def with_table(new_ids):
    alt = {D.DISPOSITION_DECISION_ID: {"mechanism": D.DISPOSITION_MECHANISM, "content_ids": frozenset(new_ids)}}
    return patch.object(D, "DISPOSITION_DECISIONS", alt)
print("V0 real issued valid", valid(issued))
with with_table(set(ids) - {sorted(ids)[0]}): print("V1 table drops one id ->", valid(issued))
with with_table(set(ids) | {"b"*64}): print("V2 table gains id absent from prior set ->", valid(issued))
old = next(r for r in prior if r["epoch_id"] != "d079_epoch_25g83" and r["disposition"] == "valid")
with with_table(set(ids) | {old["content_id"]}): print("V3 table gains a 25F84 valid prior row id ->", valid(issued), "(silent drift; only test D1 catches)")
w1inv = next(r for r in prior if r.get("session_id","") and r["session_id"].endswith("w1-20260927") and r["disposition"] != "valid")
with with_table(set(ids) | {w1inv["content_id"]}): print("V4 table gains an invalid W1 row id ->", valid(issued))
alt2 = dict(D.DISPOSITION_DECISIONS); alt2["D-999-future"] = {"mechanism": "x", "content_ids": frozenset({old["content_id"]})}
with patch.object(D, "DISPOSITION_DECISIONS", alt2): print("V5 a later decision disposing a row already in this prior set ->", valid(issued), "(fail-closed: issued file stops loading)")
# counts
from collections import Counter
c = Counter((r["epoch_id"], r["disposition"], (r.get("session_id") or "")[-14:]) for r in prior)
v = [r for r in prior if r["disposition"]=="valid"]
print("C prior", len(prior), "valid", len(v), "valid target", sum(r["epoch_id"]=="d079_epoch_25g83" for r in v), "valid earlier", sum(r["epoch_id"]!="d079_epoch_25g83" for r in v), "excluded_members", len(issued["derivation_notes"].get("excluded_members", [])), "declared", issued["prior_observation_set"].get("disposing_decision_ids"))
print("C disposed rows present", sum(r["content_id"] in ids for r in prior), "their sessions", sorted({r["session_id"] for r in prior if r["content_id"] in ids}), "dispositions", sorted({r["disposition"] for r in prior if r["content_id"] in ids}))
