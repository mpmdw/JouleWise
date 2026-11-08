# Timing receipts: Sol delta re-review

2026-11-08. **Verdict: ADMIT_WITH_FIXES.** The three Opus HIGH findings are
corrected. Before integrating with the current v4 head, resolve the two merge
conflicts as described below and update one stale receipt-test fixture. This
is admission of the synthetic software delta; STRICT re-registration and
the existing native/full-desk gates remain required before capture.

## Reviewed objects and integration

- Original HOLD:
  `origin/perf/2026-11-08-timing-receipts-opus-review:docs/perf/timing-receipts-opus-review.md`,
  also preserved in the fix tree at that repository-relative path.
- Fix head: `origin/receipts-fix` at
  `bec6c8ae3` (implementation `ed9fd3ca16fa7c634657be03dc4f0a5c4cf22fc6`).
- Current comparison target: `origin/align/2026-11-08-v4-r11` at
  `03253edcac230e39a0905d24cee317069c4ae50e`, including the newer DCT series.
- Tested scratch merge:
  `4c937e0be8731fd79a7c08832139aed682728767`, parents `bec6c8ae3` and
  `03253edca`. The review branch remains based on the brief's `bcd4fd3c2`;
  production source was not changed there.

The merge is **not clean**. In `joulewise/align/apple/v4_registration.py`,
retain `joulewise/timing_receipts.py` in the closure, preserving coverage of
v4 U3/battery modules. In `scripts/align_v4_session.py`, retain both the
`v4_installer_handoff` timing context and the incoming call
`pilot.install(session, now=now or time.time, **kwargs)`. These are the only
manual source resolutions in the tested merge. The closure/template tests
pass with those resolutions.

## Finding requiring a fix

**MEDIUM — the receipt fixture predates the new series-binding gate.**
On the integrated tree,
`tests.align.test_timing_receipts.ProducerTests.test_v4_disk_gate_and_installer_handoff_close_on_success_and_refusal`
has one error and one failure, across its two subtests. Its mocked
`arm_checks` record has no `next_arm_triage.rebuilt_packet`. The current
`_arm_and_install` correctly refuses it with
`series_binding: W1: the arm could not rebuild the packet`, before either
the disk or installer boundary is exercised. The other 20 tests pass.

Update this isolated fixture with a synthetic rebuilt packet and a scoped
`scripts.align_v4_series.bind_packet` seam, or use the existing valid series
fixture. Keep the production binding gate intact. The real series arm route
is separately exercised by `tests.align.test_v4_series_e2e`.
An in-memory trial of the minimal fixture update passed both subtests (one
focused test, 0.135 s); the shipped test was left unchanged for the lead.

## Delta verification

**HIGH-1 — closed.** Separate Python processes ran the actual full W1
synthetic producer against the current v4 target and the scratch merge,
including injected timeout/fault cases. `joulewise.cli.validate_bundle`
returns `[]` for **all 20 bundles on each tree**: 18 W1 members and two pilot
references. The controller now buffers timing rows as RuntimeEvents, preserves
the injected float timestamp, and sorts them with ordinary events. Both
finalize boundaries precede `run_finalized`. The validator is unchanged.
This is structural validity, not strict physics/uncertainty eligibility.

**HIGH-2 — closed.** `_timing_journal` appends to existing `night.log` with
`O_APPEND` and without `O_CREAT`; an absent log leaves rows in memory. It has
no child-stage-journal open/write. The unchanged Opus witnesses pass. The
cross-tree helper also compares the complete serialized session-structure
record and actual harvest yield JSON, stage-journal result, collection
presence and flags byte for byte on happy and pre-chain-refusal fixtures.
Both paths match. On refusal the journal stays absent, `stage_journal` stays
`None`, presence stays `True`, and flags stay empty. Neither
`session_structure.py` nor `b5/harvest.py` changed, so filters are unnecessary.
These desk fixtures use an empty synthetic member roster, not a production
harvest.

**HIGH-3 — closed.** Static executed-closure binding (4 tests), dynamic
closure (10, including a fresh minimal W1 trace), registration (22), and the
specific driver reason-code lint all pass on the current-head integration.
`timing_receipts.py` is bound and strict, and is in the committed dynamic
trace. A pending template is not a signed registration.

**Capture identity.** The two trees produce the same **286-file** capture
set and equal SHA-256 for every normalized file. The common helper supplies
synthetic battery/source-provenance seams and formats tracebacks to retain
exception types/messages while removing source locations. Normalization
removes RSS and source-tree paths; only the added timing-boundary lines are
stripped. No clocks, gate results, numeric metrics or ordinary events are
normalized. Unlike the old same-tree emit-disabling test, this comparison
uses distinct source trees and the **current** v4 base.

