# Fable 5.1 cold final pass: block-5 measurement code, e6b6a0ce..a434e363d

Reviewer: Fable 5.1, single foreground session, read-only in every repository. Worktree
`/Users/edr/code/JouleWise-wt-int4` at `a434e363d96621318657418e60b8d14410079d82` (confirmed with
`git rev-parse HEAD`), branch `integrate/2026-10-06-gate-prune-4`. Rule applied: `REVIEW_BRIEF_RULE.md`
(physics refuses; everything else is a flag), plus the two rulings the brief binds me to
(`RULING_battery_assist_2026-10-06.md`, `RULING_fable_cooldown_2026-10-06.md`).

## Overall verdict: PASS WITH NOTES

No item is a DEFECT. I found no input that makes a wrong number reach a claim and no input that
wrongfully removes data under the rule. The notes below are either conservative over-exclusions
that need an unlikely trigger, pruning candidates under the doctrine, or places where the code
protects the number by a route other than the one named.

Tests executed here (non-venv `/opt/homebrew/bin/python3.13`, `TMPDIR=/private/tmp/fcp`):

- `tests.hazards.test_refusal_allowlist`, `tests.hazards.test_clock`, `tests.hazards.test_arm_identity`,
  `tests.test_b5_driver_lineage_real`, `tests.test_calibration_ledger_custody.ProbeCustodyGatewayCensusTests`:
  70 tests, OK, 15 s.
- `tests.test_harvest_b5_p3harv`, `tests.test_harvest_b5_window.BatteryRuleParityTests`,
  `tests.test_harvest_b5_window.WholeWindowMemberFailureTests`, `tests.test_hazard_whole_window_verdict`,
  `tests.test_controller_hazard_flags`: 132 tests, OK, 204 s.

No process I started is still alive (checked with ps after the runs).

## Per-item table

| # | Item | Verdict | Where | Note id |
|---|---|---|---|---|
| 1 | Numbers: pinned estimator files | SOUND | `joulewise/reduce.py`, `uncertainty_evidence.py`, `powermetrics_fiducial.py`, `adapters/powermetrics.py`: blob ids identical at e6b6a0ce and a434e363d (82449d58, 202acfcb, d1bd5d4b, 8fa6db3c) | |
| 1 | Numbers: the rest of the sample-to-record path | SOUND WITH NOTE | `controller.py` (flag context, verdict cache, binary digest), `whole_window.py`, `harvest.py` | N1 |
| 2 | P3-HARV F2 state-gap rule (120 s) | SOUND WITH NOTE | `harvest.py:2442-2462`, `_state_holes` 2496 | N2 |
| 2 | P3-HARV F5 assist = any negative B0AC | SOUND WITH NOTE | `harvest.py:2318-2355`, `2484-2493`, `2525-2574` | N3, N4 |
| 2 | Pair endpoint sign (negative = discharge) | SOUND | `harvest.py:2597-2636`; `battery_float._signed` 112 (2^64 wrap) | |
| 3 | P3-HAZ clock read-skew rejection; harvest clock_steps | SOUND WITH NOTE | `hazards/clock.py:152-203`, `400-416`; `harvest.py:2796-2886` | N5 |
| 4 | P3-DRV F1 `reap_orphan_monitor` without identity | SOUND WITH NOTE | `driver.py:2707-2717` | N6 |
| 4 | P3-DRV F6 supervisors not polled during G10 | SOUND WITH NOTE | `driver.py:2588-2611` | N7 |
| 5 | B-lexeme classification of `b5_window_calibration_verdict.py` | SOUND WITH NOTE | `scripts/b5_window_calibration_verdict.py:150-163`; `controller.py:543-600`, `772-810` | N8 |
| 5 | `monitor.outage` as DISCLOSE | SOUND | `driver.py:2361-2369`; `flags/catalog.py:258` | |
| 6 | 2d10e0368 sign-inconsistent accumulator | SOUND WITH NOTE | `harvest.py:2690-2702` | N4 |
| 6 | 9c17c82fc `member.whole_window_member_failure` | SOUND | `harvest.py:495-500`, `4274-4311`; catalog 113, 96, 119 | |
| 6 | ba0e0c72e endpoint currents through `_grammar` | SOUND | `harvest.py:2611-2622` | |
| 7 | b1 F1 dissent: descriptor binding vs floor-mint partial replay | SOUND WITH NOTE | `whole_window.py:2644-2667`, `2764-2778` | N9 |
| 8 | OS-build arm refusal kept as NUMBER_INTEGRITY | SOUND (agree) | `hazards/arm.py:215-220`, `313-343` | N10 |
| 9 | Driver lineage fix 3a9327e51 | SOUND WITH NOTE | `driver.py:424-489`, `2156-2192`; `window_lineage.py:609-664`, `714-742` | N11 |
| 10 | Pack-root layout flag | SOUND | `controller.py:918-940` (`records.pin_ledger`, DISCLOSE) | |
| 10 | Historical custody: evicted disclosed, mismatch scoped | SOUND | `harvest.py:5458-5515`; allowlist `window_exclusions` | |
| 10 | `ledger_snapshot_refused` not split | SOUND | `harvest.py:3886-3888`; test `test_a_ledger_integrity_reason_excludes_the_window` | |
| 10 | Crash before metadata = member failure | SOUND | `whole_window._hazard_member_lineage`; `tests/test_hazard_whole_window_verdict.py` (executed) | |
| 10 | Env-guard collector exception = flag | SOUND | `controller.py:1420-1429`, `2230-2271` | |
| 10 | `member.stderr_uncopied` = DISCLOSE | SOUND | catalog 217; allowlist member_exclusions entry removed | |
| 10 | P4 `whole_window.member_failures_unreadable` | SOUND | `harvest.py:4259-4271`, `4294-4298` | |
| 11 | Timing ruling in code | SOUND WITH NOTE | `configs/campaign_policies/quiet_mac_p2_b5.json`; `b5/chain.py:97` (SETTLE_S 60); commit f4cf90472 | N12 |

