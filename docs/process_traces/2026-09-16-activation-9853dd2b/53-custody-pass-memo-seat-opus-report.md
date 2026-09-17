# CUSTODY-PASS-MEMO-01 implementation seat — Opus 5, 2026-09-17 07:45–08:20 PDT (branch feat/2026-09-17-custody-pass-memo from main c9589525)

Brief: record 50. Verbatim report:

CUSTODY-PASS-MEMO-01 — COMPLETE. No NEEDS_SCOPE, no NEEDS_RULING. Worktree `/Users/edr/code/JouleWise-wt-memo` on `feat/2026-09-17-custody-pass-memo`, 10 modified files, all inside WRITE_SCOPE, nothing committed (lead commits by pathspec). No canonical root, no launchctl, no network, no bytecode in the tree.

## What landed, per brief item

**1. The memo (`joulewise/calibration_ledger.py`).** `CustodyDeadline.__init__` gains three fields (`:1956` `custody_passes`, plus `custody_memo_armed` / `custody_memo`) and four methods: `arm_custody_memo` `:1974`, `clear_custody_memo` `:1984`, `custody_memo_covers` `:1990`, `record_custody_memo` `:2006`. The memo is `(physical ledger head digest, frozenset of (attempt_id, absolute locator, sorted artifact-name→sha256 pairs))`. `next_operation()` `:2020` deliberately does NOT carry memo, armed flag or pass counter (comment says so). Reuse happens in `bounded_custody_reasons` `:2280`, which re-derives the required entry set from the snapshot on every call, reuses only at `:2311` when armed + digest equal + required ⊆ verified, otherwise sends the worker request and increments `custody_passes` `:2315`; only a pass with zero refusal reasons records a memo `:2320`. An unkeyed memo (no head digest) is refused outright, so it can never be un-invalidatable.

**2. Wiring (`scripts/validate_powermetrics_fiducial.py`).** `arm_custody_memo()` is called immediately after `writer_lease.acquire()` `:1544` (before `AFTER_WRITER_LEASE`), so the pre-lease preflight pass can never seed it. New `_release_writer_lease()` `:1455` clears the memo then releases; it replaces all three `writer_lease.release()` sites (begin's except, abandon, finalize). `_begin_once` snapshots the count at `:1658` into `custody_preparation_passes` `:1439`, and the success receipt gains `"custody_passes"` `:2695`.

**3. Constant and docs.** `WRITER_CUSTODY_PASSES = 2` (`joulewise/night_agent_install.py:667`), `CUSTODY_HEADROOM_FACTOR = 1.5` unchanged `:672`; the comment block now derives 2 from the memo and states that the repaired-ledger third pass is exactly what the 1.5 buys. Runbook §1.2 rewritten (custody memo defined before use, lease-arming rule, head-digest invalidation, T ≤ 40 s, worked case T = 90 s → 180 s of a 120 s allowance) and the healthy-night paragraph now names `custody_passes`; §1.4's launchd-probe paragraph now says T ≤ 40 s at a constant of 2. `docs/process/NIGHT_HANDBACK.md` multiplier text updated to 2 / T ≤ 40 s with the mechanism in three sentences. `docs/contracts/calibration_ledger_append.md` gains a full section **"The under-lease custody memo"** `:665` — custody pass and T defined first, the forcing problem with the real 90 s case, the entry/key definitions, the three reuse conditions as a numbered list, what "armed" means and its two contractual consequences, the repair 2-vs-3 arithmetic, and an explicit "what the memo does NOT cache". The receipt section documents the new field.

**4. Nothing else touched:** reservation, launchd probe, budget marker, `probe_custody` gateway, and every measurement/gate/claim constant are unchanged.

## Regressions and their base failure (base = `c9589525`, measured by restoring the three production files and re-running; working copies restored and re-verified afterwards)

New class `UnderLeaseCustodyMemoTests` in `tests/test_calibration_ledger_custody.py:1018` (7 tests, ~3 s, real `CustodyFixture` — committed historical ledger, 3 custody-bearing observations, real custody-worker subprocesses):

- (a) `test_healthy_slot_reads_the_corpus_twice_not_four_times:1056` — the writer's four sweeps over one allowance produce exactly 2 byte-reading passes. Plus the **real writer CLI** check: `tests/test_validate_powermetrics_fiducial_derivation_only.py:758` asserts `receipt["custody_passes"] == 2` inside `_assert_custody_timing_receipt`, so every healthy derivation capture in that module is a pass-count regression. Base: `KeyError: 'custody_passes'`. Independent base measurement (same fixture, counting `_bounded_custody_request` calls across the writer's four sweeps at `c9589525`): **4 worker requests, 3 observations each** — the defect, measured, not inferred.
- (b) `test_a_repair_that_mutates_the_ledger_forces_one_honest_re_read:1123` — real `repair_calibration_ledger` abandoning a torn uncommitted record between two under-lease passes. Before the repair the head digest is unchanged and the memo answers (P = 2); after it, the digest moves and the next pass re-reads. The re-read is **proven**: a governed artifact is corrupted at the same moment, so a digest-blind memo would report a sound corpus. Base: `AttributeError: arm_custody_memo`.
- (c) `test_a_pre_lease_pass_never_feeds_an_under_lease_pass:1078` — unarmed preflight pass, then a byte change to `events.jsonl`, then arm: the under-lease pass reports `calibration_ledger_custody_invalid` and the count rises to 2. It also pins that a refused pass records no memo (third pass re-reads). Companion `test_releasing_the_lease_ends_reuse:1106`.
- (d) `test_an_append_by_another_writer_invalidates_the_memo:1166` — a real second process (the reservation CLI) appends to the same ledger between two armed passes; the digest moves, the memo dies, corruption injected at the same time is caught.
- (e) `tests/test_run_night.py:2802` pins `WRITER_CUSTODY_PASSES == 2` and `CUSTODY_HEADROOM_FACTOR == 1.5`; the admission boundary at `:2828` now spells `budget/(2×1.5) = 40.0` s admitted, `×1.001` refused. Base: `AssertionError: 2 != 4` and `Refused: … 40 s x WRITER_CUSTODY_PASSES 4 x 1.5 exceeds custody_budget_s 120 s`.
- (f) receipt timing fields still read the PREPARATION allowance (`custody_elapsed_s`, `observations`, and now `custody_passes` all snapshotted at `:1658`); the existing two-slot receipt test still passes, including `observations` 0 → >0 across slots.
- Two extra soundness pins: `test_a_new_operation_starts_disarmed_and_uncounted:1192` (abandon/finalize inherit no reuse) and `test_reuse_needs_every_entry_the_pass_requires:1206` (different expected hash = different entry; superset forces a real pass; unkeyed memo refused).

