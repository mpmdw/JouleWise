#!/usr/bin/env python3
"""Attribute root-23 re-read differences to the predeclared RL-113..121 delta."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json

from b6_r12_verify import child, safe_root, sha, REPO

OLD_PROGRAM = "7d611485966a174d94ed970c35fd733def93d2d6a910da8a6cfe613619fac63a"


def differences(a, b, path=""):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        return [p for key in sorted(a.keys() | b.keys()) for p in (
            [path + "/" + key] if key not in a or key not in b else differences(a[key], b[key], path + "/" + key))]
    if isinstance(a, list):
        if len(a) != len(b):
            return [path]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differences(x, y, path + "/" + str(i))]
    return [] if a == b else [path]


def compare_outputs(old, new, old_public, new_public, old_sha, new_sha, program):
    candidate, public = deepcopy(new), deepcopy(new_public)
    attributed = []
    if old["program_sha256"] != OLD_PROGRAM or new["program_sha256"] != program:
        raise ValueError("predeclared old/current program identity required")
    candidate["program_sha256"] = old["program_sha256"]
    attributed.append({"path": "/program_sha256", "owner": "merged pin candidate bytes"})
    supplied = candidate["inputs"].pop("external_supplied")
    if supplied != {"loop_attempts": True, "loop_state": True, "block5": False}:
        raise ValueError("unexpected RL-115 external-supplied record")
    attributed.append({"path": "/inputs/external_supplied", "owner": "RL-115"})
    gate = candidate["block"]["option_c"]
    only = gate.pop("first_program_only")
    if not isinstance(only, list) or any(set(row) != {"class", "session", "key"} for row in only):
        raise ValueError("RL-113 names-only list required")
    if only != sorted(only, key=lambda row: (row["class"], row["session"], row["key"])):
        raise ValueError("RL-113 name ordering changed")
    if len(only) != len({(r["class"], r["session"], r["key"]) for r in only}):
        raise ValueError("duplicate RL-113 name")
    attributed.append({"path": "/block/option_c/first_program_only", "owner": "RL-113", "count": len(only)})
    counts = {}
    for row in only:
        counts[row["class"]] = counts.get(row["class"], 0) + 1
    classes = gate["comparator"]["classes"]
    before = old["block"]["option_c"]["comparator"]["classes"]
    if not set(counts).issubset(classes):
        raise ValueError("missing RL-113 class count")
    for name, row in list(classes.items()):
        count = row.pop("first_program_only")
        if count != counts.get(name, 0):
            raise ValueError("RL-113 class count mismatch")
        attributed.append({"path": "/block/option_c/comparator/classes/" + name + "/first_program_only", "owner": "RL-113"})
        if name not in before:
            if count <= 0 or row != {"compared": 0, "passed": 0, "failed": 0, "unmatched": 0}:
                raise ValueError("new first-program-only class was judged or has unexpected fields")
            del classes[name]
            attributed.append({"path": "/block/option_c/comparator/classes/" + name, "owner": "RL-113 zero-compared class; no pass"})
    if old_public["restricted_sha256"] != old_sha or public["restricted_sha256"] != new_sha:
        raise ValueError("public restricted digest does not bind actual numbers bytes")
    public["restricted_sha256"] = old_public["restricted_sha256"]
    attributed.append({"path": "/public/restricted_sha256", "owner": "digest of attributed restricted-output changes"})
    unexpected = differences(old, candidate) + ["/public" + p for p in differences(old_public, public)]
    return {"pass": not unexpected, "attributed": attributed, "unattributed": unexpected,
            "expected_no_numeric_or_decision_change": True,
            "RL114": "not applicable to BETA", "RL121": "no published difference expected for this passing archive",
            "comparator_failure_names": "remain empty on this passing archive"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--old-stem", required=True)
    parser.add_argument("--new-stem", required=True)
    args = parser.parse_args()
    root = safe_root(args.root)
    files = [child(root, str(root / (stem + "-" + kind + ".json")))
             for stem in (args.old_stem, args.new_stem) for kind in ("numbers", "public")]
    a, ap, b, bp = [json.loads(path.read_bytes()) for path in files]
    result = compare_outputs(a, b, ap, bp, sha(files[0]), sha(files[2]), sha(REPO / "scripts/independent_recompute_b6.py"))
    result.update(source_sha256={p.name: sha(p) for p in files}, comparer_sha256=sha(__file__),
                  old_program_sha256=a["program_sha256"], program_sha256=b["program_sha256"])
    path = child(root, str(root / (args.new_stem + "-differences.json")))
    with path.open("x") as output:
        json.dump(result, output, indent=2, sort_keys=True)
        output.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
