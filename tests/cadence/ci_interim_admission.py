"""CI runner for the frozen admission-closure matrix. Not a test module: ``unittest`` does not discover it.

    python tests/cadence/ci_interim_admission.py shard INDEX TOTAL LEDGER_DIR
    python tests/cadence/ci_interim_admission.py account LEDGER_DIR TOTAL

The suite is the frozen packet's, adapted only in its driver (lead, PR #795 round 5; ``interim_admission_shim.json``):
each case's custody is pinned in the manifest, committed and published before a committed ``stage1`` with no option
runs, so a case costs a commit and the executor's committed-mode checks, and the matrix runs in 32 shards.

``shard`` first verifies the frozen files, the shim's scope and the case list against the suite's published hashes
(``interim_admission_accounting``). It then runs ``test_interim_admission_closure.py --report INDEX/TOTAL
--separate-audit`` (shard 0 also runs the audit-3 reproductions with ``--report audit``) and judges every case it owns:

* a case under its original expectation passes only if the suite's own assertions report no problem;
* a case in ``interim_admission_corrections.json`` is judged ADMIT instead, by the suite's own assertions for an
  admitted case on the same mutation in the positive roster: stage 1 exits 0 and writes its output, preflight returns
  before the first protected open, and there are zero response reads, zero reservations and zero public writes.

It writes ``LEDGER_DIR/ledger-INDEX.json`` and exits 1 on any failure, any case it owns that did not run, and any
case that ran twice. ``account`` reads the shards' ledgers and fails unless together they hold every case ID of the
suite exactly once, each passing, and prints how many were judged under each expectation. There is no held-open case.
"""
from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODULE = HERE / "test_interim_admission_closure.py"
sys.path.insert(0, str(ROOT))

from tests.cadence import interim_admission_accounting as ACC  # noqa: E402


def load_suite():
    from tests.cadence import test_interim_admission_closure as suite
    return suite


def verify(suite):
    problems = ACC.verify_frozen()
    cases, more = ACC.verify_case_list(suite)
    return cases, problems + more


def run_report(argument, *flags):
    process = subprocess.run([sys.executable, "-B", str(MODULE), "--report", argument, *flags],
                             capture_output=True, text=True)
    rows = [json.loads(line) for line in process.stdout.splitlines() if line.startswith("{")]
    if process.returncode:
        print(process.stderr[-4000:])
        raise SystemExit(f"the suite's report mode exited {process.returncode}")
    return rows


def corrected_problems(suite, arena, case):
    """The suite's own assertions for an admitted case, on this case's mutation, in the positive roster."""
    admitted = dataclasses.replace(case, family="admit")
    if suite.admits(case) or not suite.admits(admitted):
        return ["the correction no longer changes this case's expectation"]
    row = arena.run(case)
    row.pop("target", None)
    problems = suite.problems(admitted, row)
    # The ruling's terms, stated again outright so a change to the suite's assertions cannot loosen them.
    if row["rc"] != 0 or not row["output"]:
        problems.append("stage 1 did not exit 0 and write its output")
    if not row["admission_complete"] or row["early_opens"]:
        problems.append("a protected file opened before preflight returned")
    if row["responses"] or row["spent"] or row["public"]:
        problems.append("a response read, a reservation or a public write")
    return problems


def shard(index, total, ledger_dir):
    suite = load_suite()
    cases, problems = verify(suite)
    if problems:
        for problem in problems:
            print(f"FROZEN {problem}")
        return 1
    corrected = frozenset(ACC.load_corrections()["expect_admit"])
    owned = ACC.expected_ids(cases, index, total)
    rows = run_report(f"{index}/{total}", "--separate-audit")
    if index == 0:
        rows += run_report("audit")
    names = [row["case"] for row in rows]
    failures = []
    if len(set(names)) != len(names):
        failures.append("a case ran twice")
    if sorted(names) != sorted(owned):
        failures.append(f"the shard ran {len(set(names) - set(owned))} cases it does not own and left "
                        f"{len(set(owned) - set(names))} of its own undone")
    by_name = {case.name: case for case in cases}
    ledger = []
    arena, owner = None, unittest.TestCase()
    try:
        for row in rows:
            name = row["case"]
            if name in corrected:
                if arena is None:
                    arena = suite.Arena(owner)             # the positive roster
                why = corrected_problems(suite, arena, by_name[name])
                ledger.append([name, "corrected", not why])
            else:
                why = row["problems"]
                ledger.append([name, "original", not why])
            if why:
                failures.append(f"{name}: {why}")
    finally:
        owner.doCleanups()
    out = Path(ledger_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"ledger-{index}.json").write_text(json.dumps({"index": index, "total": total, "rows": ledger}) + "\n")
    kinds = {basis: sum(1 for _, b, _ in ledger if b == basis) for basis in ("original", "corrected")}
    print(f"SHARD {index}/{total}: {len(ledger)} cases ({kinds['original']} original, {kinds['corrected']} corrected "
          f"expectation), {len(failures)} failing")
    for failure in failures[:40]:
        print(f"FAIL {failure}")
    return 1 if failures else 0


def account(ledger_dir, total):
    suite = load_suite()
    cases, problems = verify(suite)
    corrected = frozenset(ACC.load_corrections()["expect_admit"])
    ledgers = [json.loads(path.read_text()) for path in sorted(Path(ledger_dir).glob("ledger-*.json"))]
    more, counts = ACC.account(ledgers, cases, total, corrected)
    problems += more
    line = (f"ACCOUNTING: {counts['original'] + counts['corrected']} of {len(cases)} suite case IDs, each in exactly one "
            f"of {len(ledgers)} shard ledgers: {counts['original']} judged under the original expectations, "
            f"{counts['corrected']} under the corrected expectations, {counts['failed']} failing")
    print(line)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    for problem in problems[:60]:
        print(f"FAIL {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "shard" and len(sys.argv) == 5:
        raise SystemExit(shard(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]))
    if mode == "account" and len(sys.argv) == 4:
        raise SystemExit(account(sys.argv[2], int(sys.argv[3])))
    raise SystemExit(__doc__)
