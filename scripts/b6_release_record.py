#!/usr/bin/env python3
"""Block 6: Block 5 input probe, release check and release record (RL-134 items 2, 7, 10; runbook build B-5).

    b6_release_record.py b5-probe --checkout W --block5 PATH --block5-sha256 HEX --out O [--predeclared]
    b6_release_record.py check --run-dir RUN --checkout W --expect-commit S --manifest M --manifest-sha256 H
                               --block5 PATH --block5-sha256 HEX --cite 1=TEXT --cite 2=TEXT --cite 9=TEXT
                               --cite 10=TEXT --cite 11=TEXT [--kit KIT] [--root ROOT] [--tag b6/analysis]
    b6_release_record.py record --draft RUN/release-record-draft.json --out docs/registrations/block6_release_record.md
                                --registration docs/registrations/block6_replication_DRAFT.md --main-commit C
                                --signed-by NAME --date TEXT

`b5-probe` checks the Block 5 file's digest, imports the pinned RC-B6-1 from W in a separate `python -I -B`
process, runs `block5_quantities` and `pack_block5_keys` on the file, and writes, per pack, the number of
summarised keys with a finite Block 5 value and their key names. No value leaves that process. The total is the
predeclared count of between-session rows with `block5_included` true (RL-134 item 2 term 2). RL-142 item 4: it
also lists, by name, the finite summarised keys of the unfiltered `block5_quantities` that no pack keeps; that list
must be empty, or the probe holds (`b5-probe: hold unassigned=<n>`, exit 5). With `--predeclared` the per-pack
counts must equal RL-142's predeclaration for r2 (ALPHA 22, BETA 22, GAMMA 4, total 48), or the probe holds
(`b5-probe: hold predeclared`, exit 5).

`check` is the release check of runbook step 11 (§17-R1: digest re-verification plus an input census; the program
is not run again). It evaluates the eleven conditions; (1), (2), (9), (10) and (11) are supplied as `--cite`
strings and printed as cited, not checked. For (7) it runs the custody kit's `verify` into a new receipt and
compares sessions, files and bytes with receipt 1. stdout: `release-check: pass` or `release-check: fail <n,...>`;
it writes RUN/release-record-draft.json with every digest. Exit 0 on pass, 5 on fail, 2 on usage.

`record` renders the step 12 record (Markdown, and its JSON beside it) from a passing draft. The nine
`harvest_sha256` values come from the manifest; no other manifest digest is printed (RL-100 item 2).
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b6_real_run as rr  # noqa: E402  (the embedded 24-hash table and the record format)

PROBE_SCHEMA = "joulewise.b6_block5_probe.v1"
DRAFT_SCHEMA = "joulewise.b6_release_record_draft.v1"
RECORD_SCHEMA = "joulewise.b6_release_record.v1"
PROGRAM = "scripts/independent_recompute_b6.py"
DEFAULT_KIT = "/Volumes/JW-EXT/jw-wt/b6-custody-kit-r3/scripts/b6_custody_kit.py"
DEFAULT_ROOT = "/Volumes/JW-EXT/b6-custody"
CATALOG = "configs/b6/flag_catalog_b6.json"
NINE = ("r1-alpha", "r3-alpha", "r4-alpha", "r1-beta", "r2-beta", "r3-beta", "r1-gamma", "r2-gamma", "r3-gamma")
CITED = ("1", "2", "9", "10", "11")
CONDITIONS = {
    "1": "Block 6 closed: nine counting sessions (§5.3 close record, RUN_STATE item 59)",
    "2": "Block 5 released (RUN_STATE item 231)",
    "3": "the dry run completed over every session, exit 0, no refusal; every earlier attempt is in the ledger",
    "4": "option_c.pass true, comparison_stopped false, every compared class failed 0 and unmatched 0",
    "5": "term 7: pass",
    "6": "output digests equal the launcher's record; public restricted_sha256 equals the restricted file's",
    "7": "input census: a second kit verify, same sessions, files and bytes; run inputs, Block 5 and loop files "
         "re-hash to the values the run used",
    "8": "run checkout clean at the S-14 commit with 24 of 24 hashes, before the gate run and after the dry run",
    "9": "PR #748 merged; S-16 line entered or RL-134 item 17 applied",
    "10": "the RL-6 (d) line is in RUN_STATE.md",
    "11": "Ed's OK is on record",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
# RL-142 item 4: predeclared for r2 (`b6/analysis-r2`); the count at RC-B6-1 90e22603… was 44 by the pack-filter defect.
PREDECLARED_BY_PACK = {"ALPHA": 22, "BETA": 22, "GAMMA": 4}

B5_SNIPPET = r"""
import importlib.util, json, sys
from pathlib import Path
checkout, block5 = Path(sys.argv[1]), Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("rc_b6_pinned", checkout / "scripts/independent_recompute_b6.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
keys = m.block5_quantities(json.loads(block5.read_bytes()))
out = {pack: sorted(k for k, v in m.pack_block5_keys(pack, keys).items() if m.summarized(k) and m.finite(v))
       for pack in m.PACKS}
kept = {k for pack in m.PACKS for k in m.pack_block5_keys(pack, keys)}
unassigned = sorted(k for k, v in keys.items() if m.summarized(k) and m.finite(v) and k not in kept)
sys.stdout.write(json.dumps({"names": out, "unassigned": unassigned}))
"""


class Usage(Exception):
    pass


def sha256_file(path):
    return rr.sha256_file(path)


def write_new(path, data, private=True):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600 if private else 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def option(argv, name):
    values = rr.option_values(argv or [], name)
    return values[-1] if values else None


# ---------------------------------------------------------------- b5-probe

def cmd_b5_probe(args):
    if sha256_file(args.block5) != args.block5_sha256:
        print("refused: block5_digest_mismatch")
        return 4
    program = Path(args.checkout) / PROGRAM
    if sha256_file(program) != rr.PIN_TABLE[PROGRAM]:
        print("refused: program_digest_mismatch")
        return 4
    result = subprocess.run([sys.executable, "-I", "-B", "-c", B5_SNIPPET, str(Path(args.checkout).resolve()),
                             str(Path(args.block5).resolve())], capture_output=True, text=True, check=False,
                            stdin=subprocess.DEVNULL, cwd=str(Path(args.checkout).resolve()))
    if result.returncode != 0:
        print("refused: probe_failed")  # stderr is not relayed: it may quote a value
        return 4
    parsed = json.loads(result.stdout)
    names, unassigned = parsed["names"], parsed["unassigned"]
    if any(not isinstance(k, str) or re.search(r"\s|=", k) for v in [*names.values(), unassigned] for k in v):
        print("refused: probe_output_invalid")
        return 4
    doc = {"schema": PROBE_SCHEMA, "block5_sha256": args.block5_sha256, "program_sha256": sha256_file(program),
           "by_pack": {p: len(v) for p, v in names.items()}, "total": sum(len(v) for v in names.values()),
           "names": names, "unassigned": unassigned,
           "predeclared_by_pack": PREDECLARED_BY_PACK if args.predeclared else None,
           "meaning": "per pack, the summarised keys with a finite Block 5 value: the predeclared count of "
                      "between-session rows with block5_included true (RL-134 item 2 term 2); unassigned: finite "
                      "summarised Block 5 keys that no pack keeps, which must be none (RL-142 item 4)"}
    write_new(args.out, (json.dumps(doc, indent=1, sort_keys=True) + "\n").encode())
    if doc["total"] == 0:
        # Opus kit review F3: a predeclared count of 0 is a hold (an empty or falsy Block 5 file gives 0).
        print("b5-probe: hold total=0")
        return 5
    if unassigned:
        # RL-142 item 4: a released Block 5 value that no pack's line would carry is a hold; names are in the file.
        print("b5-probe: hold unassigned=" + str(len(unassigned)))
        return 5
    if args.predeclared and doc["by_pack"] != PREDECLARED_BY_PACK:
        print("b5-probe: hold predeclared total=" + str(doc["total"]) + " "
              + " ".join(p + "=" + str(n) for p, n in doc["by_pack"].items()))
        return 5
    print("b5-probe total=" + str(doc["total"]) + " " + " ".join(p + "=" + str(n) for p, n in doc["by_pack"].items()))
    return 0


# ---------------------------------------------------------------- check

def load_json(path):
    return json.loads(Path(path).read_bytes())


def ledger_rows(run):
    path = run / "attempts.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def checkout_state(checkout, commit):
    head = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=False).stdout.strip()
    porcelain = subprocess.run(["git", "-C", str(checkout), "status", "--porcelain"], capture_output=True, text=True,
                               check=False).stdout.strip()
    hashes = rr.closure_hashes(checkout)
    return {"head_is_commit": head == commit, "clean": not porcelain, "hashes_equal": hashes == rr.PIN_TABLE,
            "hashes_equal_count": sum(1 for k, v in rr.PIN_TABLE.items() if hashes.get(k) == v)}


def run_kit_verify(args, loop_dir, out):
    argv = [sys.executable, "-I", "-B", args.kit, "verify", "--manifest", args.manifest, "--manifest-sha256",
            args.manifest_sha256, "--root", args.root, "--loop-dir", str(loop_dir), "--out", str(out)]
    result = subprocess.run(argv, capture_output=True, text=True, check=False, stdin=subprocess.DEVNULL)
    return result.returncode, argv


def cmd_check(args):
    run = Path(args.run_dir)
    cites = {}
    for item in args.cite or []:
        key, sep, text = item.partition("=")
        if not sep or key not in CITED or not text.strip():
            raise Usage("cite_invalid")
        cites[key] = text.strip()
    evidence, ok = {}, {}

    def cond(n, passed, **detail):
        ok[n] = bool(passed)
        evidence[n] = {"condition": CONDITIONS[n], "result": "pass" if passed else "fail", **detail}

    for n in CITED:
        cond(n, n in cites, cited=cites.get(n), checked=False)

    # RL-139 fix 7: the passing attempts are named; a relaunch lives in a new directory.
    gate_dir = Path(args.gate_dir) if args.gate_dir else run / "gate"
    dry_dir = Path(args.dry_dir) if args.dry_dir else run / "dry"
    optional = lambda path: load_json(path) if path.is_file() else {}
    dry_record, gate_record = optional(dry_dir / "record.json"), optional(gate_dir / "record.json")
    structure, gate_structure = optional(dry_dir / "structure.json"), optional(gate_dir / "structure.json")
    public_path = Path(option(dry_record.get("argv"), "--public-out") or dry_dir / "public.json")
    restricted_path = Path(option(dry_record.get("argv"), "--restricted-out") or dry_dir / "restricted.json")
    public = load_json(public_path) if public_path.is_file() else {}
    ledger = ledger_rows(run)

    # (3) the dry run completed over every session; every attempt with a record is in the ledger.
    records = sorted(run.glob("*/record.json"))
    ledgered = {row.get("record") for row in ledger}
    unledgered = [p.parent.name for p in records if str(p) not in ledgered and str(p.resolve()) not in ledgered]
    sessions = sorted(public.get("sessions", {}))
    gate_complete = gate_record.get("exit_code") == 0 and gate_record.get("status") == "complete"
    cond("3", dry_record.get("exit_code") == 0 and dry_record.get("status") == "complete" and gate_complete
         and sessions == sorted(NINE) and not unledgered and bool(ledger),
         exit_code=dry_record.get("exit_code"), gate_exit_code=gate_record.get("exit_code"), sessions=len(sessions),
         unledgered_attempts=unledgered, ledger_rows=len(ledger))

    # (4) and (5) from the structure probe's output on the same restricted bytes.
    classes = structure.get("option_c", {}).get("comparator", {}).get("classes", {})
    dirty = sorted(c for c, r in classes.items() if "pass" in r and (r.get("failed") != 0 or r.get("unmatched") != 0))
    probed_same = structure.get("digests", {}).get("restricted_file") == dry_record.get("outputs_sha256", {}).get("restricted")
    # RL-139 fix 7: both probe outputs, each at its stage, with no check departing or not run, each bound to its
    # own run's restricted digest.
    probes = {}
    for label, doc, record, stage in (("gate", gate_structure, gate_record, "gate_run"),
                                      ("dry", structure, dry_record, "dry_run")):
        rows = doc.get("checks", {})
        probes[label] = {"stage_ok": doc.get("stage") == stage,
                         "departs": sorted(k for k, v in rows.items() if v.get("result") == "departs"),
                         "not_checked": sorted(k for k, v in rows.items() if v.get("result") == "not_checked"),
                         "bound": bool(record.get("outputs_sha256", {}).get("restricted"))
                         and doc.get("digests", {}).get("restricted_file") == record["outputs_sha256"]["restricted"]}
    # Opus kit review F3: a predeclared or observed Block 5 count of 0 is a hold, not a pass.
    b5row = structure.get("checks", {}).get("block5_included", {})
    b5_counts = {"observed": b5row.get("observed"), "expected": b5row.get("expected")}
    b5_ok = all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in b5_counts.values())
    probes_ok = b5_ok and all(p["stage_ok"] and not p["departs"] and not p["not_checked"] and p["bound"] for p in probes.values())
    cond("4", structure.get("option_c", {}).get("pass") is True
         and structure.get("identity", {}).get("comparison_stopped") is False and not dirty and probed_same
         and probes_ok, classes_not_clean=dirty, probe_ran_on_these_bytes=probed_same, probes=probes,
         block5_count=b5_counts)
    cond("5", structure.get("term7", {}).get("result") == "pass", term7=structure.get("term7", {}).get("result"))

    # (6) output digests.
    restricted_sha = sha256_file(restricted_path) if restricted_path.is_file() else None
    public_sha = sha256_file(public_path) if public_path.is_file() else None
    recorded = dry_record.get("outputs_sha256", {})
    cond("6", restricted_sha is not None and restricted_sha == recorded.get("restricted")
         and public_sha == recorded.get("public") and public.get("restricted_sha256") == restricted_sha,
         restricted_equal=restricted_sha == recorded.get("restricted"), public_equal=public_sha == recorded.get("public"),
         public_binds_restricted=public.get("restricted_sha256") == restricted_sha)

    # (7) the input census.
    argv = dry_record.get("argv") or []
    inputs_path, d_block = option(argv, "--inputs"), option(argv, "--inputs-sha256")
    loop_attempts, loop_state, block5_used = option(argv, "--loop-attempts"), option(argv, "--loop-state"), option(argv, "--block5")
    document = load_json(inputs_path) if inputs_path and Path(inputs_path).is_file() else {}
    external = document.get("external", {})
    census = {"run_inputs": bool(inputs_path) and sha256_file(inputs_path) == d_block,
              "block5": sha256_file(args.block5) == args.block5_sha256 == external.get("block5")
              and block5_used is not None and Path(block5_used).resolve() == Path(args.block5).resolve(),
              "loop_attempts": bool(loop_attempts) and sha256_file(loop_attempts) == external.get("loop_attempts"),
              "loop_state": bool(loop_state) and sha256_file(loop_state) == external.get("loop_state")}
    receipt1_path = run / "verify-receipt.json"
    receipt2_path = Path(args.receipt_out or run / "verify-receipt-release.json")
    kit_rc, kit_argv = (None, None)
    same = False
    if loop_attempts and receipt1_path.is_file() and not os.path.lexists(receipt2_path):
        kit_rc, kit_argv = run_kit_verify(args, Path(loop_attempts).parent, receipt2_path)
        if kit_rc == 0 and receipt2_path.is_file():
            r1, r2 = load_json(receipt1_path), load_json(receipt2_path)
            same = (r2.get("verdict") == "verified" and set(r1.get("sessions", {})) == set(r2.get("sessions", {}))
                    and all(r1["sessions"][s].get(k) == r2["sessions"][s].get(k)
                            for s in r1["sessions"] for k in ("files", "bytes"))
                    and r2.get("manifest_sha256") == args.manifest_sha256)
    cond("7", same and all(census.values()), kit_exit=kit_rc, receipts_agree=same, rehash=census,
         receipt_existed=os.path.lexists(receipt2_path) and kit_rc is None)

    # (8) the run checkout now, and the launcher's before/after records of the gate run and the dry run.
    now = checkout_state(args.checkout, args.expect_commit)
    records_clean = all(r.get("closure_before") == rr.PIN_TABLE and r.get("closure_after") == rr.PIN_TABLE
                        and r.get("commit") == args.expect_commit for r in (gate_record, dry_record))
    cond("8", now["head_is_commit"] and now["clean"] and now["hashes_equal"] and records_clean,
         now=now, gate_and_dry_records=records_clean)

    failed = [n for n in sorted(ok, key=int) if not ok[n]]
    manifest = load_json(args.manifest)
    tag_commit = None
    if args.tag:
        tag_commit = subprocess.run(["git", "-C", str(args.checkout), "rev-parse", args.tag + "^{commit}"],
                                    capture_output=True, text=True, check=False).stdout.strip() or None
    receipt2_sha = sha256_file(receipt2_path) if receipt2_path.is_file() and kit_rc == 0 else None
    draft = {
        "schema": DRAFT_SCHEMA, "result": "pass" if not failed else "fail", "failed_conditions": failed,
        "conditions": {n: evidence[n] for n in sorted(evidence, key=int)},
        "s14_commit": args.expect_commit, "tag": args.tag, "tag_commit_equal": (tag_commit == args.expect_commit)
        if args.tag else None, "closure_sha256": dict(rr.PIN_TABLE), "catalog_sha256": rr.PIN_TABLE[CATALOG],
        "manifest_sha256": args.manifest_sha256,
        "harvest_sha256": {e["copy_path"]: e["harvest_sha256"] for e in manifest.get("sessions", [])},
        "verify_receipt_sha256": {"first": sha256_file(receipt1_path) if receipt1_path.is_file() else None,
                                  "release": receipt2_sha},
        "run_inputs_sha256": {"block": d_block, "gate": option(gate_record.get("argv"), "--inputs-sha256")},
        "block5_sha256": args.block5_sha256,
        "outputs_sha256": {"gate": gate_record.get("outputs_sha256"), "dry": dry_record.get("outputs_sha256")},
        "python": dry_record.get("python"), "zstd": zstd_version(receipt2_path if receipt2_sha else None),
        "l9_audit": structure.get("identity", {}).get("inputs", {}).get("l9_audit"),
        "ledger": ledger, "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    data = (json.dumps(draft, indent=1, sort_keys=True) + "\n").encode()
    draft_path = run / "release-record-draft.json"
    fd = os.open(draft_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    print("release-check: pass" if not failed else "release-check: fail " + ",".join(failed))
    return 0 if not failed else 5


def zstd_version(receipt_path):
    if receipt_path is not None:
        zstd = load_json(receipt_path).get("zstd")
        if isinstance(zstd, dict) and zstd.get("version"):
            return zstd["version"]
        if isinstance(zstd, str):
            return zstd
    result = subprocess.run(["/opt/homebrew/bin/zstd", "--version"], capture_output=True, text=True, check=False)
    return result.stdout.strip() or None


# ---------------------------------------------------------------- record

def cmd_record(args):
    draft = load_json(args.draft)
    if draft.get("schema") != DRAFT_SCHEMA or draft.get("result") != "pass":
        print("refused: draft_not_passing")
        return 4
    registration_sha = sha256_file(args.registration)
    record = {"schema": RECORD_SCHEMA, "main_commit": args.main_commit, "registration_sha256": registration_sha,
              "registration_path": args.registration, "signed_by": args.signed_by, "date": args.date,
              **{k: v for k, v in draft.items() if k not in ("schema", "result", "failed_conditions")}}
    lines = ["# Block 6 release record", "",
             "Released under its registration on " + args.date + ". The commit of this record on `main` is the "
             "release event (RL-134 item 10); before it no person or agent opened the restricted outputs.", "",
             "## Identity", "",
             "| Item | Value |", "|---|---|",
             "| Registration (`" + args.registration + "` at `main` " + args.main_commit + ") | `" + registration_sha + "` |",
             "| Flag catalog (S-3) | `" + draft["catalog_sha256"] + "` |",
             "| S-14 commit | `" + draft["s14_commit"] + "` |",
             "| Tag | " + (("`" + draft["tag"] + "`" + ("" if draft.get("tag_commit_equal") else " (does not resolve to the commit)"))
                          if draft.get("tag") else "not given") + " |",
             "| Custody manifest | `" + draft["manifest_sha256"] + "` |",
             "| Verify receipt (custody copy) | `" + str(draft["verify_receipt_sha256"]["first"]) + "` |",
             "| Verify receipt (release census) | `" + str(draft["verify_receipt_sha256"]["release"]) + "` |",
             "| Run-input document, dry run (`D_block`) | `" + str(draft["run_inputs_sha256"]["block"]) + "` |",
             "| Run-input document, gate run (`D_gate`) | `" + str(draft["run_inputs_sha256"]["gate"]) + "` |",
             "| Block 5 released output | `" + draft["block5_sha256"] + "` |",
             "| Python | " + str(draft["python"]) + " |", "| zstd | " + str(draft["zstd"]) + " |",
             "| L9 audit | " + ("not run" if draft["l9_audit"] == "not_run" else str(draft["l9_audit"])) + " |", "",
             "## The 24 pinned files", "", "| Path | SHA-256 |", "|---|---|"]
    lines += ["| `" + p + "` | `" + h + "` |" for p, h in draft["closure_sha256"].items()]
    lines += ["", "## Sessions (`harvest_sha256` from the manifest)", "", "| Copy path | `harvest_sha256` |", "|---|---|"]
    lines += ["| `" + p + "` | `" + h + "` |" for p, h in sorted(draft["harvest_sha256"].items())]
    lines += ["", "## Output digests", "", "| Run | File | SHA-256 |", "|---|---|---|"]
    for run in ("gate", "dry"):
        for name, digest in sorted((draft["outputs_sha256"].get(run) or {}).items()):
            lines.append("| " + run + " | " + name + " | `" + digest + "` |")
    lines += ["", "## Attempts ledger (RL-134 item 6)", "", "| Stem | Exit | Status | Class | Code | Wall (s) | argv SHA-256 |",
              "|---|---|---|---|---|---|---|"]
    for row in draft["ledger"]:
        lines.append("| " + " | ".join(str(row.get(k)) for k in ("stem", "exit_code", "status", "class", "code", "wall_s"))
                     + " | `" + str(row.get("argv_sha256")) + "` |")
    lines += ["", "## The eleven conditions (runbook step 11)", "", "| # | Condition | Result | Evidence |", "|---|---|---|---|"]
    for n, row in draft["conditions"].items():
        detail = row.get("cited") if row.get("cited") else json.dumps({k: v for k, v in row.items()
                                                                       if k not in ("condition", "result", "cited", "checked")},
                                                                      sort_keys=True)
        lines.append("| " + n + " | " + row["condition"] + " | " + row["result"] + " | " + str(detail).replace("|", "/") + " |")
    lines += ["", "## Signature", "", "Signed: " + args.signed_by + ", " + args.date + ". The eleven conditions held at the "
              "release check of " + draft["checked_at_utc"] + " (UTC); the numbers that print are the dry run's "
              "outputs, verified by digest.", ""]
    out = Path(args.out)
    write_new(out, "\n".join(lines).encode(), private=False)
    write_new(out.with_suffix(".json"), (json.dumps(record, indent=1, sort_keys=True) + "\n").encode(), private=False)
    print("record " + str(out))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("b5-probe", help="predeclared block5_included count from Block 5's released output")
    p.add_argument("--checkout", required=True)
    p.add_argument("--block5", required=True)
    p.add_argument("--block5-sha256", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--predeclared", action="store_true",
                   help="hold unless the per-pack counts equal RL-142's predeclaration for r2 (22, 22, 4)")
    c = sub.add_parser("check", help="the release check of runbook step 11")
    c.add_argument("--run-dir", required=True)
    c.add_argument("--checkout", required=True)
    c.add_argument("--expect-commit", required=True)
    c.add_argument("--manifest", required=True)
    c.add_argument("--manifest-sha256", required=True)
    c.add_argument("--block5", required=True)
    c.add_argument("--block5-sha256", required=True)
    c.add_argument("--cite", action="append", metavar="N=TEXT", help="conditions 1, 2, 9, 10, 11, as cited")
    c.add_argument("--kit", default=DEFAULT_KIT, help="the custody kit used for the second verify")
    c.add_argument("--root", default=DEFAULT_ROOT, help="the custody copy root")
    c.add_argument("--gate-dir", help="the passing gate attempt's out dir (default RUN/gate)")
    c.add_argument("--dry-dir", help="the passing dry-run attempt's out dir (default RUN/dry)")
    c.add_argument("--receipt-out", help="the second receipt (default RUN/verify-receipt-release.json; must be new)")
    c.add_argument("--tag", help="the pin tag, checked to resolve to the commit")
    r = sub.add_parser("record", help="render the step 12 record from a passing draft")
    r.add_argument("--draft", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--registration", required=True, help="the registration file at the main commit")
    r.add_argument("--main-commit", required=True)
    r.add_argument("--signed-by", required=True)
    r.add_argument("--date", required=True, help="from `date`")
    args = parser.parse_args(argv)
    try:
        return {"b5-probe": cmd_b5_probe, "check": cmd_check, "record": cmd_record}[args.command](args)
    except Usage as exc:
        print("refused: " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
