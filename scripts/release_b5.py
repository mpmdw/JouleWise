#!/usr/bin/env python3
"""Block-5 lean release check (DLE-1): digest re-verification, independent recompute, comparator.

Standard library only; imports no repository code (neither L9's analysis package nor the two lean programs,
which run as subprocesses from this checkout). It runs on the blind dry run's custody BEFORE anything is
unsealed, and prints a BLINDED verdict: per comparator family only agree or hold with its pass/fail counts,
plus structure codes and counts. It never prints, and never writes outside --restricted-out, an energy
value, a difference or an outcome word. Unsealing is a separate step that needs Ed's OK; nothing here
unseals or reads an outcome for display.

Stages (docs/analysis/b5/DEVIATION-LOG.md, DLE-1):

(a) Digest re-verification. The dry run's record (dry-run/B5-BLIND-DRY-RUN-RECORD.json) must be a completed
    blind dry run at the pinned commit; its sealed digests must equal configs/analysis/b5/seal_pins.json at
    that commit; its window_index_sha256 must equal the window index given; every step output it holds must
    hash to its recorded digest under dry-run/restricted/ (read without following a symbolic link); every
    input-census row must hash to its recorded digest at the indexed roots (the mapping is L9's own
    _released_input_difference: the archive, original/claim-runs/ under the claim-runs root, the live ledger
    under the measurement root, sources/attempts/<plan>/ under that plan's archive); and every analysed window
    must be the indexed one. Any mismatch refuses with release_digest_differs_from_dry_run (the location goes
    to the restricted folder only). The release checkout itself must be clean, so the programs that run are
    the committed ones.
(b) The independent recompute (scripts/independent_recompute_b5.py --member-detail --workers N) on the
    indexed archive, claim-runs and bound-runs roots of each analysed window.
(c) The comparator (scripts/compare_b5_recompute.py) against the dry-run custody, with the release bar set
    (configs/analysis/b5/recompute_bars.json, whose bytes must hash to RELEASE_BARS_SHA256, the set RS item 83
    ruling 1 bound blind; there is no other bar set for a release) and each window's withheld meter record when
    the harvest wrote one.

Release condition: (a) verified, the recompute exits 0 with comparison_stopped false, and the comparator
exits 0 (every family passes, nothing unmapped, no absent step-11 output, no non-finite step-11 value) with no
within-bar attribution-limit form left undetermined (DLE-5, R704-D3: the comparator's limit_undetermined list, whose
count and row keys, never a value, the verdict carries; any such row holds the release, exit 1, whatever the rows'
numeric agreement; the cell and form is then published as "attribution limit not independently determined"). Any other result holds the release. The verdict also reports step11.uncovered_numeric (leaves under a named
exemption, the LEAN-COVERAGE-AUDIT gap) and structure_flags; like the comparator's own exit, these counts do not
gate, and a nonzero count under agree is expected, not a defect.

Exit codes (precedence 2 > 1 > 0): 0 agree; 1 hold (the comparator, itself exiting 0 or 1, found a disagreement or an
undetermined within-bar limit form); 2 hold on a refusal (custody, binding,
recompute or comparator). The verdict (stdout, and verdict.json in --restricted-out) carries structure only;
values and differences stay in --restricted-out (recompute.json, comparison.json, the programs' streams).
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RECOMPUTE = ROOT / "scripts/independent_recompute_b5.py"
COMPARATOR = ROOT / "scripts/compare_b5_recompute.py"
RELEASE_BARS = ROOT / "configs/analysis/b5/recompute_bars.json"
# The release bar set fixed blind (RS item 83 ruling 1; bar_set b5_release_recompute_coded_7e322b76, file as of
# 048085b3e). A release check runs with these bytes or refuses; alternate bars are audit work, never a release.
RELEASE_BARS_SHA256 = "2f65bba22c0afd23a637cabb5079e1c5dc6a367d53d956f77c20ead416813892"
# The only identifiers the public verdict may carry from the comparator's output (its NUMERIC, METER and
# CATEGORICAL families and its STEP11_SOURCES labels); anything else is unreadable output, never printed.
FAMILIES = frozenset({"run_phase_energy_j", "floor_j", "floor_gate_j", "dominance_ratio", "reported_cell_j",
                      "contrast_j", "contrast_p", "descriptive_ratio", "per_token_j", "b_op_s", "count",
                      "meter_j", "meter_w", "machine_j", "rho", "window_edge_s", "outcome_word", "dominance_branch",
                      "p42_status", "holm_order", "kept_units", "exclusions_rederivation", "battery_term",
                      "routing_id"})
STEP11_LABELS = frozenset({"fill", "disclosure"})
SCHEMA = "joulewise.b5_lean_release_verdict.v1"
RECORD = "dry-run/B5-BLIND-DRY-RUN-RECORD.json"
RESTRICTED = "dry-run/restricted"
RECORD_SCHEMA = "joulewise.b5_blind_dry_run.v1"
PACKS = ("alpha", "beta", "gamma")
# dry_run.SEAL_KEYS, with the record's key for the catalog mapped to seal_pins.json's (dry_run.py:2069).
SEAL_KEYS = {"registration_sha256": "registration_sha256", "analysis_plan_sha256": "analysis_plan_sha256",
             "flag_catalog_sha256": "catalog_sha256", "erratum_2_sha256": "erratum_2_sha256",
             "erratum_3_sha256": "erratum_3_sha256"}
DIFFERS = "release_digest_differs_from_dry_run"
HEX40, HEX64 = re.compile(r"[0-9a-f]{40}"), re.compile(r"[0-9a-f]{64}")
# The verdict is refused if any of its bytes reads as a decimal or exponent number (dry_run._FLOAT_TOKEN).
# A comparator row key (registered ids and structure words only): the keys of the undetermined rows the verdict names.
# Each segment takes the cell-id alphabet of the comparator's DIAG_CELL, a dot included.
LIMIT_ROW_KEY = re.compile(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+")
FLOAT_TOKEN = re.compile(r"(?<![A-Za-z0-9])(?:\d+\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)(?![A-Za-z0-9])")


class Refusal(Exception):
    """A structure-only reason the release check cannot pass; .where is restricted."""

    def __init__(self, code, where=None):
        super().__init__(code)
        self.code, self.where = code, where


def strict_json(raw, code):
    def pairs(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate key")
        return dict(items)

    def constant(name):
        raise ValueError("non-finite constant " + name)
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeDecodeError):
        raise Refusal(code) from None


def read_nofollow(base, relative):
    """Bytes of BASE/RELATIVE; refuses a symbolic link at any component under BASE, or a non-regular file."""
    parts = relative.split("/")
    if (not relative or "\\" in relative or "\x00" in relative or relative.startswith("/")
            or any(p in ("", ".", "..") for p in parts)):
        raise OSError("invalid relative path")
    path = Path(base)
    for part in parts[:-1]:
        path = path / part
        if not stat.S_ISDIR(os.lstat(path).st_mode):
            raise OSError("not a directory")
    # O_NONBLOCK: a FIFO opens at once and is then refused as not regular, never a hang.
    fd = os.open(path / parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("not a regular file")
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(fd)


def file_sha256(path):
    """SHA-256 of a regular file (symbolic links followed, as L9's census hash does); None otherwise.

    O_NONBLOCK makes opening a FIFO or similar special file return at once instead of blocking; anything that is
    not a regular file then hashes to None (a digest difference), never a hang.
    """
    digest = hashlib.sha256()
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)
    except OSError:
        return None
    finally:
        os.close(fd)


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if result.returncode != 0:
        raise Refusal("release_checkout_unavailable")
    return result.stdout


def check_checkout(repo):
    """The release programs must be the committed ones: HEAD, and a clean tree (no change, no untracked file)."""
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    if git(repo, "status", "--porcelain", "--untracked-files=all").strip():
        raise Refusal("release_checkout_not_clean")
    return head


def checkout_relation(repo, head, pinned):
    """Advisory ancestry only; unavailable history never establishes agreement.

    `unrelated` includes a checkout behind the pin as well as divergent history.
    This observation must not introduce a release refusal or change an exit code.
    """
    if not all(isinstance(value, str) and HEX40.fullmatch(value) for value in (head, pinned)):
        return "unknown"
    try:
        result = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", pinned, head],
                                capture_output=True)
    except OSError:
        return "unknown"
    if result.returncode == 0:
        return "equals_pinned" if head == pinned else "descends_from_pinned"
    return "unrelated" if result.returncode == 1 else "unknown"


def need(condition):
    if not condition:
        raise Refusal("dry_run_record_invalid")


def load_record(custody):
    try:
        raw = read_nofollow(custody, RECORD)
    except OSError:
        raise Refusal("dry_run_record_missing_or_incomplete") from None
    record = strict_json(raw, "dry_run_record_invalid")
    need(isinstance(record, dict))
    need(record.get("schema_version") == RECORD_SCHEMA and record.get("mode") == "blind-dry-run")
    need("release_difference" not in record)
    need(isinstance(record.get("analysis_commit"), str) and HEX40.fullmatch(record["analysis_commit"]))
    need(isinstance(record.get("window_index_sha256"), str) and HEX64.fullmatch(record["window_index_sha256"]))
    sealed = record.get("sealed")
    need(isinstance(sealed, dict) and set(sealed) == set(SEAL_KEYS)
         and all(isinstance(v, str) and HEX64.fullmatch(v) for v in sealed.values()))
    for name in ("windows", "input_census", "steps"):
        need(isinstance(record.get(name), list))
    for row in record["windows"]:
        need(isinstance(row, dict) and row.get("pack") in PACKS and isinstance(row.get("plan_id"), str)
             and isinstance(row.get("harvest_record_sha256"), str))
    need(len({row["pack"] for row in record["windows"]}) == len(record["windows"]))
    for row in record["input_census"]:
        need(isinstance(row, dict) and row.get("window") in PACKS and isinstance(row.get("path"), str)
             and isinstance(row.get("sha256"), str) and HEX64.fullmatch(row["sha256"]))
    for row in record["steps"]:
        need(isinstance(row, dict) and isinstance(row.get("outputs"), list))
        for output in row["outputs"]:
            need(isinstance(output, dict) and isinstance(output.get("name"), str)
                 and isinstance(output.get("sha256"), str) and HEX64.fullmatch(output["sha256"]))
    need(type(record.get("completed_without_tooling_refusal")) is bool)
    if not record["completed_without_tooling_refusal"] or not record["steps"]:
        raise Refusal("dry_run_not_completed")
    return record


def load_index(path, record):
    try:
        raw = Path(path).read_bytes()
    except OSError:
        raise Refusal("window_index_unreadable") from None
    if hashlib.sha256(raw).hexdigest() != record["window_index_sha256"]:
        raise Refusal(DIFFERS, "binding/window_index")
    index = strict_json(raw, "window_index_invalid")
    attempts = index.get("attempts") if isinstance(index, dict) else None
    if not isinstance(attempts, list) or not all(isinstance(e, dict) for e in attempts):
        raise Refusal("window_index_invalid")
    return attempts


def analysed_entries(record, attempts):
    """Each analysed window's index entry (pack and plan_id of the record's window row), with its roots."""
    entries = {}
    for row in record["windows"]:
        matches = [e for e in attempts if e.get("pack") == row["pack"] and e.get("plan_id") == row["plan_id"]]
        if len(matches) != 1:
            raise Refusal(DIFFERS, "binding/window/" + row["pack"])
        entry = matches[0]
        if entry.get("harvest_record_sha256") != row["harvest_record_sha256"]:
            raise Refusal(DIFFERS, "binding/harvest_record/" + row["pack"])
        for field in ("archive_root", "claim_runs_root", "bound_runs_root"):
            if not isinstance(entry.get(field), str) or not Path(entry[field]).is_absolute():
                raise Refusal("window_index_invalid")
        entries[row["pack"]] = entry
    if not entries:
        raise Refusal("dry_run_record_invalid")
    return entries


def census_path(row, entries, attempts):
    """L9's _released_input_difference mapping (dry_run.py:1770-1793); None for the plan-tree binding row."""
    relative = row["path"]
    if relative == "binding/plan_tree":
        return None
    entry = entries.get(row["window"])
    if entry is None:
        raise Refusal(DIFFERS, row["path"])
    if relative.startswith("sources/attempts/"):
        _, _, plan, *parts = relative.split("/")
        matches = [e for e in attempts if e.get("plan_id") == plan]
        if len(matches) != 1 or not isinstance(matches[0].get("archive_root"), str) or not parts:
            raise Refusal(DIFFERS, row["path"])
        entry, relative = matches[0], "/".join(parts)
    if any(p in ("", ".", "..") for p in relative.split("/")) or relative.startswith("/"):
        raise Refusal("dry_run_record_invalid")
    if relative.startswith("original/claim-runs/"):
        field, relative = "claim_runs_root", relative.removeprefix("original/claim-runs/")
    elif relative == "ledger/live/calibration_observation_ledger.jsonl":
        field, relative = "measurement_root", "runs/calibration_observation_ledger.jsonl"
    else:
        field = "archive_root"
    if not isinstance(entry.get(field), str) or not Path(entry[field]).is_absolute():
        raise Refusal(DIFFERS, row["path"])
    return Path(entry[field]) / relative


