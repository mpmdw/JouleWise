# Bench root cause — local IdleAdmissionCoreVerdictTests failures, consistent with macOS Low Power Mode timer slack (attribution pending the powermode-0 toggle, ruling 44 C3) (magistrate 2145630c, 2026-09-09 ~05:58 PDT)

Executed at the bench in `/Users/edr/code/JouleWise-wt-idle-rc` (detached at origin/main 83ab38ed) after the Astra xhigh root-cause
seat (41) located the derivation but was blocked from executing the fixture by its read-only sandbox.

## Mechanism (all measured this session)

1. The seat's single-test diagnostic (42-bench-diagnostic-idle-admission.out) shows the post-idle capture raising
   `subprocess.TimeoutExpired` for the FIXTURE process `tests/fixtures/fake_powermetrics_process.py -n 100 -b 0 -i 50 …` after
   **17.5 s** (`_capture_timeout_s` = max(15, 100 × 0.050 × 1.5 + 10) = 17.5 s, `joulewise/adapters/powermetrics.py:1468–1470`).
   The producer then stores `idle_drift: {status: unknown, reason: post_idle_unavailable}`, while the strict validator re-derives a
   `bounded` envelope (0.9927 W) from the 94 samples the fixture did manage to write → the two strict problems
   `idle_drift does not match pre/post raw sentinel derivation` / `idle_drift_bound_w does not match effective drift derivation`
   → `strict_valid = False` → the shared helper's assertion fails in all four tests.
2. Why the fixture is slow: `time.sleep(0.05)` measured **0.1769 s** mean (20 iterations) and `time.sleep(0.01)` **0.0717 s**; the
   fixture alone (`/usr/bin/time -p`, same argv) took **real 18.58 s** for 100 samples at a 50 ms interval — over the 17.5 s timeout.
3. Machine state co-occurring with the slack: `pmset -g custom` → **AC Power: powermode 1** (macOS Low Power Mode; Battery Power:
   powermode 0); the machine is on AC (`pmset -g batt`: 'AC Power', 100 %). Load average 1.75 (idle). The step from 'powermode 1 is
   set' to 'powermode 1 causes the slack' is inferred from co-occurrence, not from a toggle (ruling 44 Q4.1); a system-wide
   timer-coalescing cause for background-QoS process trees is not excluded. (`kern.timer.coalescing_enabled: 1` is the macOS
   default and is not evidence either way.)
4. Nothing in either PR touches this path: `git diff --stat 58d9225b..83ab38ed -- . ':!docs' ':!*.md'` = tests/test_gen_state.py only;
   PR #308 adds docs + kernel + two lines in tests/test_gen_state.py (the ID and the count 156 → 157); PR #309 touches night_gate/run_night and their tests. The failures reproduce
   identically alone (71-test class) on 5d13d0e6 (PR #308 head) and 5db38b58 (main + PR #309) — logs 39-*.log — and for one of
   the four on main itself 83ab38ed (single-test diagnostic, 42-bench-diagnostic-idle-admission.out; the cold judge re-ran it) — and CI (ubuntu, Python 3.11 and
   3.14) passes every test shard at both heads.
5. Yesterday's record 99gm (5636 tests rc 0 on this machine at 58d9225b) is consistent with Low Power Mode having been OFF then, or
   with the fixture running under a less coalesced timer while an interactive user was at the console; this session did not
   establish when powermode 1 was set (no system-log hits for the bounded predicate). Changing it is `sudo pmset` — Ed's.

## Why this matters beyond the test (recorded for the cold gate, not ruled)

- A REAL night under powermode 1 would run the real `powermetrics` capture with the same 1.5×+10 s timeout; if the real sampler
  slips the same way the post-idle capture fails → `post_idle_unavailable` → strict-invalid members. And the machine's power
  behaviour under Low Power Mode is a different state from the calibration corpus. Proposal for a lane (bookkeeping, design later):
  night preflight / arm readiness records `pmset -g custom` powermode and refuses or flags powermode 1.
- Test-side: the fixture timeout couples the suite to wall-clock timer behaviour; a cure would be a fixture-aware timeout or a
  fixture that does not sleep. Not this PR's.

## Exact tails

- Replay alone at 5d13d0e6: `WORKERS SUMMARY shards=4 modules=221 tests=5636 failures=4 errors=0 skipped=108 failed_shards=4
  result=FAIL` / `rc=1` (38-replay-308-5d13d0e6-tail.txt).
- Class alone at 5d13d0e6: `Ran 71 tests in 154.947s` / `FAILED (failures=4)` / rc=1 (39-idle-admission-alone-5d13d0e6.log).
- Class alone at 5db38b58: `Ran 71 tests in 153.215s` / `FAILED (failures=4)` / rc=1 (39-idle-admission-alone-5db38b58.log).

## Addendum (2026-09-09 ~06:35 PDT, after cold gate 44 + Opus refuter 45) — attribution WITHDRAWN to "unknown slack; flaky coupling"

- Process note first: this file was amended in place at 06:04 (the judge's Q4 wording corrections) after the judge's ruling was
  written and while the refuter was reading; the packet hash pinned only files 43/44. Both are recorded as defects of this gate's
  assembly (refuter 45 over-statement 6); a post-hoc hash of P1–P6 plus 44/45 is in `44-coldgate-packet-P1-P6-posthoc.sha256`.
  Future amendments to packet files are dated addenda, never in-place edits.
- The refuter (45 R1) re-ran the failing single test on the same tree with powermode 1 still set: `Ran 1 test in 24.890s / OK`; the
  fixture measured 18.94 s and 11.58 s two minutes apart. The Low Power Mode attribution is therefore withdrawn: the machine state
  co-occurs, the slack drifts (2.1×–3.6×) and its cause is not established. What IS established: a knife-edge 3.5× timeout margin on a
  sleeping fixture (lane FIXTURE-TIMEOUT-WALLCLOCK-01).
- Magistrate re-runs of the full 71-test class alone in-process on 5d13d0e6 after the refutation (39b-*.log): attempt 1 `FAILED
  (failures=4)`, attempt 2 `FAILED (failures=4)`, attempt 3 `FAILED (failures=3)` — variable, consistent with flakiness near the
  margin; the refuter's cheap green-before-merge condition was NOT met in three attempts.
- "Alone" in this file and in 38/39 means alone in-process; the replay ran four shards concurrently and the rest of the machine's
  state was not recorded (refuter over-statement 3). `failed_shards=4` in the replay tail is the LIST of failing shard indices
  (`scripts/shard_tests.py:853–858`, comma-joined indices, "none" when empty), i.e. shard 4 only; shards 1–3 passed.
