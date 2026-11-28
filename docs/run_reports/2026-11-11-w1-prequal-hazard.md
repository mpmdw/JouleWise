# W1 PREQUAL F-6: installed-plan clock budget

Seat: `w1-prequal-hazard`. Branch: `ops/2026-11-11-w1-prequal-hazard`.
Base: `2b60c350d` (`origin/ops/2026-11-11-w1-presign`, PR #734).

## Authority and scope

Mission M0: read the repository agent instructions, playbook preflight,
RUN_STATE stop-card/current-status/workspace/restart sections, queue and
do-not-do-yet pointers, and source-of-truth map. No active stop card.
The user's explicit F-6 brief selects this bounded AGENT repair ahead of
the generated lane head and forbids coordination-state writes. RUN_STATE,
TASK_QUEUE, the state kernel and its tests remain untouched.

Read `git show origin/main:docs/perf/SPEED-TOOLBOX.md`; this is a fixture
correctness repair, with no throughput change, batching or decision cache.
No network, weights download, measurement pipeline or real custody reads.
All exercised plans, records, model bytes and host observations are synthetic.

The requested registration check printed `False`:

```text
python3.13 -B -c "from joulewise.align.apple import v4_registration as r; print('joulewise/align/w1_prequal.py' in set(map(str, r.ARTIFACTS)))"
False
```

## Production path confirmation (before editing the fixture)

The arm's field access is correct for a successfully staged v4 W1 plan:

1. [v4 prepare](../../scripts/align_v4_session.py#L60) selects W1 without
   substituting a later-window kit; lines 73–78 pass `kit.KIT`, `kit.PACK_ID`
   and the `align-v4-` prefix to `pilot.prepare`.
2. [pilot.prepare](../../scripts/align_pilot_session.py#L40) delegates to
   `bytes_h_session.prepare` (lines 40–43).
3. [shared preparation](../../scripts/bytes_h_session.py#L359) builds the
   inputs, calls `plan.write_window_plan` at line 373, and records that
   writer's exact plan path/digest at lines 391–394. Writer failure leaves
   `INPUTS_ONLY`, not a successfully staged/installable plan.
4. [input builder](../../joulewise/b6/plan_inputs.py#L100) obtains
   `T_stream_max_s` from the kit's registered sizing (lines 100–113), and
   obtains thresholds via the production `thresholds` helper (line 115).
   That helper copies registered thresholds, applies `CLOCK_THRESHOLDS`
   and registered sparse overrides (lines 44–53).
5. [writer](../../joulewise/b5/plan.py#L819) reads that stream allowance and
   audits all thresholds against the hazard contract (lines 819–827,
   355–416). Its unconditional `hazard_window` construction includes
   `T_stream_max_s` and `thresholds` at lines 942–945; lines 958–972 emit
   `receipt_class=HAZARD_PACK` and `hazard_window`. It parses the result
   before publishing bytes (lines 976–980).
6. [NightPlan](../../joulewise/night_gate.py#L456) requires the
   `hazard_window` key for HAZARD_PACK (lines 456–461), validates it at
   lines 628–630, and retains it in `HazardNightPlan` (line 644).
   Its validator requires a finite `T_stream_max_s` and all six threshold
   objects, including clock (lines 805–813).
7. [arm preflight](../../scripts/align_v4_session.py#L679) rereads and
   checks the digest of the installed plan, then consumes exactly
   `hazard_window.thresholds.clock` and `hazard_window.T_stream_max_s`
   (lines 679–692). The shared installer uses that same `state['plan_path']`
   and digest ([lines 425–433](../../scripts/bytes_h_session.py#L425)).

Thus this is a PREQUAL fixture defect, not a production plan/arm contract
defect. This confirmation concerns code and planning configuration only;
it makes no statement about any real staged session or measurement.

## Fixture change and regression

`arm_fixture` now carries the clock-budget slice of `hazard_window`:
thresholds come from production `plan_inputs.thresholds`, and the stream
span is the maximum synthetic W1 member duration. That is the production
W1 sizing law ([align_v4_kit.py:1171](../../scripts/align_v4_kit.py#L1171),
1188); values come from the existing planning-only `synthetic_w1_plan`,
not real R1 observations. The clock's sized threshold is replaced with
that same span, as the window writer does. No threshold numbers were
hand-copied. The synthetic plan remains a minimal fixture, not a complete
NightPlan suitable for real installation.

This base already had an unconditional `FakeHost.frequency_check` for both
frequency seams. Consequently, its baseline control was **admitted** and
the original 8-test ArmCliTests class passed; the inherited F-6 failure from
`b4a6c217f` was masked on this base. Merely adding JSON keys would leave
the missing-budget refusal untested.

The arm-CLI probe now uses `FakeHost.frequency_plan_check`: it calls the
real production preflight with an explicit synthetic reader. A private
exception stops at the first native read and supplies synthetic frequency
evidence. Plan byte/digest, t0 and hazard-field parsing therefore run for
the control and every CLI fault, while native probes and host setters
never run. Other probes retain their existing seam; in particular the
smoke harness deliberately uses past-t0 plan copies to isolate other gates.
The test guard still rejects a frequency call without a supplied reader.
This does not validate native clock readings or the subsequent physics gate.

The new `plan-hazard-window-missing` CLI case removes the field and
recomputes `session.json`'s plan digest, isolating missing-budget admission
from changed-byte refusal. Both PREQUAL and unittest require the entire
reason array to equal exactly:

```json
["clock.frequency_plan_invalid: ValueError: plan clock budget unavailable: 'hazard_window'"]
```

An additional test checks the fixture budget against the production
threshold helper and W1 planning durations.

## Red then green

Initial red, before fixture/seam changes:

```text
python3.13 -B -m unittest tests.align.test_w1_prequal.ArmCliTests.test_missing_hazard_window_is_refused_before_installer -v
FAIL: test_missing_hazard_window_is_refused_before_installer
    self.assertNotEqual(out['rc'], 0)
AssertionError: 0 == 0
Ran 1 test in 19.737s
FAILED (failures=1)
```

Focused green after the fix:

```text
python3.13 -B -m unittest tests.align.test_w1_prequal.ArmCliTests.test_missing_hazard_window_is_refused_before_installer tests.align.test_w1_prequal.ArmCliTests.test_synthetic_plan_carries_production_clock_budget -v
test_missing_hazard_window_is_refused_before_installer ... ok
test_synthetic_plan_carries_production_clock_budget ... ok
Ran 2 tests in 18.505s
OK
```

## Verification

Sequential runs only. Baseline first: `tests.align.test_w1_prequal.ArmCliTests`,
8 tests, **OK**, 419.115 s. The baseline and final module use the standard
unittest loader/TextTestRunner in `python3.13 -B -` wrappers so that a
transparent `wp.probe` observer can retain the exact arm-CLI rows. The
observer returns each result unchanged. It also records the deliberately
sabotaged OBC-flag witness; before/after comparison uses only the normal
PASS probe, not that intentionally failing witness.

Actual loader selections in the `python3.13 -B -` wrappers were:

```python
unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromTestCase(test.ArmCliTests))
unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromModule(test))
```

The final full-module invocation ran **once**, against code commit
`dedf958eb`. All **10 ArmCliTests passed**. I interrupted the later
`CadenceTests.test_an_arm_that_keeps_no_rebuild_or_trusts_the_supplied_packet_fails`
while it was inside `check_packet_tamper` / `_arms`, to preserve the user's
approximately 20-minute total test budget and leave time for the required
watchdog module. The module exited **130 (KeyboardInterrupt)**, without a
complete unittest summary. There was no completed failing test before the
interruption. This is **not a passing full-module result**. Its elapsed time
was less than the conservative 687.1 s bound observed immediately afterward
(that bound includes a short post-interruption tool gap).

The complete module still needs a separate run to completion. No full
repository suite was run, per the user's explicit machine-load constraint.
Watchdog results are recorded in the closing verification section below.

## Exact arm-CLI before/after evidence

The normal probe is PASS: one admitted control and 13 refusals before the
installer. Every one of the 13 original case records is exactly unchanged,
including the complete ordered refusal strings, return code, admission
and installer-called fields. Canonical JSON bytes for those 13 rows
(original case order; sorted keys; compact separators) are byte-identical:

`before SHA-256 = after SHA-256 = f6e5ee785758390f02303db5a8f1ef3acf580cd965ecb5add0627618c7fd2c38`

The added missing-budget case has no prior row (`before: null`).

### control

```json
{
  "before": {
    "case": "control",
    "rc": 0,
    "admitted": true,
    "installer_called": true,
    "reasons": []
  },
  "after": {
    "case": "control",
    "rc": 0,
    "admitted": true,
    "installer_called": true,
    "reasons": []
  }
}
```

### plan-hazard-window-missing

```json
{
  "before": null,
  "after": {
    "case": "plan-hazard-window-missing",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "clock.frequency_plan_invalid: ValueError: plan clock budget unavailable: 'hazard_window'"
    ]
  }
}
```

### triage-missing

```json
{
  "before": {
    "case": "triage-missing",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "series_binding: W1: the arm could not rebuild the packet",
      "held_window: unreadable: TypeError: 'NoneType' object is not subscriptable",
      "next_arm_triage: next-arm triage packet missing or wrong schema",
      "next_arm_triage: packet has no numeric valid_until_epoch_s (expiry is mandatory)",
      "next_arm_triage: triage packet needs previous_window as a registered window id (R1, W1, Cn, Tn, Dn)",
      "next_arm_triage: calibration evidence contradictory or malformed: windows must be a sequence in frozen order",
      "next_arm_triage: triage record_committed missing or malformed",
      "next_arm_triage: triage terminal_completion missing or malformed",
      "next_arm_triage: triage quiet_start_state missing or malformed",
      "next_arm_triage: triage capture_faults missing or malformed",
      "next_arm_triage: triage thermal_escalation missing or malformed",
      "next_arm_triage: triage cohort_pool_rules missing or malformed",
      "next_arm_triage: triage sentinel_roster missing or malformed",
      "next_arm_triage: triage member_eligibility missing or malformed",
      "next_arm_triage: triage calibration_stop: windows must be a sequence in frozen order does not allow a None arm",
      "next_arm_triage: triage battery_window missing or malformed",
      "next_arm_triage: triage full_desk_gate missing or malformed",
      "next_arm_triage: packet could not be rebuilt from its named sources: ValueError: packet is not an object"
    ]
  },
  "after": {
    "case": "triage-missing",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "series_binding: W1: the arm could not rebuild the packet",
      "held_window: unreadable: TypeError: 'NoneType' object is not subscriptable",
      "next_arm_triage: next-arm triage packet missing or wrong schema",
      "next_arm_triage: packet has no numeric valid_until_epoch_s (expiry is mandatory)",
      "next_arm_triage: triage packet needs previous_window as a registered window id (R1, W1, Cn, Tn, Dn)",
      "next_arm_triage: calibration evidence contradictory or malformed: windows must be a sequence in frozen order",
      "next_arm_triage: triage record_committed missing or malformed",
      "next_arm_triage: triage terminal_completion missing or malformed",
      "next_arm_triage: triage quiet_start_state missing or malformed",
      "next_arm_triage: triage capture_faults missing or malformed",
      "next_arm_triage: triage thermal_escalation missing or malformed",
      "next_arm_triage: triage cohort_pool_rules missing or malformed",
      "next_arm_triage: triage sentinel_roster missing or malformed",
      "next_arm_triage: triage member_eligibility missing or malformed",
      "next_arm_triage: triage calibration_stop: windows must be a sequence in frozen order does not allow a None arm",
      "next_arm_triage: triage battery_window missing or malformed",
      "next_arm_triage: triage full_desk_gate missing or malformed",
      "next_arm_triage: packet could not be rebuilt from its named sources: ValueError: packet is not an object"
    ]
  }
}
```

### triage-edited

```json
{
  "before": {
    "case": "triage-edited",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "next_arm_triage: packet does not match its committed sources (the supplied packet differs from the arm's own build)"
    ]
  },
  "after": {
    "case": "triage-edited",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "next_arm_triage: packet does not match its committed sources (the supplied packet differs from the arm's own build)"
    ]
  }
}
```

### triage-stale-schema

```json
{
  "before": {
    "case": "triage-stale-schema",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "next_arm_triage: packet does not match its committed sources (the supplied packet differs from the arm's own build)"
    ]
  },
  "after": {
    "case": "triage-stale-schema",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "next_arm_triage: packet does not match its committed sources (the supplied packet differs from the arm's own build)"
    ]
  }
}
```

### record-commit-unknown

```json
{
  "before": {
    "case": "record-commit-unknown",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "series_binding: W1: the arm could not rebuild the packet",
      "held_window: unreadable: TypeError: 'NoneType' object is not subscriptable",
      "next_arm_triage: next-arm triage packet missing or wrong schema",
      "next_arm_triage: packet has no numeric valid_until_epoch_s (expiry is mandatory)",
      "next_arm_triage: triage packet needs previous_window as a registered window id (R1, W1, Cn, Tn, Dn)",
      "next_arm_triage: calibration evidence contradictory or malformed: windows must be a sequence in frozen order",
      "next_arm_triage: triage record_committed missing or malformed",
      "next_arm_triage: triage terminal_completion missing or malformed",
      "next_arm_triage: triage quiet_start_state missing or malformed",
      "next_arm_triage: triage capture_faults missing or malformed",
      "next_arm_triage: triage thermal_escalation missing or malformed",
      "next_arm_triage: triage cohort_pool_rules missing or malformed",
      "next_arm_triage: triage sentinel_roster missing or malformed",
      "next_arm_triage: triage member_eligibility missing or malformed",
      "next_arm_triage: triage calibration_stop: windows must be a sequence in frozen order does not allow a None arm",
      "next_arm_triage: triage battery_window missing or malformed",
      "next_arm_triage: triage full_desk_gate missing or malformed",
      "next_arm_triage: packet could not be rebuilt from its named sources: ValueError: Git evidence unavailable: rev-parse --verify"
    ]
  },
  "after": {
    "case": "record-commit-unknown",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "series_binding: W1: the arm could not rebuild the packet",
      "held_window: unreadable: TypeError: 'NoneType' object is not subscriptable",
      "next_arm_triage: next-arm triage packet missing or wrong schema",
      "next_arm_triage: packet has no numeric valid_until_epoch_s (expiry is mandatory)",
      "next_arm_triage: triage packet needs previous_window as a registered window id (R1, W1, Cn, Tn, Dn)",
      "next_arm_triage: calibration evidence contradictory or malformed: windows must be a sequence in frozen order",
      "next_arm_triage: triage record_committed missing or malformed",
      "next_arm_triage: triage terminal_completion missing or malformed",
      "next_arm_triage: triage quiet_start_state missing or malformed",
      "next_arm_triage: triage capture_faults missing or malformed",
      "next_arm_triage: triage thermal_escalation missing or malformed",
      "next_arm_triage: triage cohort_pool_rules missing or malformed",
      "next_arm_triage: triage sentinel_roster missing or malformed",
      "next_arm_triage: triage member_eligibility missing or malformed",
      "next_arm_triage: triage calibration_stop: windows must be a sequence in frozen order does not allow a None arm",
      "next_arm_triage: triage battery_window missing or malformed",
      "next_arm_triage: triage full_desk_gate missing or malformed",
      "next_arm_triage: packet could not be rebuilt from its named sources: ValueError: Git evidence unavailable: rev-parse --verify"
    ]
  }
}
```

### topup-no-charge

```json
{
  "before": {
    "case": "topup-no-charge",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "completed top-up evidence missing or inadmissible: require --battery-log showing a completed charge within 30 min or continuous float since"
    ]
  },
  "after": {
    "case": "topup-no-charge",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "completed top-up evidence missing or inadmissible: require --battery-log showing a completed charge within 30 min or continuous float since"
    ]
  }
}
```

### topup-stale

```json
{
  "before": {
    "case": "topup-stale",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "completed top-up evidence missing or inadmissible: require --battery-log showing a completed charge within 30 min or continuous float since"
    ]
  },
  "after": {
    "case": "topup-stale",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "completed top-up evidence missing or inadmissible: require --battery-log showing a completed charge within 30 min or continuous float since"
    ]
  }
}
```

### topup-future

```json
{
  "before": {
    "case": "topup-future",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "completed top-up evidence missing or inadmissible: require --battery-log showing a completed charge within 30 min or continuous float since"
    ]
  },
  "after": {
    "case": "topup-future",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "completed top-up evidence missing or inadmissible: require --battery-log showing a completed charge within 30 min or continuous float since"
    ]
  }
}
```

### obc-unattested

```json
{
  "before": {
    "case": "obc-unattested",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "OBC off requires --obc-off-attested-by"
    ]
  },
  "after": {
    "case": "obc-unattested",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "OBC off requires --obc-off-attested-by"
    ]
  }
}
```

### disk-image-mounted

```json
{
  "before": {
    "case": "disk-image-mounted",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "external_volume: external_volume_mounted:/Volumes/JWSMOKE"
    ]
  },
  "after": {
    "case": "disk-image-mounted",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "external_volume: external_volume_mounted:/Volumes/JWSMOKE"
    ]
  }
}
```

### battery-charging

```json
{
  "before": {
    "case": "battery-charging",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "battery top-up incomplete/unobserved: require fresh AC, >=99%, not charging, |InstantAmperage| <=200 mA"
    ]
  },
  "after": {
    "case": "battery-charging",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "battery top-up incomplete/unobserved: require fresh AC, >=99%, not charging, |InstantAmperage| <=200 mA"
    ]
  }
}
```

### powermode-mismatch

```json
{
  "before": {
    "case": "powermode-mismatch",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "ac_powermode: AC powermode 2 != expected 0"
    ]
  },
  "after": {
    "case": "powermode-mismatch",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "ac_powermode: AC powermode 2 != expected 0"
    ]
  }
}
```

### meter-not-live

```json
{
  "before": {
    "case": "meter-not-live",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "next_arm_triage: triage meter_reader_live failed"
    ]
  },
  "after": {
    "case": "meter-not-live",
    "rc": 1,
    "admitted": false,
    "installer_called": false,
    "reasons": [
      "next_arm_triage: triage meter_reader_live failed"
    ]
  }
}
```

## Closing verification and limitations

The requested second module was invoked sequentially:

```text
python3.13 -B -m unittest tests.align.test_v4_arm_watchdog_check -v
```

It completed all **18 ArmIntegrationTests** and the first **3 HeldWindowTests**
with `ok` (**21 completed tests, no observed failure**). I then interrupted
`HeldWindowTests.test_k_final_with_held_reason_and_k_plus_1_not_final_refuses_the_arm_of_k_plus_2`
at the cumulative test-time limit. It exited **130 (KeyboardInterrupt)**;
there is **no passing complete-module result**. The cumulative targeted
test time was approximately 20 minutes. Interrupted runs do not have final
unittest duration summaries; the captured elapsed bounds include short
post-stop tool gaps, so an exact aggregate duration is unavailable.

Both interruptions targeted only this seat's own exec sessions. A read-only
`ps` diagnostic was denied by the sandbox; no process list was obtained and
no other process/job was signaled. No further tests were started after the
budget stop.

`git diff --check` passed. The committed implementation's changed paths
intersect neither `v4_registration.ARTIFACTS` nor the forbidden coordination
paths. Only Python 3.13 was exercised. No full repository suite, real data,
native clock/host validation, or MLX execution is claimed. This repair adds
no MLX code or new MLX-native test requirement; existing native W1 gates
remain with the lead.

## Changed files and handoff

- `joulewise/align/w1_prequal.py`: production-derived clock-budget fixture,
  explicit synthetic native-reader seam for the CLI's production plan check,
  and exact missing-hazard refusal case.
- `tests/align/test_w1_prequal.py`: fixture budget witness, missing-budget
  refusal witness, exact CLI case assertion, and guarded reader injection.
- This report: authority/path confirmation, red/green evidence, and every
  CLI case's complete before/after refusal text.

Implementation commit: **`dedf958eb` — `fix(align): give PREQUAL arm plans the production clock budget`**.
This report is committed separately. No push.

Open source/contract questions: none. The inherited failure is masked by the
base's old synthetic frequency stub, as documented above; that is the only
baseline discrepancy. The verification blocker is the uncompleted portions
of the two requested modules, not a completed test failure.

Next exact step for the lead, in a separate session with enough test budget,
one command at a time:

```text
python3.13 -B -m unittest tests.align.test_w1_prequal
python3.13 -B -m unittest tests.align.test_v4_arm_watchdog_check
```

Complete those runs before treating the modules as green and integrating
the local commits. RUN_STATE, TASK_QUEUE, the kernel, bound production code,
and real custody remain untouched.