def verify_digests(custody, index_path, pinned, repo, threads=8):
    """Stage (a). Returns (record, entries, structure counts); raises Refusal on any mismatch."""
    if not HEX40.fullmatch(pinned or ""):
        raise Refusal("pinned_commit_invalid")
    record = load_record(custody)
    if record["analysis_commit"] != pinned:
        raise Refusal(DIFFERS, "binding/analysis_commit")
    try:
        raw_pins = git(repo, "show", pinned + ":configs/analysis/b5/seal_pins.json")
    except Refusal:
        raise Refusal("pinned_commit_unavailable") from None
    pins = strict_json(raw_pins, "seal_pins_invalid")
    sealed = pins.get("sealed") if isinstance(pins, dict) else None
    if not isinstance(sealed, dict) or any(record["sealed"][k] != sealed.get(v) for k, v in SEAL_KEYS.items()):
        raise Refusal(DIFFERS, "binding/sealed")
    attempts = load_index(index_path, record)
    entries = analysed_entries(record, attempts)
    outputs, seen = [], {}
    for row in record["steps"]:
        for output in row["outputs"]:
            if seen.setdefault(output["name"], output["sha256"]) != output["sha256"]:
                raise Refusal("dry_run_record_invalid")
            outputs.append(output)
    for output in outputs:
        try:
            # From the custody root, so dry-run/ and restricted/ themselves are also refused as links.
            actual = hashlib.sha256(read_nofollow(custody, RESTRICTED + "/" + output["name"])).hexdigest()
        except OSError:
            actual = None
        if actual != output["sha256"]:
            raise Refusal(DIFFERS, "output/" + output["name"])
    rows = [(row, census_path(row, entries, attempts)) for row in record["input_census"]]
    with concurrent.futures.ThreadPoolExecutor(threads) as pool:
        digests = list(pool.map(lambda item: None if item[1] is None else file_sha256(item[1]), rows))
    skipped = 0
    for (row, path), actual in zip(rows, digests):
        if path is None:
            skipped += 1
        elif actual != row["sha256"]:
            raise Refusal(DIFFERS, "input/" + row["window"] + "/" + row["path"])
    counts = {"outputs_verified": len(outputs), "input_census_verified": len(rows) - skipped,
              "input_census_binding_rows": skipped, "windows": sorted(entries)}
    return record, entries, counts