Counterfactual run summary at `c9589525`: memo class 7/7 ERROR, `NightProbeTests` 1 failure + 1 error, writer-CLI receipt test ERROR.

## Verification (all on the final tree)

- `tests.test_validate_powermetrics_fiducial_derivation_only` — Ran 23 in 153.9 s, OK
- `tests.test_validate_powermetrics_fiducial` — 12 in 6.6 s, OK; `tests.test_powermetrics_fiducial` — 75 in 61.5 s, OK
- `tests.test_calibration_ledger_custody` — 58 in 37.4 s (39.1 s in the tier), OK; `tests.test_calibration_custody_worker` — 12 in 1.6 s, OK
- `tests.test_run_night` — 128 in 36.3 s, OK; `tests.test_night_agent_install` — 57 in 617.7 s, OK; `tests.test_install_night_agent` — 60 in 48.9 s, OK
- `tests.test_calibration_writer_crash_matrix` — 20 in 237.9 s, OK
- `tests.test_authentication_io` — 22 in 0.9 s, OK, "KILLED 3 renderer AST mutations"
- `PYTHONPYCACHEPREFIX=/tmp/memo-pycache python3 -m compileall -q scripts joulewise` → rc 0
- `QUICK SUMMARY tier=quick modules=153 excluded=83 failures=0 seconds=85.108 result=PASS`
- `git status --short`: exactly the 10 ` M` entries; `git diff --stat`: 10 files, 551 insertions, 72 deletions. No `__pycache__`/`*.pyc` left in the tree.

## One judgement call the lead should confirm

Brief item 4(a) asked for a pass counter observable through the real writer CLI. I made it a production field rather than a test-only seam: the success receipt now carries `custody_passes`, documented in the contract and runbook. It is genuinely load-bearing — a night's own record of the count `WRITER_CUSTODY_PASSES` asserts, so a future change that adds a sweep back shows up in a real receipt instead of only in a constant. I checked it breaks no pin: `documented_keys` covers only `screen_basis` and `acceptance_preflight`, and no consumer in `scripts/` or `joulewise/` validates the writer receipt's key set. `tests/test_authentication_io.py` needed the anticipated line-pin refresh only (eight `calibration_ledger.py` entries, all +101).

Also worth naming for the review packet: the memo is armed for the whole lease, including through the capture, but no whole-corpus pass runs on that allowance after `_begin_once` (finalize and abandon take `next_operation()`), so there is no window in which a stale memo can be consumed.
