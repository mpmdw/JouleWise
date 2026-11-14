#!/usr/bin/env python3
"""RL-142 §2 item 5: names-only comparison of two Block 6 launcher run directories.

    compare_rl142.py --mode a|b --old DIR --new DIR --out result.json [--inputs-rerun]

(a) gate r2 against gate attempt 2: no difference except the program hash.
(b) dry run r2 against the held dry run: differences only in the program hash, the fields of item 1 for the four
    whole-machine keys, their block quantities and comparator tallies, `failures`, `option_c.pass`,
    `comparison_stopped` and the `option_c_disagrees` flags.

The predeclaration this implements is /Volumes/JW-EXT/scratch/rl142-expected-diff.md (rule ids R-*, judgments J*).

It prints and writes ONLY file names, key paths, difference kinds (added, removed, type, value, plus binding checks),
rule ids, counts and verdict codes. It never prints, logs or writes a value read from the files it compares. A
restricted flag code (used to group the keyed `flags` lists) is replaced by an ordinal; only public flag codes and
`option_c_disagrees` are shown by name. Files are hashed (SHA-256, in result.json only) but process-record files
(B) are never parsed.

Exit 0: no UNOWNED path. Exit 3 (HOLD): at least one UNOWNED path. Exit 2: usage, unreadable directory,
JSON parse error, or the out file already exists. Stdlib only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = "rl142.compare.v1"
OLD_PROGRAM = "90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759"  # b6/analysis, RC-B6-1
NEW_PROGRAM = "4a9f594471652581737b6cd02bd2922592f2e7cf9d575a164adb10162a5211ea"  # b6/analysis-r2, RL-142
PROGRAM_ROW = "scripts~1independent_recompute_b6.py"  # escaped closure-table key

A_FILES = ("restricted.json", "public.json", "structure.json")   # analysis outputs, key-path compared
C_FILES = ("record.json", "child-argv.json", "stdout")           # mixed records, compared with per-field rules
B_FILES = ("process.json", "samples.jsonl", "stderr", "time")    # process/wrapper records, hashed only
TEN = A_FILES + C_FILES + B_FILES

# Flag codes the pinned program publishes by name (RC-B6-1 PUBLIC_FLAG_CODES, copied) and the one RL-142 owns.
PUBLIC_FLAG_CODES = frozenset("""archive_file_missing trace_plist_missing trace_plist_unreadable phase_events_ambiguous
unit_shape_invalid kept_unit_identity_mismatch cell_below_minimum b_op_from_record calibration_capture_name_fallback
member_pre_bound_missing member_pre_bound_mismatch acceptance_record_missing acceptance_schema_unknown
acceptance_session_mismatch acceptance_pack_unknown loop_attempt_missing counting_disagrees
acceptance_kept_count_mismatch neg8_corpus_count_mismatch neg8_midpoint_lost neg8_reference_lost neg8_spare_present
excluded_run_not_in_roster pairing_floor_from_block5 pairing_floor_unavailable pairing_provisional
session_id_duplicate neg8_survivor_count_mismatch kept_member_token_mismatch loo_kept_n_equals_minimum""".split())
OCD = "option_c_disagrees"
SHOWN_CODES = PUBLIC_FLAG_CODES | {OCD}

STDOUT_LINE = re.compile(rb"^recompute sessions=(\d+) flags=(\d+) comparison_stopped=(true|false) "
                         rb"restricted_sha256=([0-9a-f]{64})\n?$")
STDOUT_TOKENS = ("sessions", "flags", "comparison_stopped", "restricted_sha256")

# ---------------------------------------------------------------- rules
# The four keys of RL-142 §2 item 1 (escaped as JSON-pointer tokens, "/" -> "~1"), each tied to its own pack.
TAG = {"ALPHA": "qwen3-1p7b", "BETA": "qwen3-8b"}


def k4(pack):
    return "lines~1whole_machine~1" + re.escape(TAG[pack]) + "~1(decode|prefill-p2048)~1mean_j"


def per_pack(template):
    return "(" + "|".join(template.format(P=p, K=k4(p)) for p in ("ALPHA", "BETA")) + ")"


# (rule id, file, regex over the escaped path, modes). The first match wins.
RULES = [
    # --- program hash (both modes) ---
    ("R-PH-1", "restricted.json", r"/program_sha256", "ab"),
    ("R-PH-1", "structure.json", r"/digests/program_sha256", "ab"),
    ("R-PH-1", "record.json", r"/closure_(before|after)/" + re.escape(PROGRAM_ROW), "ab"),
    ("R-PH-2", "record.json", r"/commit", "ab"),  # J1: --expect-commit
    # --- digests of a compared output file; each is bound to the new file's bytes (J2) ---
    ("R-DG-1", "public.json", r"/restricted_sha256", "ab"),
    ("R-DG-1", "stdout", r"/restricted_sha256", "ab"),
    ("R-DG-1", "record.json", r"/outputs_sha256/(restricted|public|stdout)", "ab"),
    ("R-DG-1", "structure.json", r"/digests/(restricted_file|public_file|public_restricted_sha256)", "ab"),
    # --- process-record fields inside record.json / child-argv.json (section B, RL-132 §1 precedent) ---
    ("R-B-1", "record.json", r"/(stem|start_time_ns|end_time_ns|wall_s|peak_rss|time_wrapper_exit)", "ab"),
    ("R-B-2", "record.json", r"/outputs_sha256/stderr", "ab"),
    ("R-B-3", "record.json", r"/argv_sha256", "ab"),
    ("R-B-4", "record.json", r"/(argv|timed_argv)/\d+|/record_path|/checkout", "ab"),
    ("R-B-4", "child-argv.json", r"/argv/\d+|/checkout", "ab"),
    # --- run-input document re-run (only with --inputs-rerun; J3) ---
    ("R-IN-1", "restricted.json", r"/inputs/run_inputs_sha256", "I"),
    ("R-IN-1", "structure.json", r"/digests/(run_inputs_sha256|inputs_file)", "I"),
    # --- (b) only: RL-142 §2 item 5's list ---
    ("R-B1-SUM", "restricted.json",
     per_pack(r"/block/between_session/{P}/values/{K}/(n|mean|sd|block5_included)"), "b"),
    ("R-B1-INC", "restricted.json",
     per_pack(r"/block/flagged_inclusive/{P}/values/{K}/(n|mean|sd|block5_included)"), "b"),
    ("R-B1-SBS", "restricted.json",
     per_pack(r"/block/side_by_side/{P}/{K}/(block5|block5_label|delta|session_deltas(/[^/]+)?)"), "b"),
    ("R-BQ", "restricted.json",
     per_pack(r"/comparison_table/block/quantities/((summary|inclusive)~1{P}~1{K}~1(n|mean|sd)|side_by_side~1{P}~1{K}~1delta)"),
     "b"),
    ("R-CT-1", "restricted.json", r"/block/option_c/comparator/classes/side_by_side/(passed|failed)", "b"),  # C3
    ("R-CT-1", "structure.json", r"/option_c/comparator/classes/side_by_side/(passed|failed)", "b"),  # C3
    ("R-CT-2", "restricted.json", r"/block/option_c/comparator/(pass|classes/side_by_side/pass)", "b"),  # J4, C3
    ("R-CT-2", "structure.json", r"/option_c/comparator/(pass|classes/side_by_side/pass)", "b"),  # J4, C3
    ("R-CT-3", "structure.json", r"/term7/per_class/side_by_side/passed", "b"),  # C2
    ("R-CT-2", "structure.json", r"/checks/compared_classes_clean/(result|names_of_classes(/\d+)?)", "b"),  # J4
    ("R-FL", "restricted.json", r"/block/option_c/failures(/\d+)?", "b"),
    ("R-FL", "structure.json", r"/names/failures(/\d+)?|/option_c/failure_count|/checks/failures_empty/(result|count)",
     "b"),
    ("R-OCP", "restricted.json", r"/block/option_c/pass", "b"),
    ("R-OCP", "structure.json", r"/option_c/pass|/checks/option_c_pass/(result|observed)", "b"),
    ("R-CS", "restricted.json", r"/comparison_stopped", "b"),
    ("R-CS", "public.json", r"/comparison_stopped", "b"),
    ("R-CS", "stdout", r"/comparison_stopped", "b"),
    ("R-CS", "structure.json",
     r"/identity/comparison_stopped|/public/comparison_stopped|/checks/comparison_stopped/(result|observed)", "b"),
    ("R-CS-X", "record.json", r"/(exit_code|status|code)", "b"),  # J5
    ("R-OCD", "restricted.json", r"/flags/" + OCD + r"(/.*)?", "b"),
    ("R-OCD", "structure.json", r"/flags/" + OCD + r"(/.*)?", "b"),
    ("R-OCD-N", "public.json", r"/flag_count|/sessions/[^/]+/restricted_flag_count", "b"),  # J6, count-verified
    ("R-OCD-N", "stdout", r"/flags", "b"),  # J6, count-verified
    ("R-B5N", "structure.json",
     r"/block5_included/(ALPHA|BETA)|/checks/block5_included/(observed|expected|by_pack/(ALPHA|BETA)"
     r"|expected_by_pack/(ALPHA|BETA))", "b"),  # J7
]
COMPILED = [(rid, f, re.compile(rx), modes) for rid, f, rx, modes in RULES]


class Usage(Exception):
    pass


# ---------------------------------------------------------------- helpers

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def esc(key):
    return str(key).replace("~", "~0").replace("/", "~1")


def get(doc, path):
    """Value at an escaped path, or a sentinel when absent."""
    cur = doc
    for tok in path.split("/")[1:]:
        tok = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict) and tok in cur:
            cur = cur[tok]
        elif isinstance(cur, list) and tok.isdigit() and int(tok) < len(cur):
            cur = cur[int(tok)]
        else:
            return MISSING
    return cur


MISSING = object()


def kind_of(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    return type(v).__name__


def differences(a, b, path=""):
    """[(path, kind)] with kind in added, removed, type, value. Lists by index."""
    if kind_of(a) != kind_of(b):
        return [(path, "type")]
    if isinstance(a, dict):
        out = []
        for key in sorted(a.keys() | b.keys(), key=str):
            p = path + "/" + esc(key)
            if key not in a:
                out.append((p, "added"))
            elif key not in b:
                out.append((p, "removed"))
            else:
                out.extend(differences(a[key], b[key], p))
        return out
    if isinstance(a, list):
        out = []
        for i in range(max(len(a), len(b))):
            p = path + "/" + str(i)
            if i >= len(a):
                out.append((p, "added"))
            elif i >= len(b):
                out.append((p, "removed"))
            else:
                out.extend(differences(a[i], b[i], p))
        return out
    return [] if a == b else [(path, "value")]


def group_flags(doc_old, doc_new):
    """The `flags` lists are sorted by (code, session, pack, scope, detail) in RC-B6-1 `finish_recompute`; they are
    keyed by code (J12). Replace each list with {code label: [rows in order]}; restricted codes get an ordinal."""
    lists = [d.get("flags") if isinstance(d, dict) else None for d in (doc_old, doc_new)]
    if not all(isinstance(x, list) for x in lists):
        return
    codes = sorted({str(r.get("code")) if isinstance(r, dict) else "<non-object>" for x in lists for r in x})
    hidden = [c for c in codes if c not in SHOWN_CODES]
    label = {c: (c if c in SHOWN_CODES else "<restricted-code-" + str(hidden.index(c) + 1) + ">") for c in codes}
    for doc, rows in zip((doc_old, doc_new), lists):
        grouped = {}
        for r in rows:
            c = str(r.get("code")) if isinstance(r, dict) else "<non-object>"
            grouped.setdefault(label[c], []).append(r)
        doc["flags"] = grouped


def isint(v):
    return isinstance(v, int) and not isinstance(v, bool)


def count_ocd(rows):
    total, by_session = 0, {}
    for r in rows or []:
        if isinstance(r, dict) and r.get("code") == OCD:
            total += 1
            by_session[r.get("session")] = by_session.get(r.get("session"), 0) + 1
    return total, by_session


# ---------------------------------------------------------------- comparison

def load_json(path, name):
    try:
        return json.loads(Path(path).read_bytes())
    except (OSError, ValueError):
        raise Usage("parse_error " + name)


def parse_stdout(path):
    m = STDOUT_LINE.match(Path(path).read_bytes())
    if not m:
        return None
    s, f, cs, h = m.groups()
    return {"sessions": int(s), "flags": int(f), "comparison_stopped": cs == b"true", "restricted_sha256": h.decode()}


def compare(mode, old_dir, new_dir, inputs_rerun):
    old_dir, new_dir = Path(old_dir), Path(new_dir)
    for d in (old_dir, new_dir):
        if not d.is_dir():
            raise Usage("not_a_directory " + ("old" if d == old_dir else "new"))
    modes = {mode} | ({"I"} if inputs_rerun else set())
    report = {"files": {}, "paths": [], "extra_files": []}
    unowned = []

    def note(fname, path, kind, rule):
        row = {"file": fname, "path": path or "/", "kind": kind, "rule": rule}
        report["paths"].append(row)
        if rule == "UNOWNED":
            unowned.append(row)

    def classify(fname, path):
        for rid, f, rx, rmodes in COMPILED:
            if f == fname and rx.fullmatch(path) and (set(rmodes) & modes):
                return rid
        return "UNOWNED"

    # File sets: the ten, by name only.
    names_old = {p.name for p in old_dir.iterdir()}
    names_new = {p.name for p in new_dir.iterdir()}
    for name in sorted((names_old | names_new) - set(TEN)):
        side = "both" if name in names_old and name in names_new else ("old" if name in names_old else "new")
        report["extra_files"].append({"name": name, "present_in": side})
        note(name, "/", "extra_file_" + side, "UNOWNED")
    present = {}
    for name in TEN:
        a, b = old_dir / name, new_dir / name
        ina, inb = a.is_file(), b.is_file()
        entry = {"class": "A" if name in A_FILES else "C" if name in C_FILES else "B",
                 "old_sha256": sha256_file(a) if ina else None, "new_sha256": sha256_file(b) if inb else None}
        entry["equal"] = ina and inb and entry["old_sha256"] == entry["new_sha256"]
        report["files"][name] = entry
        if not (ina and inb):
            note(name, "/", "file_" + ("absent_both" if not ina and not inb else "removed" if ina else "added"),
                 "UNOWNED")
        present[name] = ina and inb
    new_sha = {n: report["files"][n]["new_sha256"] for n in TEN}

    docs = {}
    for name in A_FILES + ("record.json", "child-argv.json"):
        if present[name]:
            docs[name] = (load_json(old_dir / name, name + " (old)"), load_json(new_dir / name, name + " (new)"))

    # Directory and checkout spellings from the records themselves (never printed).
    def subst_pairs():
        pairs = []
        if "record.json" in docs:
            ro, rn = docs["record.json"]
            if isinstance(ro.get("record_path"), str) and isinstance(rn.get("record_path"), str):
                pairs.append((os.path.dirname(ro["record_path"]), os.path.dirname(rn["record_path"])))
            if isinstance(ro.get("checkout"), str) and isinstance(rn.get("checkout"), str):
                pairs.append((ro["checkout"], rn["checkout"]))
        if "child-argv.json" in docs:
            co, cn = docs["child-argv.json"]
            if isinstance(co.get("checkout"), str) and isinstance(cn.get("checkout"), str):
                pairs.append((co["checkout"], cn["checkout"]))
        pairs.append((os.path.abspath(old_dir), os.path.abspath(new_dir)))
        return list(dict.fromkeys((o, n) for o, n in pairs if o and n and o != n))   # C1

    pairs = subst_pairs()

    def substituted(old, new):
        if not (isinstance(old, str) and isinstance(new, str)):
            return False
        x = old
        for o, n in pairs:
            x = re.sub(re.escape(o) + r"(?=/|$)", lambda m, n=n: n, x)   # C1: whole path components only
        return x == new

    ocd_old = ocd_new = None
    if "restricted.json" in docs:
        ocd_old = count_ocd(docs["restricted.json"][0].get("flags"))
        ocd_new = count_ocd(docs["restricted.json"][1].get("flags"))

    for name in A_FILES + ("record.json", "child-argv.json"):
        if name not in docs:
            continue
        old, new = docs[name]
        if name in ("restricted.json", "structure.json"):
            group_flags(old, new)
        for path, kind in differences(old, new):
            rule = classify(name, path)
            ov, nv = get(old, path), get(new, path)
            # Verifications that turn an allowed path into UNOWNED (values compared, never printed).
            if rule == "R-PH-1" and not (ov == OLD_PROGRAM and nv == NEW_PROGRAM):
                rule = "UNOWNED"
                kind += ":program_hash_not_the_predeclared_pair"
            elif rule == "R-DG-1":
                target = {"/restricted_sha256": "restricted.json", "/outputs_sha256/restricted": "restricted.json",
                          "/outputs_sha256/public": "public.json", "/outputs_sha256/stdout": "stdout",
                          "/digests/restricted_file": "restricted.json", "/digests/public_restricted_sha256":
                          "restricted.json", "/digests/public_file": "public.json"}.get(path)
                if target is None or nv != new_sha.get(target):
                    rule, kind = "UNOWNED", kind + ":digest_not_bound_to_new_file"
            elif rule == "R-B-2" and nv != new_sha.get("stderr"):
                rule, kind = "UNOWNED", kind + ":digest_not_bound_to_new_file"
            elif rule == "R-B-3":
                argv = new.get("argv")
                if sha256_bytes(json.dumps(argv).encode("utf-8")) != nv:
                    rule, kind = "UNOWNED", kind + ":argv_sha256_not_bound"
            elif rule == "R-B-4" and not (kind == "value" and substituted(ov, nv)):
                # Allowed only when the new string is the old with the out-dir / checkout spelling substituted.
                rule = "UNOWNED"
                if inputs_rerun and kind == "value" and re.fullmatch(r"/argv/\d+", path):
                    i = int(path.rsplit("/", 1)[1])
                    prev = (old.get("argv") or [None] * (i + 1))[i - 1] if i > 0 else None
                    if prev in ("--inputs", "--inputs-sha256") and (new.get("argv") or [None] * (i + 1))[i - 1] == prev:
                        rule = "R-IN-1"
                if rule == "UNOWNED":
                    kind += ":not_an_out_dir_or_checkout_substitution"
            elif rule == "R-CT-3":
                p = "/option_c/comparator/classes/side_by_side/passed"
                a, b = get(old, p), get(new, p)
                if not (kind == "value" and all(isint(v) for v in (ov, nv, a, b)) and nv - ov == b - a):
                    rule, kind = "UNOWNED", kind + ":term7_count_not_explained_by_comparator"
            elif rule == "R-OCD-N" and name == "public.json":
                if ocd_old is None:
                    rule, kind = "UNOWNED", kind + ":no_restricted_flags_to_explain_count"
                elif path == "/flag_count":
                    if not (kind == "value" and isint(nv) and isint(ov) and nv - ov == ocd_new[0] - ocd_old[0]):
                        rule, kind = "UNOWNED", kind + ":count_not_explained_by_option_c_disagrees"
                else:
                    sid = path.split("/")[2].replace("~1", "/").replace("~0", "~")
                    if not (kind == "value" and isint(nv) and isint(ov)
                            and nv - ov == ocd_new[1].get(sid, 0) - ocd_old[1].get(sid, 0)):
                        rule, kind = "UNOWNED", kind + ":count_not_explained_by_option_c_disagrees"
            note(name, path, kind, rule)

    # stdout: one line of four named tokens (J9). Never printed.
    if present["stdout"] and not report["files"]["stdout"]["equal"]:
        so, sn = parse_stdout(old_dir / "stdout"), parse_stdout(new_dir / "stdout")
        if so is None or sn is None:
            note("stdout", "/", "unparsed", "UNOWNED")
        else:
            for tok in STDOUT_TOKENS:
                if so[tok] == sn[tok]:
                    continue
                path, rule, kind = "/" + tok, classify("stdout", "/" + tok), "value"
                if rule == "R-DG-1" and sn[tok] != new_sha.get("restricted.json"):
                    rule, kind = "UNOWNED", "value:digest_not_bound_to_new_file"
                elif rule == "R-OCD-N" and (ocd_old is None or sn[tok] - so[tok] != ocd_new[0] - ocd_old[0]):
                    rule, kind = "UNOWNED", "value:count_not_explained_by_option_c_disagrees"
                note("stdout", path, kind, rule)

    # B files: hashed only.
    for name in B_FILES:
        if present[name] and not report["files"][name]["equal"]:
            note(name, "/", "bytes_differ_hash_only", "B-FILE")

    return report, unowned


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=("a", "b"), required=True)
    parser.add_argument("--old", required=True, help="the earlier run dir (gate-2 for a, dry for b)")
    parser.add_argument("--new", required=True, help="the r2 run dir (gate-r2 for a, dry-r2 for b)")
    parser.add_argument("--out", required=True, help="new result.json (refused if it exists)")
    parser.add_argument("--inputs-rerun", action="store_true",
                        help="J3: the run-input document was re-made for r2 (R-IN-1 applies)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    comparer_sha = sha256_file(__file__)
    if os.path.lexists(args.out):
        print("compare_rl142: refused out_exists")
        return 2
    try:
        report, unowned = compare(args.mode, args.old, args.new, args.inputs_rerun)
    except Usage as exc:
        print("compare_rl142: refused " + str(exc))
        return 2
    except Exception as exc:  # never a traceback (it could quote a value)
        print("compare_rl142: refused " + type(exc).__name__)
        return 2
    by_rule = {}
    for row in report["paths"]:
        by_rule[row["rule"]] = by_rule.get(row["rule"], 0) + 1
    verdict = "HOLD" if unowned else "PASS"
    result = {"schema": SCHEMA, "mode": args.mode, "old_dir": os.path.abspath(args.old),
              "new_dir": os.path.abspath(args.new), "inputs_rerun": args.inputs_rerun,
              "comparer_sha256": comparer_sha, "predeclared": "/Volumes/JW-EXT/scratch/rl142-expected-diff.md",
              "verdict": verdict, "exit": 3 if unowned else 0, "counts": {"differing_paths": len(report["paths"]),
              "unowned": len(unowned), "by_rule": dict(sorted(by_rule.items()))}, **report}
    data = (json.dumps(result, indent=1, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    print("compare_rl142 mode=" + args.mode + " comparer_sha256=" + comparer_sha)
    for name in TEN:
        f = report["files"][name]
        state = "equal" if f["equal"] else "differ" if f["old_sha256"] and f["new_sha256"] else "missing"
        print("file " + name + " class=" + f["class"] + " " + state)
    for row in report["extra_files"]:
        print("extra_file " + row["name"] + " in=" + row["present_in"])
    for row in report["paths"]:
        print("path " + row["file"] + ":" + row["path"] + " kind=" + row["kind"] + " rule=" + row["rule"])
    print("counts differing=" + str(len(report["paths"])) + " unowned=" + str(len(unowned)) + " "
          + " ".join(k + "=" + str(v) for k, v in sorted(by_rule.items())))
    print("verdict " + verdict + " result_sha256=" + sha256_bytes(data))
    return 3 if unowned else 0


if __name__ == "__main__":
    raise SystemExit(main())
