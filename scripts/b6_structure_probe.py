#!/usr/bin/env python3
"""Block 6 structure probe and the scripted term 7 check (RL-134 items 4, 8, 14; runbook build B-3).

    b6_structure_probe.py --restricted R --public P --r3-table T [--inputs DOC] [--loop-attempts A]
                          [--block5-expected B5PROBE] [--stage gate|dry] [--term7] --out O

Before the release this is the one program besides the pinned program that opens the restricted output. It reads
a whitelist of paths only (identity, `inputs`, `block.option_c`'s pass, families, failure names, first-program-only
names and public comparator class records, flag codes, per-session pack, round, counting, NEG-8 definedness,
contrast kept-quad counts, copied-disclosure path names, desk-hazard counts, and the count of between-session rows
with `block5_included`). It never reads `quantities`, `comparison_table`, a flag's `detail`, a copied `record` or
any float.

It checks the predeclared structure values of runbook step 7 (a run with `closed` false: the one-session gate) or
step 9 (`closed` true: the dry run), reports the per-session quantity accounting, and with `--term7` runs the
RL-113 term 7 checklist steps 1 to 8, 10, 12 and 13 as RL-125, RL-133 and RL-134 item 8 left it.

Its output passes a local copy of the pinned program's `require_structure_only` (no float, no decimal or exponent
token, no outcome word). Key and failure names go under `names`, checked to hold no `=` and no whitespace; SHA-256
values go under `digests`, checked to be 64 hex digits. If the guard fails, nothing is written.

stdout: `probe: ok` or `probe: departs <check,...>`, and with --term7 `term7: pass` or `term7: stop <class,...>`.
Exit 0 when everything holds; 5 on a departure or a term 7 stop; 6 when the guard refuses; 2 on usage.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = "joulewise.b6_structure_probe.v1"
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "configs/b6/recompute/production_comparison_keys.json"
REGISTRY_SHA256 = "62dbfaef9ebc5cfbbe5a00734f5eb8ad3d82389f54f28473ed63db6135b9174d"
EXPECT_PROGRAM_SHA256 = "90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759"
EXPECT_B5_PROGRAM_SHA256 = "d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0"

# §17-R7 (PR #748 at 27b6cacfd): the nine counting sessions and the pairing fixed by counting alone.
NINE = ("r1-alpha", "r3-alpha", "r4-alpha", "r1-beta", "r2-beta", "r3-beta", "r1-gamma", "r2-gamma", "r3-gamma")
PAIRING = {"r1-gamma": {"ALPHA": "r1-alpha", "BETA": "r1-beta"},
           "r2-gamma": {"ALPHA": "r3-alpha", "BETA": "r2-beta"},
           "r3-gamma": {"ALPHA": "r3-alpha", "BETA": "r3-beta"}}
GATE_SESSION = ("r1-alpha", "ALPHA", 1)
COUNTING_BY_PACK = {"ALPHA": 3, "BETA": 3, "GAMMA": 3}
SCIENCE_RUNS = 840  # §17-R10's registered replay: P* desk removals 0 of 840 science runs over the nine
FAMILIES = ("monitor_cost", "arm_host", "battery_phase", "subject_temperature", "reference_history",
            "attempt_history", "g10_history", "block5_codes_carried")
STEP13_FILES = ("derived/b6-flags.jsonl", "withheld/spans.json", "derived/bracket-binding.json")
PAIRING_FLAGS = ("pairing_floor_unavailable", "pairing_floor_from_block5", "pairing_provisional")
BLOCK_CLASSES = ("summary", "inclusive", "side_by_side", "replication")
COUNT_FIELDS = ("compared", "passed", "failed", "unmatched", "both_null", "first_program_only")

# The pinned program's guard (RC-B6-1 `OUTCOME_WORDS`, `NUMBER_TOKEN`, `require_structure_only`), copied.
OUTCOME_WORDS = frozenset({"direction_supported", "unresolved", "not_resolvable", "not_estimable",
                           "replicated", "not replicated", "not_replicated", "positive", "negative",
                           "agree", "L1", "L2"})
NUMBER_TOKEN = re.compile(r"\d+\.\d|\d[eE][+-]?\d")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# Quantity accounting (runbook B-3; Fable's derivation from RL-110, RL-114 and RL-133). Checked by the builder
# against the program's undefined-screen and below-minimum fixtures before use (see the run report).
FPO_BASE = {"ALPHA": 118, "BETA": 118, "GAMMA": 79}


class GuardRefusal(Exception):
    pass


class Usage(Exception):
    pass


# ---------------------------------------------------------------- small helpers

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def as_int(value):
    return value if is_int(value) else None


def as_bool(value):
    return value if isinstance(value, bool) else None


def as_str(value):
    return value if isinstance(value, str) else None


def contrast_phase(cid):
    return "decode" if "decode" in cid else "prefill-p2048"


def quantity_class(key):
    """RC-B6-1 `quantity_class`, copied."""
    head = key.split("/", 1)[0]
    if head == "reported":
        field = key.rsplit("/", 1)[-1]
        return {"per_token_j": "per_token", "attribution_floor_j": "attribution_floor"}.get(field, "reported")
    if head == "contrast":
        field = key.rsplit("/", 1)[-1]
        if field in ("outcome", "direction", "ceiling"):
            return "contrast_word"
        if field.startswith("energy_ratio") or field == "per_token_j":
            return "descriptive"
    return head


# ---------------------------------------------------------------- the guard

def guard(value, path="out"):
    """require_structure_only, with two exempt subtrees: `names` (no `=`, no whitespace, no float, no outcome
    word) and `digests` (64 hex digits or null)."""
    if isinstance(value, float):
        raise GuardRefusal("float at " + path)
    if isinstance(value, str):
        if value in OUTCOME_WORDS or NUMBER_TOKEN.search(value):
            raise GuardRefusal("restricted token at " + path)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            guard(key, path + "/<key>")
            if key == "names":
                guard_names(item, path + "/names")
            elif key == "digests":
                guard_digests(item, path + "/digests")
            else:
                guard(item, path + "/" + str(key))
        return
    if isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            guard(item, path + "/" + str(i))
        return
    if not (value is None or isinstance(value, (bool, int))):
        raise GuardRefusal("unexpected type at " + path)


def guard_names(value, path):
    if isinstance(value, dict):
        for key, item in value.items():
            guard_names(key, path + "/<key>")
            guard_names(item, path + "/" + str(key))
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            guard_names(item, path + "/" + str(i))
    elif isinstance(value, str):
        if "=" in value or re.search(r"\s", value) or value in OUTCOME_WORDS:
            raise GuardRefusal("name not structure-only at " + path)
    elif not (value is None or isinstance(value, bool) or is_int(value)):
        raise GuardRefusal("non-name at " + path)


def guard_digests(value, path):
    if isinstance(value, dict):
        for key, item in value.items():
            guard(key, path + "/<key>")
            guard_digests(item, path + "/" + str(key))
    elif not (value is None or (isinstance(value, str) and HEX64.match(value))):
        raise GuardRefusal("not a digest at " + path)


# ---------------------------------------------------------------- the R3 table

def parse_r3(text):
    """Rows of the §17-R3 table (generator stdout): number, scope, key pattern, packs, stats, label, copied paths."""
    rows = []
    for line in text.splitlines():
        if not re.match(r"^\| \d+ \| ", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) < 10:
            continue
        number, scope, group, packs, stats, _, producer, _, label = cells[:9]
        group = group.strip("`")
        row = {"row": int(number), "scope": scope, "group": group, "packs": packs.split(","),
               "stats": [] if stats in ("—", "-", "") else stats.split(","), "label": label,
               "kind": label_kind(label), "copied_paths": re.findall(r"`([^`]+)`", producer)
               if scope == "session (copied)" else []}
        regex = re.escape(group)
        for placeholder in ("<model>", "<phase>", "<mode>"):
            regex = regex.replace(re.escape(placeholder), "[^/]+")
        if row["stats"]:
            regex += "/(" + "|".join(re.escape(s) for s in row["stats"]) + ")"
        row["regex"] = re.compile("^" + regex + "$")
        rows.append(row)
    return rows


def label_kind(label):
    text = label.strip().strip('"').strip("`")
    if "UNSTATED" in label:
        return "unstated"
    if "single-source" in label:
        return "single_source"
    if text.startswith("single implementation; not independently recomputed"):
        return "r8_single_implementation"
    if text == "not independently recomputed":
        return "not_independently_recomputed"
    if "copied from the harvest or acceptance record" in label:
        return "copied"
    if label.startswith("§10-§11 arithmetic computed and compared"):
        return "block_scope"
    if "in the option (c) gate" in label and label.rstrip().endswith("not an S-13 table row"):
        return "gate"
    if label == "computed and compared (decision 6 (a))":
        return "plain_compared"
    if label.startswith("computed and compared (decision 6 (a)) when"):
        if "five or more quads" in label:
            return "conditional_p"
        if "twin returns an estimate" in label:
            return "conditional_contrast"
        return "conditional_neg8"
    return "unknown"


def lookup(rows, key, pack):
    matches = [r for r in rows if r["scope"] != "session (copied)" and r["regex"].match(key)]
    if len(matches) > 1 and pack:
        matches = [r for r in matches if pack in r["packs"] or "all" in r["packs"]]
    return matches[0] if len(matches) == 1 else None


# ---------------------------------------------------------------- extraction (the whitelist)

def extract(restricted):
    r = restricted
    inputs = r.get("inputs") if isinstance(r.get("inputs"), dict) else {}
    census = {}
    for sid, row in (inputs.get("census") or {}).items():
        census[sid] = {k: v for k, v in sorted(row.items()) if is_int(v)} if isinstance(row, dict) else {}
    supplied = inputs.get("external_supplied")
    block = r.get("block") if isinstance(r.get("block"), dict) else {}
    oc = block.get("option_c") if isinstance(block.get("option_c"), dict) else {}
    comparator = oc.get("comparator") if isinstance(oc.get("comparator"), dict) else {}
    classes = {}
    for cls, row in (comparator.get("classes") or {}).items():
        record = {k: as_int(row.get(k)) for k in COUNT_FIELDS if k in row}
        if "pass" in row:
            record["pass"] = as_bool(row["pass"])
        record["extra_fields"] = sorted(k for k in row if k not in COUNT_FIELDS and k != "pass")
        classes[cls] = record
    fpo = []
    for row in oc.get("first_program_only") or []:
        fpo.append([as_str(row.get("class")), as_str(row.get("session")), as_str(row.get("key"))])
    flags = [{"code": as_str(f.get("code")), "session": as_str(f.get("session")), "pack": as_str(f.get("pack")),
              "scope": f.get("scope") if isinstance(f.get("scope"), str) else "non_string",
              "stops_comparison": as_bool(f.get("stops_comparison"))} for f in r.get("flags") or []]
    sessions = {}
    for sid, s in (r.get("sessions") or {}).items():
        neg8 = s.get("neg8") if isinstance(s.get("neg8"), dict) else {}
        contrasts = {cid: as_int(c.get("n")) for cid, c in (s.get("contrasts") or {}).items() if isinstance(c, dict)}
        copied = None
        if isinstance(s.get("copied_disclosures"), dict):
            copied = {f: [as_str(x.get("path")) for x in rows if isinstance(x, dict)]
                      for f, rows in (s["copied_disclosures"].get("families") or {}).items()}
        hazards = s.get("desk_hazards")
        hazard_counts = None
        if isinstance(hazards, dict):
            hazard_counts = {"records": len(hazards.get("records") or {}),
                             "power_removed": len(hazards.get("power_removed") or []),
                             "processor_alternative_removed": len(hazards.get("processor_alternative_removed") or [])}
        sessions[sid] = {"pack": as_str(s.get("pack")), "round": as_int(s.get("round")),
                         "counting": as_bool(s.get("counting")), "neg8_defined": neg8.get("verdict") != "undefined",
                         "contrast_n": contrasts, "copied_disclosures": copied, "desk_hazards": hazard_counts}
    included = {}
    for pack, row in (block.get("between_session") or {}).items():
        values = row.get("values") if isinstance(row, dict) else None
        included[pack] = sum(1 for v in (values or {}).values() if isinstance(v, dict) and v.get("block5_included") is True)
    failures = list(oc.get("failures") or [])  # names; a non-string here fails the guard
    return {
        "identity": {"schema": as_str(r.get("schema")), "mode": as_str(r.get("mode")),
                     "comparison_stopped": as_bool(r.get("comparison_stopped")), "closed": as_bool(r.get("closed")),
                     "block5_input": as_bool(r.get("block5_input")),
                     "inputs": {"host": as_str(inputs.get("host")), "l9_audit": as_str(inputs.get("l9_audit")),
                                "external_supplied": {k: as_bool(v) for k, v in supplied.items()}
                                if isinstance(supplied, dict) else None,
                                "census": census}},
        "digests": {"program_sha256": as_str(r.get("program_sha256")),
                    "b5_program_sha256": as_str(r.get("b5_program_sha256")),
                    "run_inputs_sha256": as_str(inputs.get("run_inputs_sha256"))},
        "option_c": {"pass": as_bool(oc.get("pass")), "families": {k: as_int(v) for k, v in (oc.get("families") or {}).items()},
                     "failure_count": len(failures), "first_program_only_count": len(fpo),
                     "comparator": {"pass": as_bool(comparator.get("pass")),
                                    "recompute_stopped": as_bool(comparator.get("recompute_stopped")),
                                    "classes": classes}},
        "names": {"failures": failures, "first_program_only": fpo},
        "flags": flags,
        "sessions": sessions,
        "block5_included": included,
    }


def extract_public(public):
    sessions = {}
    for sid, s in (public.get("sessions") or {}).items():
        pairing = {p: {"session_id": as_str(row.get("session_id")), "rule": as_str(row.get("rule")),
                       "provisional": as_bool(row.get("provisional"))} for p, row in (s.get("pairing") or {}).items()}
        sessions[sid] = {"pack": as_str(s.get("pack")), "round": as_int(s.get("round")),
                         "counting": as_bool(s.get("counting")), "pairing": pairing,
                         "flag_counts": {k: as_int(v) for k, v in (s.get("flag_counts") or {}).items()}}
    return {"comparison_stopped": as_bool(public.get("comparison_stopped")),
            "counting_by_pack": {k: as_int(v) for k, v in (public.get("counting_by_pack") or {}).items()},
            "sessions": sessions, "restricted_sha256": as_str(public.get("restricted_sha256"))}


def pin_session_id(key):
    path = Path(key)
    return path.parent.name if path.name == "archive" else path.name


def extract_inputs(path):
    """Names only: the pinned session keys and, per session, whether its pin lists the step 13 files."""
    document = json.loads(Path(path).read_bytes())
    pins = {}
    for key, pin in (document.get("sessions") or {}).items():
        files = pin.get("files") if isinstance(pin.get("files"), dict) else {}
        pins[pin_session_id(key)] = {name: name in files for name in STEP13_FILES}
    return pins


def extract_attempts(path):
    """From each row: session_id, round, packs and the outcome status words only."""
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        outcomes = row.get("outcomes") if isinstance(row.get("outcomes"), dict) else {}
        counting = sorted(p.upper() for p, o in outcomes.items() if isinstance(o, dict) and o.get("status") == "counting")
        rows.append({"session_id": as_str(row.get("session_id")), "round": as_int(row.get("round")),
                     "counting_packs": counting})
    return rows


def load_registry(path):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != REGISTRY_SHA256:
        raise Usage("registry_digest_mismatch")
    return json.loads(data)["session_quantity_keys"]


# ---------------------------------------------------------------- checks

class Checks:
    def __init__(self):
        self.rows = {}

    def add(self, name, ok, **detail):
        self.rows[name] = {"result": "ok" if ok else "departs", **detail}

    def skip(self, name, reason):
        self.rows[name] = {"result": "not_checked", "reason": reason}

    def departs(self):
        return [k for k, v in self.rows.items() if v["result"] == "departs"]


def identity_checks(c, x, digests, closed, inputs_sha256):
    ident = x["identity"]
    c.add("program_sha256", digests["program_sha256"] == EXPECT_PROGRAM_SHA256)
    c.add("b5_program_sha256", digests["b5_program_sha256"] == EXPECT_B5_PROGRAM_SHA256)
    c.add("inputs_host", ident["inputs"]["host"] == "Air", observed=ident["inputs"]["host"])
    c.add("l9_audit", ident["inputs"]["l9_audit"] == "not_run", observed=ident["inputs"]["l9_audit"])
    if inputs_sha256 is None:
        c.skip("run_inputs_sha256", "no --inputs given")
    else:
        c.add("run_inputs_sha256", digests["run_inputs_sha256"] == inputs_sha256)
    expected = {"loop_attempts": True, "loop_state": True, "block5": bool(closed)}
    c.add("external_supplied", ident["inputs"]["external_supplied"] == expected,
          observed=ident["inputs"]["external_supplied"], expected=expected)
    c.add("closed", ident["closed"] is bool(closed), observed=ident["closed"])
    c.add("comparison_stopped", ident["comparison_stopped"] is False, observed=ident["comparison_stopped"])
    if closed:
        c.add("block5_input", ident["block5_input"] is True, observed=ident["block5_input"])


def gate_checks(c, x, closed):
    oc = x["option_c"]
    fpo = x["names"]["first_program_only"]
    c.add("option_c_pass", oc["pass"] is True, observed=oc["pass"])
    c.add("failures_empty", oc["failure_count"] == 0, count=oc["failure_count"])
    classes = oc["comparator"]["classes"]
    bad = sorted(cls for cls, r in classes.items() if "pass" in r and (r.get("failed") != 0 or r.get("unmatched") != 0))
    c.add("compared_classes_clean", not bad, names_of_classes=bad)
    if closed:
        odd = sorted(cls for cls, r in classes.items() if not record_kind_ok(r))
        c.add("class_record_kinds", not odd, classes=odd)
        over = sorted(cls for cls, r in classes.items() if is_int(r.get("both_null")) and is_int(r.get("passed"))
                      and r["both_null"] > r["passed"])
        c.add("both_null_at_most_passed", not over, classes=over)
    c.add("run_phase_energy_first_program_only", sum(1 for row in fpo if row[0] == "run_phase_energy") == 0,
          count=sum(1 for row in fpo if row[0] == "run_phase_energy"))
    c.add("no_block_entry", not any(row[1] == "__block__" for row in fpo),
          count=sum(1 for row in fpo if row[1] == "__block__"))


def record_kind_ok(r):
    """Checklist step 3 (RL-133): with `pass` and compared > 0, or without `pass` and all counts 0."""
    if "pass" in r:
        return is_int(r.get("compared")) and r["compared"] > 0
    return all(r.get(k) == 0 for k in ("compared", "passed", "failed", "unmatched", "both_null"))


def gate_session_checks(c, pub):
    sessions = pub["sessions"]
    sid, pack, rnd = GATE_SESSION
    one = len(sessions) == 1 and sid in sessions
    s = sessions.get(sid, {})
    c.add("public_one_session", one, count=len(sessions))
    c.add("public_session_shape", one and s.get("pack") == pack and s.get("round") == rnd and s.get("counting") is True,
          observed={"pack": s.get("pack"), "round": s.get("round"), "counting": s.get("counting")})


def dry_session_checks(c, x, pub, pins, attempts):
    ids = set(x["sessions"])
    c.add("nine_sessions", ids == set(NINE), missing=sorted(set(NINE) - ids), extra=sorted(ids - set(NINE)))
    if pins is None:
        c.skip("sessions_equal_pins", "no --inputs given")
    else:
        c.add("sessions_equal_pins", ids == set(pins), missing=sorted(set(pins) - ids), extra=sorted(ids - set(pins)))
    if attempts is None:
        c.skip("counting_attempts_present", "no --loop-attempts given")
    else:
        missing = counting_missing(x, attempts)
        c.add("counting_attempts_present", not missing, missing=missing)
    c.add("counting_by_pack", pub["counting_by_pack"] == COUNTING_BY_PACK, observed=pub["counting_by_pack"])
    provisional = sorted(sid for sid, s in pub["sessions"].items()
                         for row in s["pairing"].values() if row["provisional"] is not False)
    c.add("pairing_not_provisional", not provisional, sessions=provisional)
    observed = {sid: {p: row["session_id"] for p, row in s["pairing"].items()}
                for sid, s in pub["sessions"].items() if s["pack"] == "GAMMA"}
    c.add("pairing_as_r7", observed == PAIRING, observed=observed)
    counts = {code: sum(s["flag_counts"].get(code) or 0 for s in pub["sessions"].values()) for code in PAIRING_FLAGS}
    c.add("pairing_flags_zero", not any(counts.values()), counts=counts)


def counting_missing(x, attempts):
    """Checklist step 12: every counting attempt row has that pack's session of that round in the output."""
    present = {(s["pack"], s["round"]) for s in x["sessions"].values()}
    missing = []
    for row in attempts:
        for pack in row["counting_packs"]:
            if (pack, row["round"]) not in present:
                missing.append(str(row["session_id"]) + ":" + pack)
    return sorted(missing)


