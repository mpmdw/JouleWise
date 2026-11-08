# R11 delta review — Sol2

**Verdict: HOLD. One HIGH and two MED findings, with five failing-first
synthetic witnesses.** The nine original witnesses now pass. The original
cache-drift example is fixed, but the receipt still does not bind the full
executed first-party stack. The current pending registration/U3 stops remain
in force; the failures below do not demonstrate an actual armed window.

Review date: 2026-11-07 PST; brief and branch dated 2026-11-08. Branch:
`align/2026-11-08-v4-r11-delta-sol2`. Candidate:
`353446ad6`; reviewed range: **`git diff c3796bf49..353446ad6`**, all 29 changed
paths, with targeted execution dependencies. No admission of the inherited
1,117-commit historical range is implied.

Authority read: repository M0/stop-card/workspace/orchestration intake;
`docs/align/squeeze/fanout/r11-dispositions.md`; both original R11 review
reports from their `origin/align/2026-11-08-v4-r11-review-sol{1,2}` objects;
both R12 cross-check reports from
`origin/perf/2026-11-08-r12-review-sol{1,2}`; and **items 214–216 from the local
`origin/main:RUN_STATE.md` object**. Item 216 supersedes item 215's redo figure
and resolves zero-capture cap accounting. Remote refs were not refreshed.

## Findings

### DELTA-S2-H1 — HIGH: executed script bytes remain outside exact-candidate admission

`v4_registration.py:37` restricts the static closure to `joulewise/`.
`test_v4_executed_closure.py:67` deliberately filters out `scripts/` before
asserting coverage. Thus a sound AST traversal still yields an incomplete
execution receipt. This limitation is disclosed in the dispositions; disclosure
does not make these live dependencies irrelevant to exact-candidate R01/F01.

Two concrete executed omissions:

* `scripts/align_pilot_session.py:25,40–47` imports `bytes_h_session` and
  delegates preparation and installation to it. The unbound
  `scripts/bytes_h_session.py:398–427` checks job absence, prepared-plan
  identity and future t0, then invokes the installer/courier. These are live
  W1 session operations, not an unrelated B6 CLI branch.
* `joulewise/b5/driver.py:683–704` constructs the production subprocess argv
  for **`scripts/hazard_monitor.py`**. That entry point is also unbound.
  Binding `joulewise/hazards/monitor.py` alone does not prevent the wrapper
  from changing the config, suppressing invocation or exiting successfully.
  AST imports cannot discover a path embedded in subprocess argv. The same
  inventory issue applies to collector/meter script argv and installer/shell
  entry points; this review does not claim a complete replacement inventory.

Witnesses:
`ExecutedScriptBindingWitnesses.test_receipt_binds_the_actual_prepare_install_helper`
and `test_receipt_binds_the_spawned_hazard_monitor` in
`tests/align/test_r11_delta_sol2.py:89,93`. Each creates and validates an
independent synthetic receipt, commits changed executable bytes for the
omitted script, proves a clean worktree, and expects rejection. **Both fail:
`ValueError` is not raised.** No native program is executed by these tests.
The normal plan/head pin can name the later clean commit while its old
registration receipt continues to validate the earlier review.

Lead action: bind the actual preparation, acquisition, monitoring,
terminal-release and custody entry points, including subprocess/shell edges;
extend the closure regression beyond the `joulewise/` filter. Keep third-party
environment pins as a separately declared boundary. The earlier cache witness
is repaired; the larger executed-closure obligation is still incomplete.

### DELTA-S2-M1 — MED: impossible eligible counts can complete calibration and admit test

`v4_cadence.py:195–206` bounds each pair's eligible count to 0..7, but checks
its relationship to `captured_members` only when that number is exactly zero.
For a positive capture count there is no subset/conservation check.

Six final rows with **one captured member each**, but seven eligible spam
and seven eligible bank members each, return `stop_complete`, totals 42/42.
That claims 84 eligible members from six captures. `next_arm_triage` accepts
the resulting test-arm packet. This is a malformed count export that the new
mechanical predicate can detect without reading any score or energy; it is
not a statistical disagreement about stopping.

Witnesses: `CalibrationCountWitnesses` at
`tests/align/test_r11_delta_sol2.py:108`. A feasible 22-capture/window control
completes normally. The two negative assertions **both fail**: impossible rows
do not raise, and their test triage is admitted.

Lead action: reject rows whose eligible members exceed captures (at least
`spam + bank <= captured_members`, since the pair rosters are disjoint), and
derive/bind the counts from the final eligible-member roster when authoring
the packet. Existing signed/lead-owned evidence remains the trust boundary;
this finding concerns an internally contradictory packet, not fabricated
lead approval.

### DELTA-S2-M2 — MED: a contradictory W1 flag bypasses the mandatory full desk

At `v4_cadence.py:89–108`, `previous_window` and
`previous_window_is_w1` are accepted independently. `desk_required` uses only
the latter and `code_or_config_changed`. A packet explicitly naming previous
window **`W1`**, with a stale `previous_window_is_w1=False` flag and unchanged
code flag, can defer `full_desk_gate`. The actual `arm_checks` path then
returns `admitted=True` with a full desk still running. With the correct W1
flag, the otherwise identical packet refuses.

