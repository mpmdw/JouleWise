#!/usr/bin/env python3
"""RL-89: derive the R1 runtime config's R0-classified keys from R0's record.

"R0 classified" (RL-89): a key to which R0's ``smc/r0.json`` ranking gives the
class ``die`` or ``heatsink`` with ``eligible`` true. A ``record-only`` row is
not a classification. The list keeps the record's ranking order.

Standard library only, so the magistrate can run ``check`` on the Mac with any
python3 and no repository imports. Every mode verifies the record's sha256
first and refuses on a mismatch.

    derive  --r0 R0.json                   print {"r0_classified_keys", "r0_classes"}
    check   --r0 R0.json --config CONFIG   exit 0 only if CONFIG's lists equal the derivation
    write   --r0 R0.json --config CONFIG   rewrite exactly those two lines of CONFIG
    project --r0 R0.json --output FIXTURE  write the (key, class, eligible) ranking projection
    check-fixture --fixture F --config C   re-derive from a projection (CI; no r0.json needed)
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

# R0 v4 night r0-v4-20261108T0550Z, smc/r0.json (RL-89; config sensors.r0_sha256).
R0_SHA256 = "e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b"
CLASSES = ("die", "heatsink")
PROJECTION_SCHEMA = "joulewise.align.r0_ranking_classes.v1"
LINE = {"r0_classified_keys": re.compile(r'^  "r0_classified_keys": .*,$', re.M),
        "r0_classes": re.compile(r'^  "r0_classes": .*,$', re.M)}


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def load_r0(path, expected=R0_SHA256):
    raw = Path(path).read_bytes()
    digest = sha256_bytes(raw)
    if digest != expected:
        raise SystemExit(f"REFUSED: {path} sha256 {digest} != expected {expected}")
    return json.loads(raw), digest


def project(r0):
    """The ranking rows' (key, class, eligible), in order: all derive() reads."""
    return [{"key": row["key"], "class": row["class"], "eligible": row["eligible"]}
            for row in r0["response"]["ranking"]]


def derive(rows):
    """``rows``: R0's ranking (or its projection). Returns (keys, classes)."""
    keys, classes = [], {}
    for row in rows:
        if row["class"] in CLASSES and row["eligible"] is True:
            if row["key"] in classes:
                raise ValueError(f"duplicate ranking key {row['key']}")
            keys.append(row["key"])
            classes[row["key"]] = row["class"]
    return keys, classes


def compare(config, keys, classes, digest):
    problems = []
    if config.get("sensors", {}).get("r0_sha256") != digest:
        problems.append(f"config sensors.r0_sha256 {config.get('sensors', {}).get('r0_sha256')} != {digest}")
    if config.get("r0_classified_keys") != keys:
        problems.append("r0_classified_keys differs from the derivation (membership or order)")
    if config.get("r0_classes") != classes:
        problems.append("r0_classes differs from the derivation")
    return problems


def rewrite(text, keys, classes):
    for name, value in (("r0_classified_keys", keys), ("r0_classes", classes)):
        line = f'  "{name}": {json.dumps(value)},'
        text, count = LINE[name].subn(lambda _m, line=line: line, text)
        if count != 1:
            raise SystemExit(f"REFUSED: expected exactly one {name} line, found {count}")
    return text


def _report(ok, **fields):
    print(json.dumps({"ok": ok, **fields}, indent=2, sort_keys=True))
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("derive", "check", "write", "project", "check-fixture"))
    parser.add_argument("--r0", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--expected-sha256", default=R0_SHA256)
    args = parser.parse_args(argv)
    if args.mode == "check-fixture":
        fixture = json.loads(args.fixture.read_text())
        if fixture.get("schema") != PROJECTION_SCHEMA or fixture.get("source_sha256") != args.expected_sha256:
            raise SystemExit("REFUSED: fixture is not the projection of the expected R0 record")
        keys, classes = derive(fixture["ranking"])
        problems = compare(json.loads(args.config.read_bytes()), keys, classes, fixture["source_sha256"])
        return _report(not problems, problems=problems, n_keys=len(keys), source_sha256=fixture["source_sha256"])
    if args.r0 is None:
        parser.error("--r0 is required")
    r0, digest = load_r0(args.r0, args.expected_sha256)
    rows = project(r0)
    keys, classes = derive(rows)
    counts = {c: sum(1 for k in keys if classes[k] == c) for c in CLASSES}
    if args.mode == "derive":
        print(json.dumps({"r0_sha256": digest, "ranking_rows": len(rows), "counts": counts,
                          "r0_classified_keys": keys, "r0_classes": classes}, indent=2))
        return 0
    if args.mode == "project":
        value = {"schema": PROJECTION_SCHEMA, "source_sha256": digest,
                 "source": "night-align/r0-v4-20261108T0550Z/smc/r0.json response.ranking",
                 "ranking": rows}
        with args.output.open("x") as handle:
            handle.write(json.dumps(value, indent=1) + "\n")
        return 0
    if args.config is None:
        parser.error("--config is required")
    if args.mode == "write":
        text = args.config.read_text()
        new = rewrite(text, keys, classes)
        before, after = json.loads(text), json.loads(new)
        if {k: v for k, v in before.items() if k not in LINE} != {k: v for k, v in after.items() if k not in LINE}:
            raise SystemExit("REFUSED: rewrite touched other fields")
        args.config.write_text(new)
    problems = compare(json.loads(args.config.read_bytes()), keys, classes, digest)
    return _report(not problems, problems=problems, r0_sha256=digest, ranking_rows=len(rows),
                   counts=counts, n_keys=len(keys),
                   config_sha256=sha256_bytes(args.config.read_bytes()))


if __name__ == "__main__":
    sys.exit(main())