def copied_reference(rows):
    return {r["group"]: r["copied_paths"] for r in rows if r["scope"] == "session (copied)"}


def inputs_checks(c, x, r3, pins):
    reference = copied_reference(r3)
    without = sorted(sid for sid, s in x["sessions"].items()
                     if s["copied_disclosures"] is None or set(s["copied_disclosures"]) != set(FAMILIES))
    c.add("copied_disclosures_eight_families", not without, sessions=without)
    differs = {}
    for sid, s in x["sessions"].items():
        for family, paths in (s["copied_disclosures"] or {}).items():
            if paths != reference.get(family):
                differs.setdefault(family, []).append(sid)
    # RL-125 item 2: a difference is reported, the run-input document governs; not a departure.
    c.rows["copied_paths_equal_r3"] = {"result": "reported", "equal": not differs,
                                       "differing_families": {f: sorted(v) for f, v in sorted(differs.items())}}
    if pins is not None:
        lacking = {sid: sorted(n for n, listed in row.items() if not listed) for sid, row in pins.items()
                   if not all(row.values())}
        c.rows["pins_list_step13_files"] = {"result": "reported", "sessions_lacking": lacking}


def hazard_checks(c, x):
    records = sum((s["desk_hazards"] or {}).get("records", 0) for s in x["sessions"].values())
    removed = sum((s["desk_hazards"] or {}).get("power_removed", 0) for s in x["sessions"].values())
    missing = sorted(sid for sid, s in x["sessions"].items() if s["desk_hazards"] is None)
    c.add("pstar_desk_removals", removed == 0 and records == SCIENCE_RUNS and not missing,
          removed=removed, science_runs=records, expected_science_runs=SCIENCE_RUNS, sessions_without_record=missing)


