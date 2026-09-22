# BENCH-REPLAY-START-DRIFT-01 fix round 1 — seat report

Worktree `/Users/edr/code/JouleWise-wt-replay`, branch `feat/2026-09-22-bench-replay-start-drift`,
base `3e299b85`, head `9e7061be`, tree clean, nothing pushed, no commit rebased or amended.
20 items, 21 commits (item 4 needed a correction commit). Diff vs base: 7 files, +1100/-74.

## Items 1–8 (cold gate #3 rebuttal ruling 18)

1. **§Q1 C1 (MATERIAL)** `quiet_predicate_campaign.py:775-784` — `except OSError` body replaced by the
   ruled text: `asserted` + reason FIRST, then the unlink inside its own `try` appending
   `; stale session.json.tmp not removed: …`. R-C1 (`tests/test_quiet_predicate_campaign.py:1898`):
   `os.replace`→OSError("disk full") + `Path.unlink`→PermissionError; returns False, both failures in
   the reason, session bytes unchanged. KILL: unlink-first/no-guard → `PermissionError: immutable`,
   `Ran 8 tests, FAILED (errors=1)` → restored `Ran 8 tests, OK`.
2. **§Q2 C2 (MATERIAL, test-only)** `tests/…campaign.py:1443-1453` — under
   `patch.object(campaign, "CLEANUP_BUDGET_RESERVE_S", 10)`, both `attestation_timeout_s(PROTOCOL)==10`
   and `…({**PROTOCOL,"slot_pitch_s":603})==5`. KILL: body → `return ATTESTATION_TIMEOUT_FLOOR_S` →
   `AssertionError: 5 != 10`, `Ran 7, FAILED (failures=1)` → `Ran 7, OK`.
3. **§Q3 C3 (MATERIAL) — DEVIATION + NEEDS_RULING.** (i) done as dictated:
   `test_a_gap_under_six_seconds_pushes_every_spawn_late_by_six_minus_gap` (…campaign.py:1467),
   pitch 603 + scaled 2 s bar, teardown spending its 1 s budget and the query its 5 s bound
   (`attest_burn=5`) → `start_drift_abort` row and REFUSED at envelope 02, rc 2, one collector spawned;
   it replaces `assertIn("start_drift_abort_s", PROTOCOL)`. (ii) the dictated docstring wording
   ("the overrun ACCUMULATES") is DISPROVEN by execution: the collector's deadline is absolute
   (`sample_quiet_predicate_evidence.py:1019`, `deadline = scheduled + duration_s`), so a late spawn
   captures less and still ends at its scheduled end. Probe `/tmp/replay-fr1/probe_accum.py`, same
   harness: pitch 603 → drifts `[0.0, 3.0]` then abort; pitch **605 → `[0.0, 1.0 × 11]`, twelve slots,
   NO abort**; pitch 610 → all 0.0. The docstring (`campaign.py:635-655`) therefore states the measured
   behaviour (per-slot `6 − gap`, not compounding, detected at envelope 02 when it exceeds
   `start_drift_abort_s`, otherwise left to `start_drift_max_s`), and the 5 s-gap half is pinned in the
   same regression. **NEEDS_RULING:** the magistrate may prefer the ruled wording verbatim.
4. **§Q3 C4 (NIT) — DEVIATION + NEEDS_RULING.** The dictated
   `assertIn("network_time_unattested", v["excluded"])` is RED as written:
   `AssertionError: 'network_time_unattested' not found in ['incomplete_interior_support']`. With
   `session.json` unlinked, `pilot_summary` fails its own read and `continue`s with the interior
   exclusion before reaching the attestation state, so that list is the only one printed. Committed
   verbatim first (`1f64e223`, red), then corrected (`2b1be7da`) to the specific list
   (`["incomplete_interior_support"]` + `joules is None`) — still killing the vacuous
   `assertTrue(all(...))` C4 rejected — with the attestation verdict pinned on the journal row
   (`asserted` × 12) as the test's own comment says.
5. **§Q3 C5 (NIT)** `campaign.py:484-489` — the clause claiming `log show` resolves a fold-ambiguous
   string as Python does is deleted; the docstring now says it is not established.
6. **§Q3 C6 (NIT)** `tests/fixtures/qpe01_pilot_n1_20260922/SOURCES.md` — both syslog fixtures with
   digests `dba7fb7c…` / `da1b28ef…`, lines 191 / 1, windows 02:10:00–04:35:00 and the zero-match
   minute 10:48:40–10:49:40, the `timed_log_argv` capture shape, provenance activation 59857fe5
   record 07c, and why the compact capture is kept as a negative fixture.
7. **C7 (NIT)** `campaign.py:1292` — `network_time_attestation_reason` on the envelope journal row;
   pinned in `test_a_night_whose_annotations_cannot_land_still_finishes` (12 rows carry
   `session rewrite failed: PermissionError: read-only envelope`).
