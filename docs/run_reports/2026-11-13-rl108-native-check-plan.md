# RL-108 side branch: remote native-check plan (document only)

NOT FOR MERGE. Branch `sm/2026-11-13-rl108-side`, draft PR against `ops/2026-11-11-w1-presign`. Nothing here has been
run, and nothing is run until a research-lead ruling names the adoption (RL-108 "What an adoption request must bring").
Nothing in this plan is installed on the measurement Mac before that ruling.

## Preconditions (all remote; no physical step)

- The adoption ruling names this branch's head (rebased onto the W1 signing head) and the re-registration it rides
  with (RL-108: earliest a re-registration for another reason between W1 and C1; never between claim windows).
- Custody of the last night has closed: `night-results/<plan>` carries `result.json`; no night label is loaded and no
  night plist is on disk (`launchctl print gui/$UID/com.joulewise.night` absent). SSH only in that state.
- The checkout used is a scratch worktree of the adopted commit under the MBP's lane directory, never the canonical
  root or a night's measurement root, until step N4 (which is the watchdog install itself).
- Every step records the commit, the command and its output under `docs/run_reports/<date>-rl108-native/` on a
  branch of its own, pushed from the Air.

## N1. Exit contract (condition 2): reasons identical natively

- Run the PREQUAL harness's synthetic night on the adopted checkout and on the W1 signing head, in two scratch
  custody roots, with chain scripts that exit 0, 3, 4 and 7 (7 is undeclared for every contract).
- Pass: for each exit code the two `result.json` documents are equal after removing the time fields
  (`started_*`, `ended_*`, `epoch_s`, `monotonic_ns`) and `artifacts` digests; in particular `fault_reasons` and
  `chain_outcome` are equal. The adopted night's `window.journal.jsonl` `ResultWritten` line carries
  `chain_exit.declared` false for 7.
- Abort: any difference in `fault_reasons`; the adoption request is withdrawn.

## N2. One `restore_owed()` (condition 3): host end state on the production state directory

- With the session helper's own High Power entry (the path W1 uses, `align_v4_session.py` writes the host marker),
  run on each checkout in turn: (a) a rerun refusal, (b) an admission refusal (plan declares 2, host set back to 0
  by the helper's restore), (c) the normal close of a 60 s diagnostic chain, (d) `run_night.py dead-man` after (c)
  with `courier.sent` present.
- After each: `pmset -g custom` AC `powermode`, `sudo -n systemsetup -getusingnetworktime`, the host marker and
  `$MEASUREMENT_ROOT/.align-r1-high-power` present or absent, the result's `host_restoration` `ok`/`action`.
- Pass: the four tuples are equal between the two checkouts (the fake-host goldens in
  `tests/test_rl108_side_branch.py` predict them).
- Abort: any difference, or any restore left owed (`restore_owed` deferred) on a path where the signing head
  restored. Recovery: `post_window_unstrand.sh --restore-host` (W-3), which restores through `powermode.restore_owed`.

## N3. Journal (condition 4): no write inside a member

- One native smoke night on the adopted checkout (the RL-35 W1 smoke shape).
- Read `night/window.journal.jsonl`; for every line, compare its `epoch_s`/`monotonic_ns` with every member's start
  and end stamps from the night's own records (timing receipts and the member records' structural stamps; no
  measured value is read).
- Pass: no line lies inside any member's span; the sequence is DriverStarted, ChainOpen, ChainExited, ResultWritten,
  Delivered; `read()` parses it strictly.
- Abort: any line inside a member span. The activity would then have to be listed as an activity during members
  (RL-108 condition 4), which this branch claims is not needed.

## N4. Watchdog transition table (condition 6)

- Before install: confirm the canonical root that the watchdog runs from carries
  `configs/watchdog/transition_table.json` at the adopted digest. A checkout without it holds the watchdog with
  `transition_table: unreadable` (HOLD_UNSAFE): this is the version-skew case the audit names, so the table must
  reach the canonical root together with the watchdog.
- Run W-1's pre-install `watchdog_acceptance` dry run on a rendered plan, then install the watchdog through
  `install_magistrate_watchdog.sh`, then W-1's post-install check.
- Over the smoke window of N3: `events.jsonl` has no `undeclared_transition`; any `dwell_exceeded` or
  `chain_open_past_completion` is explained; `state.json` `dwell` is present and `exceeded` is false at the end.
- Abort: any `transition_table:` hold, or an `undeclared_transition` on an edge the smoke drives.

## N5. Finality field (condition 5)

- Air only. Build the next-arm packet from the committed records of the follow-up night and W1's night with the
  adopted builder, and run `held_window_check` on it.
- Pass: every `window_chain` entry carries `finality`; R1 and any window with no capture are `final`; a window whose
  desk is still running is `provisional`; counts, statuses and the series history row are byte-equal to the signing
  head's packet.

## N6. Trace and closure

- On the Air, on the adopted commit: `python3.13 -B scripts/align_v4_dynamic_trace.py --out <scratch>` (full
  profile), then `tests.align.test_v4_executed_closure` and `tests.align.test_v4_dynamic_closure`. The branch's
  trace was regenerated in the draft PR; it is regenerated again after the rebase onto the signing head.
