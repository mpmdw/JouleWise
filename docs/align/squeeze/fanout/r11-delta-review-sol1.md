# R11 delta review — Sol1

Task dated 2026-11-08; executed 2026-11-07 PST. Seat/branch:
`align/2026-11-08-v4-r11-delta-sol1`. Reviewed candidate:
`353446ad649be7c9b092ff77e7bc114de0732a6c`; comparison:
`git diff c3796bf49..353446ad6` (29 paths).

**Verdict: HOLD. Two HIGH and three MED findings have five failing-first
synthetic witnesses in `tests/align/test_r11_delta_sol1.py`.** The twelve
existing touched test modules pass (350 tests). This admits neither W1
registration nor an arm. No product code was changed by this review.

## Authority, scope and safety

Read the local AGENTS/CLAUDE conventions, M0, stop card (NONE), queue and
do-not-do sections, workspace state, orchestration, targeted D-050/D-064/
D-170 text, protocol, dispositions and relevant implementation. The explicit
review brief supersedes ordinary queue selection, full-suite execution and
coordination writes. The provisioned review branch was already at the
requested candidate and initially clean; it is distinct from the source
branch. No additional agent was invoked.

Authority and prior reviews were read from local Git objects, without fetch:

- `origin/main` at `319f6a51d5707b96799b9230ec63a446c7a12dab`, RUN_STATE
  items 214–216, including the confirmed packet schema and zero-capture rule.
- Both `origin/align/2026-11-08-v4-r11-review-sol{1,2}` reports and their
  original failing-first witnesses; `docs/align/squeeze/fanout/r11-dispositions.md`.
- Both `origin/perf/2026-11-08-r12-review-sol{1,2}` reports, especially their
  next-arm prerequisites, final-count boundary, manifest/F-C-T requirements,
  exchangeability cautions and R1 deadline reliance path.

Coverage is this delta and the necessary call paths, not the historical
main-to-candidate stack. No network, weights, native MLX, real measurement
data, sealed paths, Block-5 pipeline or live job inspection was used.
Absolute data paths in repository text were not followed. Host-state tests
used temporary overrides or mocked probes; no machine settings were changed.
Coordination files and the R1 lane were left untouched.

## Original findings

| Original finding | Delta assessment |
|---|---|
| S1-H1, executable U6 route | The specific legacy-route defect is fixed. `session_desk_evidence(v4=True)` calls `monitoring_stability_v4`; the v4 CLI opts in explicitly. The route uses half-s_r, clustered uncertainty and position means; missing scale/split/trajectory identity is inconclusive. The legacy-shaped slope result is refused by v4 acceptance. This is implementation evidence, not final-roster U6 OC qualification. |
| S1-H2, completed-top-up timing | Fixed. Required CLI completion/source fields reach `battery_arm`, with finite time, missing/future/stale refusal and the lead-ruled inclusive 1,800 s bound. Raw observation freshness no longer substitutes for completion timing. |
| S1-M1, H* dose identity | Fixed for the reported cases: fractional, negative, boolean, duplicate and nonfinite-score rows refuse instead of truncating or overwriting. |
| Sol2 F01, cache implementation omitted from receipt | The cache-specific witness now passes. Cache, adapter, sampling and parser code are bound. **The broader executed-code admission requirement remains incomplete: H01 below.** |
| Sol2 F02, zero-turn X-G | Fixed. Zero compared turns can be retained only as failed/incomplete/nonidentical identity with the INCONCLUSIVE predeclaration; cannot become PASS. No new D veto is imposed by the WP19 validator. |
| Sol2 F03, incomplete H* grid | Fixed. A missing earlier registered dose leaves the first crossing undefined; strict exceedance remains. |

The required original witness commands pass: Sol1 **5/5**, Sol2 **4/4**.
The revised U6 path also has direct passing/shift/imprecision controls in
`test_thermal_desk`; merely passing the old witness's missing-s_r case would
not have established that route.

## New findings

### H01 — HIGH: launched W1 code can still change behind an admitted receipt