def block5_checks(c, x, expected):
    observed = sum(x["block5_included"].values())
    if expected is None:
        c.skip("block5_included", "no --block5-expected given")
        return
    c.add("block5_included", observed == expected["total"], observed=observed, expected=expected["total"],
          by_pack=x["block5_included"], expected_by_pack=expected["by_pack"])


# ---------------------------------------------------------------- accounting and term 7

def accounting(x, registry):
    """Per session: registry keys = compared + first_program_only, and Fable's formula for the latter."""
    fpo = x["names"]["first_program_only"]
    report, closes = {}, True
    for sid, s in sorted(x["sessions"].items()):
        pack = s["pack"]
        listed = sum(1 for row in fpo if row[1] == sid and row[0] != "run_phase_energy")
        keys = len(registry.get(pack, ()))
        extra = 0
        if not s["neg8_defined"]:
            extra += 3 + (10 if pack == "GAMMA" else 0)
        elif pack == "GAMMA":
            for n in s["contrast_n"].values():
                extra += 5 if (n is None or n < 2) else 2 if n <= 4 else 0
        expected = FPO_BASE.get(pack, 0) + extra if pack in FPO_BASE else None
        report[sid] = {"pack": pack, "registry_keys": keys, "first_program_only": listed,
                       "compared_derived": keys - listed, "formula_first_program_only": expected,
                       "formula_holds": expected == listed}
    # Over the run: session-class compared counts (comparator) plus listed rows equal the registry keys.
    classes = x["option_c"]["comparator"]["classes"]
    by_class = {}
    for s in x["sessions"].values():
        for key in registry.get(s["pack"], ()):
            cls = quantity_class(key)
            by_class[cls] = by_class.get(cls, 0) + 1
    mismatched = []
    for cls, n in sorted(by_class.items()):
        listed = sum(1 for row in fpo if row[0] == cls and row[1] != "__block__")
        compared = (classes.get(cls) or {}).get("compared") or 0
        if compared + listed != n:
            mismatched.append(cls)
            closes = False
    return {"sessions": report, "run_closes": closes, "classes_not_closing": mismatched,
            "formula_note": "first_program_only = 118 (ALPHA, BETA) or 79 (GAMMA); +3 if the screen is undefined, "
                            "and for GAMMA +10 more; otherwise for GAMMA +5 per contrast with n below 2 and +2 per "
                            "contrast with n from 2 to 4 (runbook B-3; reported, never a stop)"}