8. **C8 (NIT, pre-existing)** `campaign.py:775` — handler widened to `(OSError, ValueError)`;
   `test_C8_a_NaN_in_the_session_record_asserts_the_envelope_not_the_night`. KILL: back to
   `except OSError` → `ValueError: Out of range float values are not JSON compliant: nan`,
   `Ran 9, FAILED (errors=1)` → `Ran 9, OK`.

## Items L1–L5 (lane contract lens, record 17a)

- **L1 (S1)** `campaign.py:967-977` — `power is None` (the provenance-refusal path) no longer counts as a
  replay; a power record that exists and is not `powermetrics` (including a non-dict) still refuses.
  `test_L1_a_real_night_with_a_power_null_envelope_is_not_a_replay`: rc 0, outcome complete, status not
  REPLAY_NEVER_EVIDENCE, envelope 07 excluded `clock_anchor_unresolved` alone, retained 11. The R5
  no-key variant now asserts a power DICT lacking the key. KILL: the 3e299b85 read →
  `'REPLAY_NEVER_EVIDENCE' == 'REPLAY_NEVER_EVIDENCE'`, `Ran 9, FAILED` → `Ran 9, OK`.
- **L2 (S2)** `campaign.py:1330-1338` — `execute` also refuses (outcome refused, `replay_recorder`, rc 2)
  when the EXECUTOR's environment carries `EVIDENCE_POWER_RECORDER_REPLAY`.
  `test_L2_a_replay_night_that_wrote_no_session_still_refuses`: summary INCONCLUSIVE, no
  `replay_recorder_envelopes`, rc 2, twelve drift rows intact. KILL: point deleted →
  `'complete' != 'refused'`, `Ran 10, FAILED` → `Ran 10, OK`.
- **L3 (N2)** `campaign.py:1085-1110` — the replay override blanks every energy number (per-envelope
  joules/combined/interior, sizing and adjacent pairs, all spread statistics, block-two), and the prose
  says so; the schedule-side diagnostics stay. Pinned inside R5.
- **L4 (N3)** `test_L4_the_drivers_own_guards_each_refuse_what_they_name` — faked `launchctl`
  (label named / census exit 1 / clean machine), faked `git` (dirty tree / wrong sha / clean),
  `write_outputs` refusing the ruled artifact suffix and writing under any other name, plan-id prefix +
  bench root via a real `execute_bench` stopped at `build_plan`, and the custody-root refusal.
- **L5 (N1/N4)** `sample_quiet_predicate_evidence.py:928-955` — `ReplayRecorder.finish` reads K and the
  basis back from the sidecar into `session.power.replay`; unreadable sidecar costs the annotation only.
  `markdown()` states that `auto` writes live-looking dates with provenance only out-of-band.
  `test_L5_…`: null at construction → 36497 after finish; unreadable → null + reason; `none` → 0.
  KILL: K not assigned → `None != 36497`, `Ran 7, FAILED` → `Ran 7, OK`.

## Items X1–X7 (lane execution lens, record 17b)

- **X1 (B1, BLOCKER)** `bench_replay_start_drift.py:320-345, 361-364, 544` — third status `ESCALATE`,
  printed in the headline, `main()` → 3 (FAIL 1, PASS 0, 2 stays the refusal code).
  `test_X1_…`: chain 0.4 / session 0.7 on slots 1,3 → ESCALATE, `**ESCALATE**` in the markdown, rc 3;
  counterfactuals in the same test give PASS/0 and FAIL/1. KILL: split falls through to PASS →
  `'PASS' != 'ESCALATE'`, `Ran 11, FAILED` → `Ran 11, OK`.
- **X2 (B2, BLOCKER)** `bench_…:291-306, 340-352` — `ADMISSIBLE_SLOT` (`collector_exit 0`,
  `cleanup_proven`, `anchor_status bounded`, `interior_complete_support`), defects named in
  `slot_defects` and the statement; `--smoke` exempts the anchor/interior pair only and the smoke
  artifact says why. `test_X2_…` names all four defects; twelve anchor-unresolved slots PASS under
  smoke, FAIL without. KILL: admission filtered on False → `'PASS' != 'FAIL'`, `Ran 12, FAILED` → OK.
- **X3 (S1)** `campaign.py:955-983` — the session is read and CHECKED before the
  `incomplete_interior_support` continue. `test_X3_…`: twelve `replay` sessions, `rounds.jsonl` absent,
  variable NOT set → REPLAY_NEVER_EVIDENCE, rc 2. KILL: check moved behind the continue →
  `'INCONCLUSIVE' != 'REPLAY_NEVER_EVIDENCE'`, `Ran 13, FAILED` → `Ran 13, OK`.
- **X4 (S2)** `replay_powermetrics_frames.py:128-146, 189-196, 243` — `source_sha256()` digests the whole
  file in its own pass before pacing; `source_frames` digests nothing; sidecar records the scope.
  `test_X4_…` builds a source LARGER than the 1 MiB read chunk (700 frames, ~1.2 MB — the 3-frame
  fixture is one chunk and cannot show the defect) and TERMs mid-file. KILL: digest folded back into the
  pacing pass → `'ef736eb9…' != '8eea85b7…'`, `Ran 8, FAILED` → `Ran 8, OK`.
