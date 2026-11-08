# R11 delta6 — independent Sol review seat 1

**Verdict: HOLD.** F1 is a plausible functional failure: a contention-only
harvest exclusion still prevents the next arm, including C1 after W1. F2
misreports the required balance disclosure. No production fix is included.

Reviewed 2026-11-08 on branch `align/2026-11-08-r11-delta6-sol1`, candidate
`c742e5722`, delta `356c41c82..c742e5722`. Authority: `origin/main:RUN_STATE.md`
items 234 (R22), 235 (R23), 236 (R24), and 238 (R24 correction), plus the
v4 protocol and deviations. Timing-receipts implementation/merge content was
excluded from this review. This is an independent review, with no further
delegation or peer consultation.

## F1 — HOLD: contention still excludes through the common desk and full-desk gate

**Failure scenario.** An otherwise valid W1 member acquires only
`contention.request_overlap` (the same path applies to
`contention.unmeasured`). The common harvest retains that EXCLUDE_MEMBER
code. R22's v4 thermal adapter correctly removes it from the thermal member,
but the original common-desk member stays excluded. The desk becomes
`instrument_incomplete`, and the packet cannot pass its required full desk
before C1. This contradicts R22-1's disclosure-only rule; it needs no
malformed record, score-dependent choice, or inaccessible hardware assumption.

Two surviving paths must be addressed together:

1. `scripts/align_pilot_session.py:327-338,363-393` derives common member and
   summary exclusions, `registered_eligible_members`, exclusion-derived checks,
   and `harvest_status` from the unfiltered harvest list.
   `scripts/align_v4_session.py:319-328` normalizes a separate thermal record;
   it does not normalize those common members. Its `full_desk_gate_pass`
   (`:189-208`) neutralizes charging-only exclusions, so contention still makes
   `no_member_exclusions` and `chain_eligibility` fail.
2. `scripts/align_v4_next_arm_packet.py:415-419` rejects
   `harvest_status=members_excluded` before considering even a passing
   `full_desk_gate`. Fixing the native gate alone is therefore insufficient.

**Executed witnesses:**
`test_f1_contention_only_must_not_fail_the_native_full_desk_gate` starts with a
passing readable synthetic member; adding only contention flips the gate to
false. `test_f1_committed_contention_only_harvest_must_not_reblock_the_arm`
starts with a ready synthetic committed W1, then reproduces the native desk
status above: `member_eligibility=pass`, `full_desk_gate=fail`, packet not
ready. It also checks that changing only the explicit gate to true still
fails `desk_passes`.

**Required repair:** apply v4's effective exclusion policy to the common desk
members, summaries, eligibility reports and exclusion-derived checks, and
reconcile the effective harvest status with the packet reader. Retain all raw
codes as disclosure and preserve real non-contention exclusions. Do not
change the shared policy for the sealed studies.

## F2 — fix required: the balance check drops disclosed contention events

**Failure scenario.** A benign member has one contention-overlap code and a
60-second unmeasured gap. `v4_contention.attach` correctly moves the two codes
to `contention.disclosed_codes` and leaves the member eligible. Immediately
afterwards, `powermode_desk_check` calls the balance check.
`joulewise/align/apple/v4_balance.py:26-27` counts only top-level `flags` and
`calibration_exclusions`, so its benign event total is **0 instead of 2**.
The per-condition/per-pair rates and exposure-adjusted expectations can
therefore conceal a condition imbalance. The individual disclosure survives;
the required R22-3 comparison does not reflect it. This is not an independent
arm blocker.

**Executed witness:**
`test_f2_balance_must_include_contention_after_it_becomes_disclosure_only`
passes the actual `disclose` and `attach` output to `balance_check`, replacing
only bundle acquisition with a synthetic source. Both disclosed codes are
present, exclusion is false, and the balance event count is zero.

**Required repair:** include the disclosed contention events in the balance
input/counting policy, avoiding duplicates already represented by flags.

## Nonblocking documentation correction

