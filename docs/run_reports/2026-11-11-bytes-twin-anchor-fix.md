# BYTES twin: operative decode anchor fix (RL-80 item 1)

2026-11-11. Fix seat on `fix/2026-11-11-bytes-twin-anchor`, based on
`df4c73e55c0fb0ad7b36f4914e800c6833759d61`. Local commit only; no push.

## Access and authority

Read RL-80 verbatim from `origin/audit/2026-11-10-fable`, and the attribution
report at `205734f27b872f7b3fc6a117c8dc428db3cedf14`, together with code,
the registration and its governing arithmetic. No probe output was opened.
No real BYTES export, predictions, key, withheld store, measurement, archive,
custody or night path was opened. Every executed fixture is synthetic and
local to the permitted temporary directory. No network, model download,
measurement, MBP operation or full test suite was used.

**Access-scope exception requiring lead adjudication.** The final automated
integrity check opened `RUN_STATE.md`, `TASK_QUEUE.md` and
`docs/process/state_kernel.json` as bytes and compared them with their base
commit blobs. It printed only that the comparisons passed; none of their
contents was printed, parsed or supplied to the model. Nevertheless, those
reads exceeded this fix seat's explicit read allowlist. This run must not be
described as strictly read-set compliant. The exception does not establish
that any additional outcome was seen, and this seat does not adjudicate its
RL-80 blinding consequence. No further reads of these files were performed.

The estimator is untouched: `joulewise/bytes_analysis.py` remains SHA-256
`18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`.
Flags and all real study data are untouched. Coordination files and kernel
tasks are untouched. Synthetic fixture generation and tests are changed.

## Changes and registered sentences

1. `scripts/bytes_twin.py` reads `calibration.operative_bound_s` from each
   archive's existing `derived/b6-acceptance.json`. Registration §16:
   “The analysis also reads the harvest's operative timing bound
   (`calibration.operative_bound_s` in `derived/b6-acceptance.json`, evaluated
   by `joulewise/b6/calibration.py`; Addendum 1 item 4) and never recomputes a
   calibration bracket.” No bracket is recomputed or cached.
2. The twin independently sums the archived interval-support trace's
   manifest rails, places them on the archived bounded clock anchor, and
   re-integrates the decode phase over all four independent-edge corners
   and all common-shift breakpoints. Coordinates are relative to a shared
   origin. It includes the operative bound and wall-minus-monotonic span
   at each edge, plus the member's common clock uncertainty. Registration
   §7's rails term is “the run's rails anchor-shift bound (block-5 plan §4
   step 4, its first kind, re-derived under the session's operative timing
   bound from `joulewise/b6/calibration.py`; Addendum 1 item 4)”. Block-5
   §4 step 4 specifies “the largest change in the energy assigned to the
   member's phase” and the `max_abs_delta_j` envelope “for the phase”, from
   the summary “reduced again, in memory, under b”. The twin uses its own
   overlap implementation, with no estimator or other `joulewise` import.
3. At stages 1 and 2, `_member` uses that independent decode term for rails
   and rest, so the existing B, interval, attribution-floor and fit-weight
   paths inherit it for every selection and basis. Registration §7 gives
   rest “rails anchor-shift bound + u + v”. Missing operative evidence
   cannot fall back to the export column. The blinded path retains §11's
   “from the blinded export's columns (no archive, key or meter reads)”.
   Per-run join status is diagnostic; no flag code or flag-selection logic
   changed.
4. `tests/fixtures/bytes/campaign.py` adds `anchor_profile` campaigns with
   a nonzero envelope, decode/whole-window distinctions, a 10 ms member
   bound and operative bounds of 54.531 and 74.531 ms, and 20 ms waveform transitions
   that the operative edge motion crosses. The existing labelled synthetic
   estimator oracle remains explicit. Registration §12: “Method differences
   must not hide under the bar”. Both new campaigns use R6's twelve sessions,
   all ten models and 50 runs per model per pass, including the post-commit
   blinded-store stage. The twin's own fixture gains explicit
   synthetic clock evidence and interval traces for the same §7 path.
5. `tests/test_bytes_agreement.py` runs both new profiles through the
   existing CLI stage chain and comparer. A mutation restoring the original
   `_member` export-column choice must disagree with the unchanged estimator
   above §12's bar. `tests/test_bytes_twin.py` adds the block-5 worked
   example, interior-breakpoint, operative-bound, invalid-input, blinded-path
   and bundle-immutability checks. Its reducer integration test stubs only
   clock/calibration reconstruction; the estimator's output-free reducer seam
   and phase-envelope arithmetic execute normally. This is synthetic
   arithmetic evidence, not live hardware or calibration validation.

## Failing-first evidence

The exact original twin source was loaded with
`git show df4c73e55:scripts/bytes_twin.py` and run against the new stage-1
regression on a tiny synthetic world. It failed as required:

- old anchor: `1.100020757207877` J;
- operative decode oracle: `2.200404896052572` J;
- difference: `1.1003841388446949` J;
- §12 bar used by the test: `0.015288075217866402` J.

The six focused tests then passed with the fixed twin in 23.786 s, including
the unchanged estimator's operative reducer seam and unchanged bundle bytes.
The tiny harness populated the registered manifest but collected only one
fit model; it is not represented as a full-size agreement campaign.