def run_program(argv, restricted, name):
    """Run a lean program with its streams kept in the restricted folder; return its exit status."""
    with open(restricted / (name + ".stdout"), "wb") as out, open(restricted / (name + ".stderr"), "wb") as err:
        return subprocess.run(argv, stdout=out, stderr=err, cwd=ROOT).returncode


def recompute_argv(entries, out, workers, python):
    argv = [python, "-B", str(RECOMPUTE)]
    for pack in PACKS:
        if pack in entries:
            entry = entries[pack]
            argv += ["--" + pack, entry["archive_root"], "--claim-runs-" + pack, entry["claim_runs_root"],
                     "--bound-runs-" + pack, entry["bound_runs_root"]]
    return argv + ["--member-detail", "--workers", str(workers), "--out", str(out)]


def comparator_argv(custody, recompute_out, index_path, entries, out, python):
    argv = [python, "-B", str(COMPARATOR), "--l9-custody", str(custody), "--recompute", str(recompute_out),
            "--window-index", str(index_path), "--restricted-out", str(out), "--bars", str(RELEASE_BARS)]
    for pack in PACKS:
        if pack in entries and (Path(entries[pack]["archive_root"]) / "withheld/meter.json").is_file():
            argv += ["--harvest-meter", pack + "=" + str(Path(entries[pack]["archive_root"]) / "withheld/meter.json")]
    return argv


