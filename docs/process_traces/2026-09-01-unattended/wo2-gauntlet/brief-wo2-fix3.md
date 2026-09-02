ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["scripts/run_night.py", "tests/test_run_night.py", "tests/test_gen_g2_phase_d.py", "joulewise/night_gate.py", "tests/test_night_gate.py"]

# WO-2 fix round 3 — night driver (D-169 stage 1)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `224b2295`). Linked worktree: do NOT
commit. `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only `python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d
tests.test_night_gate`. NEVER spawn a real chain, a real `claude`,
`launchctl`, or `git push`. Avoid the substring `t3` in anything you create.
`joulewise/night_gate.py` is in scope ONLY for adding one name to
`NIGHT_DRIVER_REASON_CODES` (+ its coverage in `tests/test_night_gate.py`).

A terra xhigh delta re-audit (report
`.../scratchpad/out/130-terra-wo2-delta2.md`) of fix round 2 ruled
FIX-ROUND. Authority for every cure stays
`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(R-7, §8 d.3). This round's evidence standard is EXECUTED, not reasoned: for
every new regression test, run it against a TMPDIR copy of `224b2295`
(`git archive 224b2295 | tar -x -C $TMPDIR/prefix`, then copy the new test
file over) and paste the failing assertion line into the report.

## Blockers

F3 — **A chain `Popen` failure loses the night.** `scripts/run_night.py:385`:
an `OSError` (ENOENT, EMFILE, EACCES) from `subprocess.Popen` is raised
AFTER the O_EXCL `chain.started` claim and BEFORE `_complete_chain_start`,
so the night ends with a zero-byte `chain.started`, no `chain.exited`, no
result, no durable push, no courier — and the dead-man then reads the empty
marker as a live chain and refuses the courier too. Cure:
- Wrap the `Popen` in `try/except OSError`. On failure: complete the marker
  honestly (`chain.started` gets `{"pid": null, "pgid": null, "epoch_s",
  "launch_error": "<class>: <text>"}`), write `chain.exited` with
  `{"exit_code": null, "launch_failed": true, "epoch_s"}` so the dead-man's
  "chain has exited" reading is true, then the ordinary refusal path with a
  NEW driver code `night_chain_launch_failed` (add it to
  `NIGHT_DRIVER_REASON_CODES`, sorted position, comment in the same style),
  durable record, courier, non-zero exit (`EXIT_REFUSED` or a distinct code —
  say which and why).
- The dead-man must treat a `chain.started` whose `pgid` is null or whose
  file is empty/unparseable as NOT a live chain: with `chain.exited` present
  it proceeds to courier; with `chain.exited` absent it writes
  `chain.exited` `{"reaped_by": "dead-man", "launch_failed": true, …}` and
  proceeds. Never `killpg` on a null pgid.
- Tests: (1) `Popen` raising `FileNotFoundError` → `night_chain_launch_failed`
  refusal validates under `validate_refusal`, `chain.exited.launch_failed is
  True`, courier attempted, push attempted, rc non-zero; (2) dead-man over a
  fixture with an EMPTY `chain.started` and no `chain.exited` → couriers, no
  `killpg` call; (3) the same with a null-pgid marker.

F1 — **The overrun boundary has no equality regression.** `run_night.py:985`
`if completion_epoch_s >= deadman_epoch_s:` — the mutant `>` survives all 84
tests. R-7 says the completion epoch must PRECEDE the dead-man hour, so
equality is a refusal. Test: a plan whose
`t0 + window_max_s + COURIER_DEADLINE_S == dead-man epoch` exactly (compute
the dead-man epoch with the driver's own `_next_deadman_epoch`, then set
`window_max_s` so the sum lands on it) → `night_plan_overruns_deadman`;
the same plan with `window_max_s - 1` → proceeds past the predicate (assert
on the next observable step, e.g. the chain `Popen` being called with a
fake). Show both the `>` mutant and the `<=`-on-the-inverse mutant die.

## Should-fix

F4 — **The courier wait sleeps across the dead-man epoch.**
`run_night.py:576-584`: the `time.sleep(1)` inside the wait loop is
unconditional, so at `stop_epoch_s - 0.3` the loop sleeps 0.7 s past the
hand-off point while holding `courier.lock`; the dead-man can then refuse
`night_courier_running` instead of sending. Cure: sleep
`min(1.0, deadline - now, stop_epoch_s - now)` clamped at 0, and re-check
both bounds before sleeping. Test: fake clock (`time.monotonic`/`time.time`
patched) at `stop_epoch_s - 0.3` → the loop returns without sleeping past
the epoch (assert the sleep argument ≤ 0.3, or that the recorded sleeps sum
to < 0.3).

F2 — **Report honesty on three round-2 tests.** Terra showed that
`test_identity_date_equals_the_full_reviewed_reconstruction`
(`tests/test_gen_g2_phase_d.py:59`),
`test_chain_exit_is_recorded_before_the_first_durable_publish` and
`test_living_chain_records_a_thirty_second_census` (`tests/test_run_night.py:666,680`)
PASS on the pre-fix body — they are guards on already-correct behaviour, not
cures. Do NOT rewrite them. Instead prove each guards what it claims by
running the named mutant against a TMPDIR copy of `224b2295`: (a) append one
line to the emitted chain → the reconstruction test fails; (b) move the
`chain.exited` write after the first `_durable_record` call → the ordering
test fails; (c) set `CENSUS_INTERVAL_S = 31` and the census count to skip
one round → the census test fails. Paste the failing assertion for each. If
a mutant SURVIVES, strengthen that test until it dies.

## Not in this round
Nothing else. No refactors; no new files.

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`). Table:
item → file:line of the cure → test name → the EXECUTED pre-fix failure line
(or the mutant's failure line for F2). New registry code listed. Test counts
before/after (84 → N) and exact commands. Under 80 lines after the envelope.