## Verification and campaign results

**Partial verification; not an all-campaign pass.** Long runs were stopped
near the requested roughly 20-minute total test budget; exact cumulative time
across interrupted setups was not recorded. An asynchronous question asking
whether to extend it had no answer before handoff. Full module verification
and the complete campaign matrix remain required.

Commands used `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1` and Python
3.13.18, serially:

| Command / harness | Result |
|---|---|
| Original-source unittest harness, `AnchorEnvelopeTests.test_stage1_uses_operative_decode_envelope` | One expected failure, 3.366 s; exact old source, numbers above. |
| Focused `AnchorEnvelopeTests` unittest harness with the tiny setup described above | Six passed, 23.786 s. |
| `python3.13 -u -B -m unittest tests.test_bytes_agreement.AgreementTests.test_nonzero_decode_anchor_campaigns` with final R6 geometry | `anchor_narrow` completed; run interrupted during `anchor_wide` setup. Overall method is **incomplete**, exit 130. |
| `python3.13 -B -m unittest tests.test_bytes_agreement.FenceTests` | Three passed, 0.436 s; standard-library-only fence, execution with `joulewise` unavailable, exact block-5 t table. |
| Pure-arithmetic unittest harness: `ConstantsTests`, `BatteryWorkedExamples`, `StudentTTests`, `PhaseEstimateTests`, `Neg8Tests`, `RegressionTests`, `H1Tests` | 25 passed, 0.200 s; unused module-wide WORLD setup omitted. Separate Decimal checks confirmed both final operative bounds and empty calibration exclusion lists. |

Completed campaign receipt:

| Campaign | Compared | Equal | Under bar | Above bar | Diagnostics / different |
|---|---:|---:|---:|---:|---:|
| `anchor_narrow`, all CLI stages | 269,017 | 263,341 | 5,676 | **0** | 84,130 / 646 |

On this same campaign, restoring the old export-column anchor produced
**48 anchor fields above §12's bar**, the smallest difference **5.301 times
its bar**, against the unchanged estimator. The mutation test also found no
above-bar mean, h or duration difference. This supplies the requested
old-versus-estimator / fixed-versus-estimator regression evidence for the
completed nonzero campaign.

The final wide fixture uses pre/post 60/50 ms, yielding 74.531 ms, inside
the synthetic registration's 92 ms stop line. Its complete CLI run is pending.
An earlier in-flight wide setup used 130 ms and was interrupted; it is not
claimed as validation of the final fixture. The narrow branch's inputs and
operative bound were unchanged by this adjustment.

The working-tree campaign map had 17 existing named cases; the two additions
make 19. The historical registration's nineteen-campaign receipt is not
substituted for a fresh run. The complete current matrix remains pending:
`bytes`, `resident`, `time`, `defects`, `minimum`, `edge_locked`, `withheld`,
`invalid_anchor`, `marker_incomplete`, `late_start`, `polls_only`,
`header_closed`, `empty_payload_n`, `replayed_batch`, `replayed_tail`,
`first_batch_tail_replayed`, `compressed`, `anchor_narrow`, `anchor_wide`.
Only `anchor_narrow` has a completed fresh full-stage receipt here.

Interrupted attempts included grouped-campaign setup, the twin's default
multi-world setup for the original-source check, an initial full agreement
module attempt, and a proposed production fixture check rebuilding unrelated
calibration pulse fits. That last check was replaced by the focused reducer
seam test above. Interrupted setup is never counted as a passing test.

The five changed Python files parse and passed targeted `py_compile`.
`git diff --check` passed. `scripts/test_timings.json` has exactly one inserted
provenance line: removing that line reproduces its original bytes exactly;
no unmeasured whole-module scheduling weight was added. Estimator and
protected coordination-file diffs are empty.

## Remaining lead gates

**NEEDS_RULING — read-set compliance.** Question: how should the nondisplayed
coordination-file byte comparison affect this seat's RL-80 qualification?
Options: accept it with a recorded exception and cold review, or require
clean-seat validation before relying on the fix. Recommendation: treat this
commit as an implementation artifact requiring clean-seat cold review and a
lead ruling. Blocked work: claiming strict fix-seat read-set compliance or
admitting the fix on that basis. The implementation and local commits remain
available for review.

**NEEDS_RULING — verification budget.** Question: may the remaining targeted
verification exceed the roughly 20-minute total limit? Options considered:
retain that limit with an explicitly incomplete handoff, or allow the full
targeted matrix to run longer. Recommendation: run the remaining commands
on an authorized `[AGENT]` seat with an explicit larger budget. Blocked work:
full module and all-campaign verification, not the code change or local commit.

Exact remaining commands (one at a time; no full suite):

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest tests.test_bytes_agreement
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest tests.test_bytes_twin
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest tests.test_bytes_stage1
```

`tests.test_bytes_stage1` was not run here. No MLX code or MLX tests changed;
there is no new native MLX test requirement from this fix.

RL-80 requires cold review. The flags item still awaits its separate ruling.
This seat cannot inspect the real stage-1 outputs: the authorized lead must
rerun the real fit-set comparison after the relevant fixes, and record that
the unchanged estimator's new predictions are byte-identical to the retained
uncommitted predictions (`a6cb172c…5f19`, attribution report). This report
does not claim that real-data agreement or byte identity has been verified.
