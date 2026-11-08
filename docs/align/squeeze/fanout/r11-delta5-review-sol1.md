# R11 delta5 review — Sol1

2026-11-08. Candidate `03253edca`; reviewed `git diff 48a4d1d76..HEAD`.
Local branch: `align/2026-11-08-v4-r11-delta5-sol1` (provisioned branch).
Authority: the task brief, `docs/align/pilot_protocol_v4.md` R15/R20,
`docs/align/next_arm_packet.md`, the frozen series, and D-161's proportionate
threat model. This is a synthetic review, not live hardware validation.

## Verdict: ADMIT_WITH_FIXES

**Admit the R1→W1 changes on the reviewed synthetic evidence. Hold C/T series
arming until F1–F3 below are fixed.** The ordinary W1 arm, meter/dwell order,
delta4 repairs, manifest preservation and strict closure passed. I found no
reason in this delta to delay W1 for another design round. The post-W1 series
has a demonstrated calibration-count defect and two concrete integration
refusals; those need bounded code repairs before that path is used.

Only the requested witness module and this report changed. Product code,
frozen manifest, raw evidence and coordination state are unchanged. The four
red witnesses are intentional requirements for the lead's fixes; they are
neither skipped nor marked expected failures.

## F1 — required before C/T: production eligibility ignores pool/supplemental roles

Locations: `scripts/align_v4_next_arm_packet.py:258–262,667–674` and
`scripts/align_v4_series.py:499–537`.

The generated plan marks sentinels `role: D`, `pool_role: sentinel`,
`counts_toward: none`. R20 additionally marks ordinals 23/24 `supplemental`.
`series.desk_row` respects those distinctions. The authenticated production
reader, `WindowRecord.eligibility`, instead counts every unexcluded benign D
member and returns the size of the entire capture set. It reads neither
`pool_role` nor `supplemental`. Its counts become `calibration_windows` and
`series_history`; `authenticated_by_rebuild=True` checks their mutual equality,
not their agreement with the desk's provisional counts or frozen pool membership.

Two witnesses demonstrate the consequences:

- `test_sentinel_pool_members_do_not_inflate_m_in_an_admitted_rebuilt_packet`:
  a synthetic C1 has the real 24-member materialized allocation. Two anchors
  have no capture, the two ordinary sentinels are excluded, and two genuine
  spam calibrators are excluded. There are **5 genuine eligible spam and 7
  bank calibrators**. The two supplemental replays supply another two spam
  members to the erroneous reader. Its raw capture total is 22, so the
  separate 22-member binding check does not catch this. The packet reports
  `{spam: 7, bank: 7}` and the **real `_arm_and_install` route admits it**, with
  canonical rebuild equality, no series-binding errors and one fake installer
  call. The final assertion requires `{spam: 5, bank: 7}` and fails.
- `test_supplemental_only_captures_do_not_advance_a_counted_calibration_window`:
  only ordinals 23/24 have captures; all ordinary members are absent/excluded
  and U1 fails. Eligibility is correctly zero, but the production reader says
  `captured_members: 2`; `calibration_stop` consumes **one** counted window.
  R20 requires `(captured_members, attempted) == (0, 0)`, not `(2, 1)`.

Important limit: these counting-isolation fixtures explicitly translate the
plan's task-pair labels to the short labels the existing reader accepts. F2
below prevents an untouched generated roster from reaching this admission
today. Do not fix F2 alone and expose F1. This is not a claim that an unchanged
native C1 currently arms with inflated counts, nor that a complete false
eight-window threshold freeze was executed.

Recommended repair: derive eligible counts from the frozen calibration pool
only; exclude both ordinary and supplemental sentinels from m. Preserve the
exhaustive raw capture inventory for custody, but exclude supplemental members
from the count used for calibration attempts, zero-capture logic and the
22-member ceiling, including the test-history branch at line 672. Reconcile
final eligibility with the desk's upper bounds and keep the existing U1–U3,
X5, no-replacement and finality rules. Do not change the manifest or threshold.

## F2 — required before C/T: generated task-pair names refuse

Location: `scripts/align_v4_next_arm_packet.py:259–260`.

The materializer emits `spam_filter_update` / `bank_transfer_2`; the production
reader requires membership in `{'spam', 'bank'}` and indexes counts directly
with the long name. The unmodified-name witness
`test_generated_pair_names_are_accepted_by_production_eligibility` uses the
generated C1 member metadata, excludes ordinary sentinels to isolate the issue,
and gets **`ValueError: unknown benign task pair`**, rather than 7/7 eligible.

This is an existing reader assumption exposed by the newly joined native
series path, not a regression in delta4. The other series tests use short
labels or the separate synthetic packet producer; they do not join the
generated roster to this record reader. Map the two frozen pair names through
the same explicit mapping as `series.PAIR_KEYS`, while still refusing unknown
pairs. Apply together with F1, not as an independent partial fix.

## F3 — required for series retries: attempt id compared with slot id

Locations: `scripts/align_v4_next_arm_packet.py:380,674` and
`scripts/align_v4_series.py:451,518–519`.

The builder preserves `previous_window: C1#2` and correctly derives the history
entry `{window_id: C1, attempt_id: C1#2}`. `calibration_rows` returns the prior
slot `C1`; `bind_packet` then compares the full prior attempt id against that
slot and refuses.

`test_captured_retry_can_bind_the_next_slot_without_losing_the_attempt_suffix`
commits W1 → C1 (zero capture) → C1#2 (captured), then builds the next C2
packet. Preflight is ready; the real arm refuses before the installer with
`series_binding: C2: triage does not arm the next frozen window (C2)`.
Keep full attempt identity in the record, chain and ruling references, and
normalize only the slot comparison. Do not drop zero attempts or their suffixes
from authenticated history.

