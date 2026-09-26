# BFG-D: cold Fable final head, rows 7 and 10, merge candidate 3453ecb6

Judge: Claude Fable 5.1 (claude-fable-5-1), single foreground session, read-only apart from this file.
Worktree: /Users/edr/code/JouleWise-wt-ed17a643-bfgd-fp, HEAD = 3453ecb6bceecfcf335a828fd58269430f3910c9 (verified `git rev-parse HEAD`; matches PR #424 headRefOid).
Date: 2026-09-26.

## Contamination disclosure

- The session's system context carried the project CLAUDE.md, the global CLAUDE.md, and the auto-memory index (MEMORY.md, one line per memory). I opened no memory file, no RUN_STATE.md, no TASK_QUEUE.md, no council log.
- I read, by instruction: the r8 contract (`33-fix-contract-r8.md`), the r8 seat report (`34-seat-report-r8.md`), the PR #424 body, the failing gate-ledger job log, the round-8 diff, `tests/battery_float_fixture.py`, and one refusal test body in `tests/test_night_agent_install.py`.
- I did not read the earlier b2c31e5b final-pass record or the Opus row-6 dissent. Nothing here re-adjudicates M-1; it is carried as a lane in the body and the body says so.
- No subagents, no background tasks.

## Task (1): the diff aa5d8c8c → 3453ecb6

`git diff --stat aa5d8c8c 3453ecb6`:

```
 .../bfg-d/33-fix-contract-r8.md   |  29 ++++++
 .../bfg-d/34-seat-report-r8.md    | 116 +++++++++++++++++++++
 tests/test_evidence_night.py      |   8 +-
 tests/test_night_kinds.py         |  10 +-
 tests/test_run_night.py           |  10 +-
 5 files changed, 169 insertions(+), 4 deletions(-)
```

Findings, each read from the full diff, not the stat:

- **Tests-only, plus the two process records.** No file under `joulewise/`, `scripts/`, `configs/`, `protocol_v3.json` changes. Pin proof `git diff --stat cab01506 -- <ruled pin list>` is empty on this HEAD (run by me).
- **No assertion or expected value changed.** Every hunk is one of: (a) a new `self.assertTrue(battery_float_fixture.install_user_site_runner(home), ...)` line, (b) adding `"HOME": str(home)` to an env patch dict that previously set only `PATH`, (c) an added `from tests import battery_float_fixture` import, (d) in `test_run_night.py` the no-courier case, replacing the literal `str(root / "home")` with the same path held in a local `home`. The four removed lines are the pre-edit forms of (b) and (d). No `assertEqual`/`assertIn`/expected literal was touched.
- **The fixture is the existing mechanism.** `install_user_site_runner` and `_USERCUSTOMIZE` exist verbatim at aa5d8c8c (`git show aa5d8c8c:tests/battery_float_fixture.py`, lines 57 and 78; introduced in cf3ba566 / 4d99d2aa). Round 8 adds no code to the fixture module. The mechanism writes a `usercustomize.py` into the user-site of a fake HOME; a child Python started with that HOME wraps `battery_float.observe` so that a call with `runner=None` reads the float capture instead of the host. An explicitly injected runner is passed through untouched, so charging/malformed refusal tests keep their meaning.
- **No production bypass.** The gate code is unchanged. The hook lives only in a per-test temp HOME. Its failure directions are safe: if the child cannot import `tests`, the hook no-ops and the child reads the real probe (fails toward refusal, never toward bypass); if the interpreter disables user site (a venv), `install_user_site_runner` returns False and the new `assertTrue` fails the test loudly rather than silently reading the host. The `home` in `test_night_kinds.py` is under `FIXTURE`, which is a `TemporaryDirectory` (line 187), not a tracked path. Working tree was clean before and after my test run.

## Task (2): test run

`python3 -m unittest tests.test_night_kinds tests.test_battery_float_consumers`, run once, foreground, this worktree:

```
........................
----------------------------------------------------------------------
Ran 24 tests in 76.210s

OK
EXIT=0
```

The larger six-module runs were not rerun here, per charge. The seat report records both required runs: normal, `Ran 637 tests in 1493.729s / OK (skipped=14)`; and from a /tmp copy with `IOREG_BATTERY_ARGV` pointed at `/nonexistent/bfg-d-r8-ioreg` (V3 shows the edit), `Ran 637 tests in 1488.924s / OK (skipped=14)`. The second run is the Linux simulation the contract demanded and is the evidence that the child-process seam is actually reached. The seat's one failed check (V6, orphan census) is a sandbox `ps` permission error, non-blocking, and the lead is to rerun it; it does not bear on this diff.

## Task (3): battery refusal tests still assert refusal

Repo-wide grep for tests asserting a battery refusal, with the round-8 diff on each file:

- `tests/test_night_agent_install.py:1938` `test_battery_not_at_float_refuses_install_validation_before_render`: injects the charging and malformed captures explicitly by patching `battery_float_fixture.runner`, asserts exit 3 and `"battery not at float"` in errors, then asserts the float capture renders with exit 0. File untouched by round 8 (empty diff).
- `tests/test_arm_readiness_evidence_t0.py:2867/2903` charging case expects `"battery not at float"`. File untouched.
- `tests/test_evidence_night.py:1040` and `:2206`, `tests/test_run_night.py:353` (the CR-smuggle refusal tests): drive the production runners through `smuggling_run`; their bodies are outside every round-8 hunk. The only `test_evidence_night.py` hunk is `PrepareTests.setUp` at line 326.
- `tests/test_night_gate.py:1637` charging refuses at c3: untouched.

The user-site hook only substitutes the runner when `runner is None`, so none of these explicit-runner assertions can be satisfied by the float fixture by accident.

## Ruling on 3453ecb6: MERGE, with the PR-body conditions below

The round-8 change is a correct, minimal hermeticity fix: it makes the three modules independent of the host battery without touching the gate, without weakening any assertion, and by reusing a mechanism that was already reviewed into the tree. The seat's forced-missing-probe run is the right proof for the hosted-CI failure signature.

Conditions, all on the PR body and the lead's own rows, none on code:

- **C-1.** Rows 7 and 10 currently read `RUN aa5d8c8c`. They must cite `3453ecb6` and this record (`42-fable-final-head-3453ecb6.md`) once it is on the docs branch.
- **C-2.** Row 11 is the real Linux proof. The `quick` job on 3453ecb6 (run 36248024296) was still pending at the time of this ruling; it must be green before merge. The `gate-ledger` job on this head fails only because rows 9, 11 and 12 are `NOT-RUN`, which are the lead's post-review items, not a defect in the diff.
- **C-3.** The body should carry one sentence naming round 8: tests-only hermeticity fix for battery-less hosts, no assertion changed, contract `33`, seat report `34`.

Non-blocking observation for the record: the `usercustomize` hook silently no-ops on `ImportError`. The direction of that failure is toward the real probe, so a broken hook can only produce a spurious refusal (as hosted CI just did), never a spurious pass. That is the right way round for a science gate and needs no change.
