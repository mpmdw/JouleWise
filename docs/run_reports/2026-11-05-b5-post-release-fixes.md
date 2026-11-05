# Block-5 post-release fixes preparation — 2026-11-05

User-directed preparation from cached `origin/main`
`92026c1849c0f053e56bdac6110c079211db2c31`, on
`lane/2026-11-05-b5-post-release-fixes`. No fetch or push.

Mission M0 read the generated stop-card/restart and queue views (no active
stop card), the manual do-not-do list, repository instructions and the
D-178/D-188–D-190 authority. Explicit user direction selects this preparation
ahead of the normal lane head. The deferred inventory is
`docs/process_traces/2026-11-04-d188-retrospective/RETROSPECTIVE.md:78`;
`docs/process/TRIM_REPORT.md` and `freeze_by_commit.md` keep integration
after release. Kernel task `B5-POSTRELEASE-FIXES-01` records the work. No
phase-exit checklist matrix exists for this bounded maintenance preparation;
no phase completion is claimed.

## Disposition and commits

| Item | Commit | Disposition |
| --- | --- | --- |
| a | `776003b52` | Step-4 exceptions clean speculative later logs/outputs and reset the counter to the consumed prefix. |
| b | `b3731cb2a` | NEEDS-LEAD; propose per-consumed-member deadline accounting. No code changes because r1 eager accounting is explicitly retained for D-188 equivalence. |
| c | `2c1598c33` | Expire path-bound L3 entries when private bracket copies leave scope, including exceptional exits. |
| d | `407628e43` | Normalize L4 ledger parents only in keys; callables and bypasses receive the original snapshot. |
| e | `711b95173` | G9 uses the driver's exact sidecar-name predicate. |
| f | `df0e71325` | Register five exact step-11 tooling reasons; keep the outcome list intact. |
| g | final commit, `docs(b5): draft non-issuable rows successor and record handoff` | NEEDS-ED decision-log draft only, plus PR draft and session handoff. No successor code or assigned decision ID. |

The plan entry for each item preceded its implementation. The existing
producer, claim engine, verdicts, measurements, registrations and released
evidence were not edited. Item f deliberately changes five error labels from
unclassified to tooling, with public tokens; both states still stop with
exit 2. This is an explicit post-release behavior change. Item b is left
untouched because it could change which refusal wins.

## Changed files

- Runtime: `joulewise/b5_analysis/dry_run.py`,
  `joulewise/b5_analysis/bracket.py`, `joulewise/analysis_verified_store.py`.
- Tooling vocabulary: `configs/analysis/b5/dry_run_refusal_classes.json`.
- Existing tests: `tests/b5_analysis/test_leaf_bracket.py`,
  `tests/b5_analysis/test_sensitivity_guard.py`.
- New focused tests: `tests/b5_analysis/test_postrelease_step4.py`,
  `test_postrelease_bracket_copies.py`, `test_postrelease_bracket_snapshot.py`,
  `test_postrelease_g9.py`, `test_postrelease_step11_codes.py` in that directory.
- Plan/draft/records: `POSTRELEASE_PLAN.md`, `.pr/post-release-fixes.md`,
  `docs/decision_log.md`, this report, `docs/process/state_kernel.json`,
  `RUN_STATE.md`, `TASK_QUEUE.md`.

Advisor-visible scientific state did not change, so `PROJECT_STATUS.md` was
not edited. No delegated sessions, external services or live gates ran.

## Verification

Both `python3 -m pytest --version` and `python3.13 -m pytest --version`
failed with `No module named pytest`. No dependency was installed; the
offline fallback was targeted stdlib unittest modules. All commands below
used `TMPDIR=/private/tmp JOULEWISE_B5_ANALYSIS_WORKERS=2` as an environment
prefix. The new modules spawn no worker pools; the existing modules use
synthetic fixtures. No full suite or block-5 analysis pipeline ran.

| Command | Recorded final result |
| --- | --- |
| `python3 -m unittest tests.b5_analysis.test_postrelease_step4 -q` | 5 passed, 0.009 s |
| `python3 -m unittest tests.b5_analysis.test_postrelease_bracket_copies -q` | 2 passed, 0.002 s |
| `python3 -m unittest tests.b5_analysis.test_postrelease_bracket_snapshot -q` | 5 passed, 0.058 s |
| `python3 -m unittest tests.b5_analysis.test_postrelease_g9 -q` | 2 passed, 0.007 s |
| `python3 -m unittest tests.b5_analysis.test_postrelease_step11_codes -q` | 7 passed, 0.045 s |
| `python3 -m unittest tests.b5_analysis.test_leaf_bracket -q` | 20 passed, 320.250 s |
| `python3 -m unittest tests.b5_analysis.test_vdl_core -q` | 63 passed, 42.640 s |
| `python3 scripts/gen_state.py --check` | exit 0 |

Recorded successful modules total 104 tests and about 6.1 minutes. An earlier
invocation of the bracket module returned a running-session handle that the
tool forwarding did not retain; its completion result is not claimed. The
logged repeat above supplies the evidence. Allowing for that duplicate and
short test corrections, test execution was approximately 12 minutes. The
two existing-module logs are `/private/tmp/jw-b5-postrelease-leaf-bracket.log`
and `/private/tmp/jw-b5-postrelease-vdl-core.log`.

During development, the new cleanup test initially expected a tooling label
for an intentionally unclassified stub refusal, then used an unsuitable
classification stub; both test expectations were corrected without changing
classification code. The first step-11 malformed-record probe called a
nonexistent helper; it was corrected to the actual `_validate_sensitivity`
emitter. All recorded final runs above passed. Lead diff review and scoped
whitespace checks passed. The state generator initially rejected the new
dependencies' sort order; canonical sorting fixed it and the final check
passed. No check produced live or measured-number
validation evidence. No real capture locator or blinded output was opened.

## Delivery limitation and next exact step

The original branch-creation command failed because this sandbox exposes
the checkout's `.git` read-only (`index.lock: Operation not permitted`).
Approval escalation is unavailable. Separate local Git metadata at
`/private/tmp/jw-b5-postrelease-20261105.git` holds the requested branch and
one commit per item. The original `.git` was not modified; the current
working files therefore appear as local changes against the detached base.
The delivery bundle is `/private/tmp/jw-b5-postrelease-20261105.bundle` and
requires the base commit above. No destructive Git operation was used.

Import the bundle into a writable repository to install the branch, then
review `.pr/post-release-fixes.md` after release. Do not use this tree for
the ongoing release analysis. Independent executing review, CI, the cold
pass and an authorized integration-suite run remain unperformed; the PR
draft keeps those gates NOT-RUN.

Open rulings are exactly item b's future accounting policy (NEEDS-LEAD) and
item g's successor design/version/custody/blinding contract (NEEDS-ED).
Item c is deliberately a cache-lifetime repair, not relocatable L3 reuse;
path-sensitive failure messages still prevent a global path-free change.
Item a does not redesign cleanup for a dispatch that fails before returning
child results. No real-data equivalence or release readiness is asserted.