`docs/align/pilot_protocol_v4.md:1037` and
`docs/align/squeeze/fanout/r11-dispositions.md:181` retain the earlier claim
that a larger cap lowers gate-admitted FPR under drift. Item 238 corrects
that result for the registered T-after-stop calendar: C14 raises it by
0.03–0.17 percentage points at b=.05, while C14 remains admitted. A reader
using these documents receives the opposite drift-sensitivity disclosure.
Update the disclosure; this does not justify HOLD by itself. I did not
rerun or independently validate the simulation.

## Checks that survived

- Frozen manifest SHA-256 is unchanged:
  `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`.
  The bytes equal the generator output. Every older manifest window,
  including T1–T3, is unchanged; reserve indices are exactly 100–147 per
  pair, eight per window C9–C14. This verifies preservation/allocation,
  not a new independent paired seed audit.
- Synthetic committed U3 failures and non-GO/nonzero-exit terminal records
  bar the whole captured window and zero its calibration contribution.
  Rewriting the working-tree terminal result cannot remove the committed bar.
  An asserted bar or score/count field outside the owning evidence creates
  no bar.
- Six structural bars consume C9–C14 in order. Skipping a reserve refuses;
  eight admitted windows finish calibration. Low m after eight is
  `insufficient_calibration` and cannot arm C9. A seventh structural bar
  makes eight unreachable; a seventh zero-capture bar escalates.
- A U5 inconclusive alone does not require escalation sentinels, while a
  U4 inconclusive does, in both the packet roster and thermal consequence.
  This conclusion concerns the inconclusive trigger changed in this delta;
  it does not claim that all pre-existing U5 FAIL consequences were removed.

## Verification and handoff

Only `tests/align/test_r11_delta6_sol1.py` and this report were added.
Coordination state and frozen manifest bytes were not edited. All fixtures
are synthetic; no measurement pipeline, model download, network, real
restricted/custody path or hardware collection was used. Tests ran one
module per process, sequentially. No full suite was run, as instructed.

- `python3.13 -B -m unittest tests.align.test_v4_replacement_windows`:
  **20 tests OK**, 39.594 s.
- `python3.13 -B -m unittest tests.align.test_r11_delta6_sol1`:
  **11 tests, OK (expected failures=3)**, 31.218 s. Those three are explicit
  desired-behavior regressions for F1's two sites and F2, not fixed behavior.
- `python3.13 -B -m unittest tests.align.test_v4_next_arm_packet`:
  **32 tests OK**, 391.172 s.
- `python3.13 -B -m unittest tests.align.test_r1_turn_counts_export`:
  **13 tests OK**, 5.405 s, including the injected inside/outside batch hours.
- An undecorated replay of just the three finding witnesses:
  **3 intended assertion failures, 0 errors, exit 1**, 8.296 s. It confirmed
  the failures occur at the intended assertions, not during fixture setup.
  Reproduce without editing the file:

  ```sh
  python3.13 -B - <<'PY'
  import unittest
  from tests.align.test_r11_delta6_sol1 import Delta6Witnesses
  names = [name for name in dir(Delta6Witnesses) if name.startswith('test_f')]
  for name in names:
      delattr(getattr(Delta6Witnesses, name), '__unittest_expecting_failure__')
  suite = unittest.TestSuite(Delta6Witnesses(name) for name in names)
  result = unittest.TextTestRunner(verbosity=2).run(suite)
  raise SystemExit(0 if result.wasSuccessful() else 1)
  PY
  ```

- `git diff --check`: passed. Aggregate test runtime was 475.685 s
  (under eight minutes). Git-reading verification used local objects only;
  the last four invocations set `GIT_NO_LAZY_FETCH=1`,
  `GIT_CONFIG_GLOBAL=/dev/null`, and `GIT_CONFIG_NOSYSTEM=1`.

**Next exact step:** lead dispositions/fixes F1 across both desk layers and
F2's balance input, removes the three `expectedFailure` decorators, then
reruns this witness module and the focused desk/packet tests. No new MLX
code/tests were introduced; these witnesses require no native MLX run.
Live collection/Metal validation and simulation reproduction remain outside
this synthetic review. No ruling question blocks describing the two failures.