def stage_recompute(entries, restricted, workers, python):
    """Stage (b). Returns (status dict, refusal code or None)."""
    out = restricted / "recompute.json"
    started = time.monotonic()
    code = run_program(recompute_argv(entries, out, workers, python), restricted, "recompute")
    status = {"exit": code, "workers": workers, "wall_ms": int((time.monotonic() - started) * 1000)}
    if code != 0:
        return status, "recompute_failed"
    try:
        result = strict_json(out.read_bytes(), "recompute_output_unreadable")
    except OSError:
        return status, "recompute_output_unreadable"
    stopped = result.get("comparison_stopped") if isinstance(result, dict) else None
    # Only a boolean reaches the verdict; any other payload is reported as null (and holds).
    status["comparison_stopped"] = stopped if isinstance(stopped, bool) else None
    if stopped is not False:
        return status, "recompute_comparison_stopped"
    return status, None


def stage_compare(custody, entries, index_path, restricted, python):
    """Stage (c). Returns (status dict, refusal code or None, disagreement)."""
    out = restricted / "comparison.json"
    started = time.monotonic()
    code = run_program(comparator_argv(custody, restricted / "recompute.json", index_path, entries, out, python),
                       restricted, "comparator")
    status = {"exit": code, "wall_ms": int((time.monotonic() - started) * 1000)}
    try:
        result = strict_json(out.read_bytes(), "comparison_output_unreadable")
    except (OSError, Refusal):
        return status, "comparison_output_unreadable", False
    if not isinstance(result, dict) or "refused" in result:
        refused = result.get("refused") if isinstance(result, dict) else None
        status["refused"] = refused if isinstance(refused, str) and re.fullmatch(r"[a-z0-9_:]+", refused) else "other"
        return status, "comparator_refused", False
    counts, cover = result.get("counts"), result.get("coverage")
    if not isinstance(counts, dict) or not isinstance(cover, dict):
        return status, "comparison_output_unreadable", False
    if not all(isinstance(cover.get(k), list) for k in ("unmapped", "nonfinite", "uncovered_numeric", "absent_sources")):
        # The comparator always writes these lists (compare_b5_recompute.coverage); absent means unreadable.
        return status, "comparison_output_unreadable", False
    if not any(isinstance(row, dict) and type(row.get("pass")) is int and row["pass"] > 0 for row in counts.values()):
        # A comparison that compared nothing is never agreement.
        return status, "comparison_vacuous", False
    families = {}
    for family, row in sorted(counts.items()):
        if not (isinstance(row, dict) and type(row.get("pass")) is int and type(row.get("fail")) is int
                and family in FAMILIES):
            return status, "comparison_output_unreadable", False
        families[family] = {"verdict": "agree" if row["fail"] == 0 else "hold", "pass": row["pass"], "fail": row["fail"]}
    status["bars_sha256"] = RELEASE_BARS_SHA256
    status["families"] = families
    status["step11"] = {"unmapped": len(cover.get("unmapped") or []), "nonfinite": len(cover.get("nonfinite") or []),
                        "uncovered_numeric": len(cover.get("uncovered_numeric") or []),
                        "absent_sources": sorted(s for s in cover.get("absent_sources") or [] if s in STEP11_LABELS)}
    if len(status["step11"]["absent_sources"]) != len(cover.get("absent_sources") or []):
        return status, "comparison_output_unreadable", False
    status["structure_flags"] = len(result.get("structure_flags") or [])
    undetermined = result.get("limit_undetermined")
    if not (isinstance(undetermined, list) and all(isinstance(k, str) and LIMIT_ROW_KEY.fullmatch(k) for k in undetermined)):
        # The comparator always writes the list (compare_b5_recompute.run); absent or odd means unreadable.
        return status, "comparison_output_unreadable", False
    status["limit_undetermined"] = {"count": len(undetermined), "rows": sorted(undetermined)}
    if code not in (0, 1):
        # Precedence is refused (exit 2) > hold (exit 1) > agree (exit 0): a comparator that refused (its exit 2, e.g.
        # unmapped step-11 leaves) or failed is a refusal whatever summary it wrote, never a family disagreement or an
        # undetermined-form hold.
        return status, "comparator_refused", False
    disagreement = any(row["fail"] for row in families.values())
    if undetermined and not disagreement and not status["step11"]["unmapped"] and not status["step11"]["nonfinite"] \
            and not status["step11"]["absent_sources"]:
        # R704-D3: the release is held mechanically; each undetermined row is reported as the label
        # "attribution limit not independently determined" (DLE-5), nothing else changes.
        return status, "within_bar_undetermined", True
    if code == 0 and not disagreement and not status["step11"]["unmapped"] and not status["step11"]["nonfinite"] \
            and not status["step11"]["absent_sources"]:
        return status, None, False
    if disagreement:
        return status, "comparator_disagreement", True
    return status, "comparator_refused", False


