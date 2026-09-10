# 61 — Seat S5 (Claude Opus) report: derivation night-chain skeleton + issuer `check`

Lane ACCEPTANCE-EPOCH-25G83-01. Worktree `/Users/edr/code/JouleWise-wt-s5-chain-watch`,
branch `feat/2026-09-10-epoch-s5-chain-watch`, on top of WIP `554d5a12` (partial Astra
seat) over main `7c4366ec`. Authority: cold-gate ruling 46 §R-b V5, §R-c, §R-d row S5,
addendum 11 A-8. Nothing committed, pushed, checked out, stashed, or reset; the diff is
left in the worktree. Canonical, the rehearsal checkout, and `/Users/edr/night-custody`
were not written to (one read-only `ls` of canonical's ledger path, cited below).

WRITE_SCOPE honoured exactly:
`scripts/issue_calibration_acceptance_generation.py`,
`scripts/night_chains/calibration_derivation_only.zsh`,
`tests/test_issue_calibration_acceptance_generation.py`.
`git status --short` shows those three files modified and nothing else.
Per the amended brief item (3), `docs/process/MAGISTRATE_WATCHDOG.md` was NOT edited.

## Verification (verbatim)

Command, run from the worktree root, rc captured in a variable:

```
$ python3 -m unittest tests.test_issue_calibration_acceptance_generation tests.test_docs_freshness
........................................................
----------------------------------------------------------------------
Ran 56 tests in 28.912s

OK
UNITTEST_RC=0

$ zsh -n scripts/night_chains/calibration_derivation_only.zsh
ZSH_RC=0
```

25 tests in the seat module (19 before this seat), 31 in `tests.test_docs_freshness`.
Baseline `tests.test_docs_freshness` alone was already green before any edit (31 tests, OK).

Live desk watch on this machine, run from this worktree:

```
$ python3 -B scripts/issue_calibration_acceptance_generation.py check ; echo rc=$?
Desk epoch watch (identity comparison only; no capture authorization)
ACTIVE acceptance: d079_calibration_acceptance_v2_n17_r6
field                  expected            observed                                  status
os_build               25F84               25G83                                     MISMATCH
hardware_model         Mac15,9             Mac15,9                                   match
powermetrics_sha256    unavailable         b762e5bf…21330c5                          MISMATCH
mlx_version            unavailable         unavailable                               MISMATCH
ledger: calibration_ledger_missing, calibration_ledger_rollback
mismatched fields: os_build, powermetrics_sha256, mlx_version
rc=3
```

(columns compressed here for width; the tool prints 64-char fields). The
`os_build 25G83` vs `25F84` mismatch the brief requires is reported, and rc is 3.

`git diff --stat`: 3 files, 369 insertions, 81 deletions.

## What the WIP had wrong

The Astra WIP was further along than "untested" suggests — all 19 of its tests passed
unmodified on first run. The defects were these.

1. **BLOCKER (chain): the window-exhaustion test judged startability, not
   completability.** The WIP aborted only when a slot could not *start* before
   `WINDOW_END_EPOCH_S`. A capture takes ~480 s (ruling 46 V3's own arithmetic budgets
   8 min for the last capture: `10 + 11×10 + 8 = 128` of 210 min). A slot starting at
   `WINDOW_END − 60` would therefore run 420 s past the agent-free window end — the
   night overruns its own [QUIET-MAC] boundary and the next window's admission. Fixed
   with `SLOT_CAPTURE_BUDGET_S` (default 480), checked both before the cadence wait and
   again after it. Two defect-shaped regressions, mutation-probed below.
2. **Chain shape was not parallel to the G2-a chain, which the brief requires.** No
   `timestamp()`, no `settle()`, and no operator-log line at any lifecycle transition —
   an aborted or stopped night left no on-disk trace of where it stopped. Added
   `timestamp()`/`settle()`/`log_event()` following the runbook's rendered chain
   (`docs/phase_2/window_runbook.md:1548-1560,1636,1727`, pinned by
   `scripts/gen_g2_phase_d.py`), writing to
   `$WINDOW_CUSTODY_ROOT/operator_logs/derivation-chain.log`: `chain_start`,
   `settle_complete`, `session_open`, `slot_start`/`slot_end` per slot,
   `slot_unused …reason=window_exhausted`, `session_abort`, `derivation_night_complete`.
3. **Chain bound no ledger or head pin.** The WIP called both
   `reserve_calibration_window_bracket.py` and `validate_powermetrics_fiducial.py`
   without `--ledger`/`--head-pin`, silently taking `DEFAULT_LEDGER_PATH`, which resolves
   relative to whichever checkout the script sits in. The runbook's own reservation and
   `calibrate_slot` pass both explicitly (`window_runbook.md:1413-1414,1587-1588`). Now
   required as `CALIBRATION_LEDGER` / `LEDGER_HEAD_PIN` env and passed to the reserve
   call, the writer call, and (as *global* args, which `recover_calibration_ledger.py`
   requires before the subcommand) the abort call.
4. **PATH-resolved binaries in a governed chain.** Bare `sleep`, `date`, `python3`.
   Now absolute and overridable: `SLEEP=/bin/sleep`, `DATE=/bin/date`,
   `PY=$REPO/.venv/bin/python` (the runbook's interpreter). The test harness injects
   fakes through those variables and sets `PATH=/bin:/usr/bin`, so any bare command left
   in the chain would reach the real one and hang rather than be silently intercepted.
5. **`$RUNS_ROOT/instrument_validation` was never created** although the writer's
   `--output-root` points into it (the runbook `mkdir -p`s it). Added, alongside the
   operator-log root.
6. **Watch: `sysctl` was PATH-resolved.** `subprocess.run(["sysctl", …])` in a tool whose
   entire job is to report this machine's true identity. Now `SYSCTL_PATH =
   Path("/usr/sbin/sysctl")`, asserted in the test.
7. **Watch: `acceptance["identity_epoch"]` was a bare subscript.** An acceptance the
   loader authenticates but that lacks the key raised `KeyError` at the desk instead of
   refusing. Now part of the same fail-closed guard, with a regression.
8. **Chain input validation logged before it validated** (once logging was added), so a
   bad `SLOT_COUNT` would have created custody directories and a log line before exiting
   64. Validation now precedes every `mkdir` and every log write; the regression asserts
   both the call list and the operator log are empty on a 64.

Reviewed and deliberately kept as the WIP had them:

- Unknown-vs-unknown counts as a mismatch (`mismatched_fields`), so `mlx_version`
  unavailable on both sides refuses rather than passing. Correct under D-161: this is an
  evidence refusal, not an operator-adversary refusal.
- The last ledger row is not silently replaced by an older row when it lacks
  `t1_bindings`; the watch reports unavailable instead. Correct — substituting would
  compare against a T1 vector nobody pinned.
- Ledger/pin/acceptance authentication failures exit 3 with a named reason rather than a
  distinct code. Fail-closed and within "exit 3 on mismatch naming the fields".
- The settle precedes the reservation, per the brief's explicit order (see open item O-1).

## What I added

Chain (`scripts/night_chains/calibration_derivation_only.zsh`, 70 → 170 lines,
mode 644 → 755 to match every other executable chain/script in `scripts/`):
completability budget; `timestamp`/`settle`/`log_event`/`abort_window_exhausted`
helpers; explicit ledger and pin binding; absolute injectable binaries; a header that
enumerates the unlanded S1/S2 surface (`--session-kind derivation --slot-count N`,
`--derivation-only`, the per-slot binding list of addendum 11 N2) and keeps the required
"SKELETON: pending S1/S2 flag landing; not to be pinned in a plan until the integration
replay" line first. `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S` default to
600/600/480 and are validated as non-negative integers with `SLOT_COUNT ≥ 1` and
`SLOT_CADENCE_S ≥ 1`. Still: one settle, one session, 600 s start-to-start cadence
anchored to the actual slot start (never compressed to catch up), `set -euo pipefail`,
no probes, no pack, no Git, no claim output.

Tests (19 → 25). New: the live-probe test; the two completability regressions; the
operator-log transition test; the missing-`identity_epoch` refusal; a static guard that
the chain source contains no `git`, no `pack`, no `generate_g2a_probe_inputs`, no
`launch_window`, exactly one `settle` call site, the SKELETON header, `set -euo
pipefail`, and an executable bit. The chain harness now returns the operator log
alongside the call list, and asserts the single 600 s settle precedes the reservation and
that the eleven later sleeps are the 120 s cadence remainders after a 480 s capture.

**Live-probe test (brief's "only if deterministic here").** It is deterministic, so it
runs for real: `test_live_probes_report_this_machine_against_the_active_epoch` calls the
real `observe_machine()` (real `/usr/sbin/sysctl`, real sha256 of `/usr/bin/powermetrics`)
and the real `check` against a fixture ledger/pin plus the production acceptance, then
asserts every value from the live reading rather than pinning a build string: expected
`os_build` equals the r6 epoch's, observed equals the live sysctl value, and *if* they
differ (they do today: 25G83 vs 25F84) the row reads MISMATCH, rc is 3, and the last line
names `os_build`. It stays green after Ed's next OS update instead of becoming a false
alarm. Skipped off darwin. Confirmed executed, not skipped (`unittest -v`: `… ok`).

## Mutation observations

- Production call site `calibration_derivation_only.zsh` slot loop → completability
  guard. Setting `SLOT_CAPTURE_BUDGET_S` default to 0 (i.e. reverting to the WIP's
  startability-only rule) fails three tests:
  `test_slot_that_cannot_finish_is_never_started` (4 != 3 python invocations — d02
  started),
  `test_first_slot_that_cannot_finish_aborts_with_no_capture` (3 != 2 — d01 started),
  `test_window_exhausted_refuses_next_slot_and_aborts_once` (5 != 4). Restored and
  re-verified (`zsh -n` rc 0, suite OK).
- Production call site `issue_calibration_acceptance_generation.check` →
  `mismatched_fields`: the pre-existing bypass and `WATCH_FIELDS`-omission mutation
  kills carried from the WIP still hold (`test_mutation_kills_check_comparator_bypass`,
  `test_mutation_kills_check_binary_field_omission`) — the second is the one that pins
  A-8's point that the r6 `identity_epoch` carries no `powermetrics_sha256`, so the watch
  must cover the binary from the ledger's T1 vector or a same-build binary swap passes.

## NEEDS_RULING

None. The ruling and addendum resolved every question this seat met.

## NEEDS_SCOPE

None taken. Two items are out of this seat's scope by construction and are recorded for
the lieutenant rather than acted on:

- **The DIAGNOSTIC_NO_PACK plan template** named in ruling 46 §R-d row S5 is not in this
  seat's WRITE_SCOPE and was not written. Ruling 46 §R-d also says no plan is authored
  before the 09-11 rehearsal harvest, so this is correctly deferred, not dropped.
- **Step-0 wiring** stays proposed per addendum 11 A-8; `MAGISTRATE_WATCHDOG.md`
  untouched. The `check` tool is the deliverable.

## Open items for the integration replay (O-1 … O-4)

- **O-1, settle-then-reserve ordering.** The brief and §R-c order the night as settle →
  open session → slots, so that is what the chain does. Consequence worth a decision
  before the plan is pinned: the reservation is a Python process that runs *after* the
  600 s settle and immediately before d01's capture, so d01 alone is preceded by ~seconds
  of machine activity where d02…d12 are preceded by ~120 s of idle. Reserving before the
  settle would make every slot's approach identical. This is a science-shape call, not a
  bench call.
- **O-2, writer flags absent by choice.** The G2-a `calibrate_slot` passes
  `--arm-countdown-s 20 --sleep-display-before-capture`; this chain passes neither,
  because the derivation night has no operator present and no display action to schedule.
  Confirm with seat S1 — if the r6 members were collected *with* the display sleep, parity
  argues for keeping it. Noted in the chain header.
- **O-3, unlanded flags.** `--session-kind`, `--slot-count` and `--derivation-only` do not
  exist in the tree today (verified: `reserve_calibration_window_bracket.py:56-90` has no
  kind/slot-count; the writer's flag inventory has no `--derivation-only`), and the
  reserve CLI still takes the per-slot flags `--pre-attempt-id/--post-attempt-id/
  --pre-custody-locator/--post-custody-locator` as four required scalars (addendum 11 N2).
  Until S2 lands the list shape, the chain forwards those bindings as its own `"$@"`
  ahead of `--execute`. `recover_calibration_ledger.py abort-session --session-id --plan
  --reason` DOES exist today and takes `--ledger`/`--head-pin` as *global* args before the
  subcommand — the chain now spells that ordering correctly.
- **O-4, where `check` must be run.** `DEFAULT_LEDGER_PATH` is `<repo>/runs/
  calibration_observation_ledger.jsonl`, resolved from the script's own location, and
  `runs/` is untracked — so in any linked worktree the watch reports
  `calibration_ledger_missing, calibration_ledger_rollback` (as it does above) and the T1
  half of the comparison is unavailable. Canonical has the file (read-only `ls`:
  `/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl`, 136253 bytes).
  Step-0 runs from canonical, so the proposed wiring is fine; anyone running the watch
  from a worktree must pass `--ledger`/`--head-pin` explicitly. Worth one sentence in
  whatever text proposes step-0 to Ed.