**Measurement safety.** The full producer run emits **68** member receipts:
28 G0 boundaries while sampling is active and 40 finalize boundaries.
A Python audit hook scoped to `Writer.emit` observed zero `open`, `os.*`,
`subprocess.*`, `_thread.*` or `socket.*` effects. Separate `os.fsync` and
`os.write` wrappers counted zero calls in that scope. The existing focused
marker test also forbids file opens, fsync, thread starts and process starts.
Static inspection confirms memory-only member callbacks and no sample/token
loop instrumentation. This audits receipt effects, not every existing native
collector operation, and makes no native observer-cost claim.

**Arm placement.** v4 install buffers markers until the operation exits and
then writes to its existing CLI stdout. Packet rebuild and meter-probe ends
precede the recorded dwell start in the executed receipt test. Disk and
installer contexts are in the pre-chain install route; the driver's launch
barrier closes before the `G` collection-release byte. The hazard dwell start
marker is above `dwell_started`, the boot read and the first clock sample.
These boundaries do not add writes inside measured members. Chain-settle
receipts run outside members and replace the existing sleep process; the
existing chain tests cover the rendered path.

**Reader completeness — closed for this synthetic.** The corrected reader
reads the producer's own member events/episode records, without invented
external spans. Across all 18 W1 members it reports **0 ns unattributed** in
an observed envelope of **12,376.133600019 s**, including e08's G0 timeout.
It retains 18 `paired_clock_bracket_only` diagnostics and the deliberately
unclosed `measured_run` stages for e14/e18. Zero unknown time does not erase
those diagnostics or establish native timing completeness.

## Commands and results

Repository targets and the scratch audit used
`python3.13 -B -m unittest TARGET`, invoked sequentially, one module per
process (the dynamic-closure test runs its own minimal W1 child trace), with `JW_WP22_FULL=1`,
`PYTHONDONTWRITEBYTECODE=1`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, `GIT_NO_LAZY_FETCH=1`, and realpath
`TMPDIR=/private/tmp/jwsol/squeeze/receipts-rereview/tmp`. Host-state fixtures
were directed to scratch as well. The full suite was expressly not run.

| TARGET | Result |
|---|---|
| `tests.align.test_timing_receipts` | 21 tests; 1 error + 1 failure in the single stale fixture above |
| Scratch `rereview_checks` module | 5 passed: current-base 20-bundle validation, 286-file identity, desk identity, audit, reader |
| `tests.align.test_timing_receipts_opus_witnesses` | 3 passed |
| `tests.align.test_window_timing` | 28 passed |
| `tests.align.test_v4_executed_closure` | 4 passed |
| `tests.align.test_v4_dynamic_closure` | 10 passed |
| `tests.align.test_v4_registration` | 22 passed |
| `tests.test_run_night.NightDriverTests.test_driver_reason_codes_are_registered_and_are_not_literal_call_sites` | 1 passed |
| `tests.align.test_v4_w1_synthetic` | 22; OK, 1 existing expected failure |
| `tests.align.test_v4_next_arm_packet` | 28 passed |
| `tests.align.test_v4_series_e2e` | 9 passed |
| `tests.test_b5_chain` | 25 passed |

The additional focused fixture trial used
`python3.13 -B /private/tmp/jwsol/squeeze/receipts-rereview/tmp/fixture_adaptation.py`.
There were 179 top-level test executions including that trial, approximately
4.1 minutes of summed unittest durations, below the 20-minute budget.

`python3.13 -B -m compileall -q joulewise tests scripts` and
`git diff --check` pass. Raw synthetic results, audit harness and command
logs are retained under the scratch TMPDIR. Cross-tree result JSON SHA-256:
`0a49ab56478a5ee9f84953495844c43c8dee55a47510cd77cbd886904ea5dc6e`.

## Limits and next step

No sealed study records, real measurements, model weights, network, analysis
pipeline or quiet-machine campaign were used. Native MLX was not run. The
lead still owns native follow-ups (including
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`
and `python3.13 -B -m unittest tests.hazards.test_arm`, separately outside this
sandbox), STRICT re-registration and the full-desk gate. Crash loss of
buffered receipts, R16 integration and off-machine completion coverage remain
the disclosed limits from the fix handoff, not newly verified live behavior.

Next exact step: integrate using the two conflict resolutions above, repair
the stale synthetic fixture, rerun `tests.align.test_timing_receipts`, and
complete the existing registration/native gates. No unresolved study-policy
question was found. Coordination files remain lead-owned and untouched.