def release(custody, index_path, pinned, restricted_out, *, workers=10, repo=ROOT, python=sys.executable):
    """Stages (a)-(c). Returns (verdict dict, exit code). Writes values only under restricted_out.

    Exit 0 only with a final verdict of agree: a verdict the structure guard replaced is a hold, exit 2.
    """
    verdict, code = _release(custody, index_path, pinned, restricted_out, workers=workers, repo=repo, python=python)
    if verdict.get("verdict") != "agree" and code == 0:
        code = 2
    return verdict, code


def _release(custody, index_path, pinned, restricted_out, *, workers, repo, python):
    restricted = Path(restricted_out)
    verdict = {"schema": SCHEMA, "verdict": "hold", "reason": None,
               "pinned_commit": pinned if isinstance(pinned, str) and HEX40.fullmatch(pinned) else None,
               "checkout_head": None, "checkout_relation": "unknown",
               "stages": {"digests": {"status": "not_run"}, "recompute": {"status": "not_run"},
                          "comparator": {"status": "not_run"}}}
    stages = verdict["stages"]
    started = time.monotonic()
    try:
        verdict["release_checkout"] = {"commit": check_checkout(repo), "clean": True}
        verdict["checkout_head"] = verdict["release_checkout"]["commit"]
        verdict["checkout_relation"] = checkout_relation(repo, verdict["checkout_head"], pinned)
        if file_sha256(RELEASE_BARS) != RELEASE_BARS_SHA256:
            raise Refusal("release_bars_differ")
        record, entries, counts = verify_digests(custody, index_path, pinned, repo)
    except Refusal as exc:
        stages["digests"] = {"status": "refused"}
        verdict["reason"] = exc.code
        if exc.where is not None:
            (restricted / "refusal-location.txt").write_text(exc.where + "\n")
        return finish(verdict, restricted, started), 2
    stages["digests"] = {"status": "verified", **counts}
    status, refusal = stage_recompute(entries, restricted, workers, python)
    stages["recompute"] = {"status": "refused" if refusal else "ok", **status}
    if refusal:
        verdict["reason"] = refusal
        return finish(verdict, restricted, started), 2
    status, refusal, disagreement = stage_compare(custody, entries, index_path, restricted, python)
    # An undetermined within-bar hold whose families all agree is its own status, not a disagreement.
    held = "undetermined_hold" if refusal == "within_bar_undetermined" else "disagree"
    stages["comparator"] = {"status": held if disagreement else ("refused" if refusal else "agree"), **status}
    if refusal:
        verdict["reason"] = refusal
        return finish(verdict, restricted, started), 1 if disagreement else 2
    verdict["verdict"] = "agree"
    return finish(verdict, restricted, started), 0