## What I checked, item by item

**1. Numbers.** The four pinned files are byte-identical (blob ids above). `scripts/validate_powermetrics_fiducial.py`
changed (+364) but is the P2-VPF validator, not a pinned estimator; its hunks are `main`, the preflight
systematic screen, the capture ledger lifecycle and the reserved-slot check. In `controller.py` the
energy arithmetic is untouched; the changes are the HAZARD flag context, the J1 verdict cache (item 5),
the guard-probe thread and the binary-digest handling (N1). `whole_window.py`'s hunks are lineage
authentication, NEG-8 freshness and the reference-energy evidence; the harvest re-derives the
corpus energies itself (b1 F2, landed in noncore).

**2. Battery rule.** `battery_join` matches the ruling point for point: exclusion only on an in-force
SMC read above +limit, IsCharging Yes or ExternalConnected No at an in-force publication or any good
poll inside the span, a charge-accumulator mean above limit x voltage, and the missing-evidence
predicate (`battery.unmeasured`). Assist is any negative SMC read holding inside the deciding phase
(`_smc_phase`, `entry["current_ma"] < 0`); the -200 mA figure survives only as `smc_reads_below` and
`smc_duration_below_s`. A span with a charging or AC-loss read gets no assist (`state_bad`). A span
whose state went unread keeps its disclosure marked `state_unread`. The energy integral is
max(0, -B0AC x B0AV) over clipped holds and goes to `withheld/battery-assist.json` only. F2: with SMC
coverage, the registry state is judged from every good ioreg read carrying both state fields, and
`_state_holes` requires no gap above `battery_unmeasured_gap_s` across the span, trailing gap to the
span end (R3-5). Pair sign: `pair_endpoint_currents` re-reads each endpoint's raw ioreg bytes only
when they hash to the recorded digest, parses with the frozen grammar through the registered
`_grammar` boundary; `battery_float._signed` maps the registry's unsigned 64-bit encoding to a signed
value, so -865 mA reads as -865, not 2^64-865. `pair_discharge_only` needs every failed endpoint
negative; an unread endpoint stays None and keeps the exclusion.

**3. Clock.** Can a real step be rejected as skew? No. Read skew is `raw_after - raw_before`, two
CLOCK_MONOTONIC_RAW reads; a wall-clock step moves CLOCK_REALTIME and leaves RAW alone, so a step
never widens the skew. If a sample's five reads are all preempted the sample is unmeasured, and
`clock_steps` compares the next usable anchor with the last one across it (the chain is not reset),
so a step beside an unmeasured sample is still found; only its interval widens. Can a skewed read
create a step? No. The anchor is REALTIME minus the RAW midpoint (`clock_reference.sample_anchor`),
so a read with skew s carries at most s/2 of anchor error; with both samples at or under step/4
(250 us at 1 ms) the residual's read error is at most step/4, so a residual above step holds at least
3/4 of a step of real movement. The harvest's `_clock_point` applies the same bound from the plan's
`clock_step_ns`, and rejects recorded anchors over it as well as samples with `rejected_anchors`
and no anchor.