`v4_registration.py:37` describes the closure as restricted to `joulewise/`.
`test_v4_executed_closure.py:68` drops reachable `scripts/` files before
checking coverage. But `joulewise/b5/chain.py:145` selects
`scripts/run_campaign.py` as `campaign_runner`; `:536` constructs the actual
measurement-interpreter command for it. That file is absent from ARTIFACTS.
This is a known, concrete execution edge, not a hypothetical dynamic import.

Witness: `ExecutedReceiptWitness.test_changed_launched_campaign_code_requires_a_new_gate`
(`test_r11_delta_sol1.py:68`). A temporary Git repository has every bound
artifact, both synthetic admitted reports and a valid receipt. A later clean
commit changes only `scripts/run_campaign.py`. Expected refusal does not
occur. This repeats F01's ordinary later-code-drift scenario beyond the
repaired cache path. The candidate code pin alone does not establish that
the old gates reviewed the new implementation.

The dispositions openly disclose exclusion of reached scripts; disclosure
does not make this a full executed dependency binding. Bind the actual
launched scripts and their measurement-relevant dependencies, including
shared runner/bracket/terminal paths, or adopt an explicit candidate/source
manifest that covers them. Keep third-party/version qualification separate.
The pending receipt and U3 gate still prevent a present-day W1 arm; this is
a latent admission defect, not evidence of an arm that occurred.

### H02 — HIGH: contradictory capture counts can authorize test entry

`v4_cadence.py:195` validates integer captures and per-pair ranges separately;
`:204` checks consistency only for zero captures. It never requires the sum
of eligible benign members to be at most the number captured.

Witness: `CalibrationEvidenceWitnesses.test_eligible_members_cannot_outnumber_captured_members`
(`:79`). Six final rows each declare one captured member and seven eligible
benign for each pair. The predicate returns `stop_complete`, 42/pair, from
six total captures. `next_arm_triage` accepts that stop for a test role.
This can be an ordinary count/export mismatch; it requires no invented
scores or deliberate falsification.

Refuse internally impossible count rows before evaluating the stop. The
count packet remains lead-owned evidence, but the derived gate should not
admit a contradiction it already has enough information to detect.

### M01 — MED: an unfinished zero-capture window disappears from the pending gate

`v4_cadence.py:204` classifies every zero-capture row as a refusal, even when
its status is `provisional`; it removes the row before `counts_are_final`
and the pending boundary are computed at `:219`.

Witness: `CalibrationEvidenceWitnesses.test_zero_capture_provisional_window_is_not_a_terminal_refusal`
(`:85`). Six final windows have 36/pair. C7 is provisional, with zero
captures and zero eligible counts: for example it is still in flight before
its first capture. Actual decision is `continue`, with `counts_are_final=True`,
rather than `pending_final_eligibility`. A calibration role is therefore
permitted despite an unresolved window after the six-window boundary.

R216 excludes a **zero-capture refusal**, not an unfinished window, from the
cap. Distinguish terminal refusal from pending zero-capture execution and
retain the latter in the no-further-arm check. Preserve the ruled exemption
for final zero-capture refusals and the two-consecutive-refusal escalation.

### M02 — MED: an internally inconsistent W1 packet can waive the full desk

`v4_cadence.py:89` accepts a previous-window identity, but `:108` derives
the desk requirement exclusively from the independent boolean flags.

Witness: `TriageEvidenceWitnesses.test_previous_w1_cannot_defer_desk_with_a_conflicting_flag`
(`:94`). The packet explicitly names previous window `W1`, but leaves
`previous_window_is_w1=False`, `code_or_config_changed=False` and the full
desk `deferred`. Actual admission is True. A stale boolean defeats the
unconditional post-W1 desk requirement even though the packet identifies W1.

Derive/cross-check that flag against the previous window's registered role;
refuse contradictory packets. Binding the packet to the actual previous
record, next planned arm and last desk-passed configuration would also avoid
ordinary reuse mistakes. The lead's confirmation of the schema does not
supply such a consistency check.

### M03 — MED: the arm record loses the calibration evidence it claims to retain

Protocol `pilot_protocol_v4.md:813` says the packet is retained in
`staging/v4-arm-NNN.json`. Instead, `arm_checks` stores only the evaluated
triage (`align_v4_session.py:304`–315); `next_arm_triage` retains only a stop
decision/role, not its input history or even the stop's count summary
(`v4_cadence.py:124`, `:148`). `_arm_and_install` writes this reduced record
at `align_v4_session.py:557`; it does not save or hash the packet elsewhere.

