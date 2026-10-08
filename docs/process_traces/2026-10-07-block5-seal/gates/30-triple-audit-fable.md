# Pre-arm full-system audit (#416), blind seat: Fable 5.1

Head audited: `/Users/edr/code/JouleWise-wt-int4` at `a434e363d96621318657418e60b8d14410079d82` (checked with `git rev-parse HEAD`).
Registration read: `/Users/edr/code/JouleWise-wt-ia-claim/configs/campaigns/v5_claim_25g83/` at `f3473b7a7`
(registration_block5.md revision 6, analysis_plan_block5.md revision 5, flag_catalog.json sha256 `94e127780ddb...`).
Read-only in every repository. Scratch and probes under `/Users/edr/night-archive/gate-prune/triple-audit/fable/`;
TMPDIR `/private/tmp/audit-fable`. No powermetrics, launchctl or sudo was run. No other seat's directory was read.

## Verdict: ARM-READY (no BLOCKER), with four MAJOR findings that should be fixed before the first claim window

No input was found under which a wrong number reaches a claim through the collection and harvest path, and no
likely input under which a real window loses all its data to a non-physics condition. Four MAJOR findings describe
less likely inputs that do lose a whole window (F1, F2, F3) and one analysis-time gap that would let an excluded
member's energy into a reported mean if the analysis ran at this head (F4). Each MAJOR fix is small (a catalog
effect change plus a short harvest or driver change); none changes a number-bearing estimator.

Two preconditions the registration already names must hold before ALPHA-1 arms (not code defects, listed so the
order is explicit): the sealed inventory must be filled (N1) and the L9 exclusions consumer must land before the
blind dry run (F4).

## Findings table

Severity: BLOCKER none. MAJOR 4. MINOR 7. NOTE 3. Evidence: EXECUTED = a probe or test I ran, or a flag observed in
the real rehearsal archive at `night-archive/gate-prune/rehearsal-real/` (structure fields only); READ = code reading.

