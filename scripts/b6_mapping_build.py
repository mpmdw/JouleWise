#!/usr/bin/env python3
"""Block 6 `mapping.json` from names (pin request O-5, O-13, O-14; runbook step 4, build B-4).

    b6_mapping_build.py --names-dir D --loop-attempts A --verify-map W/scripts/b6_r12_verify.py --out M
                        --report REP [--relocation OLD=NEW ...]

D holds one file per session, `<id>.txt`, the custody kit's `inputs --list-names <id>/archive` output (one name
per line). The mapping is built from those names alone; no session file is opened. From A it reads only each
row's session id, packs, round, t0 and outcome status words.

Per session (copy path `<id>/archive`):
- `meter_streams`: the names under `sources/night-custody/hazards/meter/` matching `stream-*.jsonl*`, `.zst`
  removed, sorted (the selection of `archive_pin`, b6_r12_verify.py:73-74);
- `contention_journal`: `sources/night-custody/hazards/monitor/contention.jsonl`;
- `clock_journal`: the one name ending `/monitor/clock.jsonl`, if any (O-14); two is a refusal;
- `copied_records`: the eight families with the file names of b6_r12_verify.py:89-97, each name kept only if the
  session lists it; `derived/b6-flags.jsonl` stands in for `derived/flags.jsonl` when only it is listed (reported);
- `relocations`: only the `--relocation` pairs given (the kit adds the source path itself).

Refuses (exit 4, `refused: <code> session=<id>[ family=<f>]`, nothing written) on a session with no meter stream,
no contention journal, an empty family, or two clock journals. The report prints `clock_journal: k of n`, each
family's equality with the verify map (O-5), and the session index from A with the three statements §17-R7
leaves open. Exit 5 (both files written) when the t0 order or the pairing it implies contradicts §17-R7: that
comes to the research lead.
"""
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path

SCHEMA = "joulewise.b6_mapping_build.report.v1"
# scripts/b6_r12_verify.py at the S-14 line, the R3 table's input of the same name (pin request section 2c).
VERIFY_MAP_SHA256 = "947d1c3d43eccf6ab6f19fb5bed785c2443b69899faa7a5c8efd356f834295c2"
MONITOR = "sources/night-custody/hazards/monitor/"
NIGHT = "sources/night-custody/night/"
METER_DIR = "sources/night-custody/hazards/meter/"
CONTENTION = MONITOR + "contention.jsonl"
CLOCK_SUFFIX = "/monitor/clock.jsonl"
FLAGS, B6_FLAGS = "derived/flags.jsonl", "derived/b6-flags.jsonl"
# b6_r12_verify.py:89-97, copied.
VERIFY_MAP = {
    "monitor_cost": [MONITOR + "monitor.jsonl"],
    "arm_host": ["sources/night-custody/hazards/arm.json", NIGHT + "arm_collectors.json"],
    "battery_phase": [MONITOR + "battery.jsonl"],
    "subject_temperature": [MONITOR + "thermal.jsonl"],
    "reference_history": [FLAGS, "withheld/b6-neg8.json"],
    "attempt_history": ["sources/night-custody/collection/idle_wait.jsonl", NIGHT + "chain-stages.jsonl"],
    "g10_history": [NIGHT + "hazard_result.json"],
    "block5_codes_carried": [FLAGS],
}
FAMILIES = tuple(VERIFY_MAP)
# §17-R7 (PR #748 at 27b6cacfd).
NINE = ("r1-alpha", "r3-alpha", "r4-alpha", "r1-beta", "r2-beta", "r3-beta", "r1-gamma", "r2-gamma", "r3-gamma")
PAIRING = {"r1-gamma": {"ALPHA": "r1-alpha", "BETA": "r1-beta"},
           "r2-gamma": {"ALPHA": "r3-alpha", "BETA": "r2-beta"},
           "r3-gamma": {"ALPHA": "r3-alpha", "BETA": "r3-beta"}}
STATED_BEFORE = (("r1-alpha", "r1-beta"), ("r1-beta", "r1-gamma"), ("r2-beta", "r3-alpha"), ("r2-gamma", "r3-alpha"),
                 ("r3-gamma", "r3-alpha"), ("r3-alpha", "r3-beta"), ("r3-beta", "r4-alpha"))
OPEN_THREE = ("r2-beta", "r2-gamma", "r3-gamma")


