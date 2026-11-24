"""Apply issued v3.2 operands to the complete v4 synthetic control.

RL-215 (lead edit 2026-11-24): the 40 operand-rulings.tsv IDs print INAPPLICABLE and are not
counted (Q3); PARITY_DIFFERENCE blocks nothing, but a must-refuse ID the archive admits is FALSE_PASS (Q5).

This is a compatibility diagnostic. The original direct issue remains independently runnable.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
V4 = HERE.parent / "tests/align/test_partc_writer_v4.py"


def module():
    spec = importlib.util.spec_from_file_location("partc_v4_normalized", V4)
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


def operands(s):
    with (HERE/"expectations.tsv").open() as stream:
        expected = {row["case"]: row["expected"] for row in csv.DictReader(stream,delimiter="\t")}
    seen = set()
    with gzip.open(HERE/"operands.jsonl.gz","rt") as stream:
        for line in stream:
            name, constructor, fields = json.loads(line)
            if constructor not in ("Mutation","DecisionCase","InputCase","LaunchCase","DescriptorCase"):
                raise ValueError(constructor)
            if "path" in fields: fields["path"] = tuple(fields["path"])
            case = getattr(s,constructor)(**fields)
            assert case.name == name and name not in seen
            seen.add(name)
            yield case, expected[name]
    assert seen == set(expected) and len(seen)==25300


def run_one(s, base, probe, case, expectation):
    if isinstance(case, s.DescriptorCase):
        result, name, why=s.descriptor_trial(case)
        assert ("expected="+expectation.removeprefix("descriptor ")+" ") in why
        return result
    if isinstance(case, s.InputCase):
        result, name, why=s.issued_trial(case)
        accepted=result in ("FALSE_PASS","AGREES_PASS")
    else:
        accepted=probe.candidate(case)
    if expectation=="must refuse" and accepted:return "FALSE_PASS"
    if expectation=="must pass" and not accepted:return "WRONG_VERDICT"
    if not isinstance(case,(s.InputCase,s.LaunchCase)):
        output=probe.tree/"native/synthetic-run/part-c"
        for role in (s.P,s.S,s.D,s.X):
            destination=output/s.pc.KINDS[role]
            if not destination.exists():s.copy_segment(base,role,destination)
        archive=s.pc.replay_archived(output,s.rt.ROOT/s.r1.DEFAULT_RUNTIME_CONFIG)
        native=s.read(output/"smoke.json")["evaluation"]
        if native["verdict"]!=archive["verdict"]:
            # RL-215 Q5: a must-refuse ID admitted on either path is a false pass
            if expectation=="must refuse" and archive["verdict"]=="pass":return "FALSE_PASS"
            return "PARITY_DIFFERENCE"
        reasons=set(native["evidence_failures"])
        if reasons != s.archive_refusal_codes(archive,reasons):
            return "PARITY_DIFFERENCE"
    return "AGREES_PASS" if accepted else "REFUSED"


def main():
    s=module()
    inventory=list(operands(s))
    if os.environ.get("JW_PARTC_INVENTORY")=="only":
        print("issued operand IDs",len(inventory))
        return
    pattern=re.compile(os.environ.get("JW_PARTC_CASE","."))
    index,count=map(int,os.environ.get("JW_PARTC_SHARD","0/1").split("/"))
    assert 0<=index<count
    with (HERE/"operand-rulings.tsv").open() as stream:
        unreachable={r["case"]:r["unavailable_operand"] for r in csv.DictReader(stream,delimiter="	")}
    chosen=[(c,e) for c,e in inventory if pattern.search(c.name)
            and int.from_bytes(hashlib.sha256(c.name.encode()).digest()[:4])%count==index]
    assert chosen,"empty selection"
    with tempfile.TemporaryDirectory(prefix="jw-v4-compat-") as tmp:
        root=Path(tmp)
        with s.v4_context(root):
            base=root/"base"
            assert not s.control(base)
            probe=s.Probe(base);s.WORKER=s.ORIGINAL=probe
            assert s.issued_verdict(probe)["pass"] and probe.candidate(None)
            failed=0
            for case,wanted in chosen:
                if case.name in unreachable:
                    # RL-215 Q3: absent observe-only status leaf; inapplicable, not counted
                    print("INAPPLICABLE",case.name,unreachable[case.name],wanted,flush=True)
                    continue
                try: outcome=run_one(s,base,probe,case,wanted)
                except Exception as exc:
                    outcome="OPERAND_ERROR"
                    print(outcome,case.name,type(exc).__name__,str(exc),flush=True)
                print(outcome,case.name,wanted,flush=True)
                # RL-215 Q5: reason/parity differences on legacy IDs are printed and block nothing
                failed+=outcome not in ("AGREES_PASS","REFUSED","PARITY_DIFFERENCE")
            assert not failed, f"{failed} compatibility discrepancies"


if __name__=="__main__":
    main()