| ID | Sev | File:line | Trigger (concrete input or state) | Wrong output | Minimal fix | Evidence |
|---|---|---|---|---|---|---|
| F1 | MAJOR | `joulewise/b5/harvest.py:4230-4232` (`whole_window`), catalog `whole_window.verdict_absent` = EXCLUDE_WINDOW | `whole-window-verdict.json` is absent at harvest. Non-physics ways to get there at this head: the ledger pin was not advanced before the harvest (`_desk_pin_problem`, 4652-4692: `pin_behind`, `pin_uncommitted`, `pin_unreadable`); the desk writer's bracket-binding build raised (4512-4516; observed on real rehearsal gamma-2: `producer_failed step=bracket_binding`, `calibration.binding_failed error_type=ValueError`); the writer child timed out or could not spawn (4524-4535, 4549-4561); `run_campaign --whole-window-verdict` raised `ValueError` before appending its row (`scripts/run_campaign.py:8231-8305`: membership, bracket-binding or calibration-snapshot validation). | `exclusions.compute` sets `claim_usable=false` on this one code (probe P1). Registration 7.2: the scheduler reads only `claim_usable`, so the pack is re-armed and every member of the window is never analysed. A record that could not be written removes a whole window. | Catalog: `whole_window.verdict_absent` -> DISCLOSE. Harvest: when the verdict is absent, run the NEG-8 screen itself from the bound root and the manifests (the `_neg8_rescreen` machinery at 4378-4470 already re-derives the bracket through `ww._derived_neg8_decision`; call it without a stored bracket) and emit `neg8.screen_failed` / `neg8.bound_not_derived` (NUMBER_INTEGRITY, already EXCLUDE_WINDOW) only when the screen cannot be derived. Member idle-admission failures are already carried per bundle by the reducer precheck (`member.target_phase_precheck_failed`). | EXECUTED (probe P1; rehearsal gamma-2 and gamma-1 flags) + READ |
| F2 | MAJOR | `joulewise/b5/harvest.py:4266-4271`, catalog `whole_window.member_failures_unreadable` = EXCLUDE_WINDOW | A verdict with `status != "passed"` whose `member_failures` is absent, or fails `whole_window._validated_member_failures` (5766-5840) on any schema deviation: a record whose keys are not exactly `{member_id, reason_code, detail}`, a `detail` longer than `MEMBER_FAILURE_DETAIL_MAX_CHARS`, an unsorted list, a repeated pair, or a reason code outside `PROSPECTIVE_MEMBER_FAILURE_REASON_CODES`. | `claim_usable=false` (probe P2). A malformed diagnostic list removes a whole window whose member bundles are intact. | Catalog -> DISCLOSE. Derive per-member failures from each bundle's own records (the reducer precheck and `environment_admission`), not from the verdict row; keep `member.whole_window_member_failure` for the listed case. | EXECUTED (probe P2) + READ |
| F3 | MAJOR | `joulewise/b5/driver.py:1283-1286` (`HazardCensus.__call__`), `CENSUS_UNMEASURED_STOP_AFTER = 4` (line 105) | Four consecutive in-window censuses are "unmeasured": each is 1 + 3 retries of `pgrep -lf '[c]odex|[c]laude|[t]3'` returning empty stdout with exit != 1 (timeout 124, spawn 127, exit 0/2/3, or a probe error; `classify` 1227-1233). About two minutes of a failing `pgrep` spawn. | The driver stops the chain (`night_stopped_census_unmeasured`). A stop before the post calibration gives `calibration.no_bracket` (registration 6.5 names "the census" as such a cause), so the whole window is lost on a failed probe, not on a measured hazard. The contention module measures the physical quantity (outside-process CPU share) directly during every member. | Flag only: keep `census.unmeasured` (already emitted, 1265-1281) and drop the stop; keep the stop for a POSITIVE census (doctrine). Remove the `STOPPED_CENSUS_UNMEASURED` entry from `configs/gates/hazard_refusals.json`. | EXECUTED (probe P3: exit 124 four times -> `night_stopped_census_unmeasured`) |
| F4 | MAJOR | `joulewise/paper_reported_energy.py:420-424, 433-436` (`_project_cell`); no module under `joulewise/analysis_engine/`, `joulewise/detection_floor.py`, `joulewise/floor_extraction.py`, `scripts/extract_detection_floors.py`, `scripts/finalize_analysis_manifest.py` or `scripts/mint_floor_artifact_generalized.py` reads `derived/exclusions.json` (grep: 0 hits) | A window whose `exclusions.json` removes a member for physics (for example `battery.member_span` on repeat 3) while the other 49 members are kept and the cells stay resolvable (8 of 10). Analysis plan 2.2/4 (revision 5) says the kept-unit estimator applies: `m = 0.2*fmean(r) + 0.8*fmean(b)`, `V = 0.04*s_r^2/n_r + 0.64*s_b^2/n_b`, `t(0.975, min(n_r,n_b)-1)`. | At this head the issuer takes exactly 50 rows in fixed positions (repeats 0-9, quads 10-49), computes `fmean(energy)` over all 50, `s_r`/`s_b` over 10 and 10, `df 9`, and no program removes the excluded member first. A member the harvest excluded for charging enters the printed mean and interval. The plan calls this the L9 consumer (`FILL`) and schedules it before the floor rehearsal and the blind dry run, so this is not an arm blocker, but it is a wrong-number path if the analysis ran today. | Land L9: the issuer takes the kept-unit list from `exclusions.json` (pinned by SHA-256), refuses any member set that differs from it, and implements the stratified m, V and t with `n_r`, `n_b` from the kept units; add a synthetic fixture with one excluded repeat and one excluded quad member. | READ |
| F5 | MINOR | `joulewise/whole_window.py:4326-4333` (`_raise_on_refusals`), called by `_mint_hazard_neg8_drift_bound` 4404-4405; harvest `neg8.bound_not_derived` 4082 (EXCLUDE_WINDOW) | A NEG-8 corpus member whose bundle bytes and energies are intact but whose record fails a representation check: `launch_lineage:<reason>` (4240-4252), `calibration_identity_unrecorded` (4294), `bundle_inventory_invalid` (4299). The mint raises, `--derive-neg8-drift-bound` exits nonzero, no bound artifact is written. | `neg8.bound_not_derived` (`problems: bound_artifact_absent`) removes the window although 10 or more members with valid numbers exist. | Treat those three as drops (`neg8.corpus_member_dropped`, DISCLOSE) when at least `NEG8_DRIFT_MINIMUM_N` remain; keep `not_canonical_condition` and `condition_differs` as refusals (they are about which condition the number measures). | READ (the rehearsal `bound_artifact_absent` cases were truncated windows, not this trigger) |
| F6 | MINOR | `joulewise/b5/harvest.py:5031-5033`, catalog `model.identity_unpinned` = EXCLUDE_WINDOW | `identity_pins.json` or the plan tree carries no `model_artifact_sha256` for an identity unit (registration 6.5: "the measurement checkout lacks identity_pins.json"). | A pin-ledger shape removes the window, although every member's `model_artifact_sha256` and `runtime_identity_sha256` are derived and recorded (5047-5049) and in-window consistency is checked (`model.identity_inconsistent_in_window`). Doctrine item 2 names pin-ledger matching a flag. | DISCLOSE, plus a block-level consistency check at analysis (every analysed window's identity units equal). Present at this head: `configs/campaigns/v5_claim_25g83/identity_pins.json` exists, so it should not fire; the classification is the defect. | READ |
| F7 | MINOR | `joulewise/b5/harvest.py:3897-3900` (`calibration.session_not_bound`), `3957-3963` (`calibration.binding_failed`), both EXCLUDE_WINDOW | `session_not_bound`: any of plan_id, plan_sha256, runs_root string, window_id or evidence_root_id differs between the bracket session row and the plan (3891-3896). `binding_failed`: any exception from `brackets.build_calibration_bracket_binding` (observed on gamma-2: `ValueError`, downstream of an invalid post slot). | A binding record or a path string removes the window. The physical facts (a pre and a post capture, each valid, passing acceptance) are checked separately by `capture_invalid`, `bracket_acceptance_failed` and `no_bracket`. | DISCLOSE both, and add one NUMBER_INTEGRITY check in their place: the session's pre capture span ends before and its post capture span starts after this window's member spans (monotonic domain), else `calibration.no_bracket`. | READ + EXECUTED (gamma-2 flags) |
| F8 | MINOR | `joulewise/hazards/arm.py:355-357` (`_refusals` counts UNMEASURED), `joulewise/hazards/thermal.py` docstring and `judge` ("a failed, timed-out or unparsable read is UNMEASURED and refuses"), `joulewise/hazards/instrument.py:139-145`, `joulewise/b5/driver.py:2223-2227` (`REFUSED_INSTRUMENT_NOT_SAMPLING` when the hazard monitor does not journal within 20 s x 3) | One `notifyutil -g` read fails at the instant or final step; or the hazard monitor process is slow to write its first battery and contention line. | The arm returns NULL on a failed probe, not on a measured hazard. No data is lost (nothing was collected); one arm cycle (cadence probe plus dwell, up to about 47 min) is spent. | For the thermal and battery instant/final reads: retry up to N times, then record and go on (the monitor reads the level every 5 s inside the window and the member join excludes on a nonzero level). Keep the instrument cadence probe's refusal: it is the instrument. Keep the monitor-readiness check but re-read the journals once more after the chain start instead of refusing. | READ |
| F9 | MINOR | `joulewise/flags/exclusions.py:194-200` (member-level EXCLUDE_MEMBER with a `run_id` not in the roster goes to `unmatched` only); line 366 counts it; nothing at this head reads `flag_counts.unmatched_member` (grep in `joulewise/b5/harvest.py`, `joulewise/flags/`, `joulewise/analysis_engine/`: 0 consumers) | A member-level exclusion flag whose `scope.run_id` differs from the roster `run_id` (the verdict's `member_failures` use bundle ids; the roster uses plan run ids; equal today because `driver.py:1393` requires a run id to be a bundle directory name). | The exclusion is silently dropped: `claim_usable` stays true, `release_blocked` false, `members_excluded` empty (probe P4). Latent number-integrity hole behind one naming drift. | Harvest: a `HarvestFault` (or a never-classified code) when `unmatched_member > 0`; it is a tooling condition, re-runnable, not a collection stop. | EXECUTED (probe P4) |
| F10 | MINOR | `joulewise/controller.py:310-318, 406-412`, catalog `instrument.binary_identity_unmeasured` = EXCLUDE_MEMBER | `_runtime_powermetrics_digest` raises for one member (the binary's bytes could not be hashed). | The member is removed on a failed probe. The binary's identity is the OS build's, read at arm (`arm.py identity_read`, refusing only an epoch no acceptance judged) and identical for every member of the window. | DISCLOSE; keep the attachment's refusal for a present digest that differs from the calibrated one (that is a number fact). | READ |
| F11 | MINOR | `joulewise/b5/harvest.py:3793-3800`, catalog `member.cooldown_evidence_unverified` = EXCLUDE_MEMBER (BASELINE in `hazard_refusals.json`) | `campaign_cooldown_evidence` has no record for the member, or its `verified` is not true, while the member succeeded. | A missing or unverified cooldown record removes a member whose idle baseline was measured directly (idle admission, `member.idle_window_suspect`) and whose cap hit has its own code (`member.cooldown_cap_hit`, physics). | DISCLOSE (`cooldown.result_unknown` already exists for the writer). | READ |
| N1 | NOTE (precondition) | `joulewise/b5/harvest.py:4843-4847` (`pack.identity_unmeasured`, `missing_input: sealed_inventory`), `4997-5001` (`code.identity_unmeasured`); `resolve_inputs` 1319-1321 defaults the path to `<measurement_root>/configs/campaigns/v5_claim_25g83/sealed_inventory.json` | At `a434e363` the measurement root has no `sealed_inventory.json` (the directory holds `identity_pins.json` and `sizing_b5.json` only); the draft in wt-ia-claim is `STUB_NOT_SEALED` with `files: null`. | Every window harvested at this head is not claim-usable by design (the stub says so). | Registration 2 item 3: seal before ALPHA-1 arms. | READ |
| N2 | NOTE | `joulewise/flags/exclusions.py:302-316`, `cell.below_minimum` EXCLUDE_WINDOW | Three of ten repeats of one cell excluded (any member codes) with the other cells intact. | The whole window is re-armed, including its resolvable cells (probe P5: 2 excluded keeps the window, 3 removes it). Registered design (fixed-n, 6.6). Statistical power, not number integrity. | None required. A later revision could make claim-usability per cell so a window's resolvable cells are analysed. | EXECUTED (probe P5) |
| N3 | NOTE | `joulewise/b5/driver.py:2343-2370` (`STOPPED_MONITOR_OUTAGE`, 600 s without an error-free battery or contention journal line) | The hazard monitor's journals stay silent or unreadable for 600 s despite the 1 s restart supervision. | The chain stops; without the post capture the window is lost. The monitor is a process, not the energy instrument, so this is one step removed from "the instrument not sampling"; but with it dead every member in that period is `battery.unmeasured` / `contention.unmeasured` (EXCLUDE_MEMBER), so continuing would keep no member unless it recovers. | None required now; revisit if the monitor ever restarts for more than a few seconds in production. | READ |

Doctrine check on the other EXCLUDE_WINDOW codes (all read): `calibration.capture_invalid`, `bracket_acceptance_failed`,
`no_bracket`, `acceptance_mismatch`, `historical_custody_mismatch`, `ledger_snapshot_refused` (bytes differ from a
recorded digest, or no drift bound: NUMBER_INTEGRITY); `calibration.capture_battery_*`, `clock.step_overlap_calibration`
(PHYSICS); `clock.systematic` (a majority of anchors unbounded: the number cannot be placed in time);
`code.executed_differs_from_sealed`, `pack.identity_mismatch`, `lineage.plan_tree_digest_differs`, `model.identity_mismatch`,
`model.identity_inconsistent_in_window` (executed code, pack or model differs from the sealed one: NUMBER_INTEGRITY);
`*.identity_unmeasured` (registration 7.2 supersession and the harvest's `supersede_identity_unmeasured` at 5599-5645 cure a
collector error; a harvest that itself cannot measure is re-run by R3); `records.source_changed_during_harvest`,
`roster.duplicate_run_id`, `roster.no_science_bundles`, `instrument.precal_screen_failed`, `neg8.screen_failed`
(NUMBER_INTEGRITY). The member codes in `hazard_refusals.json` `member_exclusions` are physics in span or number validity
except F10 and F11 above and the BASELINE `member.strict_validation_failed` / `member.target_phase_precheck_failed`, which
I read as number validity (a bundle that does not validate has no trustworthy number) and did not probe further.

Pinned estimators read without a finding: `adapters/powermetrics.py` parser (first-record-endpoint anchor, interval
supports, a truncated final frame dropped and recorded), `reduce.py` `_integrate` / `_phase_energy` / identifiability
(`MIN_PHASE_SAMPLES`), the harvest's `member.reduction_mismatch` (stored summary re-reduced byte for byte) and
`member.anchor_recompute_mismatch`, the exclusion function's blindness (reads code, scope, interval and flag_id only).

## Probes (EXECUTED)

All with `/opt/homebrew/bin/python3.13`, `TMPDIR=/private/tmp/audit-fable`, the sealed draft catalog from wt-ia-claim
(`cell_unit_minimum 8`), a synthetic roster of 10 repeats and 10 quads in one target cell (the probe source is in this
report's shell history; the re-derivation script is `rederive_d078_r01.py` beside this file).

- P1 `whole_window.verdict_absent` alone -> `claim_usable False`, `reasons ['whole_window.verdict_absent']`.
- P2 `whole_window.not_passed` + `whole_window.member_failures_unreadable` -> `claim_usable False`.
- P3 `driver.HazardCensus` with a probe returning exit 124 and empty stdout: calls 1-3 flag `census.unmeasured` and
  continue; call 4 returns `Refusal('night_stopped_census_unmeasured')`. `classify` gives `unmeasured` for exits 124,
  127, 0, 2, 3 and -1.
- P4 one `battery.member_span` at level member with `run_id='not-a-member'` -> `claim_usable True`, `members_excluded []`,
  `unmatched_member 1`, `release_blocked False`.
- P5 two repeats excluded -> `claim_usable True`, `n_repeats 8`; three -> `claim_usable False`, `reasons ['cell.below_minimum']`.
- P6 a member with no span plus a stage-level interval `thermal.os_level_nonzero` -> that member excluded,
  `span_unknown ['m0']` (the conservative rule works as documented).

Unit tests run at this head (all OK): `tests.flags.test_flags_exclusions` + `tests.flags.test_flags_catalog` (31 tests,
1 skipped); `tests.hazards.test_refusal_allowlist` (22; the allowlist matches the census at this head);
`tests.test_adapters_powermetrics` + `tests.test_audit_powermetrics_parser` + `tests.test_audit_reduce_degenerate` (11).
`tests.test_harvest_b5_window`: see the last section.

Real rehearsal evidence (structure fields only, `night-archive/gate-prune/rehearsal-real/*/archive/derived/`): alpha-1
(13 members assessed) fired `whole_window.verdict_unauthenticated`, `neg8.screen_failed`, `neg8.bound_not_derived`
(`bound_artifact_absent`), `calibration.capture_battery_pair_failed` (post slot, current reason) and 13
`contention.request_overlap` (agent sessions were alive by rehearsal override); gamma-2 (11 assessed) fired
`whole_window.producer_failed step=bracket_binding`, `whole_window.verdict_absent`, `calibration.binding_failed ValueError`,
`calibration.capture_invalid post`, `roster.duplicate_run_id neg8-window-midpoint` (three stages launch one run id; one
bundle per run id, so later positions are never measured: a plan fix is due, the exclusion itself is NUMBER_INTEGRITY).
No `member.whole_window_member_failure` fired, so HAZARD members do record admission evidence the verdict accepts.
`unmatched_member` was 0 and `span_unknown` empty in all three.

## Re-derivation from raw bytes

Number: the decode-phase energy of the fixture bundle `tests/fixtures/d078_r01` (`summary_metrics.json`
`phase_energy_j.decode = 0.18577080959892273` J), and the prefill-phase energy beside it. Script
`rederive_d078_r01.py` (this directory; output in `rederive_output.txt`) reads only `raw/powermetrics.plist`
(NUL-framed plist stream, 9 complete frames), `events.jsonl` (phase markers) and one scalar from `metadata.json`
(`uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s = 1784491122.299285`), using `plistlib` and `json` only.

Construction, as `adapters/powermetrics.py:_parse_powermetrics_records` (first-record-endpoint mode) and
`samples_from_records` define it: record 0 ends at the anchor; record i > 0 ends at anchor + sum of elapsed_ns(1..i) / 1e9;
each record's support is [end - elapsed_ns/1e9, end]; power per rail is `processor.<rail>` mW / 1000. Energy over a window is
the sum over records of P_total x overlap(support, window) (`reduce.py:_integrate`, interval-support branch, `math.fsum`).

Decode window from the markers: [1784491122.941782, 1784491123.179361], 0.237579 s. Three records overlap it (GPU and
ANE rails read 0.0 W on all of them):

| record support (s) | overlap (s) | CPU power (W) | energy (J) |
|---|---|---|---|
| [1784491122.867825, 1784491122.981352] | 0.039570 | 0.528508 | 0.020913111 |
| [1784491122.981352, 1784491123.096162] | 0.114810 | 0.984234 | 0.112999896 |
| [1784491123.096162, 1784491123.210072] | 0.083199 | 0.623300 | 0.051857803 |

Sum (fsum) = **0.18577080959892273 J** = stored `phase_energy_j.decode`; difference 0.0.

Prefill window [1784491122.8089201, 1784491122.941777], 0.132857 s: 0.058905 s x 0.829471 W = 0.048859697 J plus
0.073952 s x 0.528508 W = 0.039084328 J; sum **0.08794402541351319 J** = stored `phase_energy_j.prefill`; difference 0.0.

Cross-check of the trace the controller wrote: `power_trace.csv` row 1 (`end 1784491122.299285, cpu_w 0.143114,
start 1784491122.1874862`) equals the raw first record parsed independently. The first frame's elapsed (111.8 ms) is the
sampler's start-up interval and is clipped by the phase windows, as designed.

## Process note

No whole suite; no powermetrics, launchctl or sudo. One unit-test module (`tests.test_harvest_b5_window`) outlived the
tool's 120 s foreground limit and was moved to the background by the harness; its result or termination is recorded below.

`tests.test_harvest_b5_window` at `a434e363`: 168 tests, OK, 427 s (non-venv `/opt/homebrew/bin/python3.13`,
TMPDIR `/private/tmp/audit-fable`). It exited by itself; no process started by this seat remains
(`ps` shows none).
