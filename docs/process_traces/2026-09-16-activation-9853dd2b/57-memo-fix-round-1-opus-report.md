# CUSTODY-PASS-MEMO-01 fix round 1 — Opus 5, 2026-09-17 08:55–09:22 PDT

Brief: record 56. Verbatim report:

CUSTODY-PASS-MEMO-01 fix round 1 — COMPLETE. No NEEDS_RULING. Worktree `/Users/edr/code/JouleWise-wt-memo`, branch `feat/2026-09-17-custody-pass-memo`, nothing committed (lead commits by pathspec). 10 modified files, all inside WRITE_SCOPE; no untracked files, no bytecode in the tree, no writes outside the worktree and `/tmp`.

## Item 1 — lease overclaims replaced, accepted trade stated (SHOULD-FIX)
All three named sites plus three sibling overclaims of the same class that the refuter's list did not enumerate but that repeat the false guarantee: `calibration_ledger.py` `arm_custody_memo` docstring and `bounded_custody_reasons` docstring, `validate_powermetrics_fiducial.py::_release_writer_lease` docstring and the arm-site comment (`:1539`), plus the custody test docstring at `test_releasing_the_lease_ends_reuse`. Every one now says what the lease actually does: an advisory `flock` on the ledger's lock sidecar that every calibration writer takes before appending, so while it is held no other **calibration writer** can append to that ledger — and explicitly not that it locks the governed artifact files. A repo-wide grep for `no other process|every other process|freezes|no other writer` over the six touched files returns nothing.

New contract paragraph **"What the memo stops seeing, and why that is accepted"** (`docs/contracts/calibration_ledger_append.md`) names probe P1's scenario in full (corrupt a governed file after the under-lease sweep, head digest unchanged → readiness gate and slot validation answer from the memo; the four-pass writer would have refused `calibration_ledger_custody_invalid`), then the three facts that make it acceptable: sub-second window (one recovery step plus two sweeps), D-161 operator-only threat model, and fail-closed downstream via the next slot's unmemoized preflight. The runbook and the ledger comment point at that section rather than restating it.

## Item 2 — M1 survivor killed (SHOULD-FIX)
`CustodyDeadline.next_operation()` now calls `self.clear_custody_memo()` on the SOURCE as its first statement (before the successor is constructed, so a `WINDOW_EXHAUSTED` raise still leaves the source cleared — fail-closed). `_release_writer_lease` keeps clearing whatever `self.custody_deadline` holds. Two regressions in `tests/test_calibration_ledger_custody.py`:
- `test_releasing_the_writer_lease_clears_the_allowance_it_holds` (new) — real `_CaptureLedgerLifecycle` with a stub lease and no filesystem: after `_release_writer_lease()` the allowance has `custody_memo is None`, `custody_memo_armed False`, the stub saw exactly one `release()`, and the lifecycle still holds the same deadline object.
- `test_a_new_operation_starts_disarmed_and_uncounted` (extended) — asserts the source held a memo before the handoff and is disarmed/memo-less after.

Counterfactuals (mutation applied in the worktree, single module rerun, file restored and SHA-256-verified byte-identical afterwards):
- M1 (drop `clear_custody_memo()` from `_release_writer_lease`) → `FAILED (failures=1)`, `AssertionError: ('aaaa…', frozenset({('attempt', '/private/tmp/…/runs/member', (('m.json','bbbb…'),))})) is not None` at the new test. **Now killed.**
- M8 (drop the clear from `next_operation`) → `FAILED (failures=1)`, `AssertionError: True is not false` at `test_a_new_operation_starts_disarmed_and_uncounted`.

## Item 3 — LEAD RULING installed: `WRITER_CUSTODY_PASSES = 3`
Constant changed with a rewritten comment block that names BOTH worst cases (repair moves the head digest; corrupt corpus = preflight + refused under-lease + refusing re-read, citing the pinning test by name) and says why 3 is counted rather than absorbed by the margin: a slot that is going to refuse must reach its typed `calibration_ledger_custody_invalid` instead of being cut off by `calibration_ledger_custody_timeout`. `CUSTODY_HEADROOM_FACTOR = 1.5` unchanged, its comment now scoped to growth/uneven cost only. Gate boundary: 120/(3×1.5) = 26.67 s.

Tests: `test_run_night.py:2802` pin → `assertEqual(3, …)`; boundary test `:2828` spells `budget/(3 × 1.5)`, pins `custody_budget_s == 120.0` and `assertAlmostEqual(26.667, limit, places=3)`, admitted at the limit (production float `limit*3*1.5 == 120.0` exactly, verified) and refused at ×1.001. Counterfactual at the old constant (`WRITER_CUSTODY_PASSES = 2`): `FAILED (failures=2)` — `Refused not raised` at the boundary plus `3 != 2` at the pin.

Prose sites updated to 3 / T ≤ 26.67 s: runbook §1.2 (memo paragraph, the corrupt-case paragraph, the headroom paragraph, worked case now 90 × 3 × 1.5 = 405 s > 120 s — the old text said "two passes … 180 s"), runbook §1.4 (`:1953`), `NIGHT_HANDBACK.md` ("at most `WRITER_CUSTODY_PASSES` … 3 today … T ≤ 26.67 s"), and the contract. The healthy receipt count stays 2 everywhere (`custody_passes` assertions and the real-CLI pin unchanged); wording that implied the constant EQUALS the receipt count now says the constant BOUNDS it, in the ledger comment, the writer's receipt comment, the derivation-only assertion message and the contract.

## Item 4 — contract first-use nits
"custody-bearing observation" is now built at first use (a finalized ledger record — standalone attempt or one finalized bracket slot — naming a custody locator and each governed artifact's SHA-256). "Armed" is defined in its own paragraph BEFORE the numbered list, which now reads "the memo is armed" with no forward pointer. Two recording rules documented: same-head-digest passes UNION their entries (different digest replaces outright), and a pass whose allowance carries no head digest records nothing because an unkeyed memo could never be invalidated. A matching code comment sits at the union branch.

## Verification (final tree)
`tests.test_calibration_ledger_custody` 59 in 38.2 s OK · `tests.test_validate_powermetrics_fiducial_derivation_only` 23 in 153.0 s OK · `tests.test_run_night` 128 in 37.1 s OK · `tests.test_authentication_io` 22 in 0.9 s OK ("KILLED 3 renderer AST mutations"; its eight `calibration_ledger.py` line pins refreshed +20) · `tests.test_install_night_agent` 60 in 48.2 s OK · `tests.test_night_agent_install` 57 in 617.5 s OK · `compileall -q scripts joulewise` rc 0 · `QUICK SUMMARY tier=quick modules=153 excluded=83 failures=0 seconds=59.578 result=PASS` (the tier re-ran `test_calibration_ledger_custody` on the final tree). `git status --short`: exactly the 10 ` M` entries. `git diff --stat`: 10 files, 294 insertions, 129 deletions.

## NEEDS_SCOPE (informational — nothing blocked)
Refuter finding 5 remains: `TASK_QUEUE.md` row A223 (two copies, `:848` and `:1046`) and `docs/process/state_kernel.json` `:1395`/`:1405`/`:1415`/`:1421` still read "WRITER_CUSTODY_PASSES = 4 … lowers it to 2 … T ≤ 20 s … not started". Both are outside my WRITE_SCOPE and now contradict the landed constant of 3; they must move with the merge.
