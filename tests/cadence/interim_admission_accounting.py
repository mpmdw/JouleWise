"""The frozen admission packet's identity and accounting (RL-184 section 3.3). Not a test module: ``unittest`` does
not discover it.

The packet's 101,889-case matrix is the acceptance of stage-1 admission (lead, PR #795 round 5). Under RL-194 stage 1
admits by content address and the executor takes no path (audit 2), so the lead had only the suite's driver changed: it
writes each case's custody at the registered root, pins it in the manifest and publishes it, as the lead's pin fill
would, and runs a committed stage 1 with no option. Every case's data and expected decision are byte-identical. This
module keeps that true and accounts for every case:

* ``verify_frozen`` checks the packet's module and corpus against ``interim_admission_frozen.sha256`` (the test-side
  lines of the packet's own ``SUITE.sha256``, copied verbatim) and that the corpus directory holds nothing else. The
  suite's own line names the adopted bytes; the adapted module must be the one ``interim_admission_shim.json`` names,
  and everything in it outside the driver (``DRIVER``) must hash as the adopted module's does;
* ``verify_case_list`` checks the generated case list against the packet's published hashes (count, distinct IDs, the
  hash of the ordered IDs and the hash of the original expectations) and the corrected expectations against theirs;
* ``expected_ids`` and ``account`` partition the matrix into CI shards and require every case ID in exactly one shard
  ledger, each passing (``ci_interim_admission.py``).

The corrections are ``interim_admission_corrections.json``: a versioned list of case IDs whose expectation the lead
corrected outside the frozen files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = HERE / "interim_admission_frozen.sha256"
CORRECTIONS = HERE / "interim_admission_corrections.json"
SHIM = HERE / "interim_admission_shim.json"
SUITE = "tests/cadence/test_interim_admission_closure.py"
DRIVER = ("actor", "Arena")       # the only definitions the lead let change: the suite's driver and invocation
SHIM_KEYS = {"version", "authority", "suite", "original_sha256", "adapted_sha256", "driver", "case_source_sha256",
             "what"}
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


def load_shim():
    doc = json.loads(SHIM.read_text(encoding="utf-8"))
    if set(doc) != SHIM_KEYS or doc["version"] != 1 or doc["suite"] != SUITE or doc["driver"] != list(DRIVER):
        raise ValueError("interim_admission_shim.json: not the version-1 shape for the suite's driver")
    return doc


def case_source_sha256(data):
    """sha256 of the suite's source with its driver's lines removed: every line outside the top-level definitions named
    in ``DRIVER`` (a definition's decorators included), as written and in order. The case catalogue, the corpus
    loaders, the mutations, the expectations, the judging, the test classes and the report mode are all in it."""
    import ast
    text = data.decode("utf-8")
    dropped = set()
    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in DRIVER:
            start = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
            dropped.update(range(start, node.end_lineno + 1))
    kept = "".join(line for number, line in enumerate(text.splitlines(keepends=True), 1) if number not in dropped)
    return sha256_bytes(kept.encode("utf-8"))


def verify_frozen():
    """Problems with the frozen files: a hash that differs, a file that is absent, or one the manifest does not list.
    The suite itself is the adapted module the shim record names: its frozen line must be the record's original hash,
    its bytes the record's adapted hash, and its source outside the driver the record's case-source hash."""
    problems, listed = [], {}
    for line in FROZEN.read_text(encoding="utf-8").splitlines():
        digest, separator, relative = line.partition("  ")
        if not separator or len(digest) != 64 or relative in listed:
            problems.append(f"{FROZEN.name}: malformed or repeated line")
            continue
        listed[relative] = digest
    shim = load_shim() if SUITE in listed else None
    for relative, digest in listed.items():
        path = ROOT / relative
        if not path.is_file():
            problems.append(f"{relative}: absent")
        elif relative == SUITE:
            data = path.read_bytes()
            if digest != shim["original_sha256"]:
                problems.append(f"{relative}: the frozen line is not the shim record's original")
            if sha256_bytes(data) != shim["adapted_sha256"]:
                problems.append(f"{relative}: not the adapted module the shim record names")
            if case_source_sha256(data) != shim["case_source_sha256"]:
                problems.append(f"{relative}: changed outside its driver ({', '.join(DRIVER)})")
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
