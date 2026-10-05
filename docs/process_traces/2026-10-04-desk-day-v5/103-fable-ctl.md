FINAL PASS: PASS

Cold final pass on `9b08ecf6` (PR #482) against parent `b2ff2f36`.
Reviewer: Fable 5.1, one foreground session, no subagents, checkout left clean.

No blocker and no high or medium finding. Five low/informational findings
follow the four answers. None of them needs to hold the merge.

## What I ran

- `tests/test_controller_g2b_attachment.py`, `tests/test_controller_battery_float.py`,
  `tests/test_battery_float_consumers.py`, `tests/test_battery_float_sweep.py`:
  40 passed, 36 subtests passed (233 s).
- Neighbours: `tests/test_g2a_calibration_attachment.py`,
  `tests/test_revision_five_b_readers.py`, `tests/test_controller.py`,
  `tests/test_controller_retry_backoff.py`: 95 passed, 22 subtests passed (181 s).
- NOT run: the whole suite (budget). Everything else below is by reading
  `joulewise/controller.py`, `joulewise/battery_float.py`,
  `joulewise/arm_readiness.py` (lineage authenticators),
  `joulewise/calibration_ledger.py` (session status, snapshot),
  `joulewise/bundle.py`, `joulewise/clock.py`, `joulewise/adapters/powermetrics.py`.
- Disclosure: `tests/test_controller.py` contains non-mock-backend members and
  passes no `battery_runner`, so on this Mac those tests may each have made
  single real `/usr/sbin/ioreg` reads (see finding L4). No loop, no
  powermetrics, no sudo, no launchctl, no model.

## Question 1 — can the new route attach anything but the right session's finalized pre slot, or loosen a refused case?

No, on both counts.

- Selection (`joulewise/controller.py:451-459`): the route is taken when
  `<runs_root>/.joulewise-launch-lineage.json` exists OR is a symlink (so a
  dangling symlink selects the route and then fails in authentication instead
  of falling through). Selection grants nothing: the locator is authenticated
  by `authenticate_campaign_launch_lineage` (`controller.py:551`,
  `arm_readiness.py:11356`) — fixed basename, recorded root equals the
  selected root, consumption/start/settle chain, current boot, completion
  ABSENT, sibling claim/bound locators carrying the same lineage.
- Slot identity is checked twice, from two independent readings of the ledger:
  1. session status (`controller.py:560-575`): session id and plan id equal
     the lineage's, plan sha equals the sidecar-authenticated plan tree's,
     kind is bracket (not derivation), state open, `pre` finalized, custody
     `complete`, and the RESERVED locator resolves to the directory given;
  2. ledger snapshot (`controller.py:579-596`): governed open-bracket
     extension, window id equals the lineage's, FINALIZED pre receipt is
     `valid`, not a historical import, its locator resolves to the directory,
     `validation_id` equals the receipt's attempt id, every receipt artifact
     digest equals the bytes about to be installed, every T1 binding equals
     the evidence's.
- Then the capture's own battery pair must authenticate `pass` against
  `{session, "pre", attempt}` (`controller.py:597-601`), and the two raw ioreg
  files that get installed are re-hashed against digests inside the
  receipt-covered `instrument_evidence.json` (`controller.py:604-609`).
- Refusal controls present and passing: foreign session, unfinalized pre,
  post directory with identical bytes, finalized post slot, byte-identical
  copy at a foreign path, derivation-kind session, corrupt lineage with the
  G2-a variable set (no fallback), and no lineage (the old
  `revision_five evidence cannot be attached` refusal still fires —
  `controller.py:460-468` unchanged in effect).
- Loosening check, case by case:
  - no locator, no G2-a variable: still refused (tested);
  - no locator, G2-a variable: G2-a route unchanged;
  - locator present, Revision-5 capture: previously always refused without
    G2-a, now accepted ONLY through the checks above (the intended change);
  - locator present, G2-a variable set: G2-a is no longer reachable; the
    G2-b checks apply instead. Net effect is not weaker for the capture
    (same slot/receipt/binding checks, plus lineage, plus battery), see L1
    for the one member-side difference;
  - locator present, legacy (pre-Revision-5) capture: previously attached
    with no session check, now must pass G2-b. Tightened.

## Question 2 — are the readings outside the sampler lifetime and stamps; can a slow, failing or hung reading delay or alter a measured phase?

Outside: yes. Delay a measured phase: no. Delay the gap before the idle
baseline or before cleanup: yes, bounded at about 10 s.

- Placement (`controller.py:1039-1047`): pre runs after `prepare` completes
  and before `_begin_stage("idle_baseline")`; post runs after
  `idle_drift_sentinel` completes and before `cleanup`. The first sampler of
  a member starts inside `idle_baseline` (`measure_idle`, or
  `begin_admission_window_sampling` at `controller.py:1231-1241`); the last
  one is the sentinel capture, a synchronous `subprocess.run`
  (`adapters/powermetrics.py:1190-1217`) that has returned before the stage
  completes. The measured-window sampler is stopped inside `measured_run`
  (`controller.py:1513`).
- Stamps: the span a reader checks is
  [`stage_started idle_baseline`.monotonic_ns, `stage_completed
  idle_drift_sentinel`.monotonic_ns] (`controller.py:2597-2612`,
  `battery_float.py:1049-1061`). All four numbers (probe before/after, the two
  span ends) come from the same `_clock_stamp(...).monotonic_after_s`, taken
  in program order, so pre.after ≤ span start and post.before ≥ span end by
  construction; `authenticate_pair` enforces exactly that
  (`battery_float.py:934-946`). The measured window's
  `sampling_started`/`sampling_stopped` stamps and the no-I/O stretch between
  them (`controller.py:1477-1509`) are untouched by the diff.
- Slow or hung reading: `subprocess.run(..., timeout=PROBE_TIMEOUT_S=10)`
  (`battery_float.py:323-325`). A hang costs at most ~10 s before the idle
  baseline (pre) or before cleanup (post); neither interval is sampled,
  stamped into a window, or reduced. `preceding_gap_s` grows by the probe
  time, which is the true gap.
- Failing reading: every runner/parse failure is caught inside `observe`
  (`battery_float.py:341-346`); a raw-write failure is caught in
  `_observe_battery_float` (`controller.py:1071-1077`). Neither aborts the
  member (tested: exception, timeout, write failure → member SUCCEEDED).
- Failure path: the salvage reading runs after `stop_sampling` and is
  skipped, with a log line, if either sampler-liveness flag is still set
  (`controller.py:1079-1085`; `_stop_sampling_best_effort` clears the flags
  only on a successful stop, `controller.py:1822-1826`). Tested both ways.
  Two narrow exceptions are in L2.

## Question 3 — does anything stamped, sampled or reduced in a member move?

No.

- `_stage_measured_run` is not in the diff. Marker stamps, the dwell, the
  stop call and trace margins are byte-for-byte as before.
- Additions only: `metadata.json` gains a top-level `battery_float` key
  (every run, mock included); `stage_started idle_baseline` and
  `stage_completed idle_drift_sentinel` gain `monotonic_ns` on non-mock
  backends; two `raw/battery_float.{pre,post}.ioreg` files; and, for a
  non-mock adapter that lacks the drift protocol, a new
  begin/complete `idle_drift_sentinel` event pair with
  `status: "unavailable"` (`controller.py:1571-1575`). The real powermetrics
  adapter implements the protocol, so on the Mac that last item does not fire.
- No reader in `joulewise/` or `scripts/` other than
  `battery_float.authenticate_bundle` consumes `battery_float`, the new
  `monotonic_ns` fields, or the `idle_drift_sentinel` phase name (grep), and
  the reducer does not read them. The one extra clock read per boundary
  happens outside the measured window.

## Question 4 — are failures recorded honestly?

Yes. No path I could construct yields `pass` without two readable, fresh,
in-predicate readings positioned outside a completed span.

- Probe exception or timeout → `probe_error: true`, `passed: false`, reason
  text, empty raw file whose digest matches → reader says
  `battery_float_evidence_missing` (tested).
- Raw write failure → record flipped to `probe_error`/not passed with the
  reason; the reader then finds a missing/short file against a recorded digest
  and raises `CustodyFailure` — loud, never a pass.
- Member failed before the sentinel completed → post is salvaged but the span
  is unavailable → `battery_float_evidence_missing` (tested: "salvage must not
  invent it").
- Sampler teardown failed → no post reading, `post: null`, log line (tested).
- Member died before the pre reading → `{"pre": null, "post": null,
  "not_reached": <stage>}`; mock → `"not_applicable": "mock"`. The reader
  returns evidence-missing for both, which is conservative.
- The stored `passed` flag has no authority: `authenticate_pair` recomputes
  the predicate from the raw bytes (`battery_float.py:923-933`).
- G2-b attachment failures all raise before a bundle directory exists
  (tested for the foreign-session case).

## Findings

**L1 (low) — the G2-b route does not check that the member is a pack member.**
`joulewise/controller.py:551` calls `authenticate_campaign_launch_lineage(runs_root)`
without `config_paths`, and the G2-a registered-member check
(`controller.py:642-651`) has no G2-b counterpart. The writer checks pack
membership only for configs tagged `launch_lineage_required`
(`joulewise/bundle.py:93`). So an untagged config run by hand in a lineage
root during the open window would receive the (correct) pre-slot attachment
and a bundle with no writer-owned lineage. What gets attached is still only
the right slot, so question 1 stands; a harvest that requires bundle lineage
would drop such a bundle. Cheap hardening if wanted: pass the member config
path through, or refuse the route for untagged configs.

**L2 (low) — two edges where a reading can coincide with a leftover sampler
process; neither can produce a wrong `pass` on a measured window.**
(a) An interrupt (Ctrl-C / SystemExit) during `measure_idle` or the sentinel
capture goes to `_finalize_interrupted_run` with both liveness flags false, so
`_salvage_battery_float_post` (`controller.py:1079-1085`) probes while that
capture's process may not have exited. The member is failed and has no
completed sentinel stage, so the verdict is evidence-missing.
(b) If the sentinel capture times out, the exception is swallowed
(`controller.py:1582-1592`), the stage completes, and the post reading runs;
whether the timed-out capture's child has fully exited is not confirmed. The
measured window is already closed and the sentinel itself is recorded
`unknown`, so no measured number is affected, but the pair could still read
`pass`.

**L3 (nit) — a non-ValueError escape.** `controller.py:574`:
`Path(pre_status["custody_locator"])` raises `TypeError` if the open receipt
reserved no locator for `pre`. It still refuses (before bundle creation), just
with a traceback instead of the route's `ValueError`. Evaluation order puts
the `finalized`/`complete` checks first, so this needs a finalized slot with
no reserved locator — unlikely.

**L4 (low, tests) — non-mock controller tests now reach the real probe.**
`_observe_battery_float` uses `subprocess.run` on `/usr/sbin/ioreg` whenever
`battery_runner` is None (`controller.py:1058-1069`). Existing tests that run
a non-mock backend through `run_benchmark` without a runner (e.g. in
`tests/test_controller.py`) therefore make two real ioreg reads per member on
a Mac, and record host-dependent bytes (they still pass: a stale or failed
read never fails a member). Worth a suite-wide stub so unit tests stay
hermetic and never touch the device during a quiet window.

**L5 (info) — scope notes, not defects.**
- The G2-b acceptance test uses the mock backend, so the attachment path and
  the battery writer are each tested, but never in the same run. I found no
  interaction between them by reading.
- `battery_float.authenticate_bundle` has no caller in `joulewise/` or
  `scripts/` at this commit; the harvest-side consumer is not part of this
  change. Its handling of `CustodyFailure` (raised on a failed raw write, see
  question 4) should be per-bundle rather than aborting a whole harvest.
- The route is keyed on the lineage file, not on a "non-claim" marker; any
  launch-lineage root gets it. That matches the stated design; I flag it only
  so the claim-night implication is a known choice.
- The attachment cost per member (status + snapshot + hashing and replaying
  the ~82 MB capture) is paid before the bundle exists, outside every measured
  phase.
- `authenticate_capture` re-reads `instrument_evidence.json` from disk
  (`controller.py:597`) rather than using the already-hashed bytes in memory.
  The installed raw files are bound to the hashed copy at
  `controller.py:604-609`, so only the verdict could differ, and only if the
  file changed between two reads a moment apart.
