"""Accounting for the frozen admission matrix (RL-184 section 3.3). Not a test module: ``unittest`` does not discover it.

The matrix is 101,889 generated cases. This module is what lets CI say it accounted for every one of them exactly once:

* ``verify_frozen`` checks the suite's module and corpus against ``interim_admission_frozen.sha256`` (the test-side lines of
  the suite's own ``SUITE.sha256``, copied verbatim) and that the corpus directory holds nothing else;
* ``verify_case_list`` checks the generated case list against the suite's published hashes (count, distinct IDs, the hash
  of the ordered IDs and the hash of the original expectations) and the corrected expectations against theirs;
* ``account`` checks that the shards' ledgers together hold every ID exactly once, each with a passing result, and counts
  how many were judged under the original and under the corrected expectations.

The corrections are ``interim_admission_corrections.json``: a versioned list of case IDs whose expectation is corrected
outside the frozen files. A correction never removes a case: it changes what the case is judged against.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = HERE / "interim_admission_frozen.sha256"
CORRECTIONS = HERE / "interim_admission_corrections.json"
CORPUS = HERE / "interim_admission"
CORRECTION_KEYS = {"version", "suite_manifest_sha256", "total_cases", "case_id_sha256", "original_oracle_sha256",
                   "corrected_oracle_sha256", "reason", "authority", "expect_admit"}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_corrections():
    doc = json.loads(CORRECTIONS.read_text(encoding="utf-8"))
    if set(doc) != CORRECTION_KEYS or doc["version"] != 1:
        raise ValueError("interim_admission_corrections.json: not the version-1 shape")
    ids = doc["expect_admit"]
    if not (isinstance(ids, list) and ids and all(isinstance(i, str) for i in ids) and len(set(ids)) == len(ids)):
        raise ValueError("interim_admission_corrections.json: expect_admit is a list of distinct case IDs")
    return doc


def verify_frozen():
    """Problems with the frozen files: a hash that differs, a file that is absent, or one the manifest does not list."""
    problems, listed = [], {}
    for line in FROZEN.read_text(encoding="utf-8").splitlines():
        digest, separator, relative = line.partition("  ")
        if not separator or len(digest) != 64 or relative in listed:
            problems.append(f"{FROZEN.name}: malformed or repeated line")
            continue
        listed[relative] = digest
    for relative, digest in listed.items():
        path = ROOT / relative
        if not path.is_file():
            problems.append(f"{relative}: absent")
        elif sha256_bytes(path.read_bytes()) != digest:
            problems.append(f"{relative}: differs from the frozen hash")
    present = {path.relative_to(ROOT).as_posix() for path in CORPUS.rglob("*")
               if path.is_file() and "__pycache__" not in path.parts}
    for relative in sorted(present - set(listed)):
        problems.append(f"{relative}: in the frozen corpus directory but not in the manifest")
    return problems


def dispositions(cases, admits, corrected=frozenset()):
    """The suite's expectation per case in its published form: ``<id><TAB>ADMIT|REFUSE<LF>``, in case order."""
    return "".join(f"{case.name}\t{'ADMIT' if admits(case) or case.name in corrected else 'REFUSE'}\n"
                   for case in cases)


def verify_case_list(suite):
    """(cases, problems). ``suite`` is the frozen module. Every hash is recomputed here, never read from the suite."""
    corrections = load_corrections()
    cases = suite.cases()
    names = [case.name for case in cases]
    corrected = frozenset(corrections["expect_admit"])
    problems = []
    if len(names) != corrections["total_cases"] or len(set(names)) != len(names):
        problems.append(f"the case list is {len(names)} IDs ({len(set(names))} distinct), not "
                        f"{corrections['total_cases']}")
    if sha256_bytes(("\n".join(names) + "\n").encode()) != corrections["case_id_sha256"]:
        problems.append("the ordered case IDs differ from the frozen suite's")
    if sha256_bytes(dispositions(cases, suite.admits).encode()) != corrections["original_oracle_sha256"]:
        problems.append("the suite's original expectations differ from the frozen suite's")
    if sha256_bytes(dispositions(cases, suite.admits, corrected).encode()) != corrections["corrected_oracle_sha256"]:
        problems.append("the corrected expectations differ from the committed correction")
    by_name = {case.name: case for case in cases}
    for name in sorted(corrected):
        if name not in by_name:
            problems.append(f"{name}: a corrected case that is not in the suite")
        elif suite.admits(by_name[name]):
            problems.append(f"{name}: already admitted by the suite; the correction is stale")
    return cases, problems


def expected_ids(cases, index, total):
    """The IDs shard ``index`` of ``total`` owns, as the suite's report mode partitions them: every case that is not an
    audit-3 reproduction by its position modulo ``total``, and the audit-3 reproductions with shard 0."""
    return [case.name for position, case in enumerate(cases)
            if (case.family == "audit-3" and index == 0) or (case.family != "audit-3" and position % total == index)]


def account(ledgers, cases, total, corrected):
    """Problems with the shards' ledgers taken together. ``ledgers`` is a list of dicts
    ``{"index", "total", "rows": [[id, basis, passed], ...]}``. The result is ``(problems, counts)``."""
    problems, seen, counts = [], {}, {"original": 0, "corrected": 0, "failed": 0}
    indices = sorted(ledger["index"] for ledger in ledgers)
    if indices != list(range(total)):
        problems.append(f"shard ledgers {indices}, not 0 to {total - 1} once each")
    for ledger in ledgers:
        if ledger["total"] != total:
            problems.append(f"shard {ledger['index']} ran as 1 of {ledger['total']}, not of {total}")
        for name, basis, passed in ledger["rows"]:
            if name in seen:
                problems.append(f"{name}: in shard {seen[name]} and in shard {ledger['index']}")
            seen[name] = ledger["index"]
            if basis not in ("original", "corrected") or (basis == "corrected") != (name in corrected):
                problems.append(f"{name}: judged on the {basis} expectation")
                continue
            if passed is not True:
                counts["failed"] += 1
                problems.append(f"{name}: failed its {basis} expectation")
            counts[basis] += 1
    names = {case.name for case in cases}
    for name in sorted(names - set(seen))[:20]:
        problems.append(f"{name}: in no shard ledger")
    for name in sorted(set(seen) - names)[:20]:
        problems.append(f"{name}: in a ledger but not in the suite")
    if not problems and counts["original"] + counts["corrected"] != len(names):
        problems.append("the judged cases do not add up to the suite")
    return problems, counts