- **X5 (S3)** `bench_…:307-316, 352-355, 424-435` — `BENCH_ATTESTATION_STATES`; `slew_attested` and
  `authenticated` alike, `asserted` (or anything else) a named defect, smoke included; the artifact
  states the bench never turns network time off and that the walls are live-log-with-slews costs.
  `test_X5_…` covers `asserted`/None/"unknown". KILL: branch disabled → `'PASS' != 'FAIL'`, FAILED → OK.
- **X6 (S4)** R9 rebuilt from environment COPIES (arm-side raise with the key present; scrubbed copy for
  the thirteen child environments), and `FrozenExecutorTests.exercise` now runs every night under a
  scrubbed copy of the shell environment. Executed both ways: clean shell `Ran 125, OK`; and
  `env EVIDENCE_POWER_RECORDER_REPLAY=… Ran 125, OK` (before: red on `test_L1_…`/`test_R5_counterfactual_…`).
  KILL: arm-side `patch.dict` removed → `ValueError not raised`, `Ran 14, FAILED` → `Ran 14, OK`.
- **X7 (NIT)** `campaign.py:1318-1324, 1380-1382` — `evidence_outcome.recorder_kind` is `replay` when the
  environment says so OR any session read said so (pinned in `test_X3_…`); wall-clock tolerances
  widened (`feed` 2.6 → 3.5 s, cadence delta 0.08 → 0.25 s) with comments naming the load sensitivity.

## Exit contract

`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_uncertainty_evidence
tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign tests.test_run_night`
→ **Ran 490 tests in 248.303s — OK** (final run, quiet machine).

Two earlier runs of the same command each hit ONE timing-sensitive failure, both characterized and
neither caused by this branch (which touches no `run_night` production or test path):
`LoadTests.test_load_join_ladder…(exit_delay=60)` `-9 != -15` — reproduced identically at the base
`3e299b85` (`git archive` snapshot, same command); and
`WindowDeadlineTests.test_a_grandchild_that_ignores_sigterm_is_killed_and_still_proven`
(`SIGKILL not found in [SIGTERM × 14-19]`) — green with `tests.test_run_night` alone (231 tests, OK),
green in the third full run, absent at base. Both are real-signal / wall-clock races.

## Smoke (one real run, at head `9e7061be`)

`launchctl list | grep joulewise.night` → empty (exit 1) before the start; tree clean; load 1.63.
`python3 -B scripts/bench_replay_start_drift.py --archive /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922 --smoke --label-shift auto`
→ status **PASS**, **rc 0**, wall 226.7 s, root `~/night-bench/bench-replay-20260922T203647Z`.

| slot | chain drift s | session drift s | exit | cleanup proven/wall s | attestation/wall s | anchor | interior | tail s | frames | K s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.259 | 0.406 | 0 | True/0.015 | authenticated/0.952 | unknown | False | 0.768 | 254 | 40192 |
| 2 | 0.126 | 0.238 | 0 | True/0.016 | authenticated/0.648 | unknown | False | 0.637 | 255 | 39664 |
| 3 | 0.150 | 0.261 | 0 | True/0.015 | authenticated/0.654 | unknown | False | 0.712 | 254 | 39143 |

`verdict`: max chain 0.259 s, max session 0.406 s, both bars met, `slot_defects: []`,
`smoke_exempt_fields: [anchor_status, interior_complete_support]`, `escalate…: false`.
Markers: summary `REPLAY_NEVER_EVIDENCE` (status and evidence_status), `retained: []`, `s_upper: null`;
outcome `refused` / `replay_recorder`, chain rc **2**; `evidence_outcome.recorder_kind: "replay"`;
`network_time_restored: true`; control argv names the stub twice and neither `/usr/bin/sudo` nor
`/usr/sbin/systemsetup`. Machine 13:36 load 1.66 → 13:40 load 3.18, `pgrep claude` 0 → 0.

**Sidecar digest (X4), live:** for all three slots
`sidecar.source_sha256 == session.power.replay.source_plist_sha256 == shasum -a 256 <source>` is True —
slot 1 is `ef4429b4…`, the value the lens recorded as the TRUE digest against the old partial
`ee01f351…`. Scope string present. **K (L5), live:** `session.power.replay.label_shift_s` = 40192 /
39664 / 39143, equal to each sidecar's K, no longer null.

## Deviations / NEEDS_RULING / unfinished

- NEEDS_RULING 1 — item 3(ii): the ruled "accumulates" wording is disproven by execution; the docstring
  states the measured behaviour instead (both gaps pinned).
- NEEDS_RULING 2 — item 4: the dictated membership assertion is red; the specific exclusion list is
  pinned instead, with the attestation verdict on the journal row.
- Deviation (minor, L5): `ReplayRecorder` now overrides `finish` as well as `__init__` — required to read
  K back from a sidecar that only exists after the feeder exits; the override is `super().finish()` plus
  a `finally` that touches replay-only metadata.
- Nothing unfinished; every item 1–8, L1–L5, X1–X7 landed, one commit each (plus item 4's correction).