## Admitted checks and boundaries

- **Supplied-field forgery:** real R1→W1 and W1→C1 arm controls admit. Edits to
  `next_window_id`, `series_manifest_sha256` or `series_history` fail canonical
  equality and never reach the installer. Selecting C8 against the honest C1
  rebuild fails series binding. The arm retains its own rebuild.
- **22-member ceiling:** an illegal ordinary roster with 23 non-supplemental
  captured members is accepted by the legacy generic count predicate's 24
  maximum, but **refused by the final frozen-series binding** with
  `impossible captured/eligible counts`; no installer call. I did not make a
  22-member binding accept 23. In contrast, F1 lets two supplemental captures
  replace missing ordinary captures while leaving the erroneous total at 22.
- **Sentinel allocation/sizing:** existing R20 tests pass: 23/24 follow 22,
  are exact trajectory replays of W1:5, draw no held-out seed, preserve the
  first 22 rows, and are barred from W1. Ordinary/escalated ceilings remain
  59,520/62,400 s; synthetic maxima are 58,260/61,860 s.
- **U3/U4:** supplemental records join no identical-work group. Adding them
  leaves the one ordinary-sentinel U3 comparison unchanged. With fixed
  cross-window evidence, the desk preserves U4's supplied W=8/df=7. This last
  test does not independently validate an external K-session exporter's
  construction of U4 evidence; no off-repository exporter or measurement data
  was accessed, and I found no local U4-inflation counterexample.
- **Meter/dwell:** the real arm module's ordering witness passes, including
  refusal for a dwell starting at/before the probe end and malformed timestamps.
  This verifies the arm's monotonic ordering record, not native USB behavior or
  the separately pending R16 condition-waits evaluator.
- **Delta4:** both prior witness modules pass: per-source raw time regression
  is refused before merging; retry U3 scope is normalized; U3 admission has no
  `lru_cache`; only the nested informational pushed tip is ignored while other
  nested fields remain authoritative.
- **Frozen bytes/closure:** `git show 79777d261:<manifest>` is byte-identical
  to the checked-in manifest and current `candidate()` output. The committed
  dynamic trace contains 180 executed paths; static/dynamic closure tests pass,
  and both new series artifacts are strict. The complete dynamic trace was
  not regenerated; its focused fresh-process check passed.

## Verification

Each module ran alone in its own process, sequentially. Commands used
`python3.13 -B -m unittest tests.align.<module>`, with
`TMPDIR=/private/tmp/jw-r11-delta5-sol1` (confirmed equal to its realpath),
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and
`GIT_NO_LAZY_FETCH=1`. The batch containing WP22 also set `JW_WP22_FULL=1`;
the full W1 classes executed. No discovery/full-suite command or pytest ran.

| Module | Tests | Result |
|---|---:|---|
| `test_v4_series` | 16 | OK (29.332 s) |
| `test_v4_series_e2e` | 9 | OK |
| `test_v4_series_r20` | 7 | OK |
| `test_v4_next_arm_packet` | 28 | OK |
| `test_r11_delta4_sol1` | 11 | OK |
| `test_r11_delta4_sol2` | 10 | OK |
| `test_measurement_view_identity` | 3 | OK |
| `test_r1_round6_power` | 25 | OK |
| `test_r1_runtime` | 33 | OK |
| `test_v4_kit` | 116 | OK |
| `test_v4_topup` | 20 | OK |
| `test_v4_w1_synthetic` (`JW_WP22_FULL=1`) | 22 | OK, one existing expected failure (WP22 collector-death divergence) |
| `test_v4_cadence` | 30 | OK |
| `test_v4_registration` | 22 | OK |
| `test_v4_executed_closure` | 4 | OK |
| `test_v4_dynamic_closure` | 10 | OK |
| `test_thermal_desk` | 25 | OK |
| `test_r11_delta5_sol1` | 8 | **4 pass; 3 failures + 1 error**, intentionally red, final run 13.387 s |

The 17 existing modules ran 391 tests successfully (including the one established
expected failure). Their wall time was about 278 s. The new witness module ran
twice while refining the overflow control, about 28 s total. Total unittest
time was about **5.1 minutes**, below the brief's 20-minute budget.

`PYTHONPYCACHEPREFIX=/private/tmp/jw-r11-delta5-sol1/pycache python3.13 -m compileall -q joulewise tests`
passed; the final witness file was compiled again after its last edit. No cache
from compileall was written into the repository. `git diff --check` passed before commit.

## Handoff and limits

Changed files:

- `tests/align/test_r11_delta5_sol1.py` — eight executable witnesses, with the
  four unresolved defects intentionally red.
- `docs/align/squeeze/fanout/r11-delta5-review-sol1.md` — this report.

Commit: local review commit `review: witness delta5 series admission gaps`
(the final response supplies its object id). No push.

Next exact step: the lead repairs F1/F2 together in the production record
reader, fixes F3's slot comparison, and reruns the new module plus the focused
series/packet modules one process at a time. Preserve the frozen manifest bytes.
Do not promote the C/T path on the existing helper-only green tests.

No new scientific ruling is requested. No MLX code or native test was added;
this review does not add a new native gate. Existing lead-owned R1 closure and
the documented native smoke before long windows remain outside this sandbox.
No model weights, network, block-5 pipeline, real restricted directory or
external user-data path was accessed. No live hardware or blinding claim is
made. The user expressly reserved RUN_STATE, TASK_QUEUE, state_kernel and
test_gen_state; they were left unchanged, and no kernel task was registered.
