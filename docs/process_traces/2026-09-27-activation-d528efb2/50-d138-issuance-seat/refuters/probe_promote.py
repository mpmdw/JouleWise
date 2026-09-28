import sys, json, hashlib, copy, subprocess, difflib
from pathlib import Path
from unittest.mock import patch
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-final-d528efb2"); sys.path.insert(0, str(ROOT)); sys.dont_write_bytecode = True
import scripts.promote_calibration_candidate as P
import joulewise.calibration_bracketing as B
from scripts.issue_calibration_acceptance_generation import derivation_input_sha256, derivation_sha256
S = Path("/tmp/d138-contract-refuter/scratch")
craw = P.CANDIDATE.read_bytes(); traw = P.ISSUANCE_TEXT.read_bytes(); cand = json.loads(craw); text = json.loads(traw)
iraw = B.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH.read_bytes()
print("P0 candidate sha", hashlib.sha256(craw).hexdigest()[:16], "text sha", hashlib.sha256(traw).hexdigest()[:16])
r = subprocess.run(["/opt/homebrew/bin/python3","-B",str(ROOT/"scripts/promote_calibration_candidate.py"),"--check",str(B.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH)],capture_output=True,text=True,cwd="/tmp")
print("P1 --check committed rc", r.returncode, r.stdout.strip(), r.stderr.strip())
tamp = S/"issued_tampered.json"; tamp.write_bytes(iraw.replace(b'"claim_eligible": true', b'"claim_eligible": true ', 1))
r = subprocess.run(["/opt/homebrew/bin/python3","-B",str(ROOT/"scripts/promote_calibration_candidate.py"),"--check",str(tamp)],capture_output=True,text=True,cwd="/tmp")
print("P1b --check one-byte-different rc", r.returncode, r.stderr.strip())
out = S/"out.json"; out.write_bytes(b"{}")
r = subprocess.run(["/opt/homebrew/bin/python3","-B",str(ROOT/"scripts/promote_calibration_candidate.py"),"--out",str(out)],capture_output=True,text=True,cwd="/tmp")
print("P1c --out onto different existing bytes rc", r.returncode, r.stderr.strip(), "file untouched", out.read_bytes()==b"{}")
def ser(v): return (json.dumps(v, indent=2, ensure_ascii=True) + "\n").encode()
def tryp(c, t=traw, **pat):
    try:
        with patch.multiple(P, **pat) if pat else _null():
            P.promote(c, t); return "ACCEPTED"
    except (ValueError, KeyError, TypeError) as e: return "refused: " + str(e)[:70]
import contextlib
_null = contextlib.nullcontext
c = copy.deepcopy(cand); c["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.030000000000000000"; cb = ser(c)
print("P3a member altered ->", tryp(cb))
print("P3b + digest pin patched ->", tryp(cb, CANDIDATE_SHA256=hashlib.sha256(cb).hexdigest()))
c["derivation_input_sha256"] = derivation_input_sha256(c); c["derivation_sha256"] = derivation_sha256(c); cb2 = ser(c)
print("P3c + both candidate seals recomputed + digest patched ->", tryp(cb2, CANDIDATE_SHA256=hashlib.sha256(cb2).hexdigest()))
c = copy.deepcopy(cand); c["artifact_role"] = "issued"; c["derivation_sha256"] = derivation_sha256(c); cb3 = ser(c)
print("P3d non-candidate role ->", tryp(cb3, CANDIDATE_SHA256=hashlib.sha256(cb3).hexdigest()))
t = copy.deepcopy(text); t["issuance_record"]["rulings"][0]["file_sha256"] = "f"*64
print("P4a well-formed but WRONG ruling digest ->", tryp(craw, json.dumps(t).encode()))
t = copy.deepcopy(text); t["issuance_record"]["rulings"][0]["relative_path"] = "nonexistent.md"
print("P4b ruling path to nonexistent file ->", tryp(craw, json.dumps(t).encode()))
t = copy.deepcopy(text); t["issuance_record"]["disclosures"][7]["text"] = "x"
print("P4c D8 text replaced by 'x' ->", tryp(craw, json.dumps(t).encode()))
t = copy.deepcopy(text); t["network_time_provenance"]["text"] = "contradicts D8"
print("P4d network_time_provenance text != D8 ->", tryp(craw, json.dumps(t).encode()))
t = copy.deepcopy(text); t["issuance_record"].pop("claim_eligible_meaning", None); t["issuance_record"].pop("hold_enforcement", None)
print("P4e claim_eligible_meaning + hold_enforcement removed ->", tryp(craw, json.dumps(t).encode()))
t = copy.deepcopy(text); t["issuance_record"]["source_candidate"]["relative_path"] = "elsewhere"
print("P4f source_candidate.relative_path wrong ->", tryp(craw, json.dumps(t).encode()))
# committed file: ruling digests vs files on disk
iss = json.loads(iraw)
rec = iss["derivation_notes"]["issuance_record"]
for rr in rec["rulings"]:
    p = ROOT/rr["relative_path"]
    print("R", rr["id"], rr["relative_path"][-60:], "exists", p.exists(), "match", p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==rr["file_sha256"])
sc = rec["source_candidate"]; print("R source_candidate", sc.get("relative_path"), sc.get("file_sha256","")[:8], sc.get("derivation_sha256","")[:8], "cand derivation_sha256", cand["derivation_sha256"][:8])
ntp = iss["derivation_notes"]["network_time_provenance"]
print("R ntp keys", sorted(ntp), "text==D8", ntp.get("text") == rec["disclosures"][7]["text"])
if "source_ruling" in ntp:
    p = ROOT/ntp["source_ruling"]["relative_path"] if "relative_path" in ntp["source_ruling"] else None
    print("R ntp source_ruling", ntp["source_ruling"], "match", p is not None and p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==ntp["source_ruling"].get("sha256", ntp["source_ruling"].get("file_sha256")))
print("R issuance_record keys", sorted(rec)); print("R holds ids", [h["id"] for h in rec["holds"]]); print("R disclosures", [d["id"] for d in rec["disclosures"]])
print("R issuance", {k: (v if k!="reason" else v[:80]) for k,v in iss["issuance"].items()})
print("R backfill", {k: v for k,v in iss["backfill_candidate"].items() if k!="candidate_inventory"} )
print("R top keys order", list(iss)); print("R cand keys order ", list(cand))
# line diff
d = [l for l in difflib.unified_diff(craw.decode().splitlines(), iraw.decode().splitlines(), lineterm="", n=0) if l.startswith(("+","-")) and not l.startswith(("+++","---"))]
removed = [l for l in d if l.startswith("-")]
print("DIFF removed lines:", len(removed)); [print("   ", l[:110]) for l in removed]
added = [l for l in d if l.startswith("+")]; print("DIFF added lines:", len(added))
print("NONASCII in issued", any(b>127 for b in iraw))