**4. Driver.** `reap_orphan_monitor` signals only the last recorded `start`/`restart` pgid, never after
a proven stop or a final exit, and when `start_time` is recorded it requires the live process to
match. See N6 for the missing-`start_time` branch. G10 runs only after the chain's group is proven
gone (`started and proven and abort is None`), so every member span and both captures are over
before it; see N7.

**5. Integrator's calls.** The verdict script writes `effective_b_fiducial_s` as a binary64 float
(`float(effective)`), not a decimal lexeme. The member uses it only when all four artifact digests and
the estimator-file digests match, only if it is finite and widen-only against the stored bound, and
otherwise refits (`refit_cache_miss`). The value is what `verify_stored_evidence_physics` returned on
the same bytes with the same code, and a Python float survives JSON exactly. The harvest never reads
the file; it refits from raw bytes. So no number depends on the lexeme form, and INTERNAL
("not a stop; a failure leaves every member to refit") is the right class. `monitor.outage` is a
window-level record of the event; the member spans the outage covers are excluded by their own
joins (`battery.unmeasured`, `contention.unmeasured` EXCLUDE_MEMBER), and the stop itself
(`night_stopped_monitor_outage`) is "the instrument not sampling", a listed physics hazard. DISCLOSE
is right.

**6. Commits.** 2d10e0368 mirrors the hazard copy; the parity tests pass on the same journals (N4).
9c17c82fc: the eleven reasons are the verdict's own `PROSPECTIVE_MEMBER_FAILURE_REASON_CODES` minus
the two with their own member codes, both of which are EXCLUDE_MEMBER in the catalog
(`thermal.powermetrics_pressure_elevated` 119, `member.strict_validation_failed` 96), so no handed-off
reason loses its exclusion. The verdict's authenticity does not gate the member flags; an unauthentic
verdict can only remove members, never keep one. ba0e0c72e is the same `battery_float.parse(raw,
wall_time_s)` call reached through the registered boundary.

**7. b1 F1 dissent.** Recorded, and I side with the descriptor binding (N9).

**8. OS build.** Agree with the orchestrator: `kern.osversion` is read live, not from a settings string;
the acceptance is issued for an `{os_build, hardware_model}` epoch and the calibration bound is only
known to hold in that epoch, so an unjudged epoch makes the fiducial bound unattributable. That is
the rule's "could not be attributed" clause, surfaced at arm instead of 15 minutes in. A failed read
never refuses (`judged` None). Sol's R7 dissent stands recorded.

**9. Lineage.** Boot is read by `window_lineage.current_boot_session_id` on both sides (canonical
lowercase); publication and check share `lineage_identity()` (pack plan id, window id, bracket
session id); the only refusal is `boot_changed`, judged from the lineage's recorded boot against the
current one. Can a window whose members are unattributable launch and reach a claim? It can launch;
it cannot reach a claim. Each member authenticates the campaign lineage itself
(`authenticate_campaign`, `require_current_boot=True`) and the controller refuses on a plan-id
mismatch, so a bad locator produces failed members, not numbers; the verdict writer's
`_hazard_member_lineage` (NUMBER_INTEGRITY) refuses a foreign member; the harvest's lineage audit
emits the `lineage.*` codes. See N11 for the cost.

**10. Census and triage.** Allowlist: 2,748 sites; the lineage fix's two sites are PHYSICS (boot) and
INTERNAL (`valid=False` start state); no new BASELINE; `refusal_baseline_frozen.txt` unchanged; the
allowlist test passes here. The pack-root layout check is `records.pin_ledger` (DISCLOSE) and the
member is collected. Historical custody: `acceptance_relied_attempt_ids` names the derivation corpus
and prior observation set; a mismatch outside them is `..._mismatch_unused` (DISCLOSE); an unreadable
acceptance scopes nothing, so every mismatch excludes; evicted captures are counted under
`..._unmeasured` (DISCLOSE). The snapshot-refusal triage's claim that only integrity reasons reach the
emit is carried by a test on the real 376-row prefix, which passes here. P4's two branches (absent,
malformed) exclude; listed, empty and passed do not.

**11. Timing.** The policy file carries exactly the ruling's cooldown (5.0 / 1.0 / 0.8 / thermal nominal /
cap 300 / sub-window 5.0). `SETTLE_S = 60` for all eleven settles, recorded as a chain deviation from
the runbook's 180. Idle capture: see N12.

## Notes