class Refusal(Exception):
    def __init__(self, code, session=None, family=None):
        super().__init__(code)
        self.code, self.session, self.family = code, session, family

    def line(self):
        return ("refused: " + self.code + (" session=" + self.session if self.session else "")
                + (" family=" + self.family if self.family else ""))


def read_names(path):
    return {line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()}


def meter_streams(names):
    """b6_r12_verify.py:73-74: `glob("stream-*.jsonl*")` in the meter directory, `.zst` removed."""
    found = set()
    for name in names:
        if name.startswith(METER_DIR) and "/" not in name[len(METER_DIR):] \
                and fnmatch.fnmatchcase(name[len(METER_DIR):], "stream-*.jsonl*"):
            found.add(name.removesuffix(".zst"))
    return sorted(found)


def session_mapping(sid, names, relocations):
    streams = meter_streams(names)
    if not streams:
        raise Refusal("meter_streams_empty", sid)
    if CONTENTION not in names:
        raise Refusal("contention_journal_missing", sid)
    clocks = sorted(n for n in names if n.endswith(CLOCK_SUFFIX))
    if len(clocks) > 1:
        raise Refusal("clock_journal_ambiguous", sid)
    records, notes = {}, {}
    for family, wanted in VERIFY_MAP.items():
        kept = []
        for name in wanted:
            if name in names:
                kept.append(name)
            elif name == FLAGS and B6_FLAGS in names:
                kept.append(B6_FLAGS)
                notes[family] = "derived/b6-flags.jsonl in place of derived/flags.jsonl"
        if not kept:
            raise Refusal("family_empty", sid, family)
        records[family] = kept
    mapping = {"meter_streams": streams, "contention_journal": CONTENTION, "copied_records": records}
    if clocks:
        mapping["clock_journal"] = clocks[0]
    if relocations:
        mapping["relocations"] = dict(relocations)
    return mapping, notes


def read_attempts(path):
    """Only session_id, packs, round, t0 and the outcome status words."""
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        outcomes = row.get("outcomes") if isinstance(row.get("outcomes"), dict) else {}
        packs = [p.upper() for p in (row.get("packs") or list(outcomes))]
        status = {p.upper(): o.get("status") for p, o in outcomes.items() if isinstance(o, dict)}
        rows.append({"session_id": row.get("session_id"), "packs": packs, "round": row.get("round"),
                     "t0": row.get("t0"), "counting": any(status.get(p) == "counting" for p in packs)})
    return rows


def session_index(rows):
    ordered = sorted(rows, key=lambda r: (r["t0"] if isinstance(r["t0"], (int, float)) else float("inf"),
                                          str(r["session_id"])))
    index = []
    for rank, row in enumerate(ordered, 1):
        index.append({"session_id": row["session_id"], "pack": row["packs"][0] if len(row["packs"]) == 1
                      else row["packs"], "round": row["round"], "t0_rank": rank, "counting": row["counting"]})
    return index


def implied_pairing(index):
    """§6.2 by counting alone, ties by earlier t0 (the rule `check_block` applies)."""
    counting = [r for r in index if r["counting"]]
    out = {}
    for g in (r for r in counting if r["pack"] == "GAMMA"):
        out[g["session_id"]] = {}
        for pack in ("ALPHA", "BETA"):
            cands = [r for r in counting if r["pack"] == pack]
            same = [r for r in cands if r["round"] == g["round"]]
            later = sorted((r for r in cands if r["round"] > g["round"]), key=lambda r: (r["round"], r["t0_rank"]))
            earlier = sorted((r for r in cands if r["round"] < g["round"]), key=lambda r: (-r["round"], r["t0_rank"]))
            chosen = (same or later or earlier or [None])[0]
            out[g["session_id"]][pack] = chosen["session_id"] if chosen else None
    return out


def order_report(index):
    rank = {r["session_id"]: r["t0_rank"] for r in index}
    counting = [r["session_id"] for r in index if r["counting"]]
    contradictions = [a + " before " + b for a, b in STATED_BEFORE if a in rank and b in rank and rank[a] > rank[b]]
    missing = sorted(set(NINE) - set(counting))
    extra = sorted(set(counting) - set(NINE))
    three = sorted((s for s in OPEN_THREE if s in rank), key=rank.get)
    statements = {
        "1_order_of_the_three": " then ".join(three) if len(three) == 3 else "not all three present",
        "2_relative_to_r1_gamma": ("all three after r1-gamma" if "r1-gamma" in rank and all(rank[s] > rank["r1-gamma"]
                                   for s in three) else ", ".join(s + (" after" if rank[s] > rank.get("r1-gamma", 0)
                                   else " before") + " r1-gamma" for s in three)),
        "3_t0_order_of_the_nine": " then ".join(s for s in sorted(rank, key=rank.get) if s in NINE),
    }
    pairing = implied_pairing(index)
    return {"nine_counting": not missing and not extra, "missing": missing, "extra": extra,
            "stated_order_holds": not contradictions, "contradictions": contradictions,
            "open_statements": statements, "implied_pairing": pairing, "pairing_equals_r7": pairing == PAIRING}