def finish(verdict, restricted, started):
    verdict["wall_ms"] = int((time.monotonic() - started) * 1000)
    data = json.dumps(verdict, sort_keys=True, separators=(",", ":"))
    if FLOAT_TOKEN.search(data):
        # Defence in depth: a verdict that reads as carrying a number is never printed.
        verdict = {"schema": SCHEMA, "verdict": "hold", "reason": "verdict_not_structure_only"}
        data = json.dumps(verdict, sort_keys=True, separators=(",", ":"))
    (restricted / "verdict.json").write_text(data + "\n")
    return verdict


def prepare_restricted(path, custody):
    """A new, private folder outside this checkout (values must never land in a tracked tree)."""
    path = Path(path).absolute()
    if path.exists() or path.is_symlink():
        raise Refusal("restricted_out_exists")
    resolved = path.resolve()
    for root in (ROOT.resolve(), (Path(custody).absolute() / RESTRICTED).resolve()):
        if any(p == root or root in p.parents for p in (path, resolved)):
            raise Refusal("restricted_out_inside_checkout_or_custody")
    path.mkdir(parents=True, mode=0o700)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--custody", required=True, help="the blind dry run's custody root (holds " + RECORD + ")")
    parser.add_argument("--window-index", required=True, help="the window index the dry run read")
    parser.add_argument("--pinned-commit", required=True, help="the dry run's analysis commit (40 hex digits)")
    parser.add_argument("--restricted-out", required=True,
                        help="new folder for the recompute output, the comparison and the programs' streams")
    parser.add_argument("--workers", type=int, default=10, help="recompute member worker processes (default 10)")
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error("--workers must be a positive integer")
    try:
        restricted = prepare_restricted(args.restricted_out, args.custody)
    except Refusal as exc:
        print(json.dumps({"schema": SCHEMA, "verdict": "hold", "reason": exc.code}, sort_keys=True))
        return 2
    verdict, code = release(args.custody, args.window_index, args.pinned_commit, restricted,
                            workers=args.workers)
    print(json.dumps(verdict, sort_keys=True, indent=1))
    return code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        # An exception's text can carry a value; stderr names only its type.
        print("error: internal " + type(exc).__name__, file=sys.stderr)
        raise SystemExit(2)