**N1 (item 1, `controller.py:1157-1179`, catalog 205).** `instrument.binary_identity_unmeasured` is
EXCLUDE_MEMBER on a condition that is "a probe that failed": the adapter did not expose a valid
`executable_sha256`. A present digest that differs still refuses in the attachment, which is right.
But an absent digest cannot make the number unattributable when the arm has already judged the
`os_build` epoch (item 8): `/usr/bin/powermetrics` is a system binary bound to the OS build, and the
harvest runs on the same boot and can hash it. Disposition under the rule: flag, not refuse. Fix: the
harvest hashes the executable the executed inventory names (or the adapter's recorded path) and
downgrades to DISCLOSE when it equals the calibrated digest; EXCLUDE_MEMBER only when it differs or
cannot be read at harvest either. Trigger is rare (the pinned adapter is unchanged), so a note.

**N2 (item 2, `harvest.py:2496-2522`).** A state hole that straddles a span edge is judged by its full
length, not its in-span portion: reads inside the span to 5 s of its end, then an ioreg silence of
205 s, is a hole and `battery.unmeasured` (EXCLUDE_MEMBER) although only 5 s of the span went
unobserved. This is the standing convention (`_uncovered` at e6b6a0ce does the same), it only
excludes, and it needs a >120 s ioreg stall adjacent to a span while SMC reads continue. The
trailing no-after case is clipped to the span end (R3-5), which makes the two edges asymmetric.
Candidate fix, if a window ever loses a member to it: judge `min(right, span_end) - max(left,
span_start)` on both edges. Not a defect.

**N3 (item 2, `harvest.py:2149-2158`; `hazards/battery.py:607-615`).** `in_force` counts the first read
at or after the span end, so a +300 mA SMC read or an IsCharging=Yes publication taken right after
a member counts against that member. Pre-existing, mirrored in the hazard copy, conservative. It
matters now because the ruling expects assisted 8B members to be kept: if the SMC recharged the
battery above +200 mA in the second after an assisted member's span, the member would be excluded
by the charging rule, re-creating the bias the ruling removes. The evidence on hand says it does not
happen: at the 80 % charge limit, 600 J of discharge produced no recharge within 200 s and B0AC read
0 throughout recovery (`b0ac_validation.md` section 4). Watch `battery.member_span` with
`smc_b0ac_charging_above_limit` on members that also carry `battery.assist` in the first BETA
windows; if it appears, drop the after-end read from the charging check (the 5 s polls and 1 Hz
reads inside the span already cover it).

**N4 (items 2 and 6, `harvest.py:2694-2700`).** A positive discharge-accumulator mean beyond the
limit stays `battery.accumulator_excursion` (EXCLUDE_MEMBER) even when the 1 Hz SMC reads over the
same interval show no charging. The accumulator is a 60 s registry record disagreeing with itself,
not a measured hazard; under the pruning rule it is a "flag, not refuse" candidate once the SMC
reads cover the span. Parity with the hazard copy holds (tests pass). Not a defect: it excludes,
and a sign-inconsistent accumulator has not been observed.

**N5 (item 3, `hazards/monitor.py:391`, `harvest.py:2873-2876`).** Two small points. (a) The monitor
calls `clock.sample` with the module default skew bound (step 1 ms / 4 = 250 us) while the harvest
derives its bound from the plan's `clock_step_ns`; identical at the registered 1 ms, and the harvest
re-judges recorded anchors anyway, so no number moves; keep them in step if the step threshold is
ever re-registered. (b) A step inside a run of skew-unmeasured samples is attributed to the whole
gap; if the gap touches a member span the member gets `clock.step_overlap`. The step cannot be
located better than the gap, so the exclusion is the honest reading of the measurement, not a
wrongful loss.

**N6 (item 4 F1, `driver.py:2707-2717`).** When the journal's last start carries no `start_time`
(the identity probe failed at start), the reaper skips the identity check entirely, including the
LIVE check, and sends SIGTERM to the recorded pgid. The pgid can be reused only by a later
session leader with the same pid; that needs the monitor to have died and the pid to wrap, and the
reaper runs only after the driver never proved the stop, when the dead-man is stopping the window
anyway. No number is touched. Fix: when `identity` is given, always require `state == "LIVE"`, and
without a recorded `start_time` additionally require the live command line to name the monitor
(`b5-fake-hazard-monitor` / `hazard_monitor` signatures the orphan census already carries); else
return not signalled.

**N7 (item 4 F6, `driver.py:2599`).** `_run_g10` blocks in `process.wait(timeout=1500)`; `supervise()`
(monitor and meter poll, liveness, disk) is not called for up to 25 minutes. A monitor crash during
G10 is not restarted and the driver does not flag `monitor.outage`; the journal just ends early and
the monitor's view of the G10 step is lost. Every member span and both captures end before G10
starts, so only the diagnostic is affected. Fix: replace the blocking wait with a loop that calls
`process.poll()` and `supervise()` every few seconds until exit or the timeout.

**N8 (item 5).** No record of the "B-lexeme" question exists in the archive beyond the brief and the
TODO, so I state my reading: the question is whether the verdict's bound, carried as a binary64 float
rather than the decimal lexeme the acceptance and ledger use, can put a different number into a
member than its own refit would. It cannot: digests gate its use, it is widen-only, the float
round-trips exactly, and the harvest refits from raw. INTERNAL agreed.

**N9 (item 7, `whole_window.py:2644-2667`, `2764-2778`).** The dissent: binding the pre and post
captures by descriptor ids (bracket session id and `{pre,post}_attempt_id` from the lineage's window
context) versus partially replaying the floor mint's selection from the ledger. I side with the
descriptor binding. The ids are reserved before the chain and published in a create-once lineage
(`_write_once`, NUMBER_INTEGRITY); the evidence bytes are hashed against the descriptor before the
binding runs (line 2764); the ledger-to-bytes binding is checked independently by the harvest's
custody pass (`historical_custody_report` re-hashes present bytes against ledger hashes) and by the
capture custody (`calibration.capture_invalid`); and the harvest refits from raw. A mint replay would
re-derive a selection the ledger already fixes, adding a second derivation path to keep in step.
Residual to record: the descriptor's `evidence_sha256` is written by the verdict writer, so its
independence rests on the ledger receipt digest and the custody pass, not on the descriptor itself.

**N10 (item 8, `hazards/arm.py:334-335`).** With an empty `expected_epochs` list the identity is
recorded and never judged. Right under the rule (nothing to compare), and the calibration writer
refuses later without an acceptance; noting it so no one reads "no epochs" as "epoch passed".

**N11 (item 9, `driver.py:2176-2192`).** A locator that is absent after one retry, or that fails
`authenticate_campaign`, now launches with `records.lineage_prelaunch_mismatch` (DISCLOSE). The
science is protected by the members' own refusals, but the window runs hollow: every member refuses
at the controller and nine hours produce no bundle. The doctrine says launch, and I do not ask for a
refusal. For economics only: the magistrate brief could treat `locator_absent` or an
authentication failure in that flag as a reason to stand down and republish before the chain, since
the condition predicts zero yield with certainty. Not a science gate; the orchestrator's call.

**N12 (item 11, commit f4cf90472).** The ruling says "duration-based idle capture at 75 s"; the
implementation sets `idle_seconds` 57.6 in every `_v5` config, which the adapter turns into
ceil(57.6 / 0.1) = 576 records, measured over block 3's 37 captures at 75.0-75.9 s wall time. So
the capture is by record count calibrated to 75 s, not by wall duration; the admission thresholds
(`min_samples` 30, p95 bounds) are unchanged. The ruling is met in effect. If the sampler's record
cadence ever changes, 576 records will no longer be 75 s; the number to re-derive is the count.

## Refusals and exclusions I checked against the rule and found in place

- PHYSICS refusals seen: boot changed since lineage publication (monotonic clocks do not join),
  monitor not sampling (`night_stopped_monitor_outage`), disk low, arm instant and dwell verdicts.
- NUMBER_INTEGRITY exclusions seen: `whole_window.member_failures_unreadable` (P4),
  `calibration.historical_custody_mismatch` scoped to relied captures, `calibration.ledger_snapshot_refused`,
  `member.whole_window_member_failure`, `_hazard_member_lineage`, `_hazard_calibration_binding`,
  the os_build epoch at arm.
- Flags that used to refuse and now disclose, all correctly: `records.lineage_prelaunch_mismatch`,
  `records.pin_ledger` (pack-root layout), `env.member_guard_flagged` (`collector_raised`),
  `member.stderr_uncopied`, `calibration.historical_custody_mismatch_unused`,
  `calibration.historical_custody_unmeasured` (evicted), `battery.assist`,
  `battery.capture_pair_assist`, `calibration.capture_battery_assist`.
- The opposite failure (a physics or number hazard turned into a flag): none found. Charging, AC loss,
  the charge accumulator, missing battery evidence, clock step overlap, thermal pressure and
  contention holes all still exclude; the foreign-member and byte-mismatch refusals all still raise.