Witness: `PostW1DeskWitness.test_inconsistent_w1_flag_cannot_defer_required_full_desk_at_arm`,
`tests/align/test_r11_delta_sol2.py:124`. Host commands/state are mocked,
including power-marker access. **Fails** on the final arm refusal assertion.

Lead action: derive previous-window role from the committed series/session
record, or at minimum reject contradictory canonical W1 identity and flags.
Bind code/config freshness to that same record when the packet producer is
qualified. This is ordinary stale packet metadata, not a claim that a caller
can be prevented from deliberately lying in every lead-owned assertion.

## The six original findings

| Original finding | Delta assessment |
|---|---|
| S1-H1: U6 route | **Fixed on the portable-input route.** v4 dispatch calls `monitoring_stability_v4`, uses ±0.5 s_r and the existing trajectory-clustered helper, labels imprecision, prints position means and removes the slope gate. Missing scale/identity/split refuses a PASS; supplied legacy slope-shaped results become inconclusive. Final-roster OC and native adapter qualification are still owed. |
| S1-H2: completed top-up timing | **Fixed.** Source/time-bound completion is required; missing/nonfinite/future/stale timing refuses; exactly 1800 s is allowed. CLI requires completion/source and preserves them in arm evidence. This is an operator/log attestation, not a newly measured charging transition or B-window consequence. |
| S1-M1: H* dose coercion/duplicates | **Fixed.** Actual integer/nonnegative/unique doses and finite scores are checked before insertion; no fractional truncation or duplicate overwrite. |
| Sol2 F03: incomplete H* grid | **Fixed.** An absent earlier registered-grid dose keeps the crossing undefined; off-grid doses are reported; strict exceedance remains. |
| Sol2 F01: cache omitted from receipt | **Original witness fixed; full obligation incomplete (H1 above).** Cache, MLX adapter, sampler, attribution and meter parser now bind. Imported and spawned script entry points still do not all bind. |
| Sol2 F02: zero-turn X-G | **Fixed.** Zero compared turns validate only as failed/incomplete/nonidentical with the explicit INCONCLUSIVE predeclaration; PASS/complete/identical zero-turn variants refuse. |

`tests.align.test_r11_review_sol1_witnesses`: **5/5 pass**.
`tests.align.test_r11_review_sol2`: **4/4 pass**. These are synthetic fixes,
not evidence that the outstanding scientific/native gates have closed.

## R12 assessment against the cross-checks

| Item | Assessment |
|---|---|
| B1 terminal completion | Text correctly retains authenticated terminal result, chain closure, courier and watchdog empty-process latch, all planned stages/brackets/cleanup, custody and quiet admission. 59,520 s is a ceiling; 40,527 s and turnaround/day forecasts remain planning figures. Existing early-return machinery is retained. Actual terminal timing/installed deadlines were not inspected. |
| B2 next-arm dependencies | All 14 named checks are present and gating in ordinary cases, including thermal escalation, cohort/pool exclusion, sentinel changes and final eligibility. Power mode is the frozen series value. Missing, failed, unknown and improperly deferred checks refuse. PACKET entries are lead/off-MBP assertions plus basis strings, not newly implemented evidence evaluators. The required W1 desk exception has M2's consistency gap. |
| B3 minimum/targets/cap | Six minimum, eight counted maximum, both pairs ≥39, all eligible members in the first successful prefix, no later counted attempt, insufficient-at-cap and pending-final-eligibility outcomes are implemented. Zero captures do not count; any positive capture counts even with zero eligible members; two trailing zero refusals escalate. Item 216, rather than the earlier cross-check proposal to count every refusal, owns that choice. M1 exposes a missing positive-capture consistency check. |
| B3 prospective design | Protocol requires frozen C1–C8 order/roles, disjoint locked test, no fit/test reassignment, no ninth counted attempt and a separate exchangeability simulation before W1. It does **not** claim that counts settle R13/R14. No ≥6-sabotage target is invented. Actual series manifest, fit-support allocation, test roster and qualified scorer/simulation remain expressly pending. The pure predicate checks unique IDs and input-list order; it cannot authenticate a frozen manifest that has not yet been supplied. |
| R1 sizing | Correct default helper values: no-redo phases 56,206.9616 s; one-encounter allowance 11,163.9952 s; subtotal **67,370.9568 → 67,371 s**; retry allowance 29,055.9808 s; combined **96,426.9376 → 96,427 s**. Old keys are removed and stale instructions marked. These are conditional one-encounter subtotals/floors; bracket/close/harvest, actual redo schedule and additional encounters remain extra. No installed plan or running R1 lane was touched. |
| R1→W1 backfills | `backfill-x-g` preserves source SHA, checks G0 outcome/wait and refuses overwrite; it is unchanged from the baseline. New `backfill-turn-counts` requires exactly three gated D runs, integer capped counts, Boolean completion arrays, driver-token sum and turn-count agreement, a source digest and no overwrite. Final kit opportunity validation also checks intermediate completion. The repaired lane-shaped integration exercises both synthetic/source labels and both backfills. A digest binds the lead's export bytes; it does not independently prove those bytes were extracted from the intended real bundles. No live export was read. |