def write_new(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def build(args):
    verify_map = Path(args.verify_map)
    if hashlib.sha256(verify_map.read_bytes()).hexdigest() != VERIFY_MAP_SHA256:
        raise Refusal("verify_map_digest_mismatch")
    relocations = []
    for item in args.relocation or []:
        old, sep, new = item.partition("=")
        if not sep or not old or not new:
            raise Refusal("relocation_invalid")
        relocations.append((old, new))
    files = sorted(Path(args.names_dir).glob("*.txt"))
    if not files:
        raise Refusal("names_dir_empty")
    sessions, family_report, notes, clock = {}, {f: {"equal_to_verify_map": True, "differing": {}} for f in FAMILIES}, {}, 0
    for path in files:
        sid = path.stem
        mapping, session_notes = session_mapping(sid, read_names(path), relocations)
        sessions[sid + "/archive"] = mapping
        clock += "clock_journal" in mapping
        if session_notes:
            notes[sid] = session_notes
        for family, names in mapping["copied_records"].items():
            if names != VERIFY_MAP[family]:
                family_report[family]["equal_to_verify_map"] = False
                family_report[family]["differing"][sid] = {"names": names, "verify_map": VERIFY_MAP[family]}
    index = session_index(read_attempts(args.loop_attempts))
    order = order_report(index)
    names_vs_counting = {"names_sessions": sorted(p.stem for p in files),
                         "counting_sessions": sorted(r["session_id"] for r in index if r["counting"])}
    names_vs_counting["equal"] = names_vs_counting["names_sessions"] == names_vs_counting["counting_sessions"]
    report = {"schema": SCHEMA, "sessions": len(sessions), "clock_journal": {"with": clock, "of": len(sessions)},
              "clock_journal_line": "clock_journal: " + str(clock) + " of " + str(len(sessions)),
              "copied_records_equal": all(r["equal_to_verify_map"] for r in family_report.values()),
              "families": family_report, "flags_file_substitutions": notes,
              "meter_streams_per_session": {k.split("/")[0]: len(v["meter_streams"]) for k, v in sessions.items()},
              "session_index": index, "r7": order, "names_vs_counting_attempts": names_vs_counting,
              "verify_map_sha256": VERIFY_MAP_SHA256}
    mapping = {"sessions": sessions}
    write_new(args.out, (json.dumps(mapping, indent=1, sort_keys=True) + "\n").encode())
    write_new(args.report, (json.dumps(report, indent=1, sort_keys=True) + "\n").encode())
    print("mapping sessions=" + str(len(sessions)))
    print(report["clock_journal_line"])
    print("copied_records_equal: " + ("true" if report["copied_records_equal"] else
                                      "false " + ",".join(f for f, r in family_report.items() if not r["equal_to_verify_map"])))
    print("session_index: " + order["open_statements"]["3_t0_order_of_the_nine"])
    held = not (order["stated_order_holds"] and order["pairing_equals_r7"] and order["nine_counting"])
    if held:
        print("r7: departs (comes to the research lead)")
    return 5 if held else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--names-dir", required=True, help="one <id>.txt per session: the kit's --list-names output")
    parser.add_argument("--loop-attempts", required=True, help="the copy's attempts.jsonl")
    parser.add_argument("--verify-map", required=True, help="scripts/b6_r12_verify.py at the run checkout")
    parser.add_argument("--out", required=True, help="new mapping.json")
    parser.add_argument("--report", required=True, help="new report JSON")
    parser.add_argument("--relocation", action="append", metavar="OLD=NEW", help="a relocation pair (repeatable)")
    args = parser.parse_args(argv)
    for path in (args.out, args.report):
        if os.path.lexists(path):
            print("refused: out_exists")
            return 4
    try:
        return build(args)
    except Refusal as exc:
        print(exc.line())
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
