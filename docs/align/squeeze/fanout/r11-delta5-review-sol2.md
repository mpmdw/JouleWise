# R11 delta5 review — Sol2

2026-11-08. Reviewed `git diff 48a4d1d76..03253edca` on
`align/2026-11-08-v4-r11-delta5-sol2`. **Verdict: ADMIT_WITH_FIXES.**

The meter ordering and delta4 repairs are admitted. No supplied history,
next-window or manifest forgery exercised here reached the installer. The frozen
manifest matches the independent seed-check bytes. The new series integration
has bounded counting and retry defects below. Fix F1–F4 before using the C/T
handoff; prefer doing that before freezing W1's final strict receipt. These
findings do not require interrupting R1 or holding the W1 selection window for a
series redesign. This verdict is code-review admission, not native arm clearance.

Only the requested witness module and this report changed. No product code,
coordination state, measurement record, manifest or receipt was edited.

## Findings

### F1 — HIGH: the committed-record builder counts supplemental diagnostics

`scripts/align_v4_next_arm_packet.py:258–262` counts every eligible benign D row
and returns `len(captured)`. It does not consult `supplemental`, `pool_role` or
`counts_toward`. The calibration history copies these counts at lines 667–674;
the test-window branch independently uses `len(record.captures())` at line 672.
The desk's correct exclusion of ordinals 23/24 is not carried through this path.

Two real-builder/real-series-binding witnesses demonstrate the consequence:

- Two ordinary calibrators plus two supplemental sentinels produce
  `captured_members=4, eligible_benign={spam:3, bank:1}` instead of
  `2, {spam:1, bank:1}`. The C2 arm reaches the synthetic installer.
- With both ordinary captures absent and only the supplemental captures
  present, C1 is consumed and C2 reaches the installer. R20 requires those
  diagnostics to contribute zero captured members, leaving C1 unconsumed.

These are minimal synthetic committed rosters using the builder's existing
short task-pair aliases to isolate counting from F4. They demonstrate the
consumer defect, not a successful native 24-member window. Full ordinary
sentinels are also benign D rows, so a fix must select genuine calibration
members rather than merely subtract two from totals. A fully captured escalated
window also produces 24 captured members and conflicts with the series layer's
22-member bound.

Authenticate every capture, including the supplemental ones; separately derive
the counted regular captures and genuine eligible calibration members from the
committed roster. Apply the regular-capture rule to T histories too. Never drop
supplemental captures from the custody inventory.

Witnesses: `CommittedSeriesTests.test_builder_excludes_supplemental_captures_from_counted_members`
and `test_only_supplemental_captures_cannot_advance_the_slot`.

### F2 — MEDIUM: valid hash-suffixed retries fail the new series binding

`align_v4_series.calibration_rows` returns the previous **slot** (`C1`, line 451),
but `bind_packet` compares it literally with the builder's previous **attempt**
(`C1#1` or `C1#2`, line 518). Both witnesses have a ready real-builder preflight,
then fail only the series binding:

- An explicit zero-capture `C1#1` followed by a proposed `C1#2` refuses C1.
- A zero-capture `C1`, then a captured `C1#2`, refuses the valid C2 arm.

The refusal misleadingly names the same next frozen window the arm requested.
Normalize the previous attempt to its validated slot for this comparison, while
retaining complete attempt IDs and hash-chain ordering. The delta4 U3 scope fix
does not fix this separate comparison. Existing series e2e tests use `C1-a1`
style synthetic history and a packet-builder seam, so they miss the wire mismatch.

Witnesses: `test_canonical_c1_hash_one_zero_capture_retry_can_arm_c1` and
`test_captured_c1_hash_two_retry_can_advance_to_c2`.

### F3 — MEDIUM: rebuilding drops the desk's provisional count ceiling

The series validator enforces final counts <= `desk_eligible_benign` only when
that optional field exists (`align_v4_series.py:442–445`). The builder constructs
history without it (`align_v4_next_arm_packet.py:667–674`) and does not compare
final eligibility against the committed `pilot.extra_checks.series_desk_row`.

A committed desk upper bound `{spam:0, bank:0}`, followed by derived final
counts `{spam:1, bank:1}`, still admits C2 through the real rebuild and binding.
Carry and validate the committed provisional ceiling for each C attempt; reject
increases before the installer. The current dev-packet test of this rule is not
evidence that the production rebuild enforces it.

Witness: `test_final_counts_cannot_raise_committed_provisional_desk_counts`.

### F4 — MEDIUM: generated task-pair names fail final eligibility

The actual frozen W1 roster uses `spam_filter_update` and `bank_transfer_2`.
`WindowRecord.eligibility` instead requires a key in `{spam, bank}` at line 259.
A synthetic committed roster carrying those actual names raises
`ValueError: unknown benign task pair` when its D members otherwise qualify.
Passing the generated collection roster directly to the record reader therefore
blocks the post-W1 eligibility/cohort checks. Normalize the two registered names
explicitly before counting, together with F1's pool filtering.

This predicate predates delta5; the new frozen-series integration exposes its
schema mismatch. I did not inspect an external/native record exporter. If that
exporter rewrites names, it can mask this issue, but no such normalization is
present in the reviewed reader. The synthetic record fixtures use short aliases.

Witness: `test_frozen_roster_task_pair_names_are_accepted_by_final_eligibility`
(currently errors at the exact refusal).

### F5 — LOW: the lower-level 22-member ceiling still accepts 23

`v4_cadence.CAPTURED_MAX` remains 24 and `calibration_stop` accepts a row with
23 counted captures, despite R20's exclusion of the supplemental members even
from captured counts. Its error text still says 0..22. This is inherited code,
not a newly changed guard. Align this count-only predicate with the R20 meaning.