def term7(x, r3, registry, pins, attempts):
    """RL-113 term 7, steps 1-8, 10, 12 and 13, as RL-125, RL-133 and RL-134 item 8 left it."""
    fpo = x["names"]["first_program_only"]
    classes = x["option_c"]["comparator"]["classes"]
    stops, offending = set(), []

    def stop(cls, session=None, key=None, kind=None):
        stops.add(cls)
        offending.append([cls, session or "-", key or "-"] + ([kind] if kind else []))

    # Step 1: one run; the serial-against-pool comparison is skipped.
    # Step 2: per-class counts against the comparator; both_null against passed; the three totals.
    counts = {}
    for row in fpo:
        counts[row[0]] = counts.get(row[0], 0) + 1
    for cls in sorted(set(counts) | set(classes)):
        if counts.get(cls, 0) != (classes.get(cls) or {}).get("first_program_only", 0):
            stop("count_mismatch", key=cls)
    for cls, r in classes.items():
        if is_int(r.get("both_null")) and is_int(r.get("passed")) and r["both_null"] > r["passed"]:
            stop("both_null_exceeds_passed", key=cls)
    compared = sum(r.get("compared") or 0 for r in classes.values())
    both_null = sum(r.get("both_null") or 0 for r in classes.values())
    # Step 3: every class record is one of the two kinds.
    for cls, r in classes.items():
        if not record_kind_ok(r) or r.get("extra_fields"):
            stop("class_record_kind", key=cls)
    # Steps 4 to 6: labels.
    families = set(FAMILIES)
    kinds = {}
    for cls, sid, key in fpo:
        if cls == "run_phase_energy":
            stop("run_phase_energy", sid, key)
            continue
        if sid == "__block__":
            stop("block_scope", sid, key)
            continue
        if key in families:
            stop("copied_family", sid, key)
            continue
        session = x["sessions"].get(sid)
        pack = session["pack"] if session else None
        row = lookup(r3, key, pack)
        if row is None or row["kind"] in ("unstated", "unknown"):
            stop("no_r3_row", sid, key)
            continue
        kinds.setdefault(row["kind"], set()).add(key)
        kind = row["kind"]
        if kind in ("single_source", "not_independently_recomputed", "r8_single_implementation", "gate"):
            continue
        if kind == "plain_compared":
            stop("plain_compared_label", sid, key)
        elif kind == "block_scope":
            stop("block_scope", sid, key)
        elif kind == "copied":
            stop("copied_family", sid, key)
        elif kind.startswith("conditional_"):
            if not conditional_met(kind, key, session):
                stop("conditional_unmet", sid, key, kind)
    # Step 6, other direction, and step 7: whole-machine session keys never in a compared row; compared and
    # first-program-only rows are disjoint and together the registry, class by class.
    listed = {(sid, key) for _, sid, key in fpo}
    for sid, s in x["sessions"].items():
        for key in registry.get(s["pack"], ()):
            if key.startswith("lines/whole_machine/") and (sid, key) not in listed:
                stop("whole_machine_compared", sid, key)
    by_class = {}
    for s in x["sessions"].values():
        for key in registry.get(s["pack"], ()):
            by_class[quantity_class(key)] = by_class.get(quantity_class(key), 0) + 1
    for cls, n in sorted(by_class.items()):
        session_listed = sum(1 for row in fpo if row[0] == cls and row[1] != "__block__")
        if (classes.get(cls) or {}).get("compared", 0) + session_listed != n:
            stop("compared_overlaps_first_program_only", key=cls)
    # Step 10: host and copied disclosures.
    if x["identity"]["inputs"]["host"] != "Air":
        stop("host_not_air")
    for sid, s in x["sessions"].items():
        if s["copied_disclosures"] is None or set(s["copied_disclosures"]) != families:
            stop("copied_disclosures_missing", sid)
    # Step 12: sessions against the pins and the counting attempts.
    step12 = "not_run"
    if pins is not None:
        step12 = "run"
        for sid in sorted(set(pins) ^ set(x["sessions"])):
            stop("session_missing", sid)
    if attempts is not None:
        step12 = "run"
        for name in counting_missing(x, attempts):
            stop("session_missing", name)
    # Step 13 (reported): pins without flags, spans or bracket binding.
    step13 = None
    if pins is not None:
        step13 = {sid: sorted(n for n, listed_ in row.items() if not listed_) for sid, row in pins.items()
                  if not all(row.values())}
    return {
        "result": "pass" if not stops else "stop",
        "stop_classes": sorted(stops),
        "step1": "skipped: one run (no pool read to compare)",
        "per_class": {cls: {k: (classes.get(cls) or {}).get(k, 0) for k in ("compared", "both_null", "passed")}
                      | {"listed": counts.get(cls, 0)} for cls in sorted(set(counts) | set(classes))},
        "totals": {"compared": compared, "both_null": both_null, "agreeing_on_a_value": compared - both_null,
                   "first_program_only": len(fpo)},
        "distinct_keys_by_label_kind": {k: len(v) for k, v in sorted(kinds.items())},
        "step12": step12, "step13_sessions_lacking": step13,
        "names": {"offending": offending},
    }


