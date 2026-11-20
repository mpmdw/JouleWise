# PR #795 audit 3: stage-1 admission closed by construction

Audit 3 found five shapes no pinned writer produces that stage 1 admitted (a failed `restore` with span `rc` 0,
an unregistered receipt schema, an unknown receipt member, an explicit `error: null`, a `phase_start` without
metadata). Three fix rounds had closed the audited cases and the next audit found the next five, because stage 1
checked a few members of a few files. An independent seat then derived the three pinned writers' full output
grammar and froze an acceptance suite (`SUITE.sha256` `6b541b4462edde5269255bcd7bce4cade071c54b7efaed71d5d76e99b17dd37f`,
33 entries): 101,889 generated cases. At `237124f0d` 23,268 passed and 78,621 failed. This round adopts it byte for
byte and replaces the pre-pass with one validator built from the same grammar.

## What changed

| Piece | Where | Role |
| --- | --- | --- |
| Frozen suite | `tests/cadence/test_interim_admission_closure.py`, `tests/cadence/interim_admission/` | Copied byte for byte and verified against `SUITE.sha256`. Never edited |
| Strict decoder and closed-shape primitives | `joulewise/cadence_looks/admission_shape.py` | UTF-8, no duplicate member, no nonfinite number, no second document; a boolean is not an integer, an integral float is not an integer, text is never a number. A refusal names a file and a member, never a value |
| Receipt, step, soak, leg grammar | `joulewise/cadence_looks/admission.py` | Mirrors `scripts/cadence_legs_runner.py` and `joulewise/cadence/legs.py` at `b4b6aeb19`, `2d347f721`, `6e9d42f1d`; cross-file agreement; the registered kit and its seeded legs |
| Bundle journals | `joulewise/cadence_looks/admission_journals.py` | Config, events, salvage (at `outputs/` only), turns, thermal journal. No tool phase on the registered task |
| Registered kits | `joulewise/cadence_looks/admission_kits.py` | Generated from `docs/process/cadence/kits/*.json` and the filler registry; a test regenerates it |
| Generated spans | `joulewise/cadence_looks/admission_synthetic.py` | The synthetic generator's own closed shape. A roster is all one or all the other |
| One call site | `scripts/cadence_look_run.py` `validate_runtime_bundles` | Runs over every rostered span before any trace, telemetry or meter file opens and before the reservation, in both stages |

The old pre-pass (`_check_event`, `_check_values`, `_writer_json`) and `inclusion_34.check_writer_receipt` are
removed: one validator, one source of truth. The synthetic generator now writes writer-shaped bundle journals and soak
references, so a generated span passes the same journal grammar as a written one. The five admission modules are
pinned in the draft manifest and recorded in stage 1's code set.

## Results

| Check | Result |
| --- | --- |
| Frozen matrix, real two-stage CLI, 8 shards plus the five audit-3 reproductions | 101,889 of 101,889 pass: 101,886 under the suite's expectations, 3 under the corrected expectations |
| The three corrected cases | Pass the full positive `signal-130` CLI check, see below |
| Audit-3's five reproductions | Pass: each exits 2 before any protected open |
| F1 to F5 | Pass (84 of 84) |
| Accounting | A separate CI job reads the eight shard ledgers and fails unless every distinct ID is in exactly one ledger and passed |
| In-process projection over the same corpus | `tests/cadence/test_interim_admission.py`, numpy-free |
| CI | The matrix runs in its own eight-shard job; the module is an exclusive module in `scripts/test_timings.json` |

## Existing tests

The closed grammar refuses, earlier, custody that several older tests mutated into shapes no writer produces. Each
still exercises its own later check, using a mutation the grammar admits:

| Test | Was | Now |
| --- | --- | --- |
| `CustodyBinding.test_another_copy_refuses_before_energy` (receipt) | Added a member | Re-encodes the receipt with another layout: admitted (F3), but not the bytes stage 1 read |
| `CustodyBinding.test_changed_operational_sources_refuse_before_later_readers` | Appended a space to each file | Prepends a space (a cut final record refuses; leading layout does not) |
| `SupersededStage1.test_a_rerun_authenticates_both_kept_files_and_unchanged_source` | Changed `sensors.Tf08` only | Changes the cleaned value and its raw reading together |
| `Admission.test_committed_verdicts_cannot_admit_changed_meter_or_journal` | Deleted journal rows | Deletes them and renumbers `seq`, as the collector would have written it |
| `Admission.missing_start_fan` (two tests) | Nulled a fan reading | Stale `pm_observed_ns` on the start reading. A failed read sets the row's `error` and the reader drops error rows, so a null fan was never the writer-shaped way to lose the start state |
| `Admission.test_rl174_undecodable_span...` | `leg_status` `failed` | `incomplete` (a registered value) |
| `ColdSeatFixes.test_m13_custody_carries_the_synthetic_flag` | Stripped the generator's flag | Asserts that the unflagged receipt now refuses at admission |

The previous round's `WriterShapes` class, the receipt-code tests and `inclusion_34.check_writer_receipt` are
removed: the frozen matrix and `test_interim_admission.py` supersede them. The both-stages CLI test is rewritten around
the new messages and keeps its purpose: stage 2 refuses the same shapes before the reservation.

`test_look_manifest.FreezeCommit.test_the_look_s_tests_pass_on_the_frozen_tree` runs every look module in one
subprocess with a 1,800 s ceiling. On this host (load average above 200 from other lanes) it times out before and after
this round; the changed modules pass individually on a frozen copy of the tree.

## The three corrected cases (resolved NEEDS_SPEC)

`missing-key/<pin>/interrupt-after-result/runner_receipt.json/steps/13/result/remove` for `b4b6aeb19`, `2d347f721` and
`6e9d42f1d`. The case removes the soak step's `result` from the interrupted-after-result receipt, leaving `rc` 130,
`error` `SystemExit: 130` and no result, and the frozen suite expects refusal. The same suite admits that exact shape as
`signal-130`; the two receipts differ only in step timestamps (the soak step spans 1,800 s in one and 0 s in the
other). I reported that no grammar can satisfy both.

The lead ruled on 2026-11-20: under RL-184 section 3.3 each pinned writer can produce that receipt. A SIGINT before the
writer stores `result` makes its exception handler record `rc` 130 and `error` `SystemExit: 130`, and its `finally`
block record `ended`; that can happen 1,800 s into the soak. The three cases are re-expected as `ADMIT` and the existing
`signal-130` grammar applies, including every other receipt check.

* The frozen suite and corpus are unchanged byte for byte. `tests/cadence/interim_admission_frozen.sha256` holds the
  suite's own 25 test-side hash lines verbatim; CI recomputes each file's hash, requires the corpus directory to hold
  nothing else, and recomputes the suite's published case-ID and expectation hashes.
* The correction lives outside the frozen files: `tests/cadence/interim_admission_corrections.json` (version 1) names the
  three IDs and the hash of the corrected expectations. A correction never removes a case; it changes what the case is
  judged against, and CI fails if a corrected case is absent, already admitted, or no longer changes its expectation.
* A corrected case is judged ADMIT by the suite's own assertions for an admitted case on the same mutation in the
  positive roster, plus the ruling's terms stated outright: stage 1 exits 0 and writes its output, preflight returns
  before the first protected open, and there are zero response reads, zero reservations and zero public writes.
* `tests/cadence/interim_admission_open.json` (the held-open list) is removed. There is no held-open case.
* The `interim-admission-accounting` job downloads the eight shard ledgers and fails on a missing or duplicate ID, a
  case that did not pass, a case judged on the wrong expectation, a ledger from the wrong shard count, or a shard that
  is absent. It reports `101,886` judged under the original expectations and `3` under the corrected ones.
* `tests/cadence/test_interim_admission.py` covers the corrected shape (it is the signal-130 receipt with other
  timestamps; every other receipt check still refuses), the frozen-hash check, the case-list and correction checks, and
  every accounting failure.