Witness: `TriageEvidenceWitnesses.test_arm_retains_evidence_distinguishing_two_calibration_histories`
(`:101`). Two valid six-window histories with 39/pair and 42/pair both admit
test. With every arm probe mocked identically, their complete arm records
are identical. Neither history, the eligible counts, final/provisional
statuses, zero-capture accounting nor packet digest can be recovered from
that record. A mutable CLI input file is not retained custody.

Retain the count-only packet or a digest-bound immutable copy, plus the
derived stop summary, so admission can be replayed. No score disclosure is
needed to fix this.

## R12, closure breadth and R1 backfills

**B1:** Correctly distinguishes the 40,527 s programmed span from the
59,520 s authorized ceiling, preserving authenticated terminal release,
all stages/brackets/cleanup, custody and quiet admission. The earlier R12
reviews found existing early-return machinery; this text does not demonstrate
a newly measured saving. This review did not certify any installed wrapper
or terminal release.

**B2:** The fourteen-entry list names the missing next-arm prerequisites,
including U1–U3 escalation/pool rules, U4/U5 sentinel changes and final
eligibility. All entries gate, and arm-owned power/volume/battery checks
cannot be supplied by the packet. Missing/failed entries refuse. The
full-desk exception is implemented for correctly flagged packets, subject
to M02; retention is incomplete (M03). Packet `pass`/basis fields are
lead-owned assertions: the validator does not itself calculate U1–U5 or
verify the underlying records. I have not treated that confirmed manifest
design as a hostile-input forgery defect.

**B3:** The normal minimum-six/cap-eight, both-pair >=39, first qualifying
prefix, no ninth counted attempt, final-count wait and insufficient outcome
work for consistent completed histories. Final zero-capture exemptions and
trailing two-refusal escalation follow R216. H02/M01 are boundary gaps.
The unadopted >=6 sabotage target has correctly not become an implicit stop.
The code does not validate a frozen ordered C1–C8/T manifest; those actual
roles/seeds/fit deductions remain lead-owned and absent here. The text's
separate simulation/scorer/rank/dependence qualification remains a pre-W1
hold, not evidence supplied by this predicate. Neither fresh counts nor a
successful simulation alone proves live exchangeability.

**Receipt breadth/brittleness:** There are 221 ARTIFACTS, 188 entries in the
hard-coded EXECUTED_CLOSURE, and 197 `joulewise/` files in the recomputed
static closure (the named artifacts cover the remainder). The guard and
template agree. The walk includes all lazy imports regardless of which
campaign branch uses them, and the receipt binds 5 B5 and 29 B6 paths.
For example, the B6-only analysis import at `b5/harvest.py:3841` pulls in
`joulewise/b6/analysis_lane.py`. A clean change to that file causes receipt
digest refusal: `DeltaControls.test_receipt_currently_couples_b6_only_analysis_changes`
passes as a characterization. Thus **some unrelated B6 changes do force a
new candidate receipt/gates**, not every change anywhere in B5/B6. Shared
measurement dependencies must remain bound. Prefer a stable, reviewed
execution manifest/explicit branch-aware dependency policy over simply
deleting B5/B6 coverage. This coupling is a nonblocking design cost; H01 is
the blocking undercoverage. The static walk also cannot establish coverage
of string imports, subprocess programs or third-party packages.

**R1 sizing:** The helper now computes 56,206.9616 + 11,163.9952 =
67,370.9568 s, ceil **67,371**; adding 29,055.9808 s of R6-2 retries gives
96,426.9376 s, ceil **96,427**. An independent invocation of the actual
`wait_outside_os_batch` with an injected advancing clock at 10:30 PST on
November 8 waits **9,900 s**, ending at 13:15, without sleeping. The helper
and amended texts correctly call these one-encounter subtotals/floors,
excluding brackets, close/harvest and further encounters/redos. No launch
packet was inspected: actual t0, segments, retries, blackout encounters,
enclosing deadline and idle-accounting caveat still need the lead's audit.