def conditional_met(kind, key, session):
    """RL-134 item 8: the second clause from the first program's own structure (NEG-8 definedness and n)."""
    if session is None:
        return False
    if not session["neg8_defined"]:
        return True
    if kind == "conditional_neg8":
        return False
    phase = key.split("/")[1] if key.count("/") >= 2 else None
    ns = [n for cid, n in session["contrast_n"].items() if contrast_phase(cid) == phase]
    if len(ns) != 1 or ns[0] is None:
        return False
    n = ns[0]
    if kind == "conditional_contrast":
        return n < 2
    return n < 5  # conditional_p: no estimate (n < 2) or a short contrast (2 to 4)


# ---------------------------------------------------------------- main

def probe(args):
    restricted_path, public_path = Path(args.restricted), Path(args.public)
    restricted = json.loads(restricted_path.read_bytes())
    public = json.loads(public_path.read_bytes())
    r3_text = Path(args.r3_table).read_text(encoding="utf-8")
    r3 = parse_r3(r3_text)
    registry = load_registry(args.registry)
    x = extract(restricted)
    del restricted
    pub = extract_public(public)
    pins = extract_inputs(args.inputs) if args.inputs else None
    attempts = extract_attempts(args.loop_attempts) if args.loop_attempts else None
    block5_expected = None
    if args.block5_expected:
        doc = json.loads(Path(args.block5_expected).read_bytes())
        block5_expected = {"total": doc["total"], "by_pack": doc["by_pack"]}
    closed = args.stage == "dry" if args.stage else x["identity"]["closed"] is True
    inputs_sha = sha256_file(args.inputs) if args.inputs else None
    c = Checks()
    identity_checks(c, x, x["digests"], closed, inputs_sha)
    gate_checks(c, x, closed)
    if closed:
        dry_session_checks(c, x, pub, pins, attempts)
        inputs_checks(c, x, r3, pins)
        block5_checks(c, x, block5_expected)
        hazard_checks(c, x)
    else:
        gate_session_checks(c, pub)
    restricted_sha = sha256_file(restricted_path)
    c.add("public_binds_restricted", pub["restricted_sha256"] == restricted_sha)
    out = {"schema": SCHEMA, "stage": "dry_run" if closed else "gate_run",
           "identity": x["identity"], "option_c": x["option_c"], "flags": x["flags"],
           "sessions": x["sessions"], "block5_included": x["block5_included"],
           "public": {k: v for k, v in pub.items() if k != "restricted_sha256"},
           "checks": c.rows, "accounting": accounting(x, registry),
           "names": x["names"],
           "digests": {**x["digests"], "restricted_file": restricted_sha, "public_file": sha256_file(public_path),
                       "public_restricted_sha256": pub["restricted_sha256"], "r3_table": sha256_file(args.r3_table),
                       "inputs_file": inputs_sha}}
    if args.term7:
        t7 = term7(x, r3, registry, pins, attempts)
        out["term7"] = {k: v for k, v in t7.items() if k != "names"}
        out["names"] = {**out["names"], "term7_offending": t7["names"]["offending"]}
    guard(out)
    data = (json.dumps(out, indent=1, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    departs = c.departs()
    print("probe: ok" if not departs else "probe: departs " + ",".join(departs))
    status = 0 if not departs else 5
    if args.term7:
        t7 = out["term7"]
        print("term7: pass" if t7["result"] == "pass" else "term7: stop " + ",".join(t7["stop_classes"]))
        if t7["result"] != "pass":
            status = 5
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--restricted", required=True, help="the pinned program's restricted output")
    parser.add_argument("--public", required=True, help="the pinned program's public output")
    parser.add_argument("--r3-table", required=True, help="the §17-R3 table, generator stdout at the S-14 commit")
    parser.add_argument("--inputs", help="the run-input document (pinned session names and step 13 file names)")
    parser.add_argument("--loop-attempts", help="the loop's attempts.jsonl (session id, round, status words)")
    parser.add_argument("--block5-expected", help="b6_release_record.py b5-probe output (the predeclared count)")
    parser.add_argument("--registry", default=str(REGISTRY), help="production_comparison_keys.json (digest-checked)")
    parser.add_argument("--stage", choices=("gate", "dry"),
                        help="which predeclared values apply (step 7 or step 9); default: dry if the output is closed")
    parser.add_argument("--term7", action="store_true", help="run the RL-113 term 7 checklist")
    parser.add_argument("--out", required=True, help="new structure file (refused if it exists)")
    args = parser.parse_args(argv)
    if os.path.lexists(args.out):
        print("probe: refused out_exists")
        return 2
    try:
        return probe(args)
    except GuardRefusal:
        print("probe: refused guard (output not written)")
        return 6
    except Usage as exc:
        print("probe: refused " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