The new series layer independently rejects the same 23-capture history, so this
witness does **not** establish a 23-count arm bypass. Both layers are exercised:
`test_count_only_ceiling_refuses_a_23rd_counted_member` is red, while
`test_series_binding_refuses_a_23rd_counted_member` passes.

## Admitted coverage and limits

- The actual `_arm_and_install` path admits honest synthetic R1→W1 and W1→C1
  controls. The new witnesses use the real packet builder, Git evidence,
  canonical comparison, record/ledger binding, cadence and series binding.
  Host observations, disk verification and the final installer are seams.
- Supplied edits to `series_history`, `next_window_id` and
  `series_manifest_sha256` refuse before the installer. Even a **committed**
  next-plan pointer naming C2 after W1 cannot skip C1: the independent history
  binding refuses it. The wrong-window success in F1 comes from miscounted
  diagnostics, not acceptance of edited packet text.
- `1a2574b49`: the probe returns before the dwell-start stamp; strict monotonic
  ordering is checked and retained. Existing delta4 tests cover the refusal and
  ordering seams. Actual quiet-state acquisition/elapsed dwell and USB behavior
  remain native gates; a timestamp witness does not prove a physical quiet dwell.
- `a67de02f2`: both delta4 witness modules, top-up, runtime and kit checks pass.
  Per-source raw order refuses before merging; retry U3 scope is normalized;
  U3 caches are removed; equality ignores only the named nested tip metadata.
- The manifest bytes equal
  `79777d261:docs/align/v4/seed-check/series_manifest.json`, SHA-256
  `eba6fb0732ec26996a0c63bb679a899b71dc2009474502e59048dd67d764f0c7`.
  No regeneration or scientific ruling was made here.
- Existing R20 tests pass: slots 1–22 unchanged; 23/24 replay W1:5; no held-out
  seed; W1 refuses extras; 62,400 s applies only to the escalated variant.
  The new desk witness preserves the single ordinary U3 comparison and the
  supplied U4 W/df object when supplemental records are added. This checks
  grouping/plumbing; it does not independently validate native cross-window
  U4 aggregation. F1 shows that the builder's m/capture accounting is separate.
- The committed dynamic trace contains **180 paths**, all bound and strict.
  I checked that inventory against the current registration; I did not rerun the
  multi-scenario trace. The touched scenario modules were replayed separately.

## Verification

Python 3.13.18, serial, one module per process. All tests used resolved
`TMPDIR=/private/tmp/jwsol/squeeze/r11-delta5-sol2/tmp`, `JW_WP22_FULL=1`,
`GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`. Baseline subprocesses
also used an isolated host-state directory. No full suite, network, native
measurement, real restricted directory, model weights or block-5 pipeline was
used. Absolute custody/data locators in repository text were not followed.

Each table row ran as `python3.13 -B -m unittest <module>`:

| Module (`tests.align.` prefix) | Tests | Result | Wall s |
|---|---:|---|---:|
| test_measurement_view_identity | 3 | OK | 0.92 |
| test_r11_delta4_sol1 | 11 | OK | 32.99 |
| test_r11_delta4_sol2 | 10 | OK | 18.86 |
| test_r1_round6_power | 25 | OK | 0.79 |
| test_r1_runtime | 33 | OK | 20.03 |
| test_v4_kit | 116 | OK | 6.09 |
| test_v4_next_arm_packet | 28 | OK | 64.39 |
| test_v4_series | 16 | OK | 30.25 |
| test_v4_series_e2e | 9 | OK | 21.17 |
| test_v4_series_r20 | 7 | OK | 1.31 |
| test_v4_topup | 20 | OK | 0.69 |
| test_v4_w1_synthetic | 22 | OK, 1 existing expected failure | 51.96 |

**300 existing tests passed in 249.45 s.** The existing expected failure is
`InjectedWindowTests.test_collector_death_is_x4_and_episode_continues` (the
accepted fail-fast collector behavior).

Final new-witness command:
`python3.13 -B -m unittest -v tests.align.test_r11_delta5_sol2`:
**13 tests, 6 pass, 6 failures, 1 error, 11.178 s**, intentionally exposing the
five findings above. Earlier 12- and 13-test runs took 11.886 s and 12.172 s;
the final refinement permits rejection earlier in the rebuild and supplies
provisional desk ceilings in calibration fixtures. Combined test time was
about **285 s**, under the requested limit. Red contract assertions were not
converted into expected failures; the lead should make them green with fixes.

`python3.13 -B -m compileall -q joulewise tests` and `git diff --check` passed.
The required fixture orphan census returned exit 2 because this sandbox denies
`ps` (`PermissionError: Operation not permitted`). No clean census is claimed;
no process was signalled. The full suite was omitted under the explicit brief.

## Handoff

Witness commits: `836aca0342ceba330de082fbf4c1add261f2c7b6` (the requested test file)
and `75ba5f51b6b448bfb2c20ccb231ef10f690f3f8b` (contract assertion refinement).
The following report commit contains this document. All are local only; no push.
`RUN_STATE.md`, `TASK_QUEUE.md`, the state kernel and `tests/test_gen_state.py`
were preserved. No kernel task was registered.

Next exact step: the lead fixes F1–F4 together in the packet/series integration,
aligns the count ceiling for F5, then reruns this witness module and the touched
packet/series modules individually. Preserve the passing forgery and 23-count
series refusals. No authority or naming decision is requested by this review.

Outside this sandbox, the lead still owns final receipt/admission freshness,
R1 closure, the real meter-before-dwell/quiet-state check, native MLX readiness,
the registered native smoke (<=45 min before the first long C window), and an
observed clean fixture census. No new MLX code/tests were added here, and the
synthetic passes must not be reported as live hardware or arm validation.
