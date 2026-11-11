# W1 reliability round 2 — local Sol seat `w1-reliability-2`

Implemented the three prospectively authorized groups on
`ops/2026-11-10-w1-reliability`, starting at `5ea9be315`. No arm, install,
production host-state probe, measurement, analysis, network access, model
download, or push was performed. Hardware behavior remains **PROVISIONAL**.

## Authority and intake

Read the round-1 report `docs/run_reports/2026-11-10-w1-reliability.md` and
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/measurement-system.md`,
especially I-01 and A-04/A-05/A-09. Mission M0: targeted restart/queue and
decision-log sections, AGENTS/CLAUDE conventions, orchestration, and clean
initial Git status inspected. No active stop card. The explicit brief selects
this work and prohibits coordination-state writes. RUN_STATE.md, TASK_QUEUE.md,
docs/process/state_kernel.json and tests/test_gen_state.py are unchanged; no
kernel task was registered. No child agent or cross-model consult was used.

The lead ruling is recorded verbatim as requested:

> **LEAD RULING (Opus 5.5 lead, interactive session 41120c85, 2026-11-10 ~18:00 PST), recorded verbatim for the report:** option 2 is AUTHORIZED,
> prospectively, before W1 arms. W1 is not yet registered; STRICT re-registration at the final integrated W1 head was already required and now
> covers these changes. Authorized scope, and only this scope:
> - **I-01:** the night hazard driver refuses at arm when the KM003C reader is absent/unreadable (reuse the `align_v4_session.py:arm_checks`
>   meter probe semantics), and treats an in-window stream gap / USB loss beyond a stated bound as a recorded liveness fault (choose the
>   existing monitor-liveness mechanism; state the bound and why). Ed's rule: every measurement captures DC-in.
> - **Production host-state preflight:** `prepare` (and the W1 smoke) acquires+releases HostLock on the PRODUCTION
>   /Users/Shared/JouleWise/host-power path under `mark_production_entry`, refusing before install on failure (the 11-08 root-owned-dir failure).
> - **A-04 / A-05:** on every terminal path (normal, refusal, TERM/kill, dead-man) restore network time ON and restore High Power/Automatic,
>   recording what was restored (or why not) in the result; the dead-man restores R1/W1 markers, not only W1-tagged ones.
> Unchanged restrictions: no ALIGN v4 analysis/engine code, thresholds, registration text, seeds, or registration code. Synthetic tests for every
> terminal path; targeted modules only. List the native checks the lead must run on the MBP (meter unplug, kill, dead-man, read-back).

This ruling prospectively supersedes D-186's leave-network-time-OFF policy
for the terminal paths addressed here. No decision-log or registration text
was edited.

## Implementation

### I-01: required DC-in reader

`joulewise/b5/driver.py` calls the existing v4 `_probe_meter_live` helper before
publication/chain launch. It therefore uses the same streaming status,
aligned samples, RAW offset and closing-line requirements as `arm_checks`.
An unavailable command, absent reader, unreadable probe or probe exception
refuses with the existing `night_refused_instrument_not_sampling` reason,
records `meter_readiness`, and faults the result with `meter_not_sampling`.
There is no measurement waiver or cached availability decision.

The incremental `MeterLiveness` uses the **existing 600-second instrument
outage bound and 10-second evaluation cadence**. This applies the existing
monitor availability mechanism to the required DC-in channel, rather than
introducing a new scientific threshold. The conservative bound tolerates
short startup/restart/USB delays while preventing an indefinitely unmeasured
channel; it is far above the reader's 200 ms polls and 1 s flush cadence.
Normal scheduling adds evaluation/poll delay to the stop time.

Only a nonempty batch with a correctly sized sample payload under a streaming
header refreshes liveness. Empty polls, USB errors, malformed/partial lines,
unreadable files and missing streams do not. Header RAW/monotonic anchors
date samples; a backlog cannot refresh them to the current time. A gap at
least 600 s is latched even if a recovered batch arrives before the next
check. Restart streams are read incrementally as well. At the bound the
driver stops through the existing monitor-outage refusal mechanism, emits
the existing `meter.supervision_fault` flag with event `liveness_outage`,
and records `meter_liveness_outage` in hazard, result and courier facts.
The meter's existing process restart policy is unchanged. Stream digests
continue through the existing terminal meter summary.

### Production host-state preflight

`powermode.host_lock_preflight` unconditionally constructs, acquires and
releases HostLock, including when neither a marker nor a lock file exists.
Permission errors and a busy lock refuse. `align_v4_session.prepare` runs
this before restore/kit preparation and persists its successful path and
acquire/release record in session.json. The W1 smoke runs the same preflight
in its guards and records failures before preparation or install.

The v4 session already marks its production entry; the smoke CLI and its
prepare child now do too. Production refuses the host-directory test
override. Synthetic tests patch the production default to a temporary
directory **under that production guard**; they do not prove the actual
/Users/Shared directory is writable.

### A-04/A-05: terminal restoration

`scripts/run_night.py` closes host state before writing/delivering its normal
or refusal result, and also closes on exceptions/TERM/HUP/INT. Mode-0 plans
are included, so an R1 chain's internal High Power transition is covered.
The close restores AC powermode 0, reads it back, sets network time ON with
the existing narrow systemsetup command and authenticates an ON read-back.
Both command results and errors are retained. A power restore failure still
attempts network-time restoration; power markers clear only after verified 0.
The signal close latch prevents another termination signal interrupting
restoration. SIGKILL recovery is owned by the dead-man.

Restoration still requires proven chain termination and the host lock. A
retained inherited lock, an unproven chain or another armed W1 owner's marker
defers both setting changes and records why. The close is idempotent within
an invocation. Results carry `host_restoration`; a failed/deferred close adds
`host_restoration_incomplete`. Create-once restore records and the custody
log retain evidence when a result cannot be written. An unexpected exception
before a result also gets a structural terminal result when possible. A
rerun does not replace the original night's result, and launch-abandoned
spans receive no new driver records that would re-fence them.

The dead-man handles R1-tagged and W1-tagged host markers and the R1 marker
under the measurement root, after its existing chain/pending-launch proofs.
It no longer skips restoration because courier.sent exists. Recovery is
recorded as `dead_man_host_restoration` in the result, with separate immutable
attempt records. Updating that result clears the old sent marker so its old
digest cannot acknowledge the recovery result; courier delivery is retried.
An absent result becomes a conservative recovery/refusal result, not a claim
of successful measurement. A dead-man that is early or cannot prove the
chain gone records a deferred attempt without taking the live night's
once-only result slot. It does not add a kill ladder (A-07 is outside scope).

## Files and registration boundary

Production: joulewise/align/apple/powermode.py, joulewise/align/w1_smoke.py,
joulewise/b5/driver.py, scripts/align_v4_session.py,
scripts/align_v4_w1_smoke.py, scripts/run_night.py.

Tests: tests/test_w1_reliability_r2.py (new), tests/test_w1_reliability.py,
tests/test_b5_driver.py, tests/test_run_night.py,
tests/align/test_r1_round6_power.py, tests/align/test_v4_kit.py,
tests/align/test_w1_smoke.py. Test hosts now support the restore/read-back
commands; the hazard harness supplies a synthetic reader and live-probe seam.
Old assertions that Automatic plans never restore or courier.sent skips the
dead-man were updated to the authorized behavior. Loose prepare/supervisor
doubles were corrected to their actual return/attribute contracts.

The four changed STRICT-bound paths are powermode.py, driver.py,
align_v4_session.py and run_night.py. The two smoke paths are outside the
current registration artifact set. No new executed unbound module was added;
the existing closure tests pass. STRICT re-registration remains mandatory
at the final integrated W1 head. Analysis/engine code, scientific thresholds,
registration code/text and seeds are unchanged.

## Verification

All tests used Python 3.13/unittest, one module or class group at a time.
Baseline `python3.13 -B -m unittest tests.test_w1_reliability`: 11 passed,
4.369 s. Final focused checks:

| Command after `python3.13 -B -m unittest` | Result |
|---|---|
| tests.test_w1_reliability_r2 | 18 passed, 4.707 s |
| tests.test_w1_reliability | 11 passed, 4.222 s |
| tests.test_run_night.NightDriverTests | 156 passed, 23.689 s |
| tests.align.test_r1_round7_power | 29 passed, 2.395 s |
| tests.align.test_r1_round6_power | 25 passed, 0.265 s |
| tests.align.test_v4_kit.W1HighPowerTests | 9 passed, 0.165 s |
| tests.align.test_w1_smoke | 28 passed, 20.003 s |
| tests.align.test_v4_executed_closure | 4 passed, 2.546 s |
| tests.test_b5_driver.B6ReviewRegressionTests | 2 passed, 1.080 s |

Additional focused commands (each confined to one module):

```sh
python3.13 -B -m unittest tests.align.test_r1_round8.NightUnprovenCloseTests.test_an_unproven_chain_termination_restores_nothing tests.align.test_r1_round8.DryArmInterruptTests.test_an_interrupt_in_a_dry_arm_restores_nothing tests.align.test_r1_round8.DryArmInterruptTests.test_an_interrupt_in_the_initial_census_of_a_dry_arm_restores_nothing
python3.13 -B -m unittest tests.test_b5_driver_p2.MonitorTests.test_liveness_reads_only_new_error_free_lines tests.test_b5_driver_p2.SolReviewFixTests.test_a_malformed_liveness_line_is_not_a_reading_and_runs_into_the_outage_bound tests.test_b5_driver_p2.SolReviewFixTests.test_an_unreadable_liveness_journal_runs_into_the_outage_bound
python3.13 -B -m compileall -q joulewise tests
python3.13 -B -m py_compile scripts/run_night.py scripts/align_v4_session.py scripts/align_v4_w1_smoke.py
git diff --check
```

The two three-case groups passed (0.411 s and 0.001 s); compilation and diff
checks passed. Test time including development reruns was well under 20 min.
The full suite was deliberately not run under the owner's long-job rule.
The round-1 delivery tests still cover byte-identical result publication to
synthetic local bare Git repositories; no network transport was used.

During development, checks caught a recovered-sample gap that could have
hidden an outage, signal interruption of a normal terminal restore, legacy
log-label regressions, old policy expectations and incomplete synthetic test
doubles. Those were corrected. No remaining focused-test failure is known.

## Native checks and remaining uncertainty

These are lead-owned MBP checks, after the long blinded job and within a
permissible isolated smoke/rehearsal gap. No quiet-machine work may be run
from this agent bridge.

1. At the final integrated candidate, run production prepare and the smoke
   guard with the override unset. Verify the actual
   /Users/Shared/JouleWise/host-power lock is acquired/released even without
   a marker; confirm failures refuse before install. Native ownership and
   permissions were not inspected here.
2. Unplug the KM003C before arm: require instrument refusal, no chain start,
   recorded meter evidence/fault and terminal restores. With it connected,
   require a genuinely aligned probe and valid DC-in stream.
3. Unplug during a non-claiming smoke for at least 600 s: verify a recorded
   liveness fault and chain stop, including USB-error/empty-poll behavior and
   the final stream digests. Verify recovery cannot erase an already elapsed
   outage. Native timing/USB re-enumeration is unproven here.
4. Exercise normal completion, refusal, TERM/HUP/INT, an internal R1-driver
   kill, and an outer-driver SIGKILL followed by the scheduled dead-man.
   Cover both R1 and W1 marker tags and an already-sent courier. Require
   proven chain exit, Automatic read-back, network time ON and the result's
   restore evidence. Verify a live/unknown chain or inherited lock defers
   settings and retains the obligation. The synthetic SIGKILL witness uses
   a real temporary flock holder; it is not a native full driver kill proof.
5. Independently read `/usr/bin/pmset -g custom` and
   `/usr/bin/sudo -n /usr/sbin/systemsetup -getusingnetworktime` after each
   safe terminal path. Verify the installed unattended sudo rules permit
   the ON setter **and** this authenticated query. A refusal/read-back failure
   remains a recorded fault; native sudo access was not established here.
6. Rerun the real-process integration witness
   `python3.13 -B -m unittest tests.test_b5_driver.LaunchTests.test_chain_digest_mismatch_is_a_flag_and_the_chain_runs`
   outside this sandbox, then the required native PREQUAL/W1 smoke. The
   round-1 report documents pgrep's unavailable sysmon census here. New
   driver-result witnesses inject chain/group termination proofs; no such
   injected proof is presented as native validation.

No MLX code or native MLX tests changed or ran. No restricted/night custody,
held-out outcomes, real measurement inputs or absolute /Users/edr data paths
were accessed. There is no new scientific-policy question; remaining gates
are independent lead review, STRICT re-registration and the native checks
above. Next exact step: review/integrate this local candidate, re-register
the final W1 head, and complete the lead-owned native gates before arming.

## Local commits

- `19a862dc8` — `fix(w1): gate DC-in and restore host state on terminal paths`
  (six production files and seven test files).
- This report is the separate `docs: record W1 reliability round-2 ruling and verification`
  commit; its exact identity is available as this file's latest Git commit.

Both commits are local on the existing branch; nothing was pushed.
