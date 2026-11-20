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
| Frozen matrix, real two-stage CLI, 8 shards plus the five audit-3 reproductions | 101,886 of 101,889 pass |
| The three open cases | Held open by id, see NEEDS_SPEC below |
| Audit-3's five reproductions | Pass: each exits 2 before any protected open |
| F1 to F5 | Pass (84 of 84) |
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

## NEEDS_SPEC: three cases no grammar can satisfy

`missing-key/<pin>/interrupt-after-result/runner_receipt.json/steps/13/result/remove` (three pins). The case removes
the soak step's `result` from the interrupted-after-result receipt, leaving `rc` 130, `error` `SystemExit: 130` and no
result, and expects refusal. The same suite admits that exact shape as `signal-130`, and GRAMMAR.md says an interruption
"can leave ... an error without a result". The mutated receipt and the admitted `signal-130` receipt differ only in
step timestamps (the soak step spans 1,800 s in one and 0 s in the other), and a real signal 1,800 s into the soak
leaves exactly the former. Refusing it would refuse a producible receipt. `tests/cadence/interim_admission_open.json`
holds the three ids open; the CI runner fails if a held-open case starts passing, so the list cannot go stale.