**Backfills:** The lane-shaped integration now strips the fields absent from
the older R1 writer, refuses unbackfilled input and admits only after the
two explicit lead backfills. `backfill-x-g` copies whitelisted result fields,
checks the recorded G0 outcome/wait, records the result SHA and refuses
overwrite. `backfill-turn-counts` requires exactly the three gated run names,
integer bounded counts, matching lengths/totals/admitted turns, booleans,
source SHA and no overwrite. `kit.turn_opportunity` additionally refuses
unfinished nonfinal turns and evaluates the chosen B_D; missing evidence
stays inconclusive. I found no new end-to-end admission defect in these
backfills. This is synthetic interoperability evidence, not independent
verification that a lead export was derived from the correct live bundle.
Hashes bind the supplied export; the lead must retain its source bytes and
derive actual counts, never synthesize them from aggregate totals as a live
backfill.

## Verification

Each row used its own command/process:
`python3.13 -B -m unittest tests.align.<module>`.
The three R1 modules and `test_v4_kit` used
`JOULEWISE_HOST_STATE_DIR=/private/tmp/jw-r11-delta-sol1-host`; arm tests also
create their own temporary overrides/mocks. No full suite was run.

| Module | Result | Reported test time |
|---|---:|---:|
| test_r11_review_sol1_witnesses | 5 PASS | 0.002 s |
| test_r11_review_sol2 | 4 PASS | 0.915 s |
| test_v4_cadence | 19 PASS | 0.010 s |
| test_v4_registration | 20 PASS | 21.690 s, then serial repeat below |
| test_v4_executed_closure | 2 PASS | 3.740 s, then serial repeat below |
| test_v4_estimands | 15 PASS | 0.004 s |
| test_thermal_desk | 25 PASS | 2.504 s |
| test_v4_r11 | 27 PASS | 0.399 s |
| test_v4_kit | 116 PASS | 12.171 s |
| test_r1_rehearsal | 74 PASS | 8.060 s |
| test_r1_round6_power | 25 PASS | 0.362 s |
| test_r1_round7_science | 18 PASS | 0.352 s |
| test_r11_delta_sol1 | 8 run: 5 expected witness failures, 3 controls PASS | 0.811 s |

Scheduling exception: I initially launched the closure module before the
registration process had finished. Both passed; I repeated those two modules
serially after detecting the overlap. Every other test process was awaited
before starting the next. This was an execution mistake, not an authorized
parallel test plan. Total test time including the repeat is far below twenty
minutes. The review witnesses intentionally remain red for the lead's fixes.

Serial repeats also pass: registration 20 tests in 23.314 s and closure 2
tests in 2.938 s. Python AST parsing of the added witness file and whitespace
checks pass. Commit/handoff details are in
`docs/run_reports/2026-11-08-align-v4-r11-delta-sol1.md`.

## Remaining questions and next exact step

Lead: disposition H01–M03 against the second delta seat, implement the five
bounded repairs, rerun both original witness modules and this new witness
module, then rerun affected modules one per process. Decide the dependency
manifest's intended stable boundary explicitly; do not silently weaken the
exact-candidate guarantee.

Retain the existing scientific/native holds: U3 derivation, final-roster U6
OC, actual C/F/T manifest and scorer/asymmetry/dependence qualification,
continuous volume-audit qualification, battery-window consequence and actual
candidate gates/access chronology. The protocol's PENDING-FREEZE paragraph
at `:467` still mentions equal-pair/Welch conventions while the repaired
route pools turn rows with clustered uncertainty; the exact final weighting,
interval and missing-data treatment need reconciliation at the owning gate.
I did not invent a replacement rule or count this pending convention as a
second proven U6 implementation failure.

Outside this sandbox, on an authorized Metal host, the lead must run the
existing tiny/random native gates, one module at a time with a Python that
has the pinned offline packages:

```sh
python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
python3.13 -B -m unittest tests.align.test_r0_mlx_native
```

No weights need downloading. Passing synthetic tests here does not
replace those gates, live meter/thermal/charging evidence or the installed
deadline audit. This review neither inspected nor interfered with any live
job.

Changed files: this report, `tests/align/test_r11_delta_sol1.py`, and
`docs/run_reports/2026-11-08-align-v4-r11-delta-sol1.md`. No coordination-state
update, kernel registration, product fix, push, merge or publication.
