ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["scripts/run_night.py", "scripts/install_night_agent.sh", "tests/test_run_night.py"]

# WO-2 fix round 4 — night driver (D-169 stage 1), under cold-gate ruling D1

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `66e496a5`). Linked worktree: do NOT
commit, rebase, or push. `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only `python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d
tests.test_night_gate` (expected 88 OK before you start). NEVER spawn a real
chain, a real `claude`, `launchctl`, or `git push`. Avoid the substring `t3`
in anything you create.

Authority: `docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md`
(read it in full first; the three seat outputs beside it explain why). The
ruled cures are C1, C2, C3 exactly as written there — nothing else. In
particular: NO marker-protocol change, NO new file in the night dir, NO
change to any post-completion dead-man branch, NO `night_gate` change.
Evidence standard is EXECUTED: every new regression test is run against a
TMPDIR copy of `66e496a5` (`git archive 66e496a5 | tar -x -C
$TMPDIR/prefix`, copy the new test file over) and its failing assertion
line is pasted into the report.

## C1 — blocker: dead-man completion-epoch stand-down (cures luna D1 + Q4)

`scripts/run_night.py`:
- Hoist `t0 + window_max_s + COURIER_DEADLINE_S` (today inline at ~`:1039`
  in `run`) into one module-level helper, e.g.
  `_completion_epoch_s(plan: NightPlan) -> float`, and use it at BOTH the
  run-path overrun predicate and the new dead-man guard. The overrun
  predicate's behaviour must not change (existing boundary tests stay
  green untouched).
- In `dead_man()`, AFTER the `courier.sent` early return and BEFORE
  `_resolve_courier_bin` / `_courier_lock_is_live`: if
  `time.time() < _completion_epoch_s(plan)`, call
  `_append_log(custody_root, "dead-man fired before the night's completion epoch <int epoch>; standing down")`
  and `return EXIT_GO`. Nothing else is written or spawned on that path.
- Tests (fake clock via `unittest.mock.patch("scripts.run_night.time.time")`
  or however the existing dead-man tests fake time — follow the file's
  pattern):
  1. Empty night dir, clock = `t0 + 1` → rc `EXIT_GO`; the night dir's
     entry set is unchanged except `night.log`; no `subprocess.Popen`, no
     `subprocess.run`, no `os.killpg` call; `night.log` gained exactly one
     line containing "standing down".
  2. Same at clock = completion epoch − 1.
  3. Clock = completion epoch exactly → the pre-existing absent-marker
     behaviour runs (census → durable record → courier attempted); assert
     on the same observable the existing absent-marker test uses.
  4. The D1 scenario: EMPTY `chain.started`, no `chain.exited`, clock =
     `t0 + 2` → stand-down (no `chain.exited` written, no courier). The
     same fixture at clock = completion epoch → round-3 behaviour
     (`chain.exited` with `launch_failed: true`, courier, no `killpg`).
  Pre-fix execution: tests 1, 2, 4(first half) must FAIL on the
  `66e496a5` copy; paste the lines.

## C2 — should-fix: installer refuses the dead-man hour

`scripts/install_night_agent.sh`: after the existing range checks
(`:26-28`) and after `DEADMAN_HOUR`/`DEADMAN_MINUTE` are read (`:54-57`;
move the read earlier if needed), refuse `(( hour == deadman_hour ))` with
exit 2 and a stderr line of the form
`refusing --hour H: it is the dead-man hour (DEADMAN_HOUR=H); arm the night in another hour`.
Test: mirror the existing installer refusal tests (they run the script with
a fake `--launchctl-bin`; see `tests/test_run_night.py` around lines 237
and 470) with `--hour` = the driver's `DEADMAN_HOUR` → rc 2, message
present, and NO plist rendered. Pre-fix: the same invocation renders and
exits 0 — paste the evidence.

## C3 — should-fix: installer refuses a stale night dir

The installer already exits 3 on `chain.started` without `chain.exited`
(`:~119`). Extend that check: exit 3 (same class) if the plan's
`custody_root/night/` contains ANY of `receipt.json`, `result.json`,
`refusal.json`, `chain.started`, `chain.exited`, `courier.json`,
`courier.sent` — a plan is armed against a fresh custody root, never over a
previous night's records. Message names the offending file(s). Keep the
`--uninstall` path working on a dirty dir (uninstall must never be refused).
Tests: (1) `courier.sent` alone present → rc 3, nothing bootstrapped;
(2) `--uninstall` with the same dir → rc 0 and both `bootout`s reached.
Pre-fix: (1) exits 0 — paste.

## Mutants you must run (TMPDIR copies of your fixed tree) and kill

(a) delete the C1 guard; (b) `<` → `<=` in the guard; (c) guard on
`plan.t0_epoch_s` instead of the completion epoch; (d) remove the C2 hour
check; (e) remove the C3 stale-record check. Failing test name per mutant
or SURVIVED (a survivor means strengthen the test until it dies).

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`). Table:
item → file:line of the cure → test name → EXECUTED pre-fix failure line.
Mutant table. Test counts (88 → N) and exact commands. Under 80 lines
after the envelope.