The R12 reviews' exchangeability counterexamples remain relevant. The new text
properly leaves selection/dependence, score law, rank and LOTO/full-fit
asymmetry open. A simulation can refute an invalid design; passing a selected
simulation alone does not prove live future-window exchangeability. Neither
this review nor the new count predicate supplies that scientific ruling.

## Receipt soundness and brittleness

The batched blob reader correctly rejects listed-file byte drift in the
focused tests, while avoiding hundreds of Git subprocesses. At this candidate
`ARTIFACTS` has **221 paths** and `EXECUTED_CLOSURE` has 188 entries. The test's
unfiltered static first-party traversal finds **229 paths**, of which **26
script paths are outside ARTIFACTS**. H1 gives two live omissions; subprocess
argv and shell execution add edges that the AST traversal never discovers.
This is not a full executed-closure proof.

It also **overbinds**: an unrelated edit within any listed whole file,
including a comment-only edit in a B5/B6 file, invalidates the old receipt.
The passing characterization
`test_comment_only_b6_file_drift_currently_forces_registration_refresh`
demonstrates `digest drift` for `joulewise/b6/model_files.py`. This does not
mean every B5/B6 file in the repository is bound. The static walk includes
function imports in CLI/other-lane branches, so unrelated maintenance within
that superset can require receipt/gate renewal. That is a conservative
operational cost, not an integrity bypass. Do not reduce it by dropping shared
acquisition/identity/custody code. A lead-approved path inventory plus explicit
process edges can give a clearer boundary than calling this set the executed
closure; exact-byte binding will still deliberately invalidate comment edits
within that boundary.

## Verification

Each selection used its own process, sequentially:
`python3.13 -B -m unittest tests.align.<module>`. Synthetic controls were
`JW_B5_SYNTHETIC_ONLY=1 JW_WP22_FULL=0 JW_REAL_METER_SMOKE=0`.

| Module | Tests | Result |
|---|---:|---|
| `test_r11_review_sol1_witnesses` | 5 | OK |
| `test_r11_review_sol2` | 4 | OK |
| `test_v4_cadence` | 19 | OK |
| `test_v4_executed_closure` | 2 | OK; its `joulewise/` scope limitation is H1 |
| `test_v4_registration` | 20 | OK |
| `test_v4_estimands` | 15 | OK |
| `test_thermal_desk` | 25 | OK |
| `test_v4_kit` | 116 | OK |
| `test_v4_r11` | 27 | OK |
| `test_r1_rehearsal` | 74 | OK |
| `test_r1_round6_power` | 25 | OK |
| `test_r1_round7_science` | 18 | OK |
| `test_protocol_v4_doc` | 6 | OK |
| `test_v4_w1_plan` | 12 | OK |
| **New `test_r11_delta_sol2`** | **6** | **5 expected review failures, 1 passing brittleness characterization** |

Baseline total: **368 tests pass**, no skips. Targeted test time is well below
the 20-minute limit (under two minutes including the witness replay).
The new module is intentionally red pending lead fixes; its failures are
evidence, not a passing gate. Test transcripts/temporary synthetic Git
repositories are not live validation. No product code was modified.

No full suite, analysis pipeline, real measurements, sealed paths, model
weights, network or native MLX were used. No coordination state was edited.

## Handoff and uncertainty

Changed files: this review, `tests/align/test_r11_delta_sol2.py`, and
`docs/run_reports/2026-11-07-r11-delta-review-sol2.md`. The local review commit
is the handoff; do not push it as an admitted registration.

Next exact step: lead dispositions H1/M1/M2 against the other independent
delta seat, repairs them, then reruns both original witness modules, this new
module and the touched tests against one integrated candidate. Preserve U3,
the final-roster U6 OC, B-window consequence, native WP19/cache/transfer,
continuous mount audit, #694-on-#699 evidence, transcript sealing and
R13/R14/F-C-T/series-manifest holds until their owning gates close.

Outside this sandbox, the lead must run importability-gated tiny-native
`tests.align.test_cache_checkpoint_native` and `tests.align.test_thermal_mlx`,
the opt-in full WP22 integration, and the previously blocked native
termination/census checks from `tests.align.test_r1_round8_exec_review`.
Actual hardware/clock/custody/battery checks and prospective installed R1
deadline validation belong to the clean lead-controlled lane. These reviews
must not interrupt the existing blinded job.

Open judgments: the exact executed-file boundary/acceptable re-registration
cost; the eventual frozen C/T manifest and fit-support bill; how packet role
and freshness assertions are derived; and the scientific qualification of
count-stopped, window-clustered calibration. I have not audited a packet
producer, actual access chronology, installed schedule, live scorer or another
seat's pending simulation, and make no claims about sealed outcomes.
